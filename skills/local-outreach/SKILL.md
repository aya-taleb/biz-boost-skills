---
name: local-outreach
description: Gets customers for a local business face to face. Picks which nearby offices, shops, buildings, events and community groups to reach, then writes the walk-in script, the front-desk ask, a short leave-behind, office manager and building manager emails, a partnership pitch, an event plan and a 2-week route. Built for owners who sell to their neighborhood, like a street-food lunch subscription reaching nearby offices, a cleaner, a gym, a cafe, a repair shop or a tutor. Use it when someone says "how do I get local customers", "what do I say when I walk into an office", "pitch to the office manager", "get my food into offices nearby", "partner with local businesses", "which events should I go to", "flyer for the lobby", or "door to door plan". Reads sales/leads.csv and writes sales/local/. Drafts only, and every script goes through humanize.
---

# local-outreach

For a local business, the best channel is usually a person at a front desk. One good
conversation in a lobby beats ten cold emails, because the office manager can see you, taste
the food or meet the person who will clean the building. Email is the follow-up, not the opener.

This skill plans where to show up and writes what to say there.

## What this skill reads and writes

Reads:
- Business context from founder-context (`founder/context.md`, else
  `~/.founder/active` and `~/.founder/businesses/<slug>.md`): the offer, area,
  who buys, prices, proof, tone, sender name and postal address. If the delivery or service area
  is missing, ask for it once.
- `sales/leads.csv` and `sales/lead-facts.csv` from lead-gen, plus `sales/partners.md` if it
  exists (coworking spaces, building managers, groups).
- The user's own notes: walk notes, a list of buildings, photos they describe.
- `sales/reach-plan.md` for how many hours a week they have.

Writes, in `sales/local/`:
- `targets.md`: who to visit and why, in route order.
- `scripts.md`: walk-in, front desk, phone and follow-up lines.
- `emails.md`: office manager, building or property manager, and partner emails.
- `leave-behind.md`: the text for a half-page flyer or card (no design).
- `events.md`: events and groups worth showing up to, with links and dates you found.
- `route.md`: a 2-week plan with days, stops and what to bring.
Updates leads with the lead-gen tool after visits:
`python3 <skills>/lead-gen/scripts/leads.py set sales/leads.csv --company "<name>" --status contacted --last-contact <date> --notes "<what happened>"`
or `add` for a new place found on the walk.
`<skills>` is the parent of this skill's folder; lead-gen is installed beside it. If
lead-gen is missing, edit sales/leads.csv by hand and keep its 16 columns.

Next skill: follow-up after a good conversation or a tasting; proposal when an office asks for
a price for the whole team; call-prep before a booked tasting or meeting.

## Rules

- **Be welcome, not a nuisance.** Respect "no soliciting" signs and building security. Ask the
  front desk, do not wander floors. If a building says no, thank them and leave it. Leave
  materials only where you were allowed to.
- **Permits and food safety are the owner's job to check.** For food, sampling or vending on
  someone's property, remind the user to check the local health department and city rules,
  and the property owner's permission. Give the official links when you found them. Not legal
  advice.
