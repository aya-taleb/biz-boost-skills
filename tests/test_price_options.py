import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "proposal", "scripts"))

import price_options as po  # noqa: E402


class TotalsTest(unittest.TestCase):
    def test_monthly_and_once(self):
        r = po.option_totals({"name": "A", "term_months": 12, "lines": [
            {"item": "seat", "unit_price": 29, "qty": 6, "per": "month"},
            {"item": "setup", "unit_price": 100, "qty": 1, "per": "once"}]})
        self.assertEqual(r["monthly"], 174)
        self.assertEqual(r["term_total"], 174 * 12 + 100)

    def test_discount_applies_to_recurring_only(self):
        r = po.option_totals({"name": "A", "term_months": 12, "discount_pct": 30, "lines": [
            {"item": "seat", "unit_price": 100, "per": "month"},
            {"item": "setup", "unit_price": 50, "per": "once"}]})
        self.assertAlmostEqual(r["monthly"], 70)
        self.assertAlmostEqual(r["term_total"], 70 * 12 + 50)
        self.assertEqual(r["monthly_list"], 100)

    def test_weekly_lines(self):
        r = po.option_totals({"name": "Lunch", "term_months": 3, "lines": [
            {"item": "lunch", "unit_price": 14, "qty": 110, "per": "week"}]})
        self.assertAlmostEqual(r["monthly"], 14 * 110 * 52 / 12)

    def test_margin(self):
        r = po.option_totals({"name": "A", "term_months": 1, "lines": [
            {"item": "lunch", "unit_price": 10, "qty": 1, "per": "month"}]}, {"lunch": 6})
        self.assertAlmostEqual(r["margin_pct"], 40)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            po.option_totals({"name": "A", "lines": [{"item": "x", "unit_price": 1, "per": "day"}]})
        with self.assertRaises(ValueError):
            po.option_totals({"name": "A", "discount_pct": 100, "lines": []})

    def test_one_time_option_row(self):
        md, _ = po.table({"options": [{"name": "Trial", "term_months": 1, "lines": [
            {"item": "tasting", "unit_price": 150, "per": "once"}]}]})
        self.assertIn("| Trial | none | $150 | one time | $150 |", md)
        md, _ = po.table({"options": [{"name": "M", "term_months": 1, "lines": [
            {"item": "x", "unit_price": 5}]}]})
        self.assertIn("1 month |", md)

    def test_money(self):
        self.assertEqual(po.money(1234.5, "USD"), "$1,234.50")
        self.assertEqual(po.money(2000, "USD"), "$2,000")


class MainTest(unittest.TestCase):
    def test_table_and_exit_codes(self):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "p.json")
        with open(p, "w") as fh:
            json.dump({"currency": "USD", "options": [
                {"name": "Good", "lines": [{"item": "seat", "unit_price": 29, "qty": 6}]},
                {"name": "Better", "discount_pct": 10,
                 "lines": [{"item": "seat", "unit_price": 29, "qty": 6}]}]}, fh)
        md_path = os.path.join(d, "t.md")
        self.assertEqual(po.main([p, "--md", md_path]), 0)
        text = open(md_path).read()
        self.assertIn("| Good | $174 |", text)
        self.assertIn("(list $174)", text)
        with open(p, "w") as fh:
            json.dump({"options": []}, fh)
        self.assertEqual(po.main([p]), 2)


if __name__ == "__main__":
    unittest.main()
