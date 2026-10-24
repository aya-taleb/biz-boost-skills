#!/usr/bin/env python3
"""Pick today's LinkedIn invites from real leads, inside a daily limit, and track them.

Nothing here touches LinkedIn. It reads a CSV, writes a CSV, and prints a list.
The user sends every invite and message by hand.

Commands:
  pick   choose who to invite today from sales/leads.csv (biz-boost's lead-gen writes it).
         Leads with no linkedin_url are skipped, with the reason shown.
  mark   log that the user sent something (invite, first message, follow-up); with
         --leads, also set that lead's status and last_contact in sales/leads.csv
  due    list follow-ups that are due today or overdue
  count  count characters in an invite note (limit 200)

Usage:
  python3 dmqueue.py pick  --leads sales/leads.csv --business lunch-lane --log outreach.csv \
                           --limit 5 [--date 2026-10-23]
  python3 dmqueue.py mark  --log outreach.csv --name "Dana Ruiz" --company "Northwind" \
                           --step invite [--leads sales/leads.csv --business lunch-lane] [--date 2026-10-23]

sales/leads.csv columns (shared layout, CONVENTIONS section 5):
  business_slug,name,company,role,email,linkedin_url,instagram_handle,website,city,
  source,source_url,fit_score,fit_reason,status,last_contact,notes
Older files with other column names still work through the aliases below.
  python3 dmqueue.py due   --log outreach.csv [--date 2026-10-23]
  python3 dmqueue.py count --text "Saw your post on ..."

Daily limit: default 5, weekly stop 50. LinkedIn publishes no number. Public sources observe a ceiling of
about 100 invites a week for most accounts (checked 2026-10-23, see
references/limits.md). 5 a day and 50 a week stay well under that, so each invite can be personal.
Standard library only.
"""
import argparse
import csv
import datetime as dt
import os
import sys

NOTE_LIMIT = 200
DEFAULT_LIMIT = 5
WEEKLY_CEILING = 50
LOG_COLUMNS = ["date", "name", "company", "step", "next_step", "next_date", "note"]
STEPS = ["invite", "accepted", "message", "follow-up-1", "follow-up-2", "replied", "stopped"]
NEXT = {
    "invite": (None, None),           # wait for accept
    "accepted": ("message", 1),       # first message a day after accept
    "message": ("follow-up-1", 4),
    "follow-up-1": ("follow-up-2", 6),  # 10 days after the first message
    "follow-up-2": (None, None),
    "replied": (None, None),
    "stopped": (None, None),
}

# column names we accept in leads.csv, first match wins
LEADS_COLUMNS = ["business_slug", "name", "company", "role", "email", "linkedin_url",
                 "instagram_handle", "website", "city", "source", "source_url", "fit_score",
                 "fit_reason", "status", "last_contact", "notes"]
ALIASES = {
    "business": ["business_slug", "business slug", "business_id"],
    "name": ["name", "full_name", "full name", "contact", "person"],
    "first_name": ["first_name", "first name", "firstname"],
    "last_name": ["last_name", "last name", "lastname"],
    "company": ["company", "organization", "organisation", "account"],
    "role": ["role", "title", "job_title", "job title", "position"],
    "linkedin": ["linkedin_url", "linkedin", "linkedin url", "profile_url", "profile"],
    "fit": ["fit_score", "fit", "score", "fit score"],
    "reason": ["fit_reason", "reason", "why", "trigger"],
    "notes": ["notes", "note"],
    "status": ["status", "stage"],
    "source_url": ["source_url", "source url"],
}
NEVER = {"do-not-contact", "do not contact", "dnc", "unsubscribed", "opted out"}
# statuses from the shared layout that mean "already talking or finished": not a new invite
IN_PROGRESS = {"contacted", "replied", "meeting", "won", "lost", "customer", "invited", "stopped"}


def today(value=None):
    return dt.date.fromisoformat(value) if value else dt.date.today()


def pick_col(headers, key):
    low = {h.strip().lower(): h for h in headers}
    for alias in ALIASES[key]:
        if alias in low:
            return low[alias]
    return None


def read_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return rows, reader.fieldnames or []


