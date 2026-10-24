---
name: reach-plan
description: Makes a weekly outreach plan a solo founder can keep up: which channels to use (email, LinkedIn, phone, walk-ins, events, partners, communities), how many touches a week fit the hours they really have, which leads go first, and the few numbers to track so they know what is working by week 3. Writes sales/reach-plan.md. Use it when someone says "how should I get my first customers", "which channel should I use", "make me an outreach plan", "how many emails a week should I send", "I have 5 hours a week for sales", "where do I start with these leads", or "what should I measure". Use it before lead-email, linkedin-dm or local-outreach, and again every few weeks to adjust from results. Not a marketing or content plan.
---

# reach-plan

A plan for getting customers that fits in the user's real week. Most founders pick too many
channels, send for two weeks, and quit before they learn anything. This plan picks one or two
channels, sets a pace they can keep, and says what result would mean "keep going" or "switch".

## What this skill reads and writes

Reads:
- Business context from founder-context (`founder/context.md`, else
  `~/.founder/active` and `~/.founder/businesses/<slug>.md`): who buys, price,
  stage, goals, where the business is.
- `sales/icp.md` and `sales/leads.csv` (from lead-gen): how many leads, how good, which
  contact routes they have (email, phone, front desk, LinkedIn).
- `founder/marketing.md` if it exists, so the plan does not fight the marketing plan.
- An older `sales/reach-plan.md` and the leads' `status` column, when adjusting from results.

Asks once, in one message, only for what is missing:
1. Hours a week for outreach (be honest, not hopeful).
2. Channels they already have: an audience, a network, a local presence, a list.
3. What they would count as a win in 30 days.

If the user is not there to answer, assume 5 hours a week, say so at the top, and go on.

Writes `sales/reach-plan.md`. Next skills: lead-gen if there are fewer than 20 good leads,
then lead-email, linkedin-dm or local-outreach for the chosen channels.

## How to pick channels

Pick by where the buyer already pays attention and what the user can do well, not by what is
popular. Use `references/channels.md` for the fit of each channel by business type.

Rules of thumb that hold up:
- **Warm before cold.** People who already know the user (past colleagues, customers, local
  neighbors, classmates) convert far better. If they exist, referral-asks goes first.
- **Match the price.** A $10 a month product cannot carry an hour of selling per customer. A
  $5,000 contract can. Work out roughly how many touches the price can pay for.
- **Local means in person.** For a local business, walking in, partners and events usually beat
  email. Cold email is a support channel there.
- **One main channel, one support channel.** More than two in the first month means none gets
  enough volume to judge. Warm asks (referral-asks) are a quick first-week task, not a third
  channel. Put every other channel under "Not now" with the reason.

## How to set the volume

Turn hours into touches. Use these working estimates and say they are estimates:

| task | time each |
| --- | --- |
| research a lead well (prospect-research) | 10 to 15 min |
| personal cold email with research done | 5 min |
| follow-up email | 2 min |
| LinkedIn connection note plus a follow-up | 5 min |
| walk-in visit with travel nearby | 15 to 30 min |
| event (attend and follow up) | 3 to 4 hours |
| sales call plus notes | 45 to 60 min |

Keep a third of the hours free for calls and follow-ups, because replies create work. Write the
math in the plan so the user can change it: "5 hours: 2 hours research (10 leads), 1 hour new
emails (10), 30 min follow-ups, 1.5 hours left for calls."

Respect platform limits. LinkedIn caps invitations and the user sends by hand; keep invites
to a modest daily number and say the exact cap can change. For email, start small from a
normal inbox (tens a day, not hundreds) so the domain stays healthy. Never suggest tools that
automate LinkedIn or scrape.

## Who goes first

Order the leads: warm ones first, then the highest fit_score with a reason to reach out now
(a dated signal), then the rest. Name the first 5 to 10 by company from `sales/leads.csv` when
it exists. If it does not, say "run lead-gen first" and plan the first week as list building.

## What to measure

Keep it to four numbers a week, tracked in the leads' `status` column:
- touches sent (new + follow-ups)
- replies (any reply counts, even "no")
- conversations (calls, meetings, real back and forth)
- next step agreed (trial, proposal, sample, pilot)

Set the checkpoint before starting, from the user's own goal and volume, not from a
conversion rate: "After 3 weeks and about <N> first touches: if replies
are under <X>, change the message or the list before adding volume. If replies are fine but
no conversations, change the ask." Do not quote or assume reply, meeting or close rates, not even as
"a guess" to size the plan (no "1 in 3 tastings convert"). Size the plan from hours, then say
"after week 3 we will know your real rate." If the user wants a benchmark, use
`{{your benchmark}}` or a linked source. The same goes for costs, warm-up times and
thresholds: leave them out or link them.

## The plan format

```
# Reach plan for <business>, from <date>
Assumptions: <hours a week>, <main channel>, <support channel>. Change any of these and the
numbers below change.

## Why these channels
- <channel>: <one line, tied to the buyer and the price>
- Not now: <channels skipped and why>

## Each week
| day | what | how many | time |
...

## Who first
1. <company>, <role>, <why now> (from sales/leads.csv)
...

## What to measure and when to change
<the four numbers, the week-3 checkpoint, what each result means>

## Next steps
- <the next skill and what it does>
```

Keep the plan to one screen: about 40 lines, one table. Do not size the market or invent
counts ("40+ offices nearby") to justify the plan; use the leads file or say "unknown". The user will open it every Monday,
and a long plan stops getting read. Before saving, add up the time column and make sure the
table, the math line and the reply all say the same numbers.

## When the user asks for something risky

Mass email from a new domain, LinkedIn bots, auto-connect tools, scraped or bought lists: say
no to that part in two or three short lines (what breaks, and the account or domain risk),
then give the plan that works. Do not set up or name automation tools.

## The reply

Keep the reply under about 15 lines: the two channels, the weekly numbers, the first 3
leads, the checkpoint, and the next skill. The file has the rest; do not repeat it, and do not
paste the weekly table into the reply.

## Before you save

- Add up the time column. The table, the math line and the reply must show the same hours,
  counts and minutes. Fix the table first, then copy its numbers.
- Search the plan for any ratio that turns touches into customers ("1 in 6", "about a third
  convert", "so 60 touches gets 10 accounts"). Delete it. Size by hours; the checkpoint learns
  the real rate.
- Every claim about where buyers spend time is either from the user's files or written as a
  guess to test ("office managers may answer LinkedIn; test it with 10 notes").

## Adjusting a plan

When the user comes back with results, read the leads' status counts, compare with the
checkpoint, and change one thing at a time: the list, the message, the ask, or the channel.
Say which and why. Update the date and keep the old numbers at the bottom under "History".
