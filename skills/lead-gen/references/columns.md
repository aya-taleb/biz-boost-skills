# The two lead files

## sales/leads.csv (shared, fixed layout)

linkedin-boost and instagram-boost read this file too, so the columns and their order never
change. Empty cells are fine. Never fill a cell with a guess.

```
business_slug,name,company,role,email,linkedin_url,instagram_handle,website,city,source,source_url,fit_score,fit_reason,status,last_contact,notes
```

| column | what goes in it |
| --- | --- |
| business_slug | which of the user's businesses this lead is for (the slug from founder-context) |
| name | the person, only if the company publishes it or a connector returns it; else blank |
| company | the business name |
| role | the role to reach: owner, office manager, head of ops |
| email | only a published or verified address; else blank |
| linkedin_url | a profile or company page the user found or exported; never scraped |
| instagram_handle | the business's own handle, for instagram-dm |
| website | the company's own site, used to spot duplicates |
| city | where they are |
| source | where the row came from: "Apollo export 2026-10", "manual: company site" |
| source_url | the link that backs the row or its signal |
| fit_score | 0 to 100, from the tool |
| fit_reason | one line a person can act on |
| status | new, contacted, replied, meeting, won, lost, do-not-contact |
| last_contact | date of the last contact, YYYY-MM-DD |
| notes | anything else, appended with "; " |

## sales/lead-facts.csv (biz-boost only)

Extra facts per lead, joined by business_slug and company. The tool writes it, so you never
need to keep the two files in step by hand.

| column | what goes in it |
| --- | --- |
| country | decides which email law applies (blank means unknown, not US) |
| industry, size | for scoring; size can be a number, a range like 11-50, or "40?" for a guess |
| signals | what is happening now, with a date: hiring, moved offices, asked for an alternative |
| email_status | verified, inferred, unknown or invalid |
| contact_route | how to reach them without an email: contact form URL, main phone, front desk |
| next_step | the next action and its date |

Any extra column from an export also lands here.

## Updating a lead from another skill

```
python3 <lead-gen folder>/scripts/leads.py set sales/leads.csv --company "<name>" \
  [--business <slug>] [--status contacted] [--last-contact 2026-10-23] \
  [--next-step "email 2 on 2026-10-27"] [--notes "sent email 1"]
```

Add one researched lead by hand:

```
python3 <lead-gen folder>/scripts/leads.py add sales/leads.csv --business <slug> \
  --company "<name>" --role "office manager" --city Seattle --size 120 \
  --source "manual: walk notes 2026-10-20" --signals "no cafeteria (security desk)"
```

Every flag matches a column name with "-" for "_".
