import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from grader import check_data  # noqa: E402
from grader.__main__ import main  # noqa: E402

GOOD = os.path.join(HERE, "fixtures", "good")


class CheckDataTests(unittest.TestCase):
    def make_copy(self):
        """Copy the good fixture into a temporary directory and return it."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = os.path.join(tmp.name, "root")
        shutil.copytree(GOOD, root)
        return root

    def read_key(self, root):
        with open(os.path.join(root, "keys", "key.json"), "r", encoding="utf-8") as handle:
            return json.load(handle)

    def write_key(self, root, data):
        with open(os.path.join(root, "keys", "key.json"), "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    def assertProblem(self, problems, fragment):
        self.assertTrue(
            any(fragment in problem for problem in problems),
            "expected a problem containing %r, got %r" % (fragment, problems),
        )

    def test_good_fixture_has_no_problems(self):
        self.assertEqual(check_data.check(GOOD), [])

    def test_copy_of_good_fixture_has_no_problems(self):
        self.assertEqual(check_data.check(self.make_copy()), [])

    def test_key_id_without_case_file(self):
        root = self.make_copy()
        key = self.read_key(root)
        key.append({"id": "N9", "set": "base", "truth": "PASS", "control": True})
        self.write_key(root, key)
        problems = check_data.check(root)
        self.assertEqual(len(problems), 1)
        self.assertProblem(problems, "cases/N9.txt")

    def test_case_file_without_key_entry(self):
        root = self.make_copy()
        with open(os.path.join(root, "cases", "X1.txt"), "w", encoding="utf-8") as handle:
            handle.write("An extra case with no key entry.\n")
        problems = check_data.check(root)
        self.assertEqual(len(problems), 1)
        self.assertProblem(problems, "cases/X1.txt")

    def test_non_txt_files_in_cases_are_ignored(self):
        root = self.make_copy()
        with open(os.path.join(root, "cases", "NOTES.md"), "w", encoding="utf-8") as handle:
            handle.write("notes\n")
        self.assertEqual(check_data.check(root), [])

    def test_unknown_truth(self):
        root = self.make_copy()
        key = self.read_key(root)
        key[0]["truth"] = "MAYBE"
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "truth 'MAYBE'")

    def test_unknown_set(self):
        root = self.make_copy()
        key = self.read_key(root)
        key[0]["set"] = "bonus"
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "set 'bonus'")

    def test_control_must_be_pass_or_fail(self):
        root = self.make_copy()
        key = self.read_key(root)
        key[0]["control"] = True  # G1 has truth CANNOT_CERTIFY
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "controls must be PASS or FAIL")

    def test_control_must_be_boolean(self):
        root = self.make_copy()
        key = self.read_key(root)
        key[3]["control"] = "yes"
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "must be true or false")

    def test_missing_field(self):
        root = self.make_copy()
        key = self.read_key(root)
        del key[1]["control"]
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "missing field 'control'")

    def test_duplicate_id(self):
        root = self.make_copy()
        key = self.read_key(root)
        key.append(dict(key[0]))
        self.write_key(root, key)
        self.assertProblem(check_data.check(root), "duplicate id in key: G1")

    def test_empty_id(self):
        root = self.make_copy()
        key = self.read_key(root)
        key[5]["id"] = ""
        self.write_key(root, key)
        problems = check_data.check(root)
        self.assertProblem(problems, "missing or empty id")
        self.assertProblem(problems, "cases/C3.txt")

    def test_empty_case_file(self):
        root = self.make_copy()
        with open(os.path.join(root, "cases", "G2.txt"), "w", encoding="utf-8") as handle:
            handle.write("  \n\n")
        self.assertProblem(check_data.check(root), "case file is empty: G2.txt")

    def test_case_file_not_utf8(self):
        root = self.make_copy()
        with open(os.path.join(root, "cases", "G3.txt"), "wb") as handle:
            handle.write(b"\xff\xfe\xfa")
        self.assertProblem(check_data.check(root), "not valid UTF-8: G3.txt")

    def test_key_not_a_list(self):
        root = self.make_copy()
        self.write_key(root, {"id": "G1"})
        self.assertProblem(check_data.check(root), "must be a JSON array")

    def test_key_not_json(self):
        root = self.make_copy()
        with open(os.path.join(root, "keys", "key.json"), "w", encoding="utf-8") as handle:
            handle.write("[{not json")
        self.assertProblem(check_data.check(root), "not valid JSON")

    def test_key_with_byte_order_mark_is_accepted(self):
        root = self.make_copy()
        path = os.path.join(root, "keys", "key.json")
        with open(path, "rb") as handle:
            data = handle.read()
        with open(path, "wb") as handle:
            handle.write(b"\xef\xbb\xbf" + data)
        self.assertEqual(check_data.check(root), [])

    def test_missing_directories(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        problems = check_data.check(tmp.name)
        self.assertProblem(problems, "key file not found")
        self.assertProblem(problems, "cases directory not found")

    def test_main_exit_codes(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(check_data.main(GOOD), 0)
        self.assertIn("Data check OK", out.getvalue())

        root = self.make_copy()
        key = self.read_key(root)
        key[0]["truth"] = "MAYBE"
        self.write_key(root, key)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(check_data.main(root), 1)
        self.assertIn("Data check FAILED", out.getvalue())

    def test_cli_check_command(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(["check", "--root", GOOD])
        self.assertEqual(code, 0)

    def test_cli_without_command(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
