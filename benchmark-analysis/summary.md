# Benchmark Almanac analysis: correlations, saturation, clusters

All numbers come from the almanac's own data layer: its TypeScript `benchSummary()`, dumped as is, so they match benchmarkalmanac.com. Data as of Nov 14, 2026.

**Sources:** official leaderboards, Epoch AI's Benchmarking Hub (CC BY 4.0), and labs' launch posts. Artificial Analysis scores are not included, because of its terms.

**Scripts:** [`scripts/`](scripts/), one folder per analysis plus the shared `common.py`. `scripts/run.sh` rebuilds every chart from the almanac.

## 1. Correlations (`correlations/`)

**Set:** 43 widely used capability benchmarks, one version per family, with no safety tests. A pair is only scored when at least 15 models have results on both benchmarks. 767 of the 903 pairs meet that bar, with a median overlap of 35 models.

**Findings:**
- **Nearly everything correlates.** The median Spearman correlation is 0.67, 76% of pairs are above 0.5, and only 13 pairs are negative. GPQA Diamond and OTIS Mock AIME correlate at 0.96 across 206 models.
- **Most of that is one general-capability factor.** The control here is the Epoch Capabilities Index (ECI).
  - After controlling for ECI, the median pair falls to 0.06, and only 36 of 724 pairs stay above 0.5.
  - Controlling for release date instead leaves a median of 0.52.
- **Area labels barely matter.** Pairs in the same area average 0.64, and pairs across areas average 0.62.
- **Pairs that stay linked beyond general capability:**
  - LMArena text and Vision Arena: 0.90 (same platform).
  - SimpleQA Verified with SimpleBench (0.79) and with GPQA (0.74). This looks like a "knows facts" factor.
  - OTIS and MATH Level 5: 0.67.
  - The two chess benchmarks: 0.54.
  - LegalBench and MedCode: 0.54 (same evaluator).
- **The most independent benchmarks** are Vectara hallucination, SnakeBench, GAIA and BullshitBench V2.
  - Their correlations with ECI are 0.33, 0.53, 0.55 and 0.62.
  - On BullshitBench, models that all score above 85% on GPQA range from 10% to 95%.

**Caveats:**
- ECI is partly built from 14 of the 43 benchmarks. That flatters their fit to ECI.
- At about 30 shared models, a controlled correlation is uncertain by roughly ±0.2.
- Boards use different harnesses, and some come from lab claims.

## 2. Saturation and extinction (`saturation/`)

**Definitions:**
- **Saturation** uses the site's thresholds: the best reported score from any source passes 85%, then 95%.
- **Extinct:** a benchmark family (versions merged, so AIME 2024 to AIME 2025 is not an extinction) that meets both conditions:
  - it was named in at least 10% of all launch posts, and in at least 10% of frontier-lab posts, in some period;
  - it was then named in at most one frontier-lab launch post in the last 6 months.
- **Frontier labs:** Anthropic, OpenAI, Google, Moonshot, Meta, DeepSeek, xAI, Qwen and Z.ai.

**Findings:**
- **Most of the top benchmarks are saturated.** 24 of the 30 benchmarks named most often in launch posts are past 85%, and 12 are past 95%.
  - Still below 85%: HLE (74%), MMMU-Pro, Terminal-Bench 2.0, IFBench, AutomationBench and DeepSWE.
  - ARC-AGI-2 went from 6.5% (Apr 2025) to 95% (Sep 2026).
- **Newer benchmarks are beaten faster.** This is a Kaplan-Meier estimate over 172 benchmarks named in 10 or more launch posts.
  - The share past 85% within a year of release was 17% for 2023 releases, 30% for 2024 and 44% for 2025.
  - Within 6 months, 36% of 2026 releases are already past 85%.
  - 8 benchmarks were already at 85% when released, among them AIME 2025 and 2026, and HMMT 2026.
- **The 2023 canon is extinct at the frontier.** The canon is MMLU, HumanEval, GSM8K, MATH, BBH, HellaSwag, DROP and MGSM.
  - Every one of the 34 frontier-lab posts from 2023-24 named at least one of them.
  - In 2026, only 2 of 134 did, and both were DeepSeek base-model tables.
- **Benchmarks are saturated first and dropped second.** 32 families qualify as extinct, and 28 of them were past 85% when frontier labs last named them.
- **The long tail keeps a few alive, but only barely.** In 2026, MMLU appeared in 1 of 134 frontier-lab posts and 5 of 114 other-lab posts.
- **Next to go:** SWE-bench Verified fell from 57% of frontier-lab posts to 1.7%. The AIME family fell from 65% to 1.7%, and MMLU-Pro from 34% to 1.7%.

**Caveats:**
- 2023-24 rests on only 43 launch posts, so treat that period as rough.
- Best scores mix harnesses, tool use and lab claims.
- The pre-2023 group suffers from survivorship, so its slowness is overstated. The 2023, 2024 and 2025 groups compare fairly with each other.

## 3. Clusters / PCA (`clusters/`)

**Core data:** 125 benchmarks × 146 models, 40% filled, rank-normalized.

**Method:**
- The model is a low-rank factor model fitted only to observed cells, with its size chosen by cross-validation.
- The result was checked against soft-impute PCA (r = 0.85 on component 2), against pairwise residual correlations (r = 0.79), and against a refit on post-July-2025 models only (r = 0.94 and 0.87 on components 2 and 3).

**Findings:**
- **One factor dominates.** It is 82% of the signal and tracks release date (Spearman 0.81). On its own it predicts 61% of held-out scores, against 68% for all 10 components.
- **Component 2 (5.6%) is "building vs exams".** On one side are app-building and agentic boards (DesignArena, SWE-bench Verified, APEX-SWE). On the other are exams (AIME, SMT, BRUMO, MMLU-Pro).
- **Component 3 (2.6%) runs from games, long context and recall to human preference and writing.**
- **Clusters are soft.**
  - Silhouette is 0.04 to 0.06 for every number of clusters tried.
  - When models are resampled, the median adjusted Rand index (ARI) is 0.28.
  - The most stable groups are publisher families: Vals agent tasks and DesignArena.
- **The almanac's areas barely match the clusters.** ARI against area is 0.14, and only 47% of benchmarks sit closest to their own area.
- **Contest coding behaves like math.** IOI, ALE-Bench, LiveCodeBench and WeirdML group with math benchmarks.
- **Lab leanings, after removing overall capability:**
  - Anthropic leans to building (-0.74 SD) and Google to exams (+0.74).
  - OpenAI and Google lean to games and recall.

**Caveats:**
- Component 2 partly reflects benchmark age: building boards are newer and were scored on newer models (rho -0.63).
- Boards from the same publisher share harnesses, which makes them look more alike.
- Vision is underrepresented in the core.
