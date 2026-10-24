import csv
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "lead-gen", "scripts"))

import leads  # noqa: E402


def row(**kw):
    base = {c: "" for c in leads.COLUMNS}
    base.update(kw)
    return base


class NormaliseTest(unittest.TestCase):
    def test_company_suffixes_and_case(self):
        self.assertEqual(leads.norm_company("The Acme Co."), "acme")
        self.assertEqual(leads.norm_company("ACME, Inc"), "acme")
        self.assertEqual(leads.norm_company("Smith & Jones LLP"), "smith and jones")

    def test_domain_from_url_and_email(self):
        self.assertEqual(leads.norm_domain("https://www.acme.com/about"), "acme.com")
        self.assertEqual(leads.norm_domain("jo@Acme.com"), "acme.com")
        self.assertEqual(leads.norm_domain(""), "")


class DedupeTest(unittest.TestCase):
    def test_same_domain_merges_and_keeps_fuller_row(self):
        rows = [
            row(company="Acme", website="acme.com", source="apollo"),
            row(company="Acme Inc", website="https://www.acme.com", role="Office manager",
                source="manual", city="Seattle"),
        ]
        out, merged = leads.dedupe(rows)
        self.assertEqual(merged, 1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["role"], "Office manager")
        self.assertIn("apollo", out[0]["source"])
        self.assertIn("manual", out[0]["source"])

    def test_same_name_different_city_kept_apart(self):
        rows = [row(company="Pho House", city="Seattle"), row(company="Pho House", city="Tacoma")]
        out, merged = leads.dedupe(rows)
        self.assertEqual(merged, 0)
        self.assertEqual(len(out), 2)

    def test_personal_email_domain_does_not_merge_companies(self):
        rows = [row(company="A", email="a@gmail.com"), row(company="B", email="b@gmail.com")]
        out, merged = leads.dedupe(rows)
        self.assertEqual(len(out), 2)


class ScoreTest(unittest.TestCase):
    ICP = {
        "criteria": [
            {"name": "legal industry", "field": "industry", "match": "contains_any",
             "values": ["law", "legal"], "points": 50},
            {"name": "10-200 staff", "field": "size", "match": "range", "min": 10, "max": 200,
             "points": 30},
            {"name": "has a signal", "field": "signals", "match": "present", "points": 20},
        ],
        "disqualify": [{"name": "already a customer", "field": "status", "match": "equals_any",
                        "values": ["won"]}],
    }

    def test_full_match_scores_100(self):
        r = row(industry="Law practice", size="51-200", signals="hiring paralegals")
        score, reason = leads.score_row(r, self.ICP)
        self.assertEqual(score, 100)
        self.assertIn("legal industry", reason)

    def test_partial_match_and_reason_lists_missing(self):
        r = row(industry="Legal services", size="2-10")
        score, reason = leads.score_row(r, self.ICP)
        self.assertEqual(score, 50)
        self.assertIn("missing: 10-200 staff, has a signal", reason)

    def test_disqualified_scores_zero(self):
        r = row(industry="law", status="won")
        score, reason = leads.score_row(r, self.ICP)
        self.assertEqual(score, 0)
        self.assertTrue(reason.startswith("disqualified"))

    def test_sort_and_keep_reason(self):
        rows = [row(company="low", industry="retail", fit_reason="hand note"),
                row(company="high", industry="law", size="20", signals="x")]
        out = leads.score_rows(rows, self.ICP, keep_reason=True)
        self.assertEqual(out[0]["company"], "high")
        self.assertEqual(out[1]["fit_reason"], "hand note")

    def test_bad_match_type_raises(self):
        with self.assertRaises(ValueError):
            leads.rule_matches({"field": "x", "match": "regex"}, row())

    def test_number_parsing(self):
        self.assertEqual(leads.to_number("1,200"), 1200)
        self.assertEqual(leads.to_number("11-50"), 30.5)
        self.assertIsNone(leads.to_number("unknown"))
        self.assertIsNone(leads.to_number("40?"))
        self.assertIsNone(leads.to_number("maybe 40"))
        self.assertEqual(leads.to_number("about 120"), 120)


