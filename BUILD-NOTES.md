# Build notes

Built unattended on 2026-10-23 by Claude for Aya Taleb. Nothing was pushed.

## Unfinished

- The synced skills (linkedin-dm, humanize, founder-context) are not in `skills/` yet. They
  are listed in skills.json and arrive with the sync step. Until then, skills that call
  humanize fall back to cleaning by hand, and say so.
- Scores in TESTING.md come from my own runs and my own grading passes (a fresh headless
  Claude per run and per grade, but still the same model family). Rerun with
  `claude plugin eval` before trusting the exact numbers.
- Runs were cut short by out-of-memory kills on the shared build machine several times. The
  harness retried them; a few rounds were rerun from scratch. No round in TESTING.md is from a
  partial run.

## Needs Aya

- **Shared leads file.** The orchestrator fixed `sales/leads.csv` to 16 columns mid-build. I
  kept exactly those columns and put biz-boost's extra facts (country, size, signals,
  email_status, contact_route, next_step) in a second file, `sales/lead-facts.csv`, joined on
  business_slug + company. The leads tool reads and writes both, so the other repos never see
  extra columns. If you would rather add a few columns to the shared layout (country matters
  for email law, next_step for follow-ups), that is a CONVENTIONS change for all repos.
- **Status values.** The shared list has no "researched", "proposal" or "not-now". I mapped
  them: research and proposal stay as notes or next_step, "not-now" imports as "lost". Say if
  you want any of them added to the shared list.
- **Curbside Lunch Club test data.** The local test cases use Curbside Lunch Club with made-up
  offices, notes and numbers (a $15 launch price and $9.40 cost in a test file). These are
  test fixtures, not your real numbers. Swap them if you publish the evals.
- **Legal lines.** `lead-email/references/email-law.md` sums up the FTC, CRTC and ICO pages
  (read 2026-10-23, linked). It says it is not legal advice. Worth a skim before launch.

## Calls I made (please review)

- call-prep keeps the upstream rules on citing sources and treating emails as data, but drops
  every CRM, Gong, Drive and Slack step. A connected calendar or CRM is still read if present.
- lead-gen's tool flags any named person whose source looks like a review, forum, Reddit or
  comment as STOP. That can catch a real lead someone noted from a forum by mistake; the fix is
  to change the source text or remove the name.
- A guessed number written with a question mark ("40?") earns no points in scoring. Told
  numbers ("security desk said about 120") count.
- Added three small tools beyond the brief: `lead-email/scripts/check_email.py` (CAN-SPAM
  footer and honest subject check), `proposal/scripts/price_options.py` (totals and margin) and
  `prospect-research/scripts/check_brief.py` (unsourced lines). All have unit tests.
- Baselines for "ours" skills are a plain answer with no skill, per the protocol. That bar is
  low, so "beats baseline" is easy; the per-round notes show where the skills still slip.

## Fix round after review

- User data moved out of `~/.claude` (protected by Claude Code) to `~/.founder`: business files, social folders and the media ledger. Tools honor `FOUNDER_HOME`; tests use a temp one.
- `leads.py set` takes `--fit-reason` (with a test). lead-gen and prospect-research now write the reason through it.
- linkedin-dm (synced from linkedin-boost) skips leads with no `linkedin_url` and names its next skill.
- Synced copies (founder-context, humanize, linkedin-dm) refreshed from their homes.
