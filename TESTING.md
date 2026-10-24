# Testing

How these numbers were made, said once: every score here comes from my own runs, graded by
me. Each run was a fresh headless Claude session that saw only the skill folder and the case
prompt, working in a scratch copy of the case files. Each grade was a separate fresh session
that read the trace, the files and the grader statements. It is still the same model family
grading itself, and two runs of the same version can differ by about 5 points. Read the
trends, not single numbers. Aya can rerun every case with `claude plugin eval`.

Rubric (TEST-PROTOCOL section 2): graders 40, follows its own rules 15, nothing made up 15,
tone and format 10, handoff 10, trigger fit 10. Trigger fit was checked with each skill's
`evals/triggers.json` (6 should fire, 6 near misses) against all nine descriptions plus 12
decoy skills from Aya's other repos. It was measured on the final descriptions and applied to
every round of our skills. Baselines with no skill get 0 for trigger fit. The upstream
call-prep description scored 10 of 10.

Run outputs, traces and grades: `/home/claude/build/_work/biz-boost-skills/<skill>/<round>/`.

| skill | baseline | final | rounds | beats baseline? |
| --- | --- | --- | --- | --- |
| lead-gen | 50 | 91 | 4 | yes |
| prospect-research | 39 | 84 | 6 | yes |
| lead-email | 45 | 88 | 4 | yes |
| reach-plan | 35 | 82 | 3 | yes |
| call-prep | 73 | 90 | 4 | yes |
| follow-up | 42 | 90 | 2 | yes |
| proposal | 49 | 87 | 2 | yes |
| local-outreach | 54 | 86 | 2 | yes |
| referral-asks | 54 | 92 | 3 | yes |

### lead-gen  (ours)
baseline: 50 (no skill, the prompt answered plainly; graders 9/15)
final: 91 after 4 rounds (r4). Stopped because r3 and r4 each gained under 5 points (+1, +2).
rounds:
- v1: 91 (graders 15/15), first version: evidence-based ICP, allowed sources table, leads.py (import, dedupe, score, check, top, set), hard rules on scraping, reviewers and bought lists
- r1: 84 (graders 14/15), guessed sizes no longer earn points (tool), inferred emails kept and marked, short-refusal section; reviewer-name edit did not apply this round
- r2: 88 (graders 15/15), do not repeat a reviewer's name or employer in the reply, told-vs-guessed numbers, every check flag relayed by name
- r3: 89 (graders 15/16), moved to the shared 16-column leads.csv plus lead-facts.csv (orchestrator change), partners go to sales/partners.md, next skill named every time, header grader added
- r4: 91 (graders 16/16), keep ruled-out rows at score 0 with the reason, keep flagged emails marked instead of deleting, correction question at the top, traits only as wide as the evidence
open issues: reply sometimes puts the ICP correction question below the list; the local case adds few web facts because the test offices are fictional. After r4 the import and add command lines in SKILL.md were corrected (doc only, not retested).

### prospect-research  (ours)
baseline: 39 (no skill, the prompt answered plainly; graders 6/14)
final: 84 after 6 rounds (r6). Stopped because r5 and r6 gained under 5 points (-3, 0).
rounds:
- v1: 82 (graders 13/14), first version: five questions, brief format, every fact linked and dated, inference labels, business facts only
- r1: 78 (graders 12/14), snippets and paywalled previews are not pages read; next step inside the brief
- r2: 80 (graders 12/14), failed fetches are not reads, fit needs evidence, short refusal for personal-data asks
- r3: 78 (graders 12/14), one-sentence reason to reach out, snippet items only under Check before you send, linked contact route
- r4: 87 (graders 13/14), added check_brief.py (flags fact lines with no link or label, undated news, snippet items in the wrong place, emails) and a one-sentence refusal
- r5: 84 (graders 13/14), the link must state the thing, retry failed fetches, reason line under 25 words tied to a past event
- r6: 84 (graders 13/14), numbers (headcount, revenue, funding) only from an opened page that states them
open issues: still the weakest skill: about one line per brief rests on a search snippet or a page that does not quite say it. check_brief.py catches unlabeled lines but cannot judge whether a link supports the claim.

### lead-email  (ours)
baseline: 45 (no skill, the prompt answered plainly; graders 8/14)
final: 88 after 4 rounds (r4). Stopped because r3 and r4 gained under 5 points (-2, 0).
rounds:
- v1: 86 (graders 13/14), first version: 3-email shape, CAN-SPAM footer every email, outside-US check, check_email.py
- r1: 90 (graders 14/14), use the offer exactly as stated, no added details or pronouns, local leads point to local-outreach, say whether humanize ran
- r2: 90 (graders 14/14), beliefs about the lead become questions, look for humanize before cleaning by hand
- r3: 88 (graders 14/14), concrete day in the ask, no invented discovery story or computed savings; fixtures moved to the shared leads layout
- r4: 88 (graders 14/14), explain that next_step lives in lead-facts.csv, name the humanize result in every reply
open issues: opening lines sometimes state a guess about the lead's situation instead of asking

