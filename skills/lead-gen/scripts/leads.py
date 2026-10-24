#!/usr/bin/env python3
"""Keep sales/leads.csv clean: import, add, dedupe, score, check, list and update leads.

Standard library only. No network calls. Python 3.8+.

Two files, always side by side:
  sales/leads.csv       the shared file other skill repos read (linkedin-dm, instagram-dm).
                        Exactly these columns, in this order: see SHARED.
  sales/lead-facts.csv  biz-boost's own extra facts per lead (country, size, signals, email
                        status, next step, and any extra columns from an export). Joined to
                        leads.csv by business_slug + company.
Every command reads both files as one table and writes them back split, so the shared file
never gets extra columns.

Commands:
  init   PATH                       write empty leads.csv and lead-facts.csv headers
  import PATH SOURCE.csv --source NAME --business SLUG
                                    add rows from an export (Apollo, Vibe Prospecting,
                                    a spreadsheet), mapping common header names
  add    PATH --business SLUG --company NAME [--field value ...]
                                    add or update one lead found by manual research
  dedupe PATH                       merge duplicate companies (same domain, email,
                                    or same name in the same city)
  score  PATH --icp ICP.json        fill fit_score (0-100) and fit_reason from rules
  check  PATH                       flag rows that need care before outreach;
                                    exit code 1 if any row must not be contacted as is
  top    PATH [-n 10]               print the best leads as a Markdown table
  set    PATH --company NAME [--business SLUG] [--status S] [--last-contact DATE]
                                    [--next-step TEXT] [--notes TEXT] [--fit-reason TEXT]
                                    update one lead after a touch or after research.
                                    --fit-reason replaces the reason to reach out; run
                                    score with --keep-reason afterwards so it stays

ICP.json shape:
  {"criteria": [{"name": "...", "field": "industry", "match": "contains_any",
                 "values": ["law", "legal"], "points": 20}, ...],
   "disqualify": [{"name": "...", "field": "size", "match": "range", "max": 4}]}
  match is one of: contains_any, equals_any, range (min and/or max, numbers), present.
"""
import argparse
import csv
import io
import json
import os
import re
import sys

SHARED = [
    "business_slug", "name", "company", "role", "email", "linkedin_url",
    "instagram_handle", "website", "city", "source", "source_url", "fit_score",
    "fit_reason", "status", "last_contact", "notes",
]

FACTS = [
    "business_slug", "company", "country", "industry", "size", "signals",
    "email_status", "contact_route", "next_step",
]

COLUMNS = SHARED + [c for c in FACTS if c not in SHARED]

STATUSES = {"new", "contacted", "replied", "meeting", "won", "lost", "do-not-contact"}

ALIASES = {
    "company": ["company", "company name", "organization", "organization name",
                "account", "account name", "business", "business name", "name of business"],
    "website": ["website", "domain", "company domain", "company website", "url", "web"],
    "name": ["contact", "contact name", "full name", "person", "person name"],
    "role": ["title", "job title", "position", "contact title", "contact role"],
    "email": ["work email", "email address", "contact email", "business email"],
    "linkedin_url": ["linkedin", "person linkedin url", "linkedin url", "linkedin profile"],
    "instagram_handle": ["instagram", "instagram url", "ig handle"],
    "contact_route": ["phone", "contact route", "phone number", "work phone", "contact form"],
    "email_status": ["email status", "contact status", "email verification", "contact_status"],
    "city": ["town", "locality"],
    "country": ["company country", "country code"],
    "industry": ["category", "sector", "vertical"],
    "size": ["employees", "# employees", "employee count", "company size",
             "headcount", "number of employees"],
    "signals": ["intent", "intent signals", "signal"],
    "source_url": ["source link", "source_link", "evidence", "link"],
    "last_contact": ["last touch", "last_touch", "last contacted"],
    "notes": ["note", "comments"],
}

PERSONAL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "live.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com",
    "gmx.com", "msn.com",
}

# Sources where people post as themselves. A named person found here is a reviewer
# or commenter, not a lead: keep the company signal, never the person.
PUBLIC_POST_SOURCES = re.compile(
    r"review|reddit|hacker ?news|\bhn\b|forum|comment|g2|capterra|trustpilot|yelp|"
    r"google maps|app store|play store|product hunt|discord|thread|tweet|x\.com",
    re.I,
)

