---
name: referral-asks
description: Finds who could introduce you to the customers you want, from your own people list, customer list or the LinkedIn connections export you paste or download yourself, then writes short, low-pressure ask drafts, including a ready-to-forward blurb so the intro takes them one minute. Use it when someone says "who could introduce me to", "ask for referrals", "warm intros", "how do I ask my customers for referrals", "I know people at the bar association", "here are my LinkedIn connections, who can help", "write a referral ask", or "my first customers came from referrals, how do I get more". Writes sales/referrals.md and adds introduced leads to sales/leads.csv. Drafts only, the user sends. Never scrapes LinkedIn.
---

# referral-asks

Warm intros win more often than cold outreach because trust carries over. Most founders do
not ask, or they ask in a way that is hard to say yes to ("let me know if you know anyone").
This skill finds the few right people and writes an ask that is specific, easy, and fine to
ignore.

## What this skill reads and writes

Reads:
- Business context from founder-context (`founder/context.md`, else
  `~/.founder/active` and `~/.founder/businesses/<slug>.md`): who the user wants
  to reach (ICP), the offer, tone.
- The user's people, from what they give you: a pasted list, a customer export, notes, or the
  LinkedIn connections CSV they download themselves (LinkedIn Settings, "Get a copy of your
  data", Connections). Productivity's people notes (`~/.founder/people/`) if they exist.
- `sales/icp.md` and `sales/leads.csv`, to see which target companies a contact might know.

Writes:
- `sales/referrals.md`: who to ask, why, the ask drafts and a tracking table.
- When an intro happens, the new lead goes in with the lead-gen tool, source "referral from
  <name>": `python3 <skills>/lead-gen/scripts/leads.py add sales/leads.csv --business <slug>
  --company "<company>" --role "<role>" --source "referral from <name>" ...`
`<skills>` is the parent of this skill's folder; lead-gen is installed beside it. If
lead-gen is missing, edit sales/leads.csv by hand and keep its 16 columns.

Next skill: lead-email or follow-up once an intro email lands (reply on the intro thread);
call-prep when the intro turns into a meeting.

## Rules

- **The user's own data only.** Use lists the user owns or exported. Never log in to
  LinkedIn, scrape profiles, or guess who knows whom from public posts.
- **Never invent a connection.** "Priya might know Dana" needs a reason from the data (same
  company, same industry group, a past customer of hers). Label each reason as fact (from the
  list) or guess.
- **Easy to say no.** Every ask says plainly that no is fine. Ask each person once, plus one
  gentle reminder at most.
- **One ask per person, specific.** A named company or a clear type ("a small family law firm
  in Bellevue"), not "anyone who might need this".
- **Thank-yous and incentives honestly.** If the user offers a referral reward, say it plainly
  in the ask. Do not invent one. Some professions limit referral fees (lawyers, for example,
  under their bar's rules); suggest checking before offering money to them.
- **Drafts only, run humanize.** If humanize is not installed, clean by hand and say so.
- **When the request is off limits** (logging in, scraping, mass asks): the whole reply is
  about 6 lines. Two lines saying no and why, two lines on downloading their own connections
  export, one offer to pick 5 to 10 people from it. No plan, no templates nobody asked for.

## Step 1: Who could help

Sort the user's people into:
1. **Happy customers:** the strongest. They know the product works. Ask them who else has the
   same problem.
2. **People inside or close to the target companies:** worked there, works there, sits on a
   board or committee with them, is their supplier.
3. **Connectors in the buyer's world:** association organizers, accountants or consultants who
   serve the same customers, coworking managers, local business groups.
4. **Friends and past colleagues** who simply know a lot of people in the area or industry.

Pick 5 to 10, not 50. For each: who, which group, who they could open a door to and why (fact
or guess), and how warm the relationship is. Warmth comes only from what the user says ("we're
close", "met once"). A connection date or job title says nothing about warmth: write
"unknown, tell me" and ask in the reply. Get each person's role at their company right from the
data; do not guess who reports to whom.

With a LinkedIn connections export, match `Company` and `Position` columns against the ICP and
the companies in `sales/leads.csv`. A match is a starting point, not a promise they know the
decision maker.

## Step 2: Write the asks

Each ask is under 100 words and has:
- a personal first line (from what the user tells you about them; if nothing, use
  `{{personal line}}`),
- what the user is doing, in one sentence,
- the specific ask: "Do you know the office manager at Juniper Family Law, or anyone at a small
  family law firm on the Eastside?",
- the easy out: "Totally fine if not, or if it's awkward.",
- the offer to make it easy: "If yes, I've put a short blurb below you can forward."

**The forwardable blurb** (50 to 70 words, written so the contact can paste it): who the user is,
what they help with, why this person might care, and how to reply. No hype, no claims beyond
founder-context.

For happy customers, a different ask: thank them first for something specific, then "who else
do you know who deals with <the problem>?" Give them the blurb too.

Adapt the channel: email, text, or LinkedIn message (user sends by hand). For texts, cut to two
lines and skip the blurb unless they say yes.

Personal first lines come only from the user's notes. If you have nothing, write
`{{personal line}}`; do not make up a shared memory, and do not add details to how they met.
Use names, not pronouns you were not given. A text is two lines; if it needs more, it is an
email.

**Groups:** for a class, a club or a group chat, write one group post (3 to 4 lines, with the
blurb and one clear ask), not one message per person. Then pick the 2 or 3 members the user
knows best for a personal follow-up.

**Partners who see your buyers every day** (a food truck, a front desk, a coworking manager):
give them something to hand over, not just a question. A card or a sign-up link or QR code
(`{{sign-up link}}`) they can show, plus a line they can say, plus what is in it for them if
the user offers something.

## Step 3: Track it

A table in `sales/referrals.md`: person, asked on, for whom, answer, intro made, lead added.
Suggest a reminder after one week, once, then let it go.

## File format

```
# Referral asks for <business>, <date>

## Who to ask
| person | group | could open a door to | why (fact or guess) | warmth |

## Asks
### <person> (<channel>)
<draft>

### Forwardable blurb
<blurb>

## Tracking
| person | asked | for | answer | intro | lead added |
```

In the reply: the top 3 people to ask first and why, one sample ask, and a last line naming
the next skill ("Next: when an intro lands, run lead-email or follow-up on that thread.").
Count the words before you save: asks under 100, texts two lines, blurbs 50 to 70.
