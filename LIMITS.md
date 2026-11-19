# Limits

What this project can and cannot tell you, stated plainly.

## Limits of the results so far

- **Informal, not pre-registered.** The runs in `results/informal-2026-11-18.md` were exploratory. PREREG.md is a draft, is not frozen, and no pre-registered data has been collected.
- **Small n.** Between 1 and 4 runs per model per case. The headline figures (4 of 4 on H1; 7 of 16 on H1 to H4) come from one small model on four cases. They show that the error can happen. They are not a rate.
- **Claude models only.** Haiku, Sonnet and Opus. No other provider has been tested, so nothing here says whether the behaviour is general.
- **Model versions not recorded.** The exact version strings were not written down for the informal runs.
- **Claude Code subagent setting.** The models ran as Claude Code subagents, under that product's system prompt, not through a bare API call. That prompt may make models more or less careful than they would be elsewhere.
- **Several cases per prompt.** The hard cases were shown six at a time and the top-3 cases six per pack. A model that notices a gap in one case may look harder at the next. Results for cases shown one at a time may differ.
- **No blinding, no second scorer.** Answers were scored by the same team that wrote the cases, who knew which model gave which answer.
- **The absence set (A01 to A10) has not been run.** It was written after the informal runs, to test the explanation they suggested. It may show nothing.

## Limits of the cases

- **One author team.** All cases and keys were written for this project by one team. No outside person has checked them. Counts were checked by the writer more than once, and by text search, but errors are possible.
- **Short, tidy, fictional documents.** The longest case is about 80 log lines. Real evaluation logs are longer, messier and spread over many files. Performance here may not carry over.
- **The policy line helps the model.** Every case says "of the N planned tests", which hints that completeness matters. Real reports often give no such hint. Measured error rates may be lower than in real use.
- **Small set.** 34 cases, of which 10 are in the absence set. This supports detection of large effects only.
- **Only 6 of the 40 planned base cases exist.** PREREG.md describes a balanced 40-case design. Only its six worked examples are written.
- **English only.**
- **Some keys rest on a stated reading.** These are choices, and a reasonable person could argue the other way:
  - H1, A01: per-test lines are treated as the evidence; a summary or closing line that claims more tests ran is treated as unverified.
  - H3: a result of "n/a" on a planned test counts as missing.
  - H5: a test's final result is its last completed attempt; earlier failed attempts do not make it missing.
  - T03: a one-character difference in a build hash means the evidence does not support approval until the build is confirmed.
  - A03: a note that reports 52 graded tests against 60 planned is treated as incomplete even though the note never says so.
- **Mapped truth labels.** The status-line and wrong-build cases do not ask for a PASS / FAIL verdict. Their truth is mapped onto the three labels in `keys/key.json` (see README.md). Scoring them needs a human or a carefully tested rule.
- **Partial detection can flip a verdict.** In H3 and A01, spotting only some of the missing items leads to a PASS by correct arithmetic on a wrong count. The key scores the verdict; it does not separate "did not look" from "looked and miscounted".

## Limits of what the test measures

- **One reporting error.** MINZ measures whether a summary turns missing results into a pass, and whether it raises false alarms on complete runs. It does not measure honesty, intent or deception. A wrong answer is a reporting error.
- **Not a safety rating.** A model that does well here is not thereby safe to deploy, and a model that does badly is not thereby unsafe. The data is fictional.
- **Not a measure of real harm.** We have not shown that this error has let an unsafe change through any real review.
- **Not new ground.** Related work on abstention, omissions, missing table values and absence detection already exists (see RELATED.md). This project is a narrow application of those ideas to safety-evaluation reports.
- **Public cases can leak into training data.** Once published, the cases may be seen by future models. Scores on public cases should be read with that in mind.