### reach-plan  (ours)
baseline: 35 (no skill, the prompt answered plainly; graders 6/14)
final: 82 after 3 rounds (r3). Stopped because r2 and r3 gained under 5 points (-3, +1).
rounds:
- v1: 86 (graders 13/14), first version: channel rules, hours-to-touches table, four numbers, week-3 checkpoint, one-screen plan
- r1: 84 (graders 13/14), no conversion rates even as guesses, one screen, numbers must add up, short refusal for bots and blasts
- r2: 81 (graders 13/14), warm asks are a first-week task not a channel, no market sizing, reply under 15 lines
- r3: 82 (graders 13/14), pre-save checklist: totals match, delete any touches-to-customers ratio, buyer-habit claims written as tests
open issues: the shipped version (82) scores below v1 (86). The later rounds added rules against invented conversion rates and long replies, and the grader then found more rule breaks. Reply length is still over the 15-line target in 2 of 3 cases.

### call-prep  (reworked)
baseline: 73 (Anthropic's original call-prep from knowledge-work-plugins sales, same 3 cases; graders 11/15)
final: 90 after 4 rounds (r4). Stopped because r3 and r4 gained under 5 points (-1, 0).
rounds:
- v1: 84 (graders 14/15), reworked from Anthropic call-prep: files in sales/ instead of CRM and Gong, local call types, lead update, handoff to follow-up
- r1: 86 (graders 14/15), next step section and follow-up handoff in the brief, do not hedge a booked time
- r2: 91 (graders 15/15), ask for missing details in one list and keep going, Bring only real assets, update the lead before finishing, one screen
- r3: 90 (graders 15/15), missing-detail list goes first in the reply, no computed buyer costs
- r4: 90 (graders 15/15), 
open issues: briefs run a little past one screen; the missing-details list is not always the first thing in the reply

### follow-up  (ours)
baseline: 42 (no skill, the prompt answered plainly; graders 7/15)
final: 90 after 2 rounds (r2). Stopped because r1 and r2 gained under 5 points (+2, 0).
rounds:
- v1: 88 (graders 15/15), first version: debrief, same-day recap, two dated nudges then stop, do-not-contact handling
- r1: 90 (graders 15/15), no prices in the recap, nudges add only what the notes promised, no reply at all to an opt-out, next_step location explained
- r2: 90 (graders 15/15), 
open issues: recaps sometimes add one question or promise the notes do not support

### proposal  (ours)
baseline: 49 (no skill, the prompt answered plainly; graders 9/14)
final: 87 after 2 rounds (r2). Stopped because r1 and r2 gained under 5 points (+1, 0).
rounds:
- v1: 86 (graders 14/14), first version: buyer's words, 2 to 3 options, price_options.py totals, terms to check, no invented prices or proof
- r1: 87 (graders 14/14), scope only what notes support (rest under To confirm), price exactly what they asked for first, placeholders plus a pricing path when there are no prices, name follow-up
- r2: 87 (graders 14/14), 
open issues: with no pricing, it can still add scope the context does not support

### local-outreach  (ours)
baseline: 54 (no skill, the prompt answered plainly; graders 10/15)
final: 86 after 2 rounds (r2). Stopped because r1 and r2 gained under 5 points (-3, +1).
rounds:
- v1: 88 (graders 14/15), first version: buyers, gatekeepers, partners; 20-second scripts; office manager, building manager and partner emails; events; leave-behind; 2-week route; permit reminder
- r1: 85 (graders 15/15), ask with two real days, no small invented promises, footer on every email, finish checklist (humanize, add leads, official permit links)
- r2: 86 (graders 15/15), small specifics become {{confirm}}, short honest refusals without unchecked legal claims, use the humanize tool when present
open issues: small unconfirmed specifics (time slots, setup promises) still slip in unmarked; humanize was not always run even when installed

### referral-asks  (ours)
baseline: 54 (no skill, the prompt answered plainly; graders 10/14)
final: 92 after 3 rounds (r3). Stopped because r2 and r3 gained under 5 points (+2, +1).
rounds:
- v1: 76 (graders 11/14), first version: four kinds of people, specific asks with an easy out, forwardable blurb, tracking table, user-owned data only
- r1: 89 (graders 14/14), warmth only from the user's words, group posts for groups, hand-over kit for partners like a food truck, no invented personal lines, short refusal
- r2: 91 (graders 14/14), 
- r3: 92 (graders 14/14), 
open issues: off-limits replies run longer than the 6-line target

## Calls I made

- **Shared leads file.** Mid-build the orchestrator fixed `sales/leads.csv` to 16 columns. I
  kept those exactly and added `sales/lead-facts.csv` for biz-boost's extra facts (country,
  size, signals, email_status, contact_route, next_step). `leads.py` joins and splits the two
  files, so nothing outside biz-boost sees extra columns. Test fixtures were rebuilt for the
  new layout from lead-gen r3 and every other skill's next round on.
