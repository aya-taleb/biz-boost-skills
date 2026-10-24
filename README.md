# biz-boost-skills

Get customers as a solo founder or a small local business, with plain files and no CRM.

## What do you want to do?

| I want to... | run this |
| --- | --- |
| figure out who to sell to and get a scored list of leads | /lead-gen |
| clean up and score a lead export I already have | /lead-gen |
| learn about one company before I reach out | /prospect-research |
| write a cold email and two follow-ups | /lead-email |
| plan how many people to reach each week, and where | /reach-plan |
| get ready for a sales call or a tasting | /call-prep |
| turn my call notes into next steps and a recap email | /follow-up |
| send a quote with 2 or 3 price options | /proposal |
| get nearby offices, shops or neighbors as customers | /local-outreach |
| ask people I know for warm intros | /referral-asks |
| write a LinkedIn note to a lead (I send it myself) | /linkedin-dm |

## Install

/plugin marketplace add aya-taleb/biz-boost-skills
/plugin install biz-boost-skills@biz-boost-skills

## Start here

Run /lead-gen and tell it what you sell. It reads your business context (or asks for it),
builds a profile of who buys from real evidence, and writes `sales/leads.csv` with a score and
a reason for each lead. Then run /reach-plan to set a weekly pace you can keep.

Everything lives in a `sales/` folder in your project: leads, research, emails, call notes and
proposals. Each skill reads what the last one wrote.

## Good to know

- No scraping and no bots. Skills read pages the normal way and work from exports you own.
  Nothing logs in to LinkedIn, email or any site for you.
- People who post reviews or comments are not leads. Their words shape your profile. Their
  names never go into a cold outreach list.
- Nothing is sent for you. Every email and message is a draft. Cold emails include your postal
  address and an opt-out, and leads outside the US get a GDPR, PECR or CASL check first.
- Nothing is made up. Every fact has a link or a file it came from, and missing numbers stay as
  `{{placeholders}}`. Paid data tools wait for your yes on the cost.
- This is not legal advice. For big campaigns or other countries, ask a lawyer who knows email
  marketing law.

## Credits

Made by Aya Taleb (github.com/aya-taleb). call-prep is changed from Anthropic's call-prep skill
in knowledge-work-plugins (Apache 2.0). Thanks to Anthropic's sales and small-business plugins
for ideas. See CREDITS.md. MIT.
