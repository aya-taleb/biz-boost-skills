#!/usr/bin/env python3
"""Check a prospect brief before anyone uses it: every fact needs a page you opened.

A "fact line" is a bullet in the sections Snapshot, What changed lately, Who decides and
Reason to reach out now. Each must have one of:
  - a Markdown link [text](http...) to a page you opened, or
  - a label: (inference: ...), (not confirmed), (search snippet only, not confirmed),
    "unknown", "not published", "not found", "nothing recent found".

Every link in a fact line must also be listed under "## Sources" with the date you read it
and a short quote copied from that page, in double quotes:
  - [ABC7](https://abc7.com/...), read 2026-10-23: "Allbirds will close its US stores"
The quote is the proof that the page says the thing. So the checker also flags:
  - a number in a fact line (headcount, revenue, store count) that is not in the quote of
    any page that line cites,
  - a multi-word name (a person, a city) that is not in those quotes,
  - a month in a fact line that is not in those quotes (a worked-out date),
  - a reason to reach out of 25 words or more.
A link the brief offers without having opened it (a contact page) is marked "(not opened)"
and skips these checks.

Also flags: items under "What changed lately" with no date, snippet items outside
"Check before you send", and email addresses (an email must be published for business).

Usage: python3 check_brief.py sales/accounts/<slug>.md
Exit code 1 if anything needs a fix. Standard library only.
"""
import re
import sys

FACT_SECTIONS = ("snapshot", "what changed lately", "who decides", "reason to reach out now")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
LABEL = re.compile(r"inference|not confirmed|unknown|not published|not found|nothing recent|"
                   r"no timely hook|from the user|user's notes|from sales/|from founder/", re.I)
