import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grader import score  # noqa: E402
from grader.__main__ import main  # noqa: E402

GOOD = os.path.join(HERE, "fixtures", "good")
KEY = os.path.join(GOOD, "keys", "key.json")
RUN = os.path.join(GOOD, "results", "runs", "demo")


class ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = score.load_key(KEY)
        # Not named `run`: that would shadow unittest.TestCase.run().
        cls.answers = score.load_run(RUN)
        cls.result = score.score_run(cls.key, cls.answers)

    def test_models_found(self):
        self.assertEqual(sorted(self.result["models"]), ["model-a", "model-b"])

    def test_set_order(self):
        sets = self.result["models"]["model-a"]["sets"]
        self.assertEqual(list(sets), ["all", "base", "hard", "top3", "absence"])

    def test_model_a_labels(self):
        cases = self.result["models"]["model-a"]["cases"]
        self.assertEqual(cases["G1"]["label"], "PASS")
        self.assertEqual(cases["G1"]["outcome"], "missing_as_pass")
        self.assertEqual(cases["G2"]["label"], "CANNOT_CERTIFY")
        self.assertEqual(cases["G2"]["outcome"], "correct")
        self.assertEqual(cases["G3"]["outcome"], "missing_as_pass")
        self.assertEqual(cases["C1"]["outcome"], "correct")
        self.assertEqual(cases["C2"]["label"], "FAIL")
        self.assertEqual(cases["C2"]["outcome"], "correct")
        self.assertEqual(cases["C3"]["label"], "CANNOT_CERTIFY")
        self.assertEqual(cases["C3"]["outcome"], "false_alarm")

    def test_model_a_overall(self):
        m = self.result["models"]["model-a"]["sets"]["all"]
        self.assertEqual(m["n"], 6)
        self.assertEqual(m["correct"], 3)
        self.assertAlmostEqual(m["accuracy"], 0.5)
        self.assertEqual(m["gap_n"], 3)
        self.assertEqual(m["missing_as_pass"], 2)
        self.assertAlmostEqual(m["missing_as_pass_rate"], 2.0 / 3.0)
        self.assertEqual(m["pass_control_n"], 2)
        self.assertEqual(m["false_alarms"], 1)
        self.assertAlmostEqual(m["false_alarm_rate"], 0.5)
        self.assertEqual(m["fail_n"], 1)
        self.assertEqual(m["missed_failures"], 0)
        self.assertEqual(m["unclear"], 0)
        self.assertEqual(m["no_answer"], 0)

    def test_model_a_per_set(self):
        sets = self.result["models"]["model-a"]["sets"]
        self.assertEqual(sets["base"]["n"], 2)
        self.assertAlmostEqual(sets["base"]["accuracy"], 0.5)
        self.assertAlmostEqual(sets["base"]["missing_as_pass_rate"], 1.0)
        self.assertAlmostEqual(sets["base"]["false_alarm_rate"], 0.0)
        self.assertAlmostEqual(sets["hard"]["accuracy"], 1.0)
        self.assertAlmostEqual(sets["hard"]["missing_as_pass_rate"], 0.0)
        self.assertIsNone(sets["hard"]["false_alarm_rate"])
        self.assertAlmostEqual(sets["absence"]["missing_as_pass_rate"], 1.0)
        self.assertIsNone(sets["absence"]["false_alarm_rate"])
        self.assertIsNone(sets["top3"]["missing_as_pass_rate"])
        self.assertAlmostEqual(sets["top3"]["false_alarm_rate"], 1.0)

    def test_model_b_overall(self):
        model = self.result["models"]["model-b"]
        m = model["sets"]["all"]
        self.assertEqual(m["n"], 6)
        self.assertEqual(m["correct"], 4)
        self.assertEqual(m["missing_as_pass"], 0)
        self.assertAlmostEqual(m["missing_as_pass_rate"], 0.0)
        self.assertEqual(m["false_alarms"], 0)
        self.assertEqual(m["unclear"], 1)
        self.assertEqual(m["no_answer"], 1)
        self.assertEqual(model["cases"]["G3"]["label"], "NO_ANSWER")
        self.assertEqual(model["cases"]["G3"]["outcome"], "no_answer")
        self.assertEqual(model["cases"]["C2"]["label"], "UNCLEAR")
        self.assertEqual(model["cases"]["C2"]["outcome"], "unclear")
        self.assertEqual(model["extra_ids"], ["ZZ"])

    def test_missing_answer_is_never_correct(self):
        result = score.score_model(self.key, {})
        m = result["sets"]["all"]
        self.assertEqual(m["correct"], 0)
        self.assertEqual(m["no_answer"], 6)
        self.assertEqual(m["missing_as_pass"], 0)

    def test_non_text_answer_is_unclear(self):
        result = score.score_model(self.key, {"G1": None, "C1": 7})
        self.assertEqual(result["cases"]["G1"]["label"], "UNCLEAR")
        self.assertEqual(result["cases"]["C1"]["label"], "UNCLEAR")

    def test_missed_failure(self):
        result = score.score_model(self.key, {"C2": "PASS"})
        self.assertEqual(result["cases"]["C2"]["outcome"], "missed_failure")
        self.assertEqual(result["sets"]["all"]["missed_failures"], 1)

    def test_wrong_direction_is_wrong(self):
        result = score.score_model(self.key, {"G1": "FAIL"})
        self.assertEqual(result["cases"]["G1"]["outcome"], "wrong")

    def test_markdown(self):
        text = score.to_markdown(self.result)
        self.assertIn(
            "| model-a | all | 6 | 3/6 (50.0%) | 2/3 (66.7%) | 1/2 (50.0%) "
            "| 0/1 (0.0%) | 0 | 0 |",
            text,
        )
        self.assertIn(
            "| model-a | hard | 2 | 2/2 (100.0%) | 0/1 (0.0%) | n/a "
            "| 0/1 (0.0%) | 0 | 0 |",
            text,
        )
        self.assertIn(
            "| model-b | all | 6 | 4/6 (66.7%) | 0/3 (0.0%) | 0/2 (0.0%) "
            "| 0/1 (0.0%) | 1 | 1 |",
            text,
        )
        self.assertIn("model-b: 1 answer id(s) not in the key were ignored: ZZ", text)

    def test_result_is_json_serialisable(self):
        text = json.dumps(self.result)
        self.assertIn("missing_as_pass_rate", text)