- **Shipped the last round, not the best round.** prospect-research peaked at 87 (r4) and
  reach-plan at 86 (v1). I shipped their final rounds (84 and 82) because the later rules fix
  real failures the graders found (snippet facts, invented conversion rates), and the gaps sit
  inside run-to-run noise. Aya may prefer the other call; the earlier versions are in the run
  folders.
- **Baseline for call-prep** was Anthropic's original skill, run on the same cases with the
  same files and no connectors. It scored 73, mostly losing on handoff (it saves no file and
  names no next step) and on the no-files case.
- **Out-of-memory kills.** The build machine is shared, and the kernel killed some runs. The
  harness caps itself at 2 sessions at a time and retries a killed run from a clean folder.
  A few grading passes failed to return JSON and were regraded; no score uses a partial run.
- **Humanize in tests.** Once the shared humanize and founder-context skills existed in
  entrepreneur-skills, they were copied next to our skills in each test install, the way the
  sync step will ship them. Earlier rounds ran without them, so those skills cleaned drafts by
  hand, as their fallback says.

## Independent review (blind)

A second agent reviewed prospect-research (final 84 above). Goal: every fact comes from a
page actually opened and linked, and unverified items are marked. Same harness as the builder
(fresh `claude -p` runs with web search and fetch, now each with its own HOME, separate
grader), outputs in `/home/claude/build/_work/review/weakest/`. A new case,
app-rumor-check-opened-pages, was added: a company with a half-remembered rumor from the user
("layoffs or a new CEO?") and lots of snippet-only news.

| skill | case | winner | ours score | baseline score | fix rounds | one-line reason |
| --- | --- | --- | --- | --- | --- | --- |
| prospect-research | app-research-dtc-brand | ours (both label orders) | 38 / 40 | 40 / 38 | 0 | close; the judge preferred ours for quote-backed sources, though the start version scored 2 higher in one order |
| prospect-research | app-rumor-check-opened-pages | ours (both label orders) | 41 / 41 | 38 / 38 | 0 | ours quotes each opened page and keeps snippet numbers out of the facts; the start version cites pages that don't state some lines |

Baseline = the version this review started from (r6). Scores are the blind judge's 0 to 50
totals, one per label order. The judge saw each run's fetched pages and searches, so it could
check citations.

check_brief.py now needs every cited link listed under Sources with a read date and a quote
copied from the page, and flags a number, a multi-word name or a month in a fact line that is
not in the quote of the page it cites, plus a reason to reach out of 25 words or more. Links
offered but not opened are marked `(not opened)`. 16 new unit tests (66 in the repo, all pass).

### prospect-research  (review rounds, 4 cases)
start: 86 on the 3 old cases; 87 on all 4 cases.
final: 84 after 4 rounds. Stopped because r3 (+0.3) and r4 (+1.2) both gained under 5.
rounds:
- r1: 81, quote-backed Sources (date + copied quote per fact); fetch pages asking for exact sentences; links not opened are labeled; check_brief.py checks Sources, quotes and numbers.
- r2: 83, names not in the quote become a fix; reason line length check; one quote per fact; Best route links only a real contact route; no hedged reasons.
- r3: 83, worked-out months flagged; cite the page the quote came from; nothing in the reason or opening lines rests on an unconfirmed item; snippet-only names stay out of the reply too.
- r4: 84, the next step always names a skill; opening lines sendable as written; facts from the user are labeled.
open issues: the rubric score did not beat the start (84 vs 87, inside the noise of about 4 points) while the blind judge picked ours in all 4 judgments. My read: the quotes let the grader see small mismatches it could not see before, so the rubric got stricter at the same time the briefs got easier to check. WebFetch returns a model's reading of the page, so a "quote" is only as exact as that reading. The skill still sometimes writes "No timely hook" when a dated event exists, and an opening line can still lean on an item marked unconfirmed.

## Polish round (Oct 24)

linkedin-dm 0.1.1 synced from linkedin-boost-skills: proof is cleared for use, only the
off-limits line is off limits, and follow-up 1 adds nothing the file does not state. Blind
results are in linkedin-boost-skills/TESTING.md (won both orders on both cases).
