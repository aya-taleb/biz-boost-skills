import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "prospect-research", "scripts"))

import check_brief  # noqa: E402

GOOD = """# Acme
## Snapshot
- What they do: shoes [site](https://acme.com/about), read 2026-10-23
- Size: unknown
## What changed lately
- 2026-10-01: new store in San Diego, its 12th [news](https://news.example/acme), read 2026-10-23
## Who decides
- Role: head of marketing (inference: team page lists a marketing team)
- Best route: [contact page](https://acme.com/contact) (not opened)
## Reason to reach out now
New store opened 2026-10-01 [news](https://news.example/acme).
## Check before you send
- Revenue figure (search snippet only, not confirmed)
## Sources
- [Acme about](https://acme.com/about/), read 2026-10-23: "Acme makes running shoes"
- [News](https://news.example/acme), read 2026-10-23: "Acme opened its 12th store, in San Diego"
"""


class CheckBriefTest(unittest.TestCase):
    def test_good_brief_passes(self):
        problems, notes = check_brief.check(GOOD)
        self.assertEqual(problems, [])
        self.assertEqual(notes, [])

    def test_unsourced_fact_fails(self):
        problems, _ = check_brief.check("## Snapshot\n- They have 500 staff\n")
        self.assertEqual(len(problems), 1)

    def test_news_without_date(self):
        brief = ("## What changed lately\n- New CEO [x](https://x.com)\n"
                 "## Sources\n- [x](https://x.com), read 2026-10-23: \"names a new CEO\"\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("no date" in p for p in problems))

    def test_snippet_outside_check_section_noted(self):
        _, notes = check_brief.check("## Snapshot\n- Revenue $50M (search snippet only, not confirmed)\n")
        self.assertTrue(any("snippet" in n for n in notes))

    def test_email_noted(self):
        brief = ("## Who decides\n- Jo, jo@acme.com [team](https://acme.com/team)\n"
                 "## Sources\n- [team](https://acme.com/team), read 2026-10-23: \"Jo, jo@acme.com\"\n")
        _, notes = check_brief.check(brief)
        self.assertTrue(any("jo@acme.com" in n for n in notes))

    def test_other_sections_ignored(self):
        problems, _ = check_brief.check("## Opening line ideas\n- Saw your new store\n")
        self.assertEqual(problems, [])

    def test_link_missing_from_sources_fails(self):
        problems, _ = check_brief.check("## Snapshot\n- Shoes [site](https://acme.com/about)\n")
        self.assertTrue(any("not under Sources" in p for p in problems))

    def test_source_without_quote_fails(self):
        brief = ("## Snapshot\n- Shoes [site](https://acme.com/about)\n"
                 "## Sources\n- [site](https://acme.com/about), read 2026-10-23\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("no quote" in p for p in problems))

    def test_source_without_read_date_fails(self):
        brief = ("## Snapshot\n- Shoes [site](https://acme.com/about)\n"
                 "## Sources\n- [site](https://acme.com/about): \"Acme makes shoes\"\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("read <date>" in p for p in problems))

    def test_number_not_in_quote_fails(self):
        brief = ("## Snapshot\n- About 500 staff [site](https://acme.com/about)\n"
                 "## Sources\n- [site](https://acme.com/about), read 2026-10-23: \"a team of 50\"\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("number 500" in p for p in problems))

    def test_number_in_quote_passes_with_commas(self):
        brief = ("## Snapshot\n- 1,200 staff [site](https://acme.com/about)\n"
                 "## Sources\n- [site](https://acme.com/about), read 2026-10-23: \"our 1200 people\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_years_and_read_dates_are_not_numbers(self):
        brief = ("## What changed lately\n- 2026-04-16: closed stores in 2026 [n](https://n.example/a), read 2026-10-23\n"
                 "## Sources\n- [n](https://n.example/a), read 2026-10-23: \"closed its stores\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_name_not_in_quote_fails(self):
        brief = ("## Snapshot\n- Based in San Francisco [n](https://n.example/a)\n"
                 "## Sources\n- [n](https://n.example/a), read 2026-10-23: \"the shoe brand said\"\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("San Francisco" in p for p in problems))

    def test_name_in_quote_passes(self):
        brief = ("## Who decides\n- Name: Jo Park, CMO [team](https://acme.com/team)\n"
                 "## Sources\n- [team](https://acme.com/team), read 2026-10-23: \"Jo Park, Chief Marketing Officer\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_long_reason_fails(self):
        brief = ("## Reason to reach out now\n" + " ".join(["word"] * 30) + " (inference: x)\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("30 words" in p for p in problems))

    def test_short_reason_with_link_passes(self):
        brief = ("## Reason to reach out now\nThey opened a new store on 2026-10-01 [news](https://n.example/a), read 2026-10-23.\n"
                 "## Sources\n- [news](https://n.example/a), read 2026-10-23: \"opened a new store\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_not_opened_link_skips_source_check(self):
        problems, _ = check_brief.check("## Who decides\n- Route: [contact](https://acme.com/c) (not opened)\n")
        self.assertEqual(problems, [])

    def test_url_match_ignores_trailing_slash_and_www(self):
        brief = ("## Snapshot\n- Shoes [site](https://www.acme.com/about/)\n"
                 "## Sources\n- [site](https://acme.com/about), read 2026-10-23: \"Acme makes shoes\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_curly_quotes_count(self):
        brief = ("## Snapshot\n- 40 stores [site](https://acme.com/a)\n"
                 "## Sources\n- [site](https://acme.com/a), read 2026-10-23: “we run 40 stores”\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_worked_out_month_fails(self):
        brief = ("## Snapshot\n- Sold in March 2026 [n](https://n.example/a)\n"
                 "## Sources\n- [n](https://n.example/a), read 2026-10-23: \"sold last month\"\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("month 'march'" in p for p in problems))

    def test_month_in_news_prefix_is_fine(self):
        brief = ("## What changed lately\n- Apr 15, 2026: brand sold [n](https://n.example/a), read 2026-10-23\n"
                 "## Sources\n- [n](https://n.example/a), read 2026-10-23: \"sold its shoe brand\"\n")
        problems, _ = check_brief.check(brief)
        self.assertEqual(problems, [])

    def test_reason_of_25_words_fails(self):
        brief = ("## Reason to reach out now\n" + " ".join(["word"] * 25) + " (inference: x)\n")
        problems, _ = check_brief.check(brief)
        self.assertTrue(any("25 words" in p for p in problems))

    def test_main_exit_code(self):
        path = os.path.join(tempfile.mkdtemp(), "b.md")
        with open(path, "w") as fh:
            fh.write(GOOD)
        self.assertEqual(check_brief.main([path]), 0)
        with open(path, "w") as fh:
            fh.write("## Snapshot\n- 500 staff\n")
        self.assertEqual(check_brief.main([path]), 1)


if __name__ == "__main__":
    unittest.main()
