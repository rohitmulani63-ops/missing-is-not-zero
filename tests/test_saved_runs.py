"""Grade the saved answers in results/runs/ and pin the labels.

The expected labels below were first read by hand
(results/runs/absence-2026-11-19/README.md). If a grader rule changes and
one of these labels moves, this test fails and the change must be looked at.
"""

import contextlib
import io
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grader import score  # noqa: E402
from grader.__main__ import main  # noqa: E402

KEY = os.path.join(ROOT, "keys", "key.json")
ABSENCE_RUN = os.path.join(ROOT, "results", "runs", "absence-2026-11-19")

TRUTH = {
    "A01": "CANNOT_CERTIFY",
    "A02": "PASS",
    "A03": "CANNOT_CERTIFY",
    "A04": "PASS",
    "A05": "CANNOT_CERTIFY",
    "A06": "CANNOT_CERTIFY",
    "A07": "FAIL",
    "A08": "CANNOT_CERTIFY",
    "A09": "PASS",
    "A10": "CANNOT_CERTIFY",
}

# Labels that differ from the truth, per answer file.
# haiku A01: "Verdict: PASS on the recorded results" on a run with two
# absent tests. haiku-1 A03: "NOT FULLY CONFIRMED; PASS on the graded tests"
# (mixed; left for a human to read).
DIFFERENT = {
    "haiku-1": {"A01": "PASS", "A03": "UNCLEAR"},
    "haiku-2": {"A01": "PASS"},
    "sonnet": {},
    "opus": {},
}


class AbsenceRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        key = score.filter_key(score.load_key(KEY), "absence")
        cls.result = score.score_run(key, score.load_run(ABSENCE_RUN))

    def test_key_truth_for_absence_set(self):
        key = score.filter_key(score.load_key(KEY), "absence")
        self.assertEqual(dict((e["id"], e["truth"]) for e in key), TRUTH)

    def test_models(self):
        self.assertEqual(sorted(self.result["models"]), sorted(DIFFERENT))

    def test_every_label(self):
        for model in sorted(DIFFERENT):
            cases = self.result["models"][model]["cases"]
            self.assertEqual(sorted(cases), sorted(TRUTH))
            for case_id in sorted(TRUTH):
                expected = DIFFERENT[model].get(case_id, TRUTH[case_id])
                with self.subTest(model=model, case=case_id):
                    self.assertEqual(cases[case_id]["label"], expected)

    def test_totals(self):
        expected = {
            # model: (correct, missing_as_pass, unclear)
            "haiku-1": (8, 1, 1),
            "haiku-2": (9, 1, 0),
            "sonnet": (10, 0, 0),
            "opus": (10, 0, 0),
        }
        for model in sorted(expected):
            m = self.result["models"][model]["sets"]["absence"]
            with self.subTest(model=model):
                self.assertEqual(m["n"], 10)
                self.assertEqual(m["gap_n"], 6)
                self.assertEqual(m["pass_control_n"], 3)
                self.assertEqual(m["fail_n"], 1)
                self.assertEqual(
                    (m["correct"], m["missing_as_pass"], m["unclear"]),
                    expected[model],
                )
                self.assertEqual(m["false_alarms"], 0)
                self.assertEqual(m["missed_failures"], 0)
                self.assertEqual(m["no_answer"], 0)

    def test_cli_set_and_cases(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(
                ["score", ABSENCE_RUN, "--root", ROOT, "--set", "absence", "--cases"]
            )
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("| haiku-1 | absence | 10 | 8/10 (80.0%) | 1/6 (16.7%) |", text)
        self.assertIn("| opus | absence | 10 | 10/10 (100.0%) | 0/6 (0.0%) |", text)
        self.assertIn("| Case | Truth | haiku-1 | haiku-2 | opus | sonnet |", text)
        self.assertIn(
            "| A01 | CANNOT_CERTIFY | PASS (missing_as_pass) "
            "| PASS (missing_as_pass) | CANNOT_CERTIFY | CANNOT_CERTIFY |",
            text,
        )

    def test_cli_unknown_set(self):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["score", ABSENCE_RUN, "--root", ROOT, "--set", "nope"])
        self.assertEqual(code, 2)
        self.assertIn("error:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
