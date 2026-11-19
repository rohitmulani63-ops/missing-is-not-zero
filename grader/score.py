"""Score a run: one JSON file of answers per model, graded by fixed rules.

Input
-----
key      keys/key.json: a JSON array of
         {"id", "set", "truth", "control", ...}
run dir  results/runs/<run-id>/<model>.json, each a JSON object
         {"<case id>": "<free-text answer>", ...}

Metrics (per model, for all cases and for each set)
---------------------------------------------------
accuracy              extracted label equals the truth
missing-as-pass rate  among cases whose truth is CANNOT_CERTIFY, the share
                      labelled PASS (the main error)
false-alarm rate      among control cases whose truth is PASS, the share
                      labelled FAIL or CANNOT_CERTIFY
missed failures       cases whose truth is FAIL that were labelled PASS
UNCLEAR               answers the rules could not decide
no answer             case ids absent from the model's file

UNCLEAR answers and absent answers stay in every denominator and are never
counted as correct. A missing answer is not a pass.
"""

from __future__ import annotations

import os

from .check_data import ALLOWED_TRUTH, read_json
from .extract import CANNOT_CERTIFY, FAIL, PASS, UNCLEAR, extract_verdict

NO_ANSWER = "NO_ANSWER"
SET_ORDER = ("base", "hard", "top3", "absence")


def load_key(path):
    """Load and minimally validate the key. Raises ValueError on bad data."""
    data = read_json(path)
    if not isinstance(data, list):
        raise ValueError("key file must be a JSON array: %s" % path)
    seen = set()
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("key entries must be objects: %s" % path)
        for field in ("id", "set", "truth", "control"):
            if field not in entry:
                raise ValueError("key entry is missing '%s': %r" % (field, entry))
        if not isinstance(entry["id"], str) or not isinstance(entry["set"], str):
            raise ValueError("key id and set must be text: %r" % (entry,))
        if entry["truth"] not in ALLOWED_TRUTH:
            raise ValueError("key entry has unknown truth: %r" % (entry,))
        if entry["id"] in seen:
            raise ValueError("duplicate id in key: %s" % entry["id"])
        seen.add(entry["id"])
    return data


def load_run(run_dir):
    """Return {model name: {case id: answer}} for every *.json in run_dir."""
    if not os.path.isdir(run_dir):
        raise ValueError("run directory not found: %s" % run_dir)
    run = {}
    for name in sorted(os.listdir(run_dir)):
        path = os.path.join(run_dir, name)
        if not os.path.isfile(path) or not name.endswith(".json"):
            continue
        data = read_json(path)
        if not isinstance(data, dict):
            raise ValueError("answers file must be a JSON object: %s" % path)
        run[name[: -len(".json")]] = data
    if not run:
        raise ValueError("no *.json answer files in: %s" % run_dir)
    return run


def _outcome(entry, label):
    truth = entry["truth"]
    if label == NO_ANSWER:
        return "no_answer"
    if label == UNCLEAR:
        return "unclear"
    if label == truth:
        return "correct"
    if truth == CANNOT_CERTIFY and label == PASS:
        return "missing_as_pass"
    if entry["control"] is True and truth == PASS:
        return "false_alarm"
    if truth == FAIL and label == PASS:
        return "missed_failure"
    return "wrong"


def _rate(count, total):
    if total == 0:
        return None
    return count / total


def _metrics(rows):
    """rows: list of (key entry, label, outcome)."""
    n = len(rows)
    correct = sum(1 for _, _, o in rows if o == "correct")
    gap_n = sum(1 for e, _, _ in rows if e["truth"] == CANNOT_CERTIFY)
    missing_as_pass = sum(1 for _, _, o in rows if o == "missing_as_pass")
    pass_control_n = sum(
        1 for e, _, _ in rows if e["control"] is True and e["truth"] == PASS
    )
    false_alarms = sum(1 for _, _, o in rows if o == "false_alarm")
    fail_n = sum(1 for e, _, _ in rows if e["truth"] == FAIL)
    missed_failures = sum(1 for _, _, o in rows if o == "missed_failure")
    unclear = sum(1 for _, _, o in rows if o == "unclear")
    no_answer = sum(1 for _, _, o in rows if o == "no_answer")
    return {
        "n": n,
        "correct": correct,
        "accuracy": _rate(correct, n),
        "gap_n": gap_n,
        "missing_as_pass": missing_as_pass,
        "missing_as_pass_rate": _rate(missing_as_pass, gap_n),
        "pass_control_n": pass_control_n,
        "false_alarms": false_alarms,
        "false_alarm_rate": _rate(false_alarms, pass_control_n),
        "fail_n": fail_n,
        "missed_failures": missed_failures,
        "unclear": unclear,
        "no_answer": no_answer,
    }


def _set_names(key):
    present = []
    for entry in key:
        if entry["set"] not in present:
            present.append(entry["set"])
    ordered = [name for name in SET_ORDER if name in present]
    ordered.extend(sorted(name for name in present if name not in SET_ORDER))
    return ordered


def score_model(key, answers):
    """Grade one model's answers against the key."""
    rows = []
    cases = {}
    for entry in key:
        case_id = entry["id"]
        if case_id not in answers:
            label = NO_ANSWER
        else:
            label = extract_verdict(answers[case_id])
        outcome = _outcome(entry, label)
        rows.append((entry, label, outcome))
        cases[case_id] = {
            "set": entry["set"],
            "truth": entry["truth"],
            "control": entry["control"],
            "label": label,
            "outcome": outcome,
        }
    sets = {"all": _metrics(rows)}
    for name in _set_names(key):
        sets[name] = _metrics([row for row in rows if row[0]["set"] == name])
    key_ids = set(entry["id"] for entry in key)
    extra = sorted(str(case_id) for case_id in answers if case_id not in key_ids)
    return {"sets": sets, "cases": cases, "extra_ids": extra}


def score_run(key, run):
    """Grade every model in a run. `run` is the output of load_run()."""
    return {"models": dict((model, score_model(key, run[model])) for model in sorted(run))}


def _frac(count, total):
    if total == 0:
        return "n/a"
    return "%d/%d (%.1f%%)" % (count, total, 100.0 * count / total)


def to_markdown(result):
    """Render the result of score_run() as a Markdown table."""
    lines = [
        "| Model | Set | Cases | Accuracy | Missing-as-pass (gap cases) "
        "| False alarms (pass controls) | Missed failures | UNCLEAR | No answer |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for model in sorted(result["models"]):
        sets = result["models"][model]["sets"]
        for name in sets:
            m = sets[name]
            lines.append(
                "| %s | %s | %d | %s | %s | %s | %s | %d | %d |"
                % (
                    model,
                    name,
                    m["n"],
                    _frac(m["correct"], m["n"]),
                    _frac(m["missing_as_pass"], m["gap_n"]),
                    _frac(m["false_alarms"], m["pass_control_n"]),
                    _frac(m["missed_failures"], m["fail_n"]),
                    m["unclear"],
                    m["no_answer"],
                )
            )
    notes = []
    for model in sorted(result["models"]):
        extra = result["models"][model]["extra_ids"]
        if extra:
            notes.append(
                "- %s: %d answer id(s) not in the key were ignored: %s"
                % (model, len(extra), ", ".join(extra))
            )
    text = "\n".join(lines) + "\n"
    text += (
        "\nUNCLEAR and absent answers stay in every denominator and are "
        "never counted as correct.\n"
    )
    if notes:
        text += "\n" + "\n".join(notes) + "\n"
    return text
