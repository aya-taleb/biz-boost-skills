import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "lead-email", "scripts"))

import check_email  # noqa: E402

GOOD = """# Drafts for Acme

## Email 1 (day 0)
Subject: Billing at Acme Legal

Hi Dana,

Saw your billing clerk job post. Ledgerly does billing for small firms.

Worth a 15 minute look?

Sam Ortiz, Ledgerly Inc., 1200 Fifth Ave Suite 400, Seattle WA 98101
Not for you? Reply "no" and I won't email again.

## Email 2 (day 4)
Subject: Re: Billing at Acme Legal

Short follow-up.

Sam, Ledgerly Inc., 1200 Fifth Ave Suite 400, Seattle WA 98101
Reply "stop" to opt out.
"""


class SplitTest(unittest.TestCase):
    def test_finds_two_drafts(self):
        self.assertEqual(len(check_email.split_drafts(GOOD)), 2)

    def test_ignores_headings_without_subject(self):
        self.assertEqual(len(check_email.split_drafts("## Notes\nno subject here\n")), 0)


class CheckTest(unittest.TestCase):
    def test_good_drafts_pass(self):
        drafts = check_email.split_drafts(GOOD)
        for i, d in enumerate(drafts):
            problems, _ = check_email.check_draft(d, i)
            self.assertEqual(problems, [], d["title"])

    def test_reply_subject_ok_on_follow_up_only(self):
        d = {"title": "x", "lines": ["Subject: Re: hello", "1 Main St", "reply stop to opt out"]}
        self.assertTrue(any("pretends" in p for p in check_email.check_draft(d, 0)[0]))
        self.assertFalse(any("pretends" in p for p in check_email.check_draft(d, 1)[0]))

    def test_missing_address_and_opt_out(self):
        d = {"title": "x", "lines": ["Subject: hello", "Hi there, want lunch?"]}
        problems, _ = check_email.check_draft(d, 0)
        self.assertTrue(any("address" in p for p in problems))
        self.assertTrue(any("opt-out" in p for p in problems))

    def test_address_placeholder_accepted_and_listed(self):
        d = {"title": "x", "lines": ["Subject: hello", "Nora, {{street address}}, Seattle WA",
                                     "Not interested? Reply no and I won't email again."]}
        problems, notes = check_email.check_draft(d, 0)
        self.assertEqual(problems, [])
        self.assertTrue(any("{{street address}}" in n for n in notes))

    def test_po_box_counts(self):
        d = {"title": "x", "lines": ["Subject: hi", "PO Box 123, Seattle", "unsubscribe"]}
        self.assertEqual(check_email.check_draft(d, 0)[0], [])

    def test_style_notes(self):
        d = {"title": "x", "lines": ["Subject: URGENT offer", "We leverage AI — fast.",
                                     "1 Main St", "unsubscribe"]}
        problems, notes = check_email.check_draft(d, 0)
        self.assertTrue(any("bait" in n for n in notes))
        self.assertTrue(any("em dash" in n for n in notes))
        self.assertTrue(any("leverage" in n for n in notes))

    def test_all_caps_subject(self):
        d = {"title": "x", "lines": ["Subject: FREE LUNCH", "1 Main St", "unsubscribe"]}
        self.assertTrue(any("caps" in p for p in check_email.check_draft(d, 0)[0]))

    def test_main_exit_codes(self):
        path = os.path.join(tempfile.mkdtemp(), "d.md")
        with open(path, "w") as fh:
            fh.write(GOOD)
        self.assertEqual(check_email.main([path]), 0)
        with open(path, "w") as fh:
            fh.write("## E1\nSubject: hi\nno footer\n")
        self.assertEqual(check_email.main([path]), 1)


if __name__ == "__main__":
    unittest.main()
