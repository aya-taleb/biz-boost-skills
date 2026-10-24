---
name: lead-email
description: >-
  Writes cold email drafts for one lead or a few: a first email and 2 follow-ups, built on
  real research about that lead, short, and legal to send (sender's physical address, a
  working opt-out, an honest subject). Flags GDPR, PECR or CASL when the lead is outside the
  US. Drafts only, the user sends. Use it when someone says "write a cold email to", "draft
  outreach for my top leads", "email sequence for this prospect", "how do I pitch this
  office manager by email", "follow-up emails for leads.csv", or "write to Acme about my
  product", or "I need an email to send to a prospect". Reads sales/accounts/ briefs and
  sales/leads.csv. Runs every draft through humanize. Not for replies after a call (use
  follow-up) or LinkedIn messages (use linkedin-dm).
---

# lead-email

Three short emails a real person would write to one lead: a first email and two follow-ups.
The user sends them from their own inbox. This skill never sends.

Cold email works when it is about them, short, and easy to say no to. It fails when it reads
like a template, makes claims the sender cannot back, or breaks the law.

## What this skill reads and writes

Reads:
- Business context from founder-context (`founder/context.md`, else
  `~/.founder/active` and `~/.founder/businesses/<slug>.md`): the offer, tone,
  words to avoid, proof the user may use, off-limits topics, and the sender's name, business and
  postal address. If the address is missing, use `{{street address}}` and say it must be filled.
- The lead's brief in `sales/accounts/<slug>.md` (from prospect-research). If there is none,
  offer to run prospect-research first. If the user wants to go ahead anyway, write from what is
  in `sales/leads.csv` and say the email is less personal because of it.
- `sales/leads.csv` for the name and role, and `sales/lead-facts.csv` for country and
  email_status (both written by lead-gen).

Writes:
- `sales/emails/<company-slug>.md`: the three drafts, plus a short header with who, why now,
  send dates and anything to check.
- Updates the lead with the lead-gen tool: `python3 <skills>/lead-gen/scripts/leads.py set
  sales/leads.csv --company "<name>" --next-step "send email 1 on <date>"`. The tool keeps
  next_step in `sales/lead-facts.csv`, because the shared leads.csv has fixed columns. That is
  expected. Do not set status to `contacted`; the user does that when they send.
`<skills>` is the parent of this skill's folder; lead-gen is installed beside it. If
lead-gen is missing, edit sales/leads.csv by hand and keep its 16 columns.

Next skill: follow-up when someone replies or a call is booked; call-prep before the call.

## Rules

- **Drafts only.** Never send, never log in to email, never schedule sends. Say "you send these"
  once in the reply.
- **Every claim must be true and backed.** Use only facts from the brief, the leads file or the
  business context. Proof (customers, numbers, results) only if founder-context lists it as
  usable. Missing numbers become `{{your number}}`. Never invent a customer, a result, or a
  shared connection.
- **Respect off-limits topics** in founder-context, for example "don't name current customers".
- **CAN-SPAM, every email** (it covers business email too, see `references/email-law.md`):
  1. The sender's real name and business in the From line and signature.
  2. A valid physical postal address in the footer (street address or PO box).
  3. A clear opt-out, honored within 10 business days. Plain words work: "Not for you? Reply
     'no' and I won't email again."
  4. An honest subject that matches the email. No fake "Re:" or "Fwd:" on a first email, no
     bait.
- **Outside the US, stop and flag.** Look at the lead's country. EU and UK: GDPR, and PECR in
  the UK; emailing a named person at a company needs a lawful basis and an easy opt-out, and
  sole traders often need consent first. Canada: CASL needs consent, which can be implied if the
  address is published for business with no "no marketing" note and the email is about their
  role. Write the drafts if the user wants them, and put the check at the top of the file.
- **Unverified address, say so.** If email_status is `inferred` or `unknown`, tell the user to
  verify before sending. A bounce hurts their domain.
- **Not legal advice.** For a big campaign or one outside the US, they should ask a lawyer who
  knows email marketing law.

