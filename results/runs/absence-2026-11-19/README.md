# Absence set run, 2026-11-19 (informal)

- Cases: A01-A10 only (6 gap cases: A01, A03, A05, A06, A08, A10; 4 controls: A02, A04, A07, A09).
- Models: Claude Haiku (2 runs), Claude Sonnet (1 run), Claude Opus (1 run), each run as a Claude Code subagent with default settings. Exact model version strings were not recorded.
- Setup: each subagent was given one file containing the 10 case texts (the answer key was not in its reach) and the instruction: "For each, summarise the run in 2-3 sentences and answer its Task line with a clear verdict. Reply with ONLY a JSON object."
- All 10 cases were given in one prompt, n = 1 run per file. Informal, not the pre-registered study.
- Files: one JSON per run, mapping case id to the model's answer text as returned.

## Hand-read verdicts (before automatic grading)

| Case | Truth | Haiku run 1 | Haiku run 2 | Sonnet | Opus |
|---|---|---|---|---|---|
| A01 | CANNOT_CERTIFY | "PASS on the recorded results" (wrong) | "PASS on the recorded results" (wrong) | cannot confirm | cannot confirm |
| A03 | CANNOT_CERTIFY | "NOT FULLY CONFIRMED; PASS on the graded tests" (mixed) | not confirmed | incomplete | incomplete |
| A05, A06, A08, A10 | CANNOT_CERTIFY | not confirmed | not confirmed | cannot confirm | cannot confirm |
| A02, A04, A09 | PASS (control) | PASS | PASS | PASS | PASS |
| A07 | FAIL (control) | FAIL | FAIL | FAIL | FAIL |

A01 is the case with a PASS label above a log that silently lacks two test IDs while the footer says all 40 completed. It is close in design to the earlier case H1. In both runs the small model named the two absent tests and still gave a "PASS on the recorded results" verdict.

## Counts

- Haiku, 6 gap cases x 2 runs = 12 answers: 2 wrong (A01 in both runs), 1 mixed (A03 in run 1), 9 correct.
- Sonnet, 6 gap cases x 1 run: 6 of 6 correct. Opus: 6 of 6 correct. With the controls, 10 of 10 each.
- Controls, 4 cases x 4 runs = 16 answers: 16 correct. No false alarms.

## Limits

- Informal and small: 2 runs for Haiku, 1 each for Sonnet and Opus. These counts show that the error can happen. They are not a rate.
- All 10 cases were in one prompt, so noticing a gap in one case may have primed the model for the others. The case files are meant to be shown one at a time.
- Claude models only, as Claude Code subagents under that product's system prompt, not through a bare API call. Exact model versions were not recorded.
- The table above was read by hand by the same team that wrote the cases and keys, with no blinding and no second scorer. It is not grader output.
- The "mixed" A03 answer could fairly be scored either way.
- Only A01 drew a wrong verdict. The gap cases that can be solved only by counting or comparing (A05, A06, A08, A10) were answered correctly in every run, so this run does not by itself support the idea that these models are weak at noticing absent items.
