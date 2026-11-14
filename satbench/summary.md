# SatBench: a benchmark whose questions are benchmarks

Data: Benchmark Almanac (benchmarkalmanac.com), read through the site's own TypeScript data layer, so every number matches the site. Includes Epoch AI's Benchmarking Hub (CC BY 4.0). Data as of Nov 14, 2026.

## The definition

- **Items ("questions"):** the 173 benchmarks named in 10 or more AI lab launch posts that are scored in percent, where higher is better. Each version counts as its own item, so AIME 2024 and AIME 2025 are two items. This is the same set the earlier saturation work used (it had 172; one more benchmark has since reached 10 posts).
- **An item is solved** once the best score anyone has reported for it reaches **85%**. That score can come from an official leaderboard, from Epoch AI, or from a lab's own launch post. This uses the site's own `frontier` and its 85% threshold.
- **SatBench score** is the share of items solved.
  - **SatBench-live** adds each benchmark when it is released. It answers: of the benchmarks that exist, how many are beaten?
  - **The fixed editions (SatBench-2023, -2024, -2025)** freeze the item set at the end of that year, the way an exam does.
- **Kill:** the model whose score first took an item past 85%.
- **Born solved:** an item that a model had already passed 85% on before the benchmark came out. There are 9, such as new AIME and HMMT years.

## Headline results

1. **SatBench stands at 109 of 173, or 63%.**
   - It sat near 30% from 2023 to early 2025, while new benchmarks arrived about as fast as old ones fell: 30% in Jan 2024 and 31% in Jan 2025.
   - Then it climbed: 46% in Jan 2026, past 50% in Mar 2026, and 63% now. That is +20 points in 12 months.
2. **The benchmark of benchmarks has saturated its own first edition.** SatBench-2023 has 44 items and is at 86%; it crossed 85% in Sep 2026. SatBench-2024 is at 78% and SatBench-2025 at 69%. At their freeze dates the three stood at 32%, 34% and 47%.
3. **The rise does not depend on the definition, but the level does.** Today's level ranges from 24% to 82% depending on the choice. Every version is flat through 2024 and climbs in 2025-26.

   | Variant | Today |
   |---|---|
   | Solved at 75% | 82% |
   | Solved at 85% (default) | 63% |
   | Solved at 95% | 25% |
   | Independent runs only (no lab claims) | 24% |
   | Items with 3+ launch-post mentions | 47% |
   | Items with 20+ launch-post mentions | 72% |

4. **Labs keep moving to new tests, so the benchmarks they report stay about half unsolved.** The "working set" is every benchmark named in 2 or more launch posts in the trailing 6 months, which uses no hindsight.
   - Its solved share was 47-60% through 2024.
   - Since mid-2025 it has stayed at 41-47%, and it is 45% today (106 of 236).
   - The stock of benchmarks is being used up, but labs swap in harder tests about as fast as they beat the old ones.
5. **Launch posts headline fewer already-saturated tests.** The share of a post's benchmarks that were already past 85% before the post went out:
   - All labs: 48% in 2025 and 39% in 2026.
   - Frontier labs: about 32-42% through mid-2026, then 22% so far in 2026 Q4.
   - In 2026 OpenAI was lowest (24%), Anthropic was at 30%, Google at 41%, and some smaller labs above 50%.
   - GPQA Diamond still appeared in 102 launch posts in 2026, every one of them after it passed 85%.
6. **Benchmarks are falling faster.** The Kaplan-Meier median time from release to 85% is:
   - 19.5 months for 2023 and 2024 releases;
   - 13.7 months for 2025 releases (the upper bound of the confidence interval is still open);
   - not yet reached for 2026 releases.

   The share solved within 12 months went from 17% to 30% to 43% for the 2023, 2024 and 2025 cohorts, which matches the earlier analysis. Of the 43 items past 95%, the median time from 85% to 95% was 6.5 months. Most items past 85% have not reached 95%.
7. **By area:** reasoning is 80% solved and knowledge 79%, then multimodal 66%, code 55%, agents 45% and work 18%. Agents and work make up most of the newest tests. Once an agents test is a year old, it falls as fast as any other area's.

## Who solves SatBench