- **No invented facts.** Use only offer details, prices and proof from founder-context. That
  includes small promises and specifics ("same two people each time", "we set up and clean
  up", "lunch for 10", "nobody has to organize anything") unless the context says so; write
  them as `{{confirm: ...}}`, or keep the size as `{{number}}`. No made
  up customer counts, ratings or "loved by 500 offices". New business with no customers yet?
  Say what is real: "We start in December, and you'd be one of our first 15 offices."
- **No personal data harvesting.** Reach people in their work role, through the front desk or a
  published business contact. Do not look up employees' personal profiles.
- **Events and groups: show up as yourself,** follow each group's rules, help first, and do not
  mass-post. List only events you actually found, with link and date. Never invent an event.
- **Emails are drafts** with the sender's postal address and an opt-out (CAN-SPAM), as in
  lead-email. The user sends them.
- **Every script and email goes through humanize.** If humanize is not installed, clean by hand
  (no em dashes, no stock phrases, short spoken sentences) and say so.

## Step 1: Pick targets

Sort what the user has into three kinds, because each needs a different approach:
1. **Direct buyers:** offices, shops or homes that would buy. For a lunch service: offices with
   enough people on site and no cafeteria.
2. **Gatekeepers and multipliers:** one yes reaches many buyers. Building or property managers,
   coworking community managers, business improvement districts, chambers of commerce,
   HR or people teams at big employers, apartment managers.
3. **Partners:** businesses that serve the same customer without competing. For lunch: coffee
   shops in the lobby, gyms, coworking spaces, office cleaning or catering companies, local
   newsletters.

If there is no list yet, help the user build one on foot: a 60-minute walk with a note per
building (name, tenants on the lobby directory, cafe or not, front desk or not). For a list
from public sources, hand off to lead-gen.

Write `targets.md` as a table: place, kind (buyer, gatekeeper, partner), who to ask for (a role),
why it fits (from their notes or a source), and the order to visit. Group stops by block so a
route takes under an hour.

## Step 2: Write the scripts

Keep every script short enough to say in 20 seconds. People at a front desk are busy.
See `references/scripts.md` for worked examples by business type.

- **Front desk ask:** who you are, the one-line offer, and a question they can answer: "Who
  handles team lunches or office perks here?" Ask for the role, not a guess at a name.
- **Walk-in pitch to the decider:** their likely problem (from what you know about the office),
  the offer in one sentence, and a small, easy yes with a real day in it: "Could I bring lunch
  for 10 of your team next Wednesday or Thursday?" Name two days from the route so they can
  pick one. Bring the thing.
- **If they say "send me an email":** get the best address, say when you will send it, and send
  it that day (the office manager email in Step 3).
- **If they say no:** "Thanks. Is it okay if I check back in <month>?" Log it and move on.
- **Phone version:** the same ask in two sentences, for places with no walk-in access.
- **What to bring:** samples or a menu, the leave-behind, a sign-up link or QR code the user
  makes, and a way to take notes.

## Step 3: Write the emails

- **Office manager after a visit** (60 to 120 words): remind them who you are and when you met,
  the offer, the small yes with a specific date ("Can I bring lunch for 10 next Thursday?").
- **Office manager cold** (when walk-ins are not possible): same shape, open on something true
  about their office or building.
- **Building or property manager:** the offer as a tenant perk at no cost to the building
  (if true), what you need from them (a lobby table once a week, a mention in the tenant
  newsletter, a delivery spot), and how you handle trash, noise and safety.
- **Partner pitch:** what is in it for them (a referral fee, a cross-promotion, foot traffic,
  a perk for their members), what you ask, and a small first test.

Every email in the file, including partner and referral emails, ends with the sender's name,
business, postal address (or `{{street address}}`, flagged to fill) and an opt-out line.

## Step 4: Events and community

Search for real events in the area in the next 4 to 6 weeks: chamber mixers, business district
meetings, coworking open houses, industry meetups held near the target offices, farmers or
night markets, office-building tenant events. For each: name, date, link, why it fits, and what
to do there (bring samples, meet the community manager, sign people up). Pick 1 or 2, not all.

Also suggest one event the user could host if it fits (a free tasting in a coworking lounge, a
lunch-and-learn), with what to ask the host for. Write `events.md`.

## Step 5: The leave-behind

Half a page, no design, about 60 words: the offer, who it is for, the founding or launch offer
exactly as founder-context states it, how to sign up (link or QR from the user, else
`{{sign-up link}}`), and a phone or email. Plain, readable from a meter away.

## Step 6: The 2-week route

Fit it to the hours in `sales/reach-plan.md` (or ask; assume 5 hours a week if no answer).
Best times for offices are usually mid-morning, after the morning rush and before lunch;
say this is a starting guess the user should adjust. Each day: stops in walking order, the goal
(get a name, book a tasting), what to bring, and the follow-up to send that evening.

End with what to track: visits, decision makers met, tastings or trials booked, sign-ups.

## Before you finish

1. Run humanize on scripts.md, emails.md and leave-behind.md. Look for a `humanize` folder
   beside this skill first and use its tool if it is there. If it is not installed, clean by hand and write "humanize not installed,
   cleaned by hand" at the top of each file.
2. Add or update each visited or planned target in sales/leads.csv with the lead-gen tool, so
   follow-up and proposal can find them.
3. For permits and food safety, search for the official city and county pages and link them in
   route.md. If you cannot find them, name the office to ask (the county health department,
   the city business licensing office).

When the user wants something that breaks a rule (fake claims, flyers on cars, getting past
security), say no in a line each, give the reason in plain words without legal claims you
have not checked ("many cities and buildings ban this; check yours"), and give the honest
version right away. Keep that reply short.

## The reply

Short: the first 3 places to go and why, the front desk line, the next event, and where the
files are. Then the next skill.