class CheckTest(unittest.TestCase):
    def levels(self, r):
        return [(lvl, msg) for lvl, _, _, msg in leads.check_rows([r])]

    def test_named_reviewer_is_a_stop(self):
        r = row(company="Acme", name="Jane Doe", source="G2 review", country="US",
                fit_reason="x")
        self.assertTrue(any(l == "stop" and "review" in m for l, m in self.levels(r)))

    def test_company_from_review_without_person_is_fine(self):
        r = row(company="Acme", source="G2 review", country="US", fit_reason="x")
        self.assertFalse(any(l == "stop" for l, m in self.levels(r)))

    def test_outside_us_flags_law(self):
        r = row(company="Acme", source="manual", country="Germany", fit_reason="x")
        self.assertTrue(any("GDPR" in m for l, m in self.levels(r)))

    def test_inferred_email_flagged(self):
        r = row(company="Acme", email="jo@acme.com", email_status="inferred",
                source="manual", country="US", fit_reason="x")
        self.assertTrue(any("not verified" in m for l, m in self.levels(r)))

    def test_do_not_contact_is_stop(self):
        r = row(company="Acme", status="do-not-contact", source="manual", country="US",
                fit_reason="x")
        self.assertTrue(any(l == "stop" for l, m in self.levels(r)))

    def test_duplicates_flagged(self):
        rows = [row(company="Acme", website="acme.com", source="m", country="US", fit_reason="x"),
                row(company="ACME Inc", website="acme.com", source="m", country="US", fit_reason="x")]
        issues = leads.check_rows(rows)
        self.assertTrue(any("duplicate" in i[3] for i in issues))


class FileRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "sales", "leads.csv")

    def write_export(self, name, header, rows):
        p = os.path.join(self.dir, name)
        with open(p, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        return p

    def test_init_import_score_top_set(self):
        self.assertEqual(leads.main(["init", self.path]), 0)
        export = self.write_export(
            "apollo.csv",
            ["First Name", "Last Name", "Title", "Company", "Website", "Email", "Email Status",
             "# Employees", "Industry", "City", "Country", "Seniority"],
            [["Ana", "Lee", "Office Manager", "Acme Law", "acme.com", "ana@acme.com", "Verified",
              "45", "Law Practice", "Seattle", "United States", "Manager"],
             ["Ana", "Lee", "Office Manager", "Acme Law PLLC", "www.acme.com", "", "", "",
              "", "Seattle", "United States", ""],
             ["Bo", "Ng", "CEO", "Tiny Shop", "tiny.shop", "bo@tiny.shop", "guessed", "3",
              "Retail", "Seattle", "United States", "Owner"]])
        self.assertEqual(leads.main(["import", self.path, export, "--source", "Apollo export", "--business", "ledgerly"]), 0)
        rows = leads.read_rows(self.path)
        self.assertEqual(len(rows), 2)
        acme = [r for r in rows if r["company"].startswith("Acme")][0]
        self.assertEqual(acme["name"], "Ana Lee")
        self.assertEqual(acme["email_status"], "verified")
        self.assertEqual(acme["status"], "new")
        tiny = [r for r in rows if r["company"] == "Tiny Shop"][0]
        self.assertEqual(tiny["email_status"], "inferred")

        icp_path = os.path.join(self.dir, "icp.json")
        with open(icp_path, "w") as fh:
            json.dump(ScoreTest.ICP, fh)
        self.assertEqual(leads.main(["score", self.path, "--icp", icp_path]), 0)
        rows = leads.read_rows(self.path)
        self.assertEqual(rows[0]["company"], "Acme Law")
        table = leads.top_table(rows, 5)
        self.assertIn("Acme Law", table.splitlines()[2])

        self.assertEqual(leads.main(["set", self.path, "--company", "acme law",
                                     "--status", "contacted", "--last-contact", "2026-10-23",
                                     "--notes", "email 1 sent"]), 0)
        rows = leads.read_rows(self.path)
        acme = [r for r in rows if r["company"] == "Acme Law"][0]
        self.assertEqual(acme["status"], "contacted")
        self.assertEqual(leads.main(["set", self.path, "--company", "acme law",
                                     "--status", "maybe"]), 2)

        # --fit-reason replaces the rule text with a reason a person can act on
        self.assertEqual(leads.main(["set", self.path, "--company", "acme law", "--fit-reason",
                                     "hiring 3 paralegals,\n job ad Oct 2026"]), 0)
        acme = [r for r in leads.read_rows(self.path) if r["company"] == "Acme Law"][0]
        self.assertEqual(acme["fit_reason"], "hiring 3 paralegals, job ad Oct 2026")
        self.assertEqual(acme["status"], "contacted")  # other fields untouched
        # and score --keep-reason keeps it
        self.assertEqual(leads.main(["score", self.path, "--icp", icp_path, "--keep-reason"]), 0)
        acme = [r for r in leads.read_rows(self.path) if r["company"] == "Acme Law"][0]
        self.assertEqual(acme["fit_reason"], "hiring 3 paralegals, job ad Oct 2026")

    def test_check_exit_code(self):
        leads.write_rows(self.path, [row(company="A", name="Jo", source="reddit thread",
                                         country="US", fit_reason="x", business_slug="b")])
        self.assertEqual(leads.main(["check", self.path]), 1)
        leads.write_rows(self.path, [row(company="A", source="manual", country="US", fit_reason="x",
                                         business_slug="b")])
        self.assertEqual(leads.main(["check", self.path]), 0)

    def test_init_does_not_overwrite(self):
        leads.write_rows(self.path, [row(company="Keep me")])
        leads.main(["init", self.path])
        self.assertEqual(leads.read_rows(self.path)[0]["company"], "Keep me")

    def test_shared_file_has_exact_columns(self):
        leads.write_rows(self.path, [row(company="Acme", business_slug="b", size="40",
                                         country="US", my_col="x")])
        with open(self.path, newline="") as fh:
            header = next(csv.reader(fh))
        self.assertEqual(header, leads.SHARED)
        self.assertEqual(",".join(header),
                         "business_slug,name,company,role,email,linkedin_url,instagram_handle,"
                         "website,city,source,source_url,fit_score,fit_reason,status,"
                         "last_contact,notes")
        back = leads.read_rows(self.path)[0]
        self.assertEqual(back["size"], "40")
        self.assertEqual(back["my_col"], "x")

    def test_rows_written_by_other_skills_are_kept(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(leads.SHARED)
            w.writerow(["shop", "", "Acme", "", "", "", "@acme", "", "", "instagram dm", "",
                        "", "", "replied", "2026-10-01", "from ig"])
        leads.main(["dedupe", self.path])
        r = leads.read_rows(self.path)[0]
        self.assertEqual(r["instagram_handle"], "@acme")
        self.assertEqual(r["status"], "replied")

    def test_same_company_two_businesses_kept_apart(self):
        rows = [row(company="Acme", website="acme.com", business_slug="a"),
                row(company="Acme", website="acme.com", business_slug="b")]
        out, merged = leads.dedupe(rows)
        self.assertEqual(len(out), 2)
        with self.assertRaises(KeyError):
            leads.set_fields(out, "Acme", {"status": "won"})
        leads.set_fields(out, "Acme", {"status": "won"}, business="b")
        self.assertEqual([r["status"] for r in out], ["", "won"])

    def test_add_command(self):
        self.assertEqual(leads.main(["add", self.path, "--business", "btts", "--company",
                                     "Brightwave Labs", "--role", "office manager",
                                     "--size", "120", "--source", "manual: walk notes"]), 0)
        self.assertEqual(leads.main(["add", self.path, "--business", "btts", "--company",
                                     "Brightwave Labs", "--city", "Seattle"]), 0)
        rows = leads.read_rows(self.path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["city"], "Seattle")
        self.assertEqual(rows[0]["size"], "120")
        self.assertEqual(rows[0]["status"], "new")
        self.assertEqual(leads.main(["add", self.path, "--business", "btts", "--company", "X",
                                     "--status", "researched"]), 2)

    def test_old_status_words_normalised_on_import(self):
        export = self.write_export("old.csv", ["Company", "Status"], [["A", "researched"],
                                                                     ["B", "not-now"]])
        leads.main(["import", self.path, export, "--source", "old", "--business", "b"])
        got = {r["company"]: r["status"] for r in leads.read_rows(self.path)}
        self.assertEqual(got, {"A": "new", "B": "lost"})


if __name__ == "__main__":
    unittest.main()