- **Raw kills, not counting born-solved items:** OpenAI 24, Google 19, Qwen 17, Anthropic 14, ByteDance Seed 6, Meta 4. Z.ai, Mistral, NVIDIA and Liquid AI have none, despite 10 or more launch posts each.
- **Raw kills mislead, and Qwen is the clearest case.** A kill means the first *recorded* score past 85%. On a benchmark that frontier labs never run, any model that reports it gets the credit, even if other models could have scored higher.
  - Qwen's launch posts list far more benchmarks than anyone else's: 137 of the 173 items.
  - The median Qwen-killed benchmark gets 65% of all its launch-post mentions from Qwen itself. For OpenAI, Google and Anthropic the figure is 7-14%.
  - Examples: MAXIFE (11 of 11 mentions are Qwen's), SLAKE (10 of 10), MLVU (17 of 21).
  - The previous best was usually Qwen's own earlier model.
  - Five of the kills come from one Feb 2026 Qwen3.5 post, all self-reported.
- **Contested kills are the better measure.** These count only benchmarks that other frontier labs also report, in at least 5 of their launch posts.
  - **OpenAI 20, Google 14, Anthropic 14, then Qwen, ByteDance and Meta with 4 each.** 71 of the 100 kills qualify.
  - At a bar of 3+ mentions Qwen has 7; at 10+ it has 0. The top three stay the same at every bar.
  - In 2026, Anthropic has 11 of the contested kills, Google 3 and OpenAI 2.
  - Qwen's one contested kill in 2026 is MRCR v2. That is a self-reported 90.4 against Gemini 3.1 Pro's 84.9, and MRCR v2 has several context-length variants, so the two numbers may not be comparable.
- **Adjusting for how much each lab reports changes the order.**
  - Per 10 launch posts: Anthropic 5.8, OpenAI 4.7, ByteDance 4.0, Qwen 3.8, Google 3.3.
  - Per 100 SatBench items the lab ever named: OpenAI 34, Anthropic 25, Google 22, Qwen 12. Qwen names 137 of the 173 items.
- **Three in four kills are a lab grading its own model.**
  - 75 of 100 first crossings come from the lab's own launch post. That share was 81% in 2026.
  - Only 10 of those 75 were later matched by an independent run of 85% or more.
  - This is partly built in: a launch-day claim almost always comes before any outside run.

## The holdouts (64 unsolved)

- **The most-cited ones are:**
  - Humanity's Last Exam (74.2, a with-tools lab claim; the site's independent board best is 54.8);
  - MMMU-Pro (84.6), IFBench (82.9), Terminal-Bench 2.0 (84.7), DeepSWE (79.0), AutomationBench (76.1), SciCode (59.8).
- **13 of the 64 are at 82 or above.** Four are within half a point of 85: LiveBench, TextVQA, Terminal-Bench 2.0 and MMMU-Pro.
- **Most still move.** The median 12-month gain among the top 14 was +12.6 points.
- **Some holdouts are abandoned rather than hard.**
  - 21 have had no new best in 6 or more months, and 14 of those are fading or dropped from launch posts. Examples are LiveCodeBench v5 and the original tau-bench.
  - HealthBench (67.2 since Aug 2025) is still in use but stalled.
- **Some may have a ceiling below 100%.**
  - An audit (FutureHouse) disputes about 29% of HLE's chemistry and biology answers.
  - Prime Intellect found grader bugs in AutomationBench.
  - Epoch puts FrontierMath's ceiling at 57; the best score is 52.4.

## Projection (if 2026 rates hold; not a forecast)

- Over the last 12 months, an unsolved item had about a **5% chance per month** of being solved (43 crossings in 858 item-months; 10-90% range 4.1-6.0%).
- **Today's fixed set of 173 items** would reach 85% solved (SatBench itself saturated) around **May 2028** (80% range Jan to Nov 2028). Using the 6-month, 24-month or 2025 rate instead gives Aug to Oct 2028.
- **SatBench-live** climbs much more slowly, because new unsolved tests keep arriving. This assumes the 2025 rate of 4.7 new items a month, 9% of them born solved.
  - It reaches about 73% by the end of 2028.
  - It would not reach 85% until about 2033 (range 2031-2036).
  - It is a treadmill.
- **The model's main weakness:** it assumes the remaining items are no harder than the ones already solved, and that new tests are not built to resist.

## When do we run out of benchmarks?

There are 64 unsolved items today. At the last 12 months' rate, each has about a 5% chance per month of being solved. I simulated two paths:

- **If nobody made a new benchmark after today:** the last of the 64 falls around **2034** (80% range 2031-2037). 95% would be solved well before then.
- **If new benchmarks keep coming at the 2025 pace (4.7 a month) and AI keeps speeding up** (the solve rate rising 1 point a year, as it did from 2024 to 2026): the unsolved count falls to about 34 by 2034. It still doesn't reach zero.
  - Without the speed-up, the count would level off around 85, roughly new benchmarks per month divided by the solve rate. The chart leaves this path out.

**When SatBench itself saturates (85% of items solved):**
- Today's fixed set: around mid-2028.
- With new benchmarks arriving and solving rates continuing to speed up: around mid-2030 (80% range mid-2029 to mid-2031).

The share-ready chart is titled "When will SatBench be Saturated?".