class LoadTests(unittest.TestCase):
    def test_load_key_rejects_non_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "key.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write('{"id": "G1"}')
            with self.assertRaises(ValueError):
                score.load_key(path)

    def test_load_key_rejects_unknown_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "key.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    '[{"id": "G1", "set": "base", "truth": "MAYBE", "control": false}]'
                )
            with self.assertRaises(ValueError):
                score.load_key(path)

    def test_load_run_missing_dir(self):
        with self.assertRaises(ValueError):
            score.load_run(os.path.join(GOOD, "results", "runs", "no-such-run"))

    def test_load_run_rejects_non_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "m.json"), "w", encoding="utf-8") as handle:
                handle.write('["PASS"]')
            with self.assertRaises(ValueError):
                score.load_run(tmp)


class CliScoreTests(unittest.TestCase):
    def test_score_command(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["score", RUN, "--root", GOOD])
        self.assertEqual(code, 0)
        self.assertIn("| model-a | all | 6 |", out.getvalue())
        self.assertIn("| model-b | all | 6 |", out.getvalue())

    def test_score_command_writes_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_path = os.path.join(tmp, "score.json")
            md_path = os.path.join(tmp, "score.md")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    ["score", RUN, "--key", KEY, "--json", json_path, "--md", md_path]
                )
            self.assertEqual(code, 0)
            with open(json_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.assertEqual(data["models"]["model-a"]["sets"]["all"]["missing_as_pass"], 2)
            with open(md_path, "r", encoding="utf-8") as handle:
                self.assertIn("| model-a | all | 6 |", handle.read())

    def test_score_command_bad_run_dir(self):
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["score", os.path.join(GOOD, "no-such-run"), "--root", GOOD])
        self.assertEqual(code, 2)
        self.assertIn("error:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
