---
name: proposal
description: >-
  Writes a short proposal or quote a small business can send: the problem in the buyer's
  words, what you will do, 2 to 3 price options with totals checked by a script, timeline,
  what is not included, and terms to check before signing. Reads pricing from founder/
  (pricing.md, numbers.json, offer.md) and the call notes in sales/calls/. Use it when
  someone says "write a proposal", "send them a quote", "they asked for pricing", "put
  together three options", "price this job", "quote for 110 people", or "turn my call notes
  into a proposal". Works for app plans, services, catering, retainers and local jobs.
  Drafts only, and never invents prices: missing numbers become placeholders. Not a contract
  and not legal advice.
---

# proposal

A proposal is the buyer's notes, written back to them, with a price. Keep it short enough to
read on a phone: one to two pages. Long proposals do not win more; clear ones do.

## What this skill reads and writes

Reads, using what exists:
- The call debrief or notes: `sales/calls/*<company-slug>*` (from follow-up or call-prep). This
  is where the buyer's problem, words, decider, budget and dates come from. If there are no
  notes, ask for the basics in one message: what they need, quantity, start date, who signs.
- Prices: `founder/pricing.md`, `founder/numbers.json` (unit costs, price), `founder/offer.md`
  (bonuses, guarantee). Also the business context from founder-context.
- `sales/leads.csv` and `sales/accounts/<slug>.md` for the company's details.

Writes:
- `sales/proposals/<company-slug>-<YYYY-MM-DD>.md`: the proposal.
- `sales/proposals/<company-slug>-prices.json`: the price options, for the script.
- Updates the lead: `python3 <skills>/lead-gen/scripts/leads.py set sales/leads.csv --company
  "<name>" --next-step "proposal sent <date>, decision by <date>"` (status stays `meeting`
  until they decide). If lead-gen is not installed, edit the row by hand.
`<skills>` is the parent of this skill's folder; lead-gen is installed beside it. If
lead-gen is missing, edit sales/leads.csv by hand and keep its 16 columns.

Next skill: follow-up to plan the nudges after it is sent; call-prep if a review call is set.

## Rules

- **No invented prices.** Use prices from founder/ files or the user. If a price is missing,
  write `{{price per seat}}` and list it at the top as "fill before sending". Never pick a
  number because it sounds right.
- **No invented proof.** Case studies, testimonials, customer counts and results only if
  founder-context or founder/ lists them as usable. Respect off-limits topics.
- **Totals come from the script,** not mental math:
  `python3 scripts/price_options.py sales/proposals/<slug>-prices.json --md sales/proposals/<slug>-table.md`
  Paste its table into the proposal. If prices are placeholders, skip the script and show the
  formula instead ("{{price}} x 6 seats x 12 months").
- **Only promise what the notes support.** Scope lists only what the notes or founder files
  say the user will do. Anything the buyer asked for that the user did not confirm (a trial
  account, a dietary option, rotating vendors) goes under "To confirm", not in scope.
- **No prices yet?** Do not stop and do not guess. Write the whole proposal with
  `{{price}}` placeholders, and tell the user the fastest way to set prices: their own costs
  and competitors, or a pricing skill if they have one (for example founder-pricing from
  biz-ready). Keep scope to what founder-context says the product does.
- **Not legal advice.** The "terms to check" list is a reminder of what to decide, not a
  contract. For a large deal, the user should have a lawyer or an advisor read the final terms.
- **Drafts only.** The user sends it and signs nothing through this skill.

## How to build the options

Two or three options, never more. Each one solves the problem; they differ in scope (how many
people, which days, how much service) as well as term, not just in contract length. If a
launch or founding price exists, show the option it applies to at that price, with the normal
price beside it.

A pattern that is easy to choose from:
1. **Start small:** the smallest thing that solves the main problem. Lowest risk for them.
2. **Recommended:** what the notes say they need. Mark it "Recommended" and say why in one
   line, tied to their words.
3. **Full:** more scope, longer term or more service, often with a discount for the commitment
   if founder/ allows one.

Price what they asked for first. If they asked for "about 110 people", one option is exactly
that at the standard price, so they can compare. Apply a founding or launch discount only to
what the offer covers, and show it as its own line.

If the buyer named a budget line ("anything over $200 a month needs more thought"), make sure
one option sits under it if the business can do that profitably, and say so.

Use a founding or early price only if founder-context or founder/offer.md offers one, with
its exact terms (how many seats, how long, deadline).

If `founder/numbers.json` gives unit costs, add `cost_per_unit` to the JSON and check the
margin the script prints. Flag any option under the user's target margin before they send it.

## Proposal format

```
# Proposal for <company>
Prepared for <name, role> by <sender, business>, <date>. Valid until <date>.

## What you told us
- <their problem, in their words from the notes>
- <what it costs them now, if they said>
- <what they want to be true>

## What we will do
- <scope, plain and specific>

## Options
<table from the script>

**Recommended: <option>.** <one line on why, tied to what they said>

## Timeline
- <start date>: ...
- <milestones, from the notes or as {{date}}>

## Not included
- <things outside scope, and options they asked about that are not confirmed>

## Terms to check before signing
- Payment: when and how (upfront, monthly, net 15)
- Term and cancel: how long, notice to cancel
- Changes: what happens if the quantity or scope changes
- <business-specific: delivery window, minimum order, data import, dietary labels...>

## Next step
<one action: "reply with the option you want and we start on <date>", or a review call>
(In your reply to the user, also name the next skill: follow-up, to plan the nudges.)

Questions: <sender name, email or phone from context>
```

More terms by business type: `references/terms-by-business.md`.

## Before showing it

1. Check every number against the script output or the founder/ file it came from.
2. List every `{{placeholder}}` at the top under "Fill before sending". Search the file for
   `{{` and make sure each one is on the list.
3. Run humanize on the proposal text (not the table). If humanize is not installed, clean it
   by hand: no em dashes, no stock phrases, short sentences, and say so in the reply.

In the reply: the options in one line each, the recommended one, the placeholders to fill,
and the next step.