US_NAMES = {"", "us", "usa", "u.s.", "u.s.a.", "united states", "united states of america"}

COMPANY_SUFFIXES = re.compile(
    r"\b(inc|llc|ltd|limited|corp|corporation|co|company|gmbh|plc|pllc|lp|llp|pc|sa|bv)\b\.?",
    re.I,
)


def norm_company(name):
    text = (name or "").lower().replace("&", " and ")
    text = COMPANY_SUFFIXES.sub(" ", text)
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"^the\s+", "", text.strip())
    return re.sub(r"\s+", " ", text).strip()


def norm_domain(value):
    text = (value or "").strip().lower()
    if not text:
        return ""
    if "@" in text:
        text = text.split("@", 1)[1]
    text = re.sub(r"^[a-z]+://", "", text)
    text = text.split("/", 1)[0].split("?", 1)[0]
    if text.startswith("www."):
        text = text[4:]
    return text


def facts_path(path):
    return os.path.join(os.path.dirname(path), "lead-facts.csv")


def _read_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = [{(k or "").strip(): (v or "").strip() for k, v in raw.items() if k} for raw in reader]
        return rows, reader.fieldnames or []


def key_of(row):
    return (row.get("business_slug", "").strip().lower(), norm_company(row.get("company")))


def read_rows(path):
    """Read leads.csv and lead-facts.csv as one list of records with every column."""
    shared, _ = _read_csv(path)
    facts, _ = _read_csv(facts_path(path))
    by_key = {}
    for f in facts:
        by_key.setdefault(key_of(f), f)
    rows = []
    for raw in shared:
        row = {col: raw.get(col, "") for col in COLUMNS}
        for k, v in raw.items():
            if k not in row:
                row[k] = v  # unknown column in leads.csv: moved to facts on write
        for k, v in by_key.get(key_of(row), {}).items():
            if k in ("business_slug", "company"):
                continue
            if v and not row.get(k):
                row[k] = v
        rows.append(row)
    return rows


def extra_columns(rows):
    extras = []
    for row in rows:
        for key in row:
            if key not in COLUMNS and key not in extras:
                extras.append(key)
    return extras


