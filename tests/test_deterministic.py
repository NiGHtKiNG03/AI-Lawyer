"""Offline unit tests for the deterministic safeguards (no LLM, no network).
Run: python3 -m unittest tests.test_deterministic -v
These test CODE behaviour only. They say nothing about the quality of model output; see tests/run_scenarios.py."""
import unittest

from lawyer import kb, safety, validate


class TestSafety(unittest.TestCase):
    def test_court_notice_received(self):
        self.assertIn("court_notice", safety.scan("I got a court notice yesterday, reply by next week"))
        self.assertIn("court_notice", safety.scan("मुझे कोर्ट का नोटिस मिला है"))

    def test_sending_a_notice_is_not_urgent(self):
        self.assertNotIn("court_notice", safety.scan("I want to send a legal notice to my landlord"))

    def test_criminal_and_emergency(self):
        self.assertIn("criminal", safety.scan("The landlord filed an FIR against me"))
        self.assertIn("emergency", safety.scan("he is beating me and threatened to kill me"))

    def test_plain_deposit_dispute_has_no_flags(self):
        self.assertEqual(safety.scan("My landlord is not returning my 20,000 rupee security deposit"), [])

    def test_amount_threshold(self):
        r = safety.reasons([], amount_inr=500000, category="tenant")
        self.assertIn("substantial_amount", [x["code"] for x in r])
        self.assertEqual(safety.reasons([], amount_inr=20000, category="tenant"), [])

    def test_redaction(self):
        t = safety.redact("card 4111 1111 1111 1111 and aadhaar 1234 5678 9012, otp is 482913")
        self.assertNotIn("4111", t)
        self.assertNotIn("5678", t)
        self.assertNotIn("482913", t)


class TestCitationValidation(unittest.TestCase):
    def setUp(self):
        self.cons = [e for e in kb.retrieve("consumer")]
        self.ten = [e for e in kb.retrieve("tenant")]

    def test_verified_section_with_correct_act_is_kept(self):
        txt = "A complaint must be filed within two years under Section 69 of the Consumer Protection Act, 2019."
        out, removed = validate.scrub_text(txt, self.cons)
        self.assertEqual(out, txt)
        self.assertEqual(removed, [])

    def test_invented_section_is_removed(self):
        out, removed = validate.scrub_text("Under Section 999A of the Consumer Protection Act you get a refund.", self.cons)
        self.assertNotIn("999A", out)
        self.assertTrue(removed)

    def test_section_not_backed_for_this_category_is_removed(self):
        out, removed = validate.scrub_text("Your deposit is protected by Section 69 of the Act.", self.ten)
        self.assertNotIn("69", out)

    def test_pending_section_never_leaks_to_model(self):
        for e in kb.for_model(kb.load().values()):
            if e["verification"] == "pending_section":
                self.assertIsNone(e["section"], e["id"])

    def test_case_law_citation_removed(self):
        out, removed = validate.scrub_text("As held in Rajesh Kumar v. State Bank of India (2015) 4 SCC 123, you win.", self.cons)
        self.assertNotIn("SCC 123", out)
        self.assertTrue(removed)

    def test_user_cited_nonexistent_section_is_flagged(self):
        r = validate.check_user_cited_sections("What does Section 999A of the Consumer Protection Act 2019 say?", list(kb.load().values()))
        self.assertEqual(len(r), 1)
        self.assertFalse(r[0]["verified"])

    def test_user_cited_real_section_is_verified(self):
        r = validate.check_user_cited_sections("Is Section 69 of the Consumer Protection Act 2019 a time limit?", list(kb.load().values()))
        self.assertTrue(r[0]["verified"])

    def test_repealed_act_section_not_matched_to_new_code(self):
        r = validate.check_user_cited_sections("Section 69 of the Payment of Wages Act 1936 says what?", list(kb.load().values()))
        self.assertFalse(r[0]["verified"])

    def test_invalid_kb_ids_dropped(self):
        self.assertEqual(validate.valid_ids(["CPA-LIMITATION", "MADE-UP"], self.cons), ["CPA-LIMITATION"])


class TestKnowledgeBase(unittest.TestCase):
    def test_every_entry_has_source_and_verification(self):
        for e in kb.load().values():
            self.assertTrue(e["source_url"].startswith("https://"), e["id"])
            self.assertIn(e["verification"], ("verified", "secondary_verified", "single_secondary",
                                              "general_principle", "pending_section"))
            if e["verification"] == "pending_section":
                self.assertIsNone(e.get("section"), e["id"])


if __name__ == "__main__":
    unittest.main()