def normalise_leads(rows, headers):
    cols = {k: pick_col(headers, k) for k in ALIASES}
    leads = []
    for row in rows:
        get = lambda k: (row.get(cols[k]) or "").strip() if cols[k] else ""
        name = get("name") or (" ".join(p for p in (get("first_name"), get("last_name")) if p))
        if not name:
            continue
        try:
            fit = float(get("fit")) if get("fit") else None
        except ValueError:
            fit = None
        leads.append({
            "name": name, "company": get("company"), "role": get("role"),
            "linkedin": get("linkedin"), "fit": fit, "reason": get("reason"),
            "notes": get("notes"), "status": get("status").lower(),
            "business": get("business").lower(), "source_url": get("source_url"),
        })
    missing = [k for k in ("company", "reason", "linkedin") if not cols[k]]
    return leads, missing


def key(name, company):
    return (name.strip().lower(), company.strip().lower())


def read_log(path):
    rows, _ = read_csv(path)
    return rows


def week_start(day):
    return day - dt.timedelta(days=day.weekday())


def sent_counts(log, day):
    invites = [r for r in log if r.get("step") == "invite"]
    today_n = sum(1 for r in invites if r.get("date") == day.isoformat())
    start = week_start(day)
    week_n = 0
    for r in invites:
        try:
            d = dt.date.fromisoformat(r.get("date", ""))
        except ValueError:
            continue
        if start <= d <= day:
            week_n += 1
    return today_n, week_n


def pick(leads, log, day, limit, business=None):
    touched = {key(r.get("name", ""), r.get("company", "")) for r in log}
    today_n, week_n = sent_counts(log, day)
    room = max(0, min(limit - today_n, WEEKLY_CEILING - week_n))
    skipped = []
    pool = []
    business = (business or "").strip().lower()
    for lead in leads:
        k = key(lead["name"], lead["company"])
        if business and lead["business"] and lead["business"] != business:
            continue  # another business's lead; not counted, not shown
        if lead["status"] in NEVER:
            skipped.append((lead["name"], "do-not-contact"))
            continue
        if business and not lead["business"]:
            skipped.append((lead["name"], "no business_slug; check which business it is for"))
            continue
        if k in touched:
            skipped.append((lead["name"], "already in outreach log"))
            continue
        if lead["status"] in IN_PROGRESS:
            skipped.append((lead["name"], "status is '%s'" % lead["status"]))
            continue
        if not lead["reason"]:
            skipped.append((lead["name"], "no reason to reach out yet; research first"))
            continue
        if not lead["linkedin"]:
            # No profile link means the user would have to search LinkedIn by name and may
            # invite the wrong person. Ask for the link, or reach them another way.
            skipped.append((lead["name"], "no linkedin_url; add their profile link, or use lead-email"))
            continue
        pool.append(lead)
    pool.sort(key=lambda l: (-(l["fit"] if l["fit"] is not None else -1), l["name"]))
    return pool[:room], pool[room:], skipped, today_n, week_n, room


def add_log(path, row):
    exists = os.path.exists(path) and os.path.getsize(path) > 0
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_COLUMNS)
        if not exists:
            writer.writeheader()
        writer.writerow({c: row.get(c, "") for c in LOG_COLUMNS})


def mark(path, name, company, step, day, note=""):
    if step not in STEPS:
        raise ValueError("step must be one of: " + ", ".join(STEPS))
    nxt, gap = NEXT[step]
    row = {
        "date": day.isoformat(), "name": name, "company": company, "step": step,
        "next_step": nxt or "", "next_date": (day + dt.timedelta(days=gap)).isoformat() if gap else "",
        "note": note,
    }
    add_log(path, row)
    return row


def update_lead(path, name, company, status, day, business=None):
    """Set status and last_contact for one lead in the shared leads.csv. Returns True if found."""
    rows, headers = read_csv(path)
    if not rows:
        return False
    cols = {k: pick_col(headers, k) for k in ALIASES}
    headers = list(headers)
    for col in ("status", "last_contact"):
        if col not in headers and not (col == "status" and cols["status"]):
            headers.append(col)
    status_col = cols["status"] or "status"
    found = False
    for row in rows:
        get = lambda k: (row.get(cols[k]) or "").strip() if cols[k] else ""
        rname = get("name") or " ".join(p for p in (get("first_name"), get("last_name")) if p)
        if key(rname, get("company")) != key(name, company):
            continue
        if business and get("business") and get("business").lower() != business.lower():
            continue
        row[status_col] = status
        row["last_contact"] = day.isoformat()
        found = True
    if found:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=headers)
            w.writeheader()
            for row in rows:
                w.writerow({h: row.get(h, "") for h in headers})
    return found