def write_rows(path, rows):
    """Write records back: shared columns to leads.csv, the rest to lead-facts.csv."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=SHARED, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({f: row.get(f, "") for f in SHARED})
    fact_fields = FACTS + extra_columns(rows)
    with open(facts_path(path), "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fact_fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            data = {f: row.get(f, "") for f in fact_fields}
            if any(data[f] for f in fact_fields if f not in ("business_slug", "company")):
                writer.writerow(data)


def map_headers(headers):
    """Return {source_header: our_column} for headers we recognise."""
    mapping = {}
    used = set()
    lowered = {h: re.sub(r"\s+", " ", (h or "").strip().lower().replace("_", " ")) for h in headers}
    for col in COLUMNS:
        if col in [lowered[h] for h in headers]:
            for h in headers:
                if lowered[h] == col and h not in mapping:
                    mapping[h] = col
                    used.add(col)
    for col, names in ALIASES.items():
        if col in used:
            continue
        for h in headers:
            if h in mapping:
                continue
            if lowered[h] in names:
                mapping[h] = col
                used.add(col)
                break
    return mapping


def import_rows(src_path, source_name, business=""):
    with open(src_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []
        mapping = map_headers(headers)
        lowered = {h.strip().lower(): h for h in headers if h}
        first = lowered.get("first name") or lowered.get("first_name")
        last = lowered.get("last name") or lowered.get("last_name")
        out = []
        for raw in reader:
            row = {col: "" for col in COLUMNS}
            for h, col in mapping.items():
                row[col] = (raw.get(h) or "").strip()
            if not row["name"] and (first or last):
                parts = [(raw.get(first) or "").strip() if first else "",
                         (raw.get(last) or "").strip() if last else ""]
                row["name"] = " ".join(p for p in parts if p)
            row["email_status"] = normalise_email_status(row["email_status"], row)
            row["status"] = normalise_status(row["status"])
            if business and not row["business_slug"]:
                row["business_slug"] = business
            if not row["source"]:
                row["source"] = source_name
            if not row["status"]:
                row["status"] = "new"
            if not row["company"] and not row["website"]:
                continue
            out.append(row)
        return out, mapping


def normalise_status(value):
    text = (value or "").strip().lower()
    if text in STATUSES:
        return text
    return {"researched": "new", "proposal": "meeting", "not-now": "lost",
            "unsubscribed": "do-not-contact", "opted out": "do-not-contact"}.get(text, "")


def normalise_email_status(value, row):
    text = (value or "").strip().lower()
    if text in ("verified", "valid", "deliverable"):
        return "verified"
    if text in ("guessed", "inferred", "likely", "risky", "unverified", "catch-all", "accept all"):
        return "inferred"
    if text in ("invalid", "bounced", "undeliverable"):
        return "invalid"
    if text in ("unknown", ""):
        return "unknown" if row.get("email") else ""
    return text


def completeness(row):
    return sum(1 for col in COLUMNS if row.get(col))


def merge_into(keep, other):
    for key, val in other.items():
        if not val:
            continue
        if not keep.get(key):
            keep[key] = val
        elif key in ("source", "signals", "notes", "source_url") and val not in keep[key]:
            keep[key] = keep[key] + "; " + val
    return keep


def dedupe(rows):
    """Merge rows that are the same company. Returns (rows, merged_count)."""
    groups = []
    index = {}
    for row in rows:
        keys = []
        biz = (row.get("business_slug") or "").strip().lower() + "|"
        domain = norm_domain(row.get("website")) or ""
        email_domain = norm_domain(row.get("email"))
        if domain:
            keys.append(biz + "d:" + domain)
        elif email_domain and email_domain not in PERSONAL_DOMAINS:
            keys.append(biz + "d:" + email_domain)
        if row.get("email"):
            keys.append(biz + "e:" + row["email"].strip().lower())
        name = norm_company(row.get("company"))
        if name:
            keys.append(biz + "n:" + name + "|" + (row.get("city") or "").strip().lower())
        hit = None
        for key in keys:
            if key in index:
                hit = index[key]
                break
        if hit is None:
            groups.append([row])
            hit = len(groups) - 1
        else:
            groups[hit].append(row)
        for key in keys:
            index.setdefault(key, hit)
    out = []
    merged = 0
    for group in groups:
        group.sort(key=completeness, reverse=True)
        keep = dict(group[0])
        for other in group[1:]:
            merge_into(keep, other)
            merged += 1
        out.append(keep)
    return out, merged


GUESS_MARK = re.compile(r"\?|guess|unknown|maybe|unsure|not sure", re.I)


def to_number(text):
    """Read a count like 45, 1,200 or 11-50. A value marked as a guess ("40?", "maybe 40")
    returns None, so a guess never earns points."""
    text = (text or "").replace(",", "").strip()
    if GUESS_MARK.search(text):
        return None
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", text)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def rule_matches(rule, row):
    value = row.get(rule.get("field", ""), "") or ""
    match = rule.get("match", "contains_any")
    if match == "present":
        return bool(value.strip())
    if match == "range":
        num = to_number(value)
        if num is None:
            return False
        if "min" in rule and num < float(rule["min"]):
            return False
        if "max" in rule and num > float(rule["max"]):
            return False
        return True
    values = [str(v).lower() for v in rule.get("values", [])]
    low = value.lower()
    if match == "equals_any":
        return low.strip() in values
    if match == "contains_any":
        return any(v and v in low for v in values)
    raise ValueError("unknown match type: %s" % match)


def load_icp(path):
    with open(path, encoding="utf-8") as fh:
        icp = json.load(fh)
    crit = icp.get("criteria", [])
    if not crit:
        raise ValueError("ICP file has no criteria")
    for rule in crit + icp.get("disqualify", []):
        if "field" not in rule or "name" not in rule:
            raise ValueError("every rule needs a name and a field: %r" % rule)
    return icp


def score_row(row, icp):
    for rule in icp.get("disqualify", []):
        if rule_matches(rule, row):
            return 0, "disqualified: " + rule["name"]
    total = sum(float(r.get("points", 10)) for r in icp["criteria"])
    got = 0.0
    hits, misses = [], []
    for rule in icp["criteria"]:
        if rule_matches(rule, row):
            got += float(rule.get("points", 10))
            hits.append(rule["name"])
        else:
            misses.append(rule["name"])
    score = int(round(100 * got / total)) if total else 0
    reason = "matches: " + (", ".join(hits) if hits else "none")
    if misses:
        reason += " | missing: " + ", ".join(misses)
    return score, reason


def score_rows(rows, icp, keep_reason=False):
    for row in rows:
        score, reason = score_row(row, icp)
        row["fit_score"] = str(score)
        if keep_reason and row.get("fit_reason"):
            continue
        row["fit_reason"] = reason
    rows.sort(key=lambda r: int(r.get("fit_score") or 0), reverse=True)
    return rows


def check_rows(rows):
    """Return list of (level, row_number, company, message). level is 'stop' or 'care'."""
    issues = []
    seen = {}
    for n, row in enumerate(rows, 2):
        company = row.get("company") or row.get("website") or "(no name)"
        email = (row.get("email") or "").strip().lower()
        source = " ".join([row.get("source", ""), row.get("source_url", "")])
        country = (row.get("country") or "").strip().lower()
        status = (row.get("status") or "").strip().lower()
        if (row.get("name") or row.get("linkedin_url") or row.get("instagram_handle")) \
                and PUBLIC_POST_SOURCES.search(source):
            issues.append(("stop", n, company,
                           "named person from a public review or post. Keep the company and "
                           "the signal, remove the person, and find the decision maker another way."))
        if status == "do-not-contact":
            issues.append(("stop", n, company, "marked do-not-contact. Leave out of every send."))
        if status and status not in STATUSES:
            issues.append(("care", n, company, "unknown status '%s'" % row.get("status")))
        if email and norm_domain(email) in PERSONAL_DOMAINS:
            issues.append(("care", n, company,
                           "personal email address. Treat as an individual: cold email here is "
                           "riskier, and outside the US it usually needs consent."))
        if email and (row.get("email_status") or "") in ("inferred", "unknown", ""):
            issues.append(("care", n, company,
                           "email not verified. Verify before sending, a bounce hurts your domain."))
        if (row.get("email_status") or "") == "invalid":
            issues.append(("stop", n, company, "email marked invalid. Do not send."))
        if not country:
            issues.append(("care", n, company,
                           "no country. Fill it in, the email rules depend on it."))
        elif country not in US_NAMES:
            issues.append(("care", n, company,
                           "outside the US (%s). Check the local email law first: GDPR and PECR "
                           "in the EU and UK, CASL in Canada." % row.get("country")))
        if not row.get("business_slug"):
            issues.append(("care", n, company, "no business_slug. Say which business this lead is for."))
        if not (row.get("source") or row.get("source_url")):
            issues.append(("care", n, company, "no source. Say where this lead came from."))
        if not row.get("fit_reason"):
            issues.append(("care", n, company, "no fit reason yet."))
        key = norm_domain(row.get("website")) or norm_company(company)
        if key in seen:
            issues.append(("care", n, company, "looks like a duplicate of row %d" % seen[key]))
        else:
            seen[key] = n
    return issues


def top_table(rows, count):
    rows = sorted(rows, key=lambda r: int(r.get("fit_score") or 0), reverse=True)
    rows = [r for r in rows if (r.get("status") or "") not in ("do-not-contact", "won", "lost")]
    out = io.StringIO()
    out.write("| # | company | contact | score | why |\n| --- | --- | --- | --- | --- |\n")
    for i, row in enumerate(rows[:count], 1):
        contact = row.get("role") or row.get("name") or "unknown"
        why = (row.get("fit_reason") or "").replace("|", "/")
        out.write("| %d | %s | %s | %s | %s |\n" % (
            i, row.get("company", ""), contact, row.get("fit_score", ""), why))
    return out.getvalue()


def set_fields(rows, company, updates, business=None):
    target = norm_company(company)
    hits = [r for r in rows if norm_company(r.get("company")) == target
            and (not business or (r.get("business_slug") or "").lower() == business.lower())]
    if not hits:
        raise KeyError("no lead named %r" % company)
    if len(hits) > 1:
        raise KeyError("more than one lead named %r, pass --business or run dedupe" % company)
    status = updates.get("status")
    if status and status not in STATUSES:
        raise ValueError("status must be one of: " + ", ".join(sorted(STATUSES)))
    for key, val in updates.items():
        if val is None:
            continue
        if key == "notes" and hits[0].get("notes"):
            hits[0]["notes"] = hits[0]["notes"] + "; " + val
        else:
            hits[0][key] = val
    return hits[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Keep sales/leads.csv clean.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("path")
    p = sub.add_parser("import")
    p.add_argument("path")
    p.add_argument("source_csv")
    p.add_argument("--source", required=True, help="where the export came from")
    p.add_argument("--business", default="", help="business_slug from founder-context")
    p = sub.add_parser("add")
    p.add_argument("path")
    p.add_argument("--business", required=True)
    p.add_argument("--company", required=True)
    for col in COLUMNS:
        if col not in ("business_slug", "company"):
            p.add_argument("--" + col.replace("_", "-"), dest=col)
    p = sub.add_parser("dedupe")
    p.add_argument("path")
    p = sub.add_parser("score")
    p.add_argument("path")
    p.add_argument("--icp", required=True)
    p.add_argument("--keep-reason", action="store_true",
                   help="keep fit_reason text you wrote by hand, only refresh the score")
    p = sub.add_parser("check")
    p.add_argument("path")
    p = sub.add_parser("top")
    p.add_argument("path")
    p.add_argument("-n", type=int, default=10)
    p = sub.add_parser("set")
    p.add_argument("path")
    p.add_argument("--company", required=True)
    p.add_argument("--business")
    p.add_argument("--status")
    p.add_argument("--last-contact")
    p.add_argument("--next-step")
    p.add_argument("--notes")
    p.add_argument("--fit-reason", dest="fit_reason",
                   help="one line a person can act on, e.g. 'hiring 3 paralegals, job ad Oct 2026'")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "init":
            if read_rows(args.path):
                print("%s already has leads, left it alone" % args.path)
                return 0
            write_rows(args.path, [])
            print("wrote empty %s" % args.path)
        elif args.cmd == "import":
            rows = read_rows(args.path)
            new, mapping = import_rows(args.source_csv, args.source, args.business)
            unmapped = [h for h in (csv_headers(args.source_csv)) if h not in mapping]
            rows, merged = dedupe(rows + new)
            write_rows(args.path, rows)
            print("imported %d rows, merged %d duplicates, %d leads now" % (len(new), merged, len(rows)))
            if unmapped:
                print("columns not mapped (kept out): " + ", ".join(unmapped))
        elif args.cmd == "add":
            rows = read_rows(args.path)
            new = {col: "" for col in COLUMNS}
            new["business_slug"] = args.business
            new["company"] = args.company
            for col in COLUMNS:
                val = getattr(args, col, None)
                if val:
                    new[col] = val
            if new["status"] and new["status"] not in STATUSES:
                raise ValueError("status must be one of: " + ", ".join(sorted(STATUSES)))
            new["status"] = new["status"] or "new"
            if new["email_status"]:
                new["email_status"] = normalise_email_status(new["email_status"], new)
            same = [r for r in rows if key_of(r) == key_of(new)]
            if same:
                for k, v in new.items():
                    if v and (k != "status" or getattr(args, "status", None)):
                        same[0][k] = v
                print("updated %s" % args.company)
            else:
                rows, _ = dedupe(rows + [new])
                print("added %s" % args.company)
            write_rows(args.path, rows)
        elif args.cmd == "dedupe":
            rows, merged = dedupe(read_rows(args.path))
            write_rows(args.path, rows)
            print("merged %d duplicates, %d leads now" % (merged, len(rows)))
        elif args.cmd == "score":
            rows = score_rows(read_rows(args.path), load_icp(args.icp), args.keep_reason)
            write_rows(args.path, rows)
            print("scored %d leads" % len(rows))
        elif args.cmd == "check":
            issues = check_rows(read_rows(args.path))
            stops = [i for i in issues if i[0] == "stop"]
            for level, n, company, msg in issues:
                print("%s row %d (%s): %s" % (level.upper(), n, company, msg))
            print("%d to fix before contact, %d to take care with" % (len(stops), len(issues) - len(stops)))
            return 1 if stops else 0
        elif args.cmd == "top":
            sys.stdout.write(top_table(read_rows(args.path), args.n))
        elif args.cmd == "set":
            rows = read_rows(args.path)
            set_fields(rows, args.company, {
                "status": args.status, "last_contact": args.last_contact,
                "next_step": args.next_step, "notes": args.notes,
                "fit_reason": " ".join(args.fit_reason.split()) if args.fit_reason else None,
            }, args.business)
            write_rows(args.path, rows)
            print("updated %s" % args.company)
    except (KeyError, ValueError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    return 0


def csv_headers(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return next(csv.reader(fh), [])


if __name__ == "__main__":
    sys.exit(main())
