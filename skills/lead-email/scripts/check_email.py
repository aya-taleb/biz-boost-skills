#!/usr/bin/env python3
"""Check cold email drafts for the parts the law and good sense need before anyone sends them.

Reads a Markdown file of drafts. Each draft starts with a heading line that begins with
"## " and has a "Subject:" line. Checks per draft:
  - a physical postal address in the footer (CAN-SPAM)
  - a working opt-out line (CAN-SPAM, CASL, PECR)
  - an honest subject: no fake "Re:" or "Fwd:" on a first email, no all caps, no bait words
  - length: under 150 words in the body is the target for a cold email
  - placeholders left to fill ({{...}}), listed so the sender sees them
  - writing rules: no em dashes, none of the stock words (a fallback if humanize is absent)

Usage: python3 check_email.py sales/emails/<slug>.md [--first-touch-only]
Exit code 1 if any draft is missing an address or an opt-out, or has a fake reply subject.
Standard library only. This is a checklist, not legal advice.
"""
import argparse
import re
import sys

OPT_OUT = re.compile(
    r"unsubscribe|opt[ -]?out|not interested\?|reply (with )?\"?(stop|no|remove)|"
    r"(don't|do not|rather not) (want|hear|get)|let me know and i('| wi)ll (stop|not)|"
    r"won't (email|write|contact) (you )?again|remove you", re.I)
ADDRESS = re.compile(
    r"(\d{1,6}\s+\w+(\s\w+)*\s(st|street|ave|avenue|rd|road|blvd|way|dr|drive|ln|lane|pl|place|"
    r"ct|court|pkwy|hwy|sq|square|suite|ste)\b)|(p\.?\s?o\.?\s+box\s+\d+)|(\{\{\s*(street|postal|physical|mailing)?\s*address\s*\}\})",
    re.I)
FAKE_REPLY = re.compile(r"^\s*(re|fwd?|fw)\s*:", re.I)
BAIT = re.compile(r"\b(free money|act now|urgent|guaranteed|winner|100% free|risk[- ]free|last chance)\b", re.I)
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}")
BANNED = ["delve", "leverage", "seamless", "streamline", "comprehensive", "journey", "unlock",
          "elevate", "empower", "foster", "thoughtful", "relatable", "storytelling", "robust",
          "crucial", "utilize", "synergy", "cutting-edge", "game-changer", "revolutionize",
          "tapestry", "testament", "moreover", "furthermore", "i hope this email finds you well",
          "just following up", "circle back", "touch base", "quick question"]


def split_drafts(text):
    drafts = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                drafts.append(current)
            current = {"title": line[3:].strip(), "lines": []}
        elif current is not None:
            current["lines"].append(line)
    if current:
        drafts.append(current)
    return [d for d in drafts if any(l.lower().startswith("subject:") for l in d["lines"])]


def check_draft(draft, position):
    problems, notes = [], []
    lines = draft["lines"]
    subject = ""
    body = []
    for line in lines:
        if line.lower().startswith("subject:") and not subject:
            subject = line.split(":", 1)[1].strip()
        else:
            body.append(line)
    body_text = "\n".join(body)
    if not ADDRESS.search(body_text):
        problems.append("no physical postal address (CAN-SPAM needs one; a {{street address}} placeholder is fine in a draft)")
    if not OPT_OUT.search(body_text):
        problems.append("no opt-out line (add one, e.g. 'Not for you? Reply \"no\" and I won't email again.')")
    if position == 0 and FAKE_REPLY.search(subject):
        problems.append("subject pretends to be a reply or forward on a first email: '%s'" % subject)
    if subject and subject.isupper() and len(subject) > 4:
        problems.append("subject is all caps")
    if BAIT.search(subject):
        notes.append("subject has a bait word: '%s'" % BAIT.search(subject).group(0))
    if not subject:
        problems.append("no subject line")
    words = len(re.findall(r"[A-Za-z0-9']+", re.split(r"\n-{3,}\n|\n_{3,}\n", body_text)[0]))
    if words > 150:
        notes.append("body is about %d words; aim for under 150" % words)
    if "—" in body_text or "—" in subject:
        notes.append("has an em dash")
    low = (subject + "\n" + body_text).lower()
    for word in BANNED:
        if re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])", low):
            notes.append("stock phrase: '%s'" % word)
    for ph in sorted(set(PLACEHOLDER.findall(subject + body_text))):
        notes.append("to fill: %s" % ph)
    return problems, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check cold email drafts before sending.")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    with open(args.path, encoding="utf-8") as fh:
        drafts = split_drafts(fh.read())
    if not drafts:
        print("no drafts found (each needs a '## ' heading and a 'Subject:' line)")
        return 1
    failed = 0
    for i, draft in enumerate(drafts):
        problems, notes = check_draft(draft, i)
        status = "FIX" if problems else "ok"
        print("[%s] %s" % (status, draft["title"]))
        for p in problems:
            print("   fix: " + p)
        for n in notes:
            print("   note: " + n)
        failed += bool(problems)
    print("%d draft(s), %d need fixes" % (len(drafts), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