## How to write the three emails

Write in the user's tone from founder-context. Plain words, short sentences, no em dashes.
Use the offer exactly as founder-context states it (a founding price, a free trial, a sample),
because a real, specific offer is the strongest line in a cold email. Do not add details the
context does not give, like "nothing to sign" or "on my route". Use the contact's name if you
have it, and no pronouns you were not given. Never invent how you found them ("came across you
while looking at...") or a cost or saving the inputs do not give (no multiplying the price by
their headcount). Anything you believe about their situation that
the brief does not state ("one person runs billing", "the daily scramble") goes in as a
question, not a statement: "Is billing still on one person's desk?"

**Email 1 (day 0), 50 to 120 words:**
- Subject: 2 to 6 words, specific to them, lowercase is fine. "billing clerk hire at juniper"
  beats "Quick question".
- Line 1: the reason you are writing to *them*, tied to a fact from the brief (dated, real).
- Line 2 to 3: the problem you think they have, said as a question or a guess, and what the
  user's offer does about it in one sentence.
- One small ask with a concrete option: "15 minutes Tuesday or Thursday?", "can I drop off
  lunch for 10 on Wednesday the 5th?". One ask, not three.
- Signature, postal address, opt-out line.

**Email 2 (day 3 to 4), 30 to 80 words:** a new angle or a useful thing (a relevant
question, a second fact from the brief, a sample or overview offer). Not "just bumping this".
The new angle must come from the brief or the business context too: no "most firms like yours
find...", no claims about how others work. Reply on the same thread, so "Re:" is honest here.

**Email 3 (day 8 to 10), 20 to 50 words:** the close-the-loop email. Easy no: "If now's not the
time, no problem, I'll leave it here." Then stop. Three emails is the limit without a reply.

Each email keeps the address and opt-out. Put the send dates in the header, counting from
today or the date the user gives.

For a local business lead (an office near a food business, a shop near a service), keep the
same shape but make the ask physical: "can I drop off a sample lunch for your team Thursday?"
Email works best here next to a visit, so say in the reply that local-outreach has the
walk-in script for the same office.

## Before showing the drafts

1. Run the checker on the file (from this skill's folder):
   `python3 scripts/check_email.py sales/emails/<slug>.md`
   Fix every `fix:` line. Read the `note:` lines and fix what is fair.
2. Run humanize on every email, every time, and name the result in the reply ("humanize: 3
   drafts cleaned, score 92 to 97" or "humanize not installed, cleaned by hand"). Look for it first (a `humanize` folder next to this skill, or
   the humanize skill being available). If it is not installed, do its job by hand and say
   "humanize is not installed, I cleaned the drafts by hand" in the reply:
   remove em dashes and curly quotes, cut stock phrases ("I hope this finds you well", "just
   following up", "I wanted to reach out"), cut the banned words in CONVENTIONS, read each line
   out loud in your head and shorten anything a person would not say.
3. Make sure every `{{placeholder}}` is listed in the header under "fill before sending".

## File format

```
# Emails for <Company>, <role>
Why now: <one line, with the source from the brief>
Send: email 1 <date>, email 2 <date>, email 3 <date>. You send these from your inbox.
Check first: <unverified address / outside-US law / placeholders to fill>

## Email 1 (send <date>)
Subject: ...

<body>

<name>, <business>
<postal address>
<opt-out line>

## Email 2 (send <date>, reply on the same thread)
Subject: Re: <subject of email 1>
...

## Email 3 (send <date>, reply on the same thread)
...
```

Show the three emails in the reply too, so the user can read them without opening the file,
and end with what to fill in and the next step.

## Several leads at once

For "write emails for my top 5", take rows from `sales/leads.csv` by fit_score, skip
`do-not-contact`, and write one file per lead. If a lead has no brief, write the email from the
row, mark it "less personal, no research yet", and suggest prospect-research. Never paste the
same email with the name swapped; if two leads would get the same first line, the research is
too thin.
