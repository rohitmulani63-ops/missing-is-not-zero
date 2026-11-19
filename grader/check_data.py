"""Validate cases/ against keys/key.json.

Checks
------
- keys/key.json exists, is UTF-8, is a JSON array of objects
- every entry has id (non-empty text), set, truth, control
- ids are unique
- set is one of: base, hard, top3, absence
- truth is one of: PASS, FAIL, CANNOT_CERTIFY
- control is true or false
- a control case has truth PASS or FAIL (never CANNOT_CERTIFY)
- cases/ exists; every key id has cases/<id>.txt and every cases/*.txt
  has a key entry (1:1)
- every case file is valid UTF-8 and not empty

`check()` returns a list of problem strings; an empty list means the data
is consistent. `main()` prints the problems and returns an exit code.
"""

from __future__ import annotations

import json
import os

ALLOWED_SETS = ("base", "hard", "top3", "absence")
ALLOWED_TRUTH = ("PASS", "FAIL", "CANNOT_CERTIFY")
REQUIRED_FIELDS = ("id", "set", "truth", "control")


def read_text_utf8(path):
    """Read a file as strict UTF-8. A leading byte-order mark is dropped."""
    with open(path, "rb") as handle:
        data = handle.read()
    text = data.decode("utf-8")
    if text.startswith("﻿"):
        text = text[1:]
    return text


def read_json(path):
    return json.loads(read_text_utf8(path))


def _check_key(key_path, problems):
    """Validate the key file. Return the list of ids, or None if unreadable."""
    if not os.path.isfile(key_path):
        problems.append("key file not found: %s" % key_path)
        return None
    try:
        data = read_json(key_path)
    except UnicodeDecodeError:
        problems.append("key file is not valid UTF-8: %s" % key_path)
        return None
    except ValueError as exc:
        problems.append("key file is not valid JSON: %s (%s)" % (key_path, exc))
        return None
    if not isinstance(data, list):
        problems.append("key file must be a JSON array of objects")
        return None
    if not data:
        problems.append("key file has no entries")

    ids = []
    seen = set()
    for index, entry in enumerate(data):
        where = "key entry %d" % index
        if not isinstance(entry, dict):
            problems.append("%s is not an object" % where)
            continue
        case_id = entry.get("id")
        if isinstance(case_id, str) and case_id.strip():
            where = "key entry %d (id %s)" % (index, case_id)
            if case_id in seen:
                problems.append("duplicate id in key: %s" % case_id)
            else:
                seen.add(case_id)
                ids.append(case_id)
        else:
            problems.append("%s has a missing or empty id" % where)
        for field in REQUIRED_FIELDS:
            if field not in entry:
                problems.append("%s is missing field '%s'" % (where, field))
        if "set" in entry and entry["set"] not in ALLOWED_SETS:
            problems.append(
                "%s has set %r; allowed: %s"
                % (where, entry["set"], ", ".join(ALLOWED_SETS))
            )
        truth = entry.get("truth")
        if "truth" in entry and truth not in ALLOWED_TRUTH:
            problems.append(
                "%s has truth %r; allowed: %s"
                % (where, truth, ", ".join(ALLOWED_TRUTH))
            )
        control = entry.get("control")
        if "control" in entry and not isinstance(control, bool):
            problems.append("%s has control %r; must be true or false" % (where, control))
        if control is True and truth not in ("PASS", "FAIL"):
            problems.append(
                "%s is a control but its truth is %r; controls must be PASS or FAIL"
                % (where, truth)
            )
    return ids


def _check_cases(cases_dir, ids, problems):
    if not os.path.isdir(cases_dir):
        problems.append("cases directory not found: %s" % cases_dir)
        return
    found = []
    for name in sorted(os.listdir(cases_dir)):
        path = os.path.join(cases_dir, name)
        if not os.path.isfile(path) or not name.endswith(".txt"):
            continue
        case_id = name[: -len(".txt")]
        found.append(case_id)
        try:
            text = read_text_utf8(path)
        except UnicodeDecodeError:
            problems.append("case file is not valid UTF-8: %s" % name)
            continue
        if not text.strip():
            problems.append("case file is empty: %s" % name)
    if ids is None:
        return
    found_set = set(found)
    id_set = set(ids)
    for case_id in ids:
        if case_id not in found_set:
            problems.append("key id has no case file: cases/%s.txt" % case_id)
    for case_id in found:
        if case_id not in id_set:
            problems.append("case file has no key entry: cases/%s.txt" % case_id)


def check(root="."):
    """Return a list of problems found under `root` (empty list = all good)."""
    problems = []
    ids = _check_key(os.path.join(root, "keys", "key.json"), problems)
    _check_cases(os.path.join(root, "cases"), ids, problems)
    return problems


def main(root="."):
    problems = check(root)
    if problems:
        print("Data check FAILED: %d problem(s)" % len(problems))
        for problem in problems:
            print("- " + problem)
        return 1
    print("Data check OK: cases and key are consistent.")
    return 0