**Why the unsolved count rises and then falls.**
- **2023-2025, rising:** new benchmarks came faster than models solved them. 18 entered in 2023 against 10 solved; 44 in 2024 against 16; 56 in 2025 against 38.
- **2026, falling:** 41 benchmarks were solved but only 29 new ones are counted. Most of that gap is a counting lag. A benchmark enters SatBench only once it has 10 launch-post mentions, which took 2025 releases a median of about 9 months, so few 2026 releases count yet.
- **Adjusted:** at the 2025 arrival pace, the unsolved count would be about 83 today, roughly flat, instead of 64. The chart shows this as a dotted line.

So we only run out of benchmarks if people stop making them. The real constraint is whether new tests can stay hard. The share of new benchmarks that are already solved at release is rising: 0% for 2023 releases, 2% for 2024, 7% for 2025 and 14% for 2026.

## What the data cannot support

- **Many "solved" items rest only on labs' own claims.** Best scores mix harnesses, tool use, best-of-n and lab self-reports. With independent runs only, SatBench is 24%, not 63%.
  - 44 items have no independent runs at all.
  - Among the 129 that do, the independent-only score is 33%, against 60% from all sources.
- **Part of the last year's jump comes from new benchmarks not yet counting.** A benchmark needs time to reach 10 launch-post mentions: 2025 releases took a median of 8.7 months. So 2026 releases are under-counted, and they are mostly unsolved.
  - With about 20 more unsolved 2026 items, the live score would be about 57%, not 63%.
  - The fixed 2025 edition is the cleanest measure of speed. It went from 47% to 69% during 2026.
- **The 2023-24 numbers are rough.** There are only 43 launch posts from those two years, against about 230 a year since.
- **Some crossings are dated before the benchmark existed** (9 born-solved items), because scores are dated by model release rather than by when the test was run.
- **The index gives every item the same weight.** Weighting by mentions raises the level (items with 20+ mentions: 72%).

## Data issues worth checking (possible errors in the almanac)

- **Crossings dated before the benchmark's release:**
  - AIME 2026, by Qwen3-30B-A3B-Thinking (Jul 2025, 88.3); a 30B model going first is suspicious.
  - HMMT Nov 2025 (grok-4), HMMT 2026 (Gemini 3 Pro), tau3-bench (Claude Opus 4.5), PinchBench (Gemini 3 Flash), RULER (Command R).
- **OSWorld 2.0:** the leaderboard tops out at 20.6. Lab launch posts then report 62.6 to 77.9, probably a different variant or harness.
- **Lab claims far above an independent run of the same model:**
  - Chartography: Claude Opus 5.5 claims 89.0; an independent run gives 66.3.
  - GDP-PDF: Claude Fable 5.1 claims 85.4; an independent run gives 49.4.
- **SimpleQA's "kill" is Perplexity Sonar Pro (85.8),** which answers with web search, not closed-book.
- **Mismatched fields and labels:**
  - For onemillion-bench, `best` (42.1) does not match the end of its `frontier` (68.8).
  - PMC-VQA is filed under "work", and LiveBench under "other".
  - Two kill models have no lab in models.json: palm-2-l and minicpm-v-2-6.

## Files

- **Share-ready** (`share/`):
  - `satbench_summary_card.png`: one-image summary.
  - `satbench_leaderboard.png`: lab leaderboard.
  - `satbench_by_year.png`: how fast each year's new benchmarks are solved.
  - `satbench_run_out.png`: when we run out of benchmarks.

- **Index** (`index/`):
  - `satbench_hero.png`: the live index and the fixed editions.
  - `satbench_robustness.png`: the index under the other definitions above.
  - `satbench_working_set.png`: the working set against the live index.
  - `satbench_projection.png`: the projections.
  - `satbench_by_area.png`: solved share by area.
- **Items** (`items/`):
  - `scorecard.png`: the 109/173 card.
  - `holdouts.png`: the most-cited unsolved items.
  - `half_life_by_cohort.png`: time to 85% by release year.
  - `areas.png`: solved and unsolved items per area.
- **Labs** (`labs/`):
  - `labs_kills_contested.png`: the best version of the lab ranking; it counts only benchmarks other frontier labs also report.
  - `labs_kills_by_lab.png`, `labs_kills_source.png`, `labs_kills_normalized.png`, `labs_kills95.png`, `labs_top_models.png`: who solved what, from which source, and adjusted for reporting volume.
  - `labs_headline_saturation_2026.png`, `labs_headline_saturation_quarterly.png`: how many already-saturated tests labs put in launch posts.
- **Scripts** (`scripts/`): `common.py` holds the definition. The `.mts` and `.mjs` files dump the site's data layer, and `run.sh` rebuilds every chart.