LEAD_STATUS_FOR_STEP = {"invite": "contacted", "accepted": "contacted", "message": "contacted",
                        "follow-up-1": "contacted", "follow-up-2": "contacted",
                        "replied": "replied", "stopped": None}


def due(log, day):
    latest = {}
    for r in log:
        latest[key(r.get("name", ""), r.get("company", ""))] = r
    out = []
    for r in latest.values():
        nd = r.get("next_date", "")
        if r.get("next_step") and nd:
            try:
                if dt.date.fromisoformat(nd) <= day:
                    out.append(r)
            except ValueError:
                continue
    return sorted(out, key=lambda r: r["next_date"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pick")
    p.add_argument("--leads", required=True)
    p.add_argument("--business", help="active business slug; only its leads are picked")
    p.add_argument("--log", required=True)
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p.add_argument("--date")
    m = sub.add_parser("mark")
    m.add_argument("--log", required=True)
    m.add_argument("--name", required=True)
    m.add_argument("--company", default="")
    m.add_argument("--step", required=True, choices=STEPS)
    m.add_argument("--note", default="")
    m.add_argument("--leads", help="also update status and last_contact in this leads.csv")
    m.add_argument("--business")
    m.add_argument("--date")
    d = sub.add_parser("due")
    d.add_argument("--log", required=True)
    d.add_argument("--date")
    c = sub.add_parser("count")
    c.add_argument("--text", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "count":
        n = len(args.text)
        print("[%d/%d]%s" % (n, NOTE_LIMIT, "  over by %d" % (n - NOTE_LIMIT) if n > NOTE_LIMIT else ""))
        return 0 if n <= NOTE_LIMIT else 1
    if args.cmd == "mark":
        day = today(args.date)
        row = mark(args.log, args.name, args.company, args.step, day, args.note)
        print("logged %s for %s. next: %s %s" % (row["step"], row["name"],
                                                row["next_step"] or "none", row["next_date"]))
        if args.leads:
            status = LEAD_STATUS_FOR_STEP.get(args.step)
            if status and update_lead(args.leads, args.name, args.company, status, day, args.business):
                print("updated %s: status %s, last_contact %s" % (args.leads, status, day))
            elif status:
                print("note: %s not found in %s; leads file not changed" % (args.name, args.leads))
        return 0
    if args.cmd == "due":
        rows = due(read_log(args.log), today(args.date))
        if not rows:
            print("nothing due")
        for r in rows:
            print("%s  %-12s %s (%s)" % (r["next_date"], r["next_step"], r["name"], r["company"]))
        return 0

    day = today(args.date)
    if args.limit > 20:
        print("warning: %d a day is above 20; accounts that send fast get restricted. "
              "Consider 5 to 10." % args.limit)
    rows, headers = read_csv(args.leads)
    if not rows:
        print("no leads found at %s" % args.leads)
        return 1
    leads, missing = normalise_leads(rows, headers)
    chosen, waiting, skipped, today_n, week_n, room = pick(leads, read_log(args.log), day,
                                                           args.limit, args.business)
    if not args.business:
        print("note: no --business given, so leads for every business are mixed together")
    print("date %s | sent today %d of %d | this week %d of about %d | room today %d"
          % (day, today_n, args.limit, week_n, WEEKLY_CEILING, room))
    if missing:
        print("note: leads file has no column for: %s" % ", ".join(missing))
    print("\nINVITE TODAY")
    for i, l in enumerate(chosen, 1):
        print("%2d. %s, %s at %s | fit %s | why: %s%s" % (
            i, l["name"], l["role"] or "role ?", l["company"] or "company ?",
            "?" if l["fit"] is None else ("%g" % l["fit"]), l["reason"],
            (" | " + l["linkedin"]) if l["linkedin"] else ""))
    if not chosen:
        print("  none: daily or weekly limit reached, or no lead has a reason yet")
    if waiting:
        print("\nWAITING FOR ANOTHER DAY: %d" % len(waiting))
    if skipped:
        print("\nSKIPPED")
        for name, why in skipped:
            print("  - %s: %s" % (name, why))
    return 0


if __name__ == "__main__":
    sys.exit(main())