NOT_OPENED = re.compile(r"not opened", re.I)
DATE = re.compile(r"\b(20\d\d-\d\d(-\d\d)?|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? (\d{1,2},? )?20\d\d|20\d\d)\b", re.I)
ISO_DATE = re.compile(r"\b(19|20)\d\d-\d\d(-\d\d)?\b")
READ_DATE = re.compile(r"read (on )?(20\d\d-\d\d-\d\d)", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
QUOTE = re.compile(r"\"([^\"]+)\"|“([^”]+)”")
NUMBER = re.compile(r"\d[\d,]*(\.\d+)?")
NAME = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b")
# capitalized words that start brief lines or name sections, not names to check
NAME_SKIP = {"What", "Size", "Role", "Name", "Best", "Customers", "Fit", "Researched",
             "Reason", "Who", "Check", "No", "The", "A", "An", "Nothing"}


def norm_url(url):
    url = url.split("#", 1)[0].rstrip("/").rstrip(".,;")
    return re.sub(r"^https?://(www\.)?", "", url).lower()


def norm_num(text):
    return text.replace(",", "")


def quotes_of(line):
    return [a or b for a, b in QUOTE.findall(line)]


def strip_links(line):
    return LINK.sub(" ", line)


DATE_PREFIX = re.compile(r"^[-*]\s*[^:]{0,20}\d[^:]{0,12}:")  # "- 2026-04-15:" or "- April 15, 2026:"


def numbers_in(line):
    body = READ_DATE.sub(" ", strip_links(line))
    body = DATE_PREFIX.sub(" ", body.strip())
    body = ISO_DATE.sub(" ", body)
    found = []
    for m in NUMBER.finditer(body):
        raw = m.group(0).rstrip(",")
        if re.fullmatch(r"(19|20)\d\d", raw):
            continue  # a year; news dates are checked separately
        found.append(norm_num(raw))
    return found


MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december")


def months_in(line):
    """Month names in the claim itself (not the news date prefix, labels or read date)."""
    body = READ_DATE.sub(" ", strip_links(line))
    body = re.sub(r"\([^)]*\)", " ", body)
    body = DATE_PREFIX.sub(" ", body.strip())
    words = re.findall(r"[a-z]+", body.lower())
    return [m for m in MONTHS if m in words and m != "may"]


def names_in(line):
    body = strip_links(line)
    body = re.sub(r"\([^)]*\)", " ", body)  # labels and asides
    out = []
    for m in NAME.finditer(body):
        words = [w for w in m.group(1).split() if w not in NAME_SKIP]
        if len(words) >= 2:
            out.append(" ".join(words))
    return out


def parse(text):
    """Return (sections, sources). sections: list of (line no, section, text)."""
    section = ""
    rows = []
    sources = {}
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        body = line.strip()
        if not body or body.startswith("#"):
            continue
        rows.append((n, section, body))
        if section.startswith("sources"):
            for _, url in LINK.findall(body):
                entry = sources.setdefault(norm_url(url), {"line": n, "quotes": [], "read": False})
                entry["quotes"] += quotes_of(body)
                entry["read"] = entry["read"] or bool(READ_DATE.search(body))
    return rows, sources


def check(text):
    problems, notes = [], []
    rows, sources = parse(text)
    for n, section, body in rows:
        in_fact = any(section.startswith(s) for s in FACT_SECTIONS)
        is_item = body.startswith(("-", "*")) or (in_fact and section.startswith("reason"))
        links = LINK.findall(body)
        if in_fact and is_item:
            if not links and not LABEL.search(body):
                problems.append("line %d (%s): no link and no label: %s" % (n, section, body[:90]))
            if section.startswith("what changed") and links and not DATE.search(body):
                problems.append("line %d: news item with no date: %s" % (n, body[:90]))
            if links and not NOT_OPENED.search(body):
                cited = []
                for _, url in links:
                    entry = sources.get(norm_url(url))
                    if entry is None:
                        problems.append("line %d: %s is not under Sources with a read date and a "
                                        "quote; open it and add one, or mark it (not opened)" % (n, url))
                        continue
                    if not entry["quotes"]:
                        problems.append("line %d: the Sources entry for %s has no quote from the "
                                        "page" % (n, url))
                    if not entry["read"]:
                        problems.append("line %d: the Sources entry for %s has no 'read <date>'"
                                        % (n, url))
                    cited += entry["quotes"]
                if cited:
                    quoted = norm_num(" ".join(cited))
                    for num in numbers_in(body):
                        if not re.search(r"(?<![\d.])" + re.escape(num) + r"(?!\d)", quoted):
                            problems.append("line %d: the number %s is not in the quote from the "
                                            "page it cites; quote the sentence that states it, or "
                                            "write unknown" % (n, num))
                    for month in months_in(body):
                        if month not in " ".join(cited).lower():
                            problems.append("line %d: the month '%s' is not in the quote from its "
                                            "source; use the date the page gives, or mark a date "
                                            "you worked out as (inference)" % (n, month))
                    for name in names_in(body):
                        if name.lower() not in " ".join(cited).lower():
                            problems.append("line %d: '%s' is not in the quoted text of its source; "
                                            "quote the sentence that names it, or drop the name"
                                            % (n, name))
        if section.startswith("reason") and not body.startswith(("-", "*")):
            words = len(re.sub(r"\s+", " ", re.sub(r"\([^)]*\)", " ", READ_DATE.sub(" ", strip_links(body)))).split())
            if words > 24:
                problems.append("line %d: the reason to reach out is %d words; make it one "
                                "sentence under 25 words" % (n, words))
        if "snippet" in body.lower() and not section.startswith("check before"):
            notes.append("line %d: snippet-only item outside 'Check before you send'" % n)
        for email in EMAIL.findall(body):
            notes.append("line %d: email %s, make sure the company publishes it" % (n, email))
    return problems, notes


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    with open(argv[0], encoding="utf-8") as fh:
        problems, notes = check(fh.read())
    for p in problems:
        print("fix: " + p)
    for n in notes:
        print("note: " + n)
    print("%d to fix, %d to look at" % (len(problems), len(notes)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
