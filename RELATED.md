# Related work

This project builds on the work below. It is not the first study of abstention, omission, absence detection, missing data in tables, harness failures, or uncertainty passing between AI agents.

How to read this list: each entry's page was opened on 18 November 2026 and the title, authors and topic were read there (for arXiv, the abstract page). That is all "checked" means here. We did not verify any paper's results, and the one-line descriptions are our own summaries. Items we saw only in search snippets have been left out. Check the source yourself before relying on any detail.

## A. Noticing what is absent

| Work | Link | Why it matters here |
|---|---|---|
| Fu, Shrivastava, Moore, West, Tan, Holtzman, "AbsenceBench: Language Models Can't Tell What's Missing" (arXiv, June 2025) | https://arxiv.org/abs/2506.11440 | Shows an original document and an edited copy and asks what was removed (number lists, poetry, pull requests). The abstract reports that even strong models do poorly. This is the closest prior work to our informal finding that models check what is present and miss what is absent; the absence set (A01 to A10) is a narrow, safety-reporting version of the same idea. |

## B. Missing or unknown results inside evaluation reporting

| Work | Link | Why it matters here |
|---|---|---|
| S. Akiyama, "Answers Without the Model: Harness Failures and a Zero-Cost Noise Floor for Small-Scale LLM Evaluation" (NeurIPS 2026 workshop poster) | https://neurips.cc/virtual/2026/166266 | Describes evaluation-harness defects, including scoring that treated non-answers as wrong answers, each producing a plausible-looking number. The mirror image of our concern (missing read as wrong, rather than missing read as pass). |
| KrishanKVerma, "An agent's account of its own work is not evidence of what it did" (EA Forum post; not peer-reviewed) | https://forum.effectivealtruism.org/posts/tAycmGwS83d9sqKJT/an-agent-s-account-of-its-own-work-is-not-evidence-of-what | Reports browser-agent runs where failed runs were not reported accurately by the agent, and argues oversight must check real system state. Related to reports that hide gaps. |

## C. Abstention and saying "I don't know"

| Work | Link | Why it matters here |
|---|---|---|
| Kirichenko, Ibrahim, Chaudhuri, Bell, "AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions" (arXiv, June 2025) | https://arxiv.org/abs/2506.09038 | 20 datasets testing when models should decline to answer. Our CANNOT_CERTIFY cases are a narrow, numeric form of "the honest answer is: can't tell". |
| rkstu, "The Compliance Trap" (GitHub repository; README read, claims not re-checked) | https://github.com/rkstu/schema-compliance-trap | Reports models inventing answers when told to always answer. Relevant to the structured condition C3 in PREREG.md: a forced-choice schema could push fabrication, which is why C3 includes an INCOMPLETE option. |

## D. Omissions in generated summaries

| Work | Link | Why it matters here |
|---|---|---|
| Schumacher et al., "Extrinsically-Focused Evaluation of Omissions in Medical Summarization" (arXiv, November 2023) | https://arxiv.org/abs/2311.08303 | Measures whether LLM summaries leave out important facts (MED-OMIT). Our "missing disclosed" measure is a narrow cousin: is the gap itself omitted? |
| E. Reiter, "Don't ignore omissions!" (blog post, 11 February 2026) | https://ehudreiter.com/2026/02/11/dont-ignore-omissions/ | Argues omissions are under-studied compared with hallucinations and harder to detect. |

## E. Missing values in tables given to LLMs

| Work | Link | Why it matters here |
|---|---|---|
| Gu et al., "RADAR: Benchmarking Language Models on Imperfect Tabular Data" (arXiv, June 2025) | https://arxiv.org/abs/2506.08249 | Injects artifacts, including missing entries, into tables and finds models do worse than on clean tables. The main prior benchmark on missing table values; ours is a much narrower, safety-reporting version. |
| Bhandari, Xing, Dan, Gao, "Exploring the Robustness of Language Models for Tabular Question Answering via Attention Analysis" (arXiv, June 2024) | https://arxiv.org/abs/2406.12719 | Table question-answering robustness under perturbations. Checked for topic only. |

## F. Uncertainty passing between AI agents

Relevant to the status-line cases (T02, T05, T08, T11, A03, A04) and the optional handoff condition C4 in PREREG.md.

| Work | Link | Why it matters here |
|---|---|---|
| Emde, Goel, Yun, Oh, Gubri, "Lost in Communication: Uncertainty Propagation in Multi-Agent Systems" (ICML 2026 listing) | https://icml.cc/virtual/2026/74490 | Describes "vanishing uncertainty": an uncertainty signal weakens when one agent relays another's answer. Closest prior work to the handoff idea. |
| Liu et al., "PropUQ-MAS: Propagation-Aware Uncertainty Quantification for LLM Multi-Agent Systems" (arXiv, August 2026) | https://arxiv.org/abs/2608.22130 | Scores each step's reliability using local uncertainty plus uncertainty inherited from upstream agents. |
| Ganguly, Chattopadhyay, Liu, Sarkar, "Estimation of Propagated Risk in LLM-based Multi-Agent Systems" (arXiv, October 2026) | https://arxiv.org/abs/2610.33282 | Models how errors from upstream agents spread downstream. |
| Duan et al., "UProp: Investigating the Uncertainty Propagation of LLMs in Multi-Step Agentic Decision-Making" (arXiv, June 2025) | https://arxiv.org/abs/2506.17419 | Splits uncertainty in multi-step agent decisions into a current part and an inherited part. |

## G. LLMs as safety evaluators

| Work | Link | Why it matters here |
|---|---|---|
| Chen, Goldfarb-Tarrant, "Safer or Luckier? LLMs as Safety Evaluators Are Not Robust to Artifacts" (arXiv, March 2025) | https://arxiv.org/abs/2503.09347 | LLM safety judges are swayed by surface features. Supports not using an LLM judge for our primary metrics. |
| Clegg, Hawkins, Habli, Lawton, "Evaluating Metrics for Safety with LLM-as-Judges" (arXiv, December 2025) | https://arxiv.org/abs/2512.15617 | Proposes weighted metrics and sending low-agreement judgements to human review. Abstract read only. |
| Anthropic, "Petri: An open-source auditing tool to accelerate AI safety research" (6 October 2025) | https://www.anthropic.com/research/petri-open-source-auditing | Shows AI-assisted auditing is a real practice (an agent runs tests and summarises behaviour). Says nothing about missing results. |

## How we describe this project

Prior work shows that language models struggle to notice what has been removed from a document (AbsenceBench), struggle to abstain when the answer is unknowable (AbstentionBench), degrade on tables with missing entries (RADAR), can omit important facts from summaries (MED-OMIT), that evaluation harnesses can silently mis-score non-answers (Akiyama), and that uncertainty can fade when one agent relays another (Lost in Communication; PropUQ-MAS). MINZ tests a narrow, safety-relevant combination of these: whether models summarising a fictional AI safety-evaluation run turn missing results into a pass, and whether they raise false alarms on complete runs.

We did not find a study that specifically measures language models turning missing safety-test results into a pass verdict. That is a statement about a short search on one day, not evidence that no such study exists. If you know of one, please open an issue.
