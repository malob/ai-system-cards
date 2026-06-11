<!-- source: source.pdf pages 252-264 -->

<!-- p.252 -->

## 8 Capabilities

### 8.1 Evaluation summary

<table><tbody><tr><th colspan="2">Evaluation</th><th colspan="4">Claude family models</th><th colspan="2">Other models</th></tr><tr><td></td><td></td><td><b>Mythos 5</b></td><td><b>Fable 5</b></td><td><b>Mythos Preview</b></td><td><b>Opus 4.8</b></td><td><b>GPT-5.5</b></td><td><b>Gemini 3.1 Pro</b></td></tr><tr><th colspan="2">SWE-bench Pro</th><td><b>80.3</b></td><td>80</td><td>77.8</td><td>69.2</td><td>58.6</td><td>54.2</td></tr><tr><th colspan="2">SWE-bench Verified</th><td><b>95.5</b></td><td>95</td><td>93.9</td><td>88.6</td><td>-</td><td>80.6</td></tr><tr><th colspan="2">Terminal-Bench 2.1</th><td><b>88.0</b></td><td>84.3</td><td>-</td><td>82.7</td><td>83.4 (Codex CLI)</td><td>70.7 (Gemini CLI)</td></tr><tr><th colspan="2">BrowseComp</th><td><b>88.0</b> (single-agent ) <b>93.3</b> (multi-agent)</td><td>-</td><td>87.9</td><td>84.3 (single-agent ) 88.5 (multi-agent)</td><td>84.4</td><td>85.9</td></tr><tr><th rowspan="2">Humanity’s Last Exam</th><td><b>No tools</b></td><td><b>59.0</b></td><td>-</td><td>56.8</td><td>49.8</td><td>41.4</td><td>44.4</td></tr><tr><td><b>With tools</b></td><td>64.5</td><td>-</td><td><b>64.7</b></td><td>57.9</td><td>52.2</td><td>51.4</td></tr><tr><th rowspan="2">CharXiv Reasoning</th><td><b>No tools</b></td><td><b>88.9</b></td><td>-</td><td>86.2</td><td>80.5</td><td>-</td><td>-</td></tr><tr><td><b>With tools</b></td><td><b>93.5</b></td><td>-</td><td>92.5</td><td>89.9</td><td>-</td><td>-</td></tr><tr><th rowspan="2">BioMystery Bench</th><td><b>Human</b></td><td><b>83.9</b></td><td>-</td><td>82.6</td><td>80.4</td><td></td><td></td></tr><tr><td><b>Hard</b></td><td><b>46.1</b></td><td>-</td><td>29.6</td><td>40</td><td></td><td></td></tr><tr><th colspan="2">OSWorld-Verified<sup>[^28]</sup></th><td>85.0</td><td>85.0</td><td><b>85.4</b></td><td>83.4</td><td>78.7</td><td>76.2 (3.5 Flash: 78.4)</td></tr><tr><th colspan="2">CritPt</th><td><b>28.6</b></td><td>-</td><td></td><td>20.9</td><td>27.1</td><td>17.7</td></tr><tr><th colspan="2">ArxivMath</th><td><b>78.5</b></td><td></td><td>68.7</td><td>71.8</td><td>71.5</td><td>64.8</td></tr><!-- p.253 --><tr><td colspan="2"><b>RiemannBench</b></td><td><b>55.0</b></td><td>-</td><td>43.0</td><td>34.0</td><td>-</td><td>-</td></tr><tr><th colspan="2">GraphWalks BFS 256K</th><td><b>91.1</b></td><td>-</td><td>85.7</td><td>85.9</td><td>73.7</td><td>-</td></tr><tr><th colspan="2">GraphWalks Parents 256K</th><td><b>99.96</b></td><td>-</td><td>99.9</td><td>99.3</td><td>90.1</td><td>-</td></tr><tr><th colspan="2">FrontierCode (Diamond)</th><td>-</td><td><b>29.3</b></td><td>-</td><td>13.4</td><td>5.7</td><td>-</td></tr><tr><th colspan="2">GDPval-AA<sup>[^29]</sup></th><td>-</td><td><b>1932</b></td><td></td><td>1890</td><td>1769</td><td>1314</td></tr><tr><th colspan="2">GDP.pdf</th><td>-</td><td><b>29.8</b></td><td></td><td>22.5</td><td>24.9</td><td>16.7</td></tr><tr><th colspan="2">OfficeQA Pro</th><td>-</td><td><b>57.9</b></td><td></td><td>48.1</td><td>52.6</td><td>18.1</td></tr><tr><th colspan="2">AutomationBench</th><td>-</td><td><b>17.4</b></td><td></td><td>15.5</td><td>12.9</td><td>9.6 (3.5 Flash: 14.5)</td></tr><tr><th colspan="2">Blueprint-Bench 2</th><td>-</td><td><b>38.6</b></td><td></td><td>14.5</td><td>36.2</td><td>26.5 (3.5 Flash: 33.6)</td></tr><tr><th rowspan="2">Legal Agent Benchmark</th><td><b>Full Public Set</b></td><td><b>16.9</b></td><td>-</td><td>13.4</td><td>9.6</td><td>-</td><td>-</td></tr><tr><td><b>Harvey’s Held-Out Set</b></td><td>-</td><td><b>13.3</b></td><td></td><td>10.4</td><td>2.1</td><td>0.0 (3.5 Flash: 0.8)</td></tr><tr><th colspan="2">HealthBench</th><td><b>62.7</b></td><td>-</td><td>61.1</td><td>59.3</td><td>56.5</td><td>-</td></tr><tr><th colspan="2">HealthBench Professional</th><td><b>66.0</b></td><td>-</td><td>64.7</td><td>56.9</td><td>51.8</td><td>-</td></tr></tbody></table>

:::caption
**[Table 8.1.A] Capability evaluation summary.** Unless otherwise noted, all Mythos 5 results use the following standard configuration: adaptive thinking at max effort, default sampling settings (temperature, top_p), averaged over 5 trials. Context window sizes are evaluation-dependent and do not exceed 1M tokens. The best score in each row is **bolded**. Competitor figures are drawn from the respective developers’ published system cards or benchmark leaderboards. Fable's scores reflect its production safeguards, including fallback to Opus 4.8, which is why certain benchmarks score slightly lower on Fable compared to Mythos.
:::

<!-- p.254 -->

### 8.2 SWE-bench Verified, Pro, Multilingual, and Multimodal

SWE-bench (Software Engineering Bench) tests AI models on real-world software engineering tasks. We report four variants, where the score is the average over 5 trials:

- SWE-bench **Verified**[^30] is a 500-problem subset, each verified by human engineers as solvable. Mythos 5 achieved 95.5% and Fable 5 achieved 95%.
- SWE-bench **Pro**[^31] is a harder variant: problems drawn from actively-maintained repositories with larger, multi-file diffs and reduced public ground-truth leakage. Claude Mythos 5 achieved 80.3% and Claude Fable 5 achieved 80%.
- SWE-bench **Multilingual** extends the format to 300 problems across 9 programming languages. Mythos 5 achieved 92.2%.
- SWE-bench **Multimodal**[^32] adds visual context (screenshots, design mockups) to the issue descriptions, (§9.3 of the [Claude Opus 4.7 System Card](https://cdn.sanity.io/files/4zrzovbb/website/037f06850df7fbe871e206dad004c3db5fd50340.pdf) for details on the internal harness). Mythos 5 achieved 54.9%.

All SWE-bench variants use the standard configuration, with thinking blocks included in the sampling results. For our memorization screening, see Section 6.2.1 in the [Mythos Preview System Card](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf).

<!-- p.255 -->

![](assets/figures/p255-1.png)

:::caption
**[Figure 8.2.A] SWE-bench Pro** score versus average cost per task across reasoning-effort levels.
:::

### 8.3 Terminal-Bench 2.1

Terminal-Bench 2.1[^33] tests AI models on real-world coding tasks in terminal and command-line environments. We’ve decided to switch to a new harness, [mini-SWE-agent](https://swe-agent.com/latest/), which is more robust to timeouts compared to the Terminus-2 harness that we’ve previously reported. For example, at xhigh effort, Terminus-2 experiences 2.7× more timeouts than mini-SWE-agent, due to the way it waits for commands execution through a tmux session; this makes final scores noisier and less legible.

Using the mini-SWE harness, with a [GKE cluster](https://www.anthropic.com/engineering/infrastructure-noise), 1× timeout rate and 3× memory ceiling before pod preemption:

- Claude Mythos 5: achieved 88% mean reward, averaged over 5 attempts for each one of the 89 unique tasks (for a total of 445 trials), at high effort.
- Claude Fable 5: achieved 84.3% mean reward—with 20.9% of trials hitting a safety refusal and falling back to Claude Opus 4.8 for the rest of the trajectory, at high effort.
- <!-- p.256 -->GPT-5.5: Harbor, the official maintainer of the Terminal-Bench 2.1 leaderboard, has externally reproduced GPT-5.5 with the mini-SWE-agent harness, and got an 81% mean reward at xhigh effort. We internally ran the same configuration (GPT-5.5 on mini-SWE-agent at xhigh thinking) on the same GKE setup, and got 83% mean reward. GPT-5.5 with Codex harness receives a mean reward of 83.4%.
- Gemini 3.1 Pro: We do not have a score with the mini-swe harness, but we include Gemini’s highest score in the Terminal-Bench 2.1 Leaderboard.
- Claude Opus 4.8: achieved 82.7% mean reward, averaged over 5 attempts for each one of the 89 unique tasks (for a total of 445 trials), at high effort.

### 8.4 FrontierCode

FrontierCode[^34] is an agentic coding benchmark of 150 software engineering tasks created by Cognition. Tasks are derived from real pull requests in open-source repositories: e.g. fixing websocket bugs in aiohttp, hardening Prisma’s browser bundle, or extending JSON schema linting rules. Each task gives the agent a checked-out repository and a single issue description; the agent then works autonomously in a containerized environment to produce a final patch, with no human intervention and no timeout information. Patches are graded against blocking functional criteria (primarily held-out unit tests) plus weighted rubric criteria, including model-graded checks for required test coverage and prohibited implementation patterns. Tasks were authored by maintainers of the underlying repositories and individually reviewed by Cognition researchers, with a random subset manually solved to verify fairness. We report patch correctness rate, the fraction of tasks on which a patch satisfies all blocking criteria, as mean@5.

Fable 5 ranks #1 on FrontierCode (Diamond subset) with a 29.3% score and 30.2% pass rate (all models at xhigh reasoning effort; score / pass rate), improving on Claude Opus 4.8 (13.4% / 14.5%) and leading GPT-5.5 (5.7% / 6.4%). Fable 5 also ranks #1 on FrontierCode (Main subset) with a 46.3% score and 48.8% pass rate, improving on Claude Opus 4.8 (34.3% / 37.3%) and leading GPT-5.5 (25.5% / 28.2%). Even at medium effort, Fable 5 outperforms every other model at any effort level.

<!-- p.257 -->

![](assets/figures/p257-1.png)

:::caption
**[Figure 8.4.A] FrontierCode (Diamond)** pass rate across reasoning effort levels with mean output tokens per task on a log scale. Cost is computed from each run's recorded API token usage at measured cache-hit rates, with cache reads billed at 0.1× the input rate and writes at 1.25×, and the full response including extended thinking at the output rate, using published per-token rates.
:::

<!-- p.258 -->

![](assets/figures/p258-1.png)

:::caption
**[Figure 8.4.B.] FrontierCode (Main)** pass rate across reasoning effort levels with mean output tokens per task on a log scale.
:::

### 8.5 Frontier SWE

FrontierSWE[^35] is an open-ended benchmark of 17 ultra-long-horizon engineering problems spanning performance engineering, large-scale implementation, and ML research—e.g., optimizing a production compiler, designing new training optimizers, and building a PostgreSQL-compatible server backed by SQLite.

Agents are given 20 hours per task; because the tasks are too large for binary grading, each is scored continuously on metrics like speedup or functional coverage, with models ranked by mean@5 and best@5 across five trials. Fable 5 ranks #1 on mean@5 at 2.12 , Opus 4.8 ranks #2 at 3.26 and GPT-5.5 ranks #3 at 3.94.

### 8.6 ProgramBench

ProgramBench[^36] is an agentic benchmark of 200 program-reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without<!-- p.259 --> internet access or decompilation tools. Tasks range from small terminal utilities (jq, ripgrep) to large systems (FFmpeg, SQLite, the PHP compiler). Submissions are graded against execution-based behavioral tests—248,000+ across the benchmark, generated via agent-driven fuzzing.

We exclude 34 tasks for which the reference binary itself scores below 0.9 on the hidden test suite (indicating test flakiness), leaving 166 tasks. We report hidden test pass rate across 1–5 episodes, each with a context budget of up to 1M tokens. On this set, Claude Mythos scores 84–93%, compared to 79–88%[^37] for Claude Opus 4.8.

We do not report separate ProgramBench results for Claude Fable 5, given that ProgramBench’s core task, reconstructing the behavior of a compiled binary, falls within that category of tasks blocked by the cyber classifiers (see §[3.1.2](#312-mitigations-and-deployment)).

### 8.7 CursorBench

CursorBench[^38] is an agentic coding benchmark from Cursor, composed of real coding tasks (drawn from internal use and external traffic) and executed in Cursor’s production agent harness. All scores and per-task costs were measured and reported independently by Cursor. Claude Fable 5 outperformed the previous best result on CursorBench, scoring 72.9% at maximum effort and 8.6 points above GPT-5.5 at its highest published effort (64.3%). Fable 5 leads at every effort level from Medium upward.

<!-- p.260 -->

![](assets/figures/p260-1.png)

:::caption
**[Figure 8.7.A] CursorBench score versus mean cost per task by reasoning-effort setting,** as measured and reported by Cursor in their production agent harness. Cost per task is as measured and reported by Cursor from recorded API usage in their production harness, consistent with published per-token rates assuming 1-hour cache writes.
:::

### 8.8 GPQA Diamond

The Graduate-Level Google-Proof Q&A benchmark (GPQA)[^39] is a set of challenging multiple-choice science questions. We use the 198-question Diamond subset—questions that domain experts answer correctly but most non-experts do not. Mythos 5 achieved 94.1% on GPQA Diamond, averaged over 5 trials.

We consider GPQA Diamond to be a saturated evaluation and plan to stop reporting the performance of future models on it.

<!-- p.261 -->

### 8.9 RiemannBench

RiemannBench[^40] is a private benchmark of 25 problems developed by Surge AI that span research-level topics in mathematics. Problems are written by mathematics professors, graduate students, and PhD-holding IMO medalists from their own research, and are designed to require sustained, multi-step theoretical reasoning beyond the scope of competition mathematics. Each problem has a unique, closed-form answer that’s checked automatically.

With maximum reasoning effort and without access to tools or web search, Claude Mythos 5 scored 55.0%, ahead of Claude Mythos Preview (43.0%) and Claude Opus 4.8 (34.0%), averaging over 4 attempts per problem.

![](assets/figures/p261-1.png)

:::caption
**[Figure 8.9.A] RiemannBench accuracy scores.** Models are evaluated with maximum reasoning effort and without access to tools or web search.
:::

### 8.10 USAMO 2026

The USA Mathematical Olympiad (USAMO) is a six-problem, two-day proof-based competition for high school students. It is the next step of the math olympiad track in the US after the AIME, which was a popular AI benchmark last year but is now saturated. The<!-- p.262 --> 2026 USAMO took place on March 21–22, 2026, after almost all of Mythos’s training data was collected, and we are confident that there was no contamination.

Because USAMO solutions are proofs rather than short answers, grading can be challenging and subjective. We follow the MathArena[^41] grading methodology, where each proof is rewritten by a neutral model (Gemini 3.1 Pro) and judged by a panel of 3 frontier models (we used Gemini 3.1 Pro, Claude Opus 4.6, and Claude Mythos Preview) according to defined rubrics. The final score is the minimum given by any judge.

Mythos 5 scored 99.8% at medium, high, and xhigh reasoning effort, and 98.3% at low effort, averaging over 10 attempts per problem. Across all 240 attempts, the only proof that more than one judge scored below full marks was a low-effort attempt on Problem 6, where the model itself declined to claim a complete solution and proved a restricted subcase instead. Average token usage per attempt ranged from roughly 42K at low effort to 100K at xhigh. Under similar settings, Opus 4.8 scored 96.7% and Opus 4.7 scored 69.3%.

### 8.11 ArxivMath

ArXivMath is a final-answer benchmark of research-level mathematics maintained by MathArena. Problems are extracted monthly from recent arXiv paper abstracts, then filtered through automated and manual checks to ensure they are self-contained, non-trivial, and verifiable. Because problems are drawn from active research, the benchmark is more realistic and more closely connected to mathematical research than contest or olympiad benchmarks.

We evaluate using the March and April 2026[^42] releases (71 problems total), chosen to avoid contamination with Fable’s training data. Mythos 5 with extended thinking scored 78.52%, averaged over four runs per problem, ahead of GPT-5.5 (xhigh) at 71.48% and Gemini 3.1 Pro Preview at 64.79%[^43].

<!-- p.263 -->

![](assets/figures/p263-1.png)

:::caption
**[Figure 8.11.A] ArxivMath (March and April) accuracy scores.** Claude models were evaluated with max thinking effort in the no-tools setting.
:::

### 8.12 CritPt

CritPt (Complex Research using Integrated Thinking–Physics Test)[^44] is a benchmark of research-level physics problems created by active physics researchers. It comprises 70 composite challenges, each simulating an entry-level research project, spanning 11 subfields including condensed matter, quantum, atomic, molecular, optical, astrophysics, high-energy, statistical, and nuclear physics. Answers use machine-verifiable formats and are scored by an automated physics-specific grading pipeline. We use the independent evaluation run by [Artificial Analysis](https://artificialanalysis.ai/evaluations/critpt) via the CritPt grading API. Claude Mythos 5 scored 28.6% on CritPt, ahead of GPT-5.5 (27.1%) and improving on Claude Opus 4.8 by 7.7 percentage points (20.9%).

<!-- p.264 -->

![](assets/figures/p264-1.png)

:::caption
**[Figure 8.12.A] CritPt accuracy scores**. Evaluated by [Artificial Analysis](https://artificialanalysis.ai/evaluations/critpt).
:::
[^28]: Changes to the Mythos OSWorld score are due to a bug fix on our zoom tool when paired with batched actions, and increasing the max tokens per turn from 16K to 128K.

[^29]: Elo score as of June 6, 2026.

[^30]: Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? arXiv:2310.06770. [https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770)

[^31]: Deng, X., et al. (2025). SWE-Bench Pro: Can AI agents solve long-horizon software engineering tasks? arXiv:2509.16941. [https://arxiv.org/abs/2509.16941](https://arxiv.org/abs/2509.16941)

[^32]: Yang, J., et al. (2024). SWE-bench Multimodal: Do AI systems generalize to visual software domains? arXiv:2410.03859. [https://arxiv.org/abs/2410.03859](https://arxiv.org/abs/2410.03859)

[^33]: Merrill, M. A., et al. (2026). Terminal-Bench: Benchmarking agents on hard, realistic tasks in command line interfaces. arXiv:2601.11868. [https://arxiv.org/abs/2601.11868](https://arxiv.org/abs/2601.11868)

[^34]: Lu, E., et al. (2026). Introducing FrontierCode. Cognition. [https://cognition.ai/blog/frontier-code](https://cognition.ai/blog/frontier-code)

[^35]: Chu, E., Agarwal, R., et al. (2026). FrontierSWE. Proximal. [https://frontierswe.com/blog](https://frontierswe.com/blog)

[^36]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^37]: Claude Opus 4.8 results are reproduced from the Claude Opus 4.8 System Card and were measured on a near-final snapshot of that model.

[^38]: Cursor. (2026). CursorBench. [https://cursor.com/cursorbench](https://cursor.com/cursorbench)

[^39]: Rein, D., et al. (2023). GPQA: A graduate-level Google-proof Q&A benchmark. arXiv:2311.12022. [https://arxiv.org/abs/2311.12022](https://arxiv.org/abs/2311.12022)

[^40]: Garre, S., et al. (2026). Riemann-Bench: A benchmark for moonshot mathematics. arXiv:2604.06802. [https://arxiv.org/abs/2604.06802](https://arxiv.org/abs/2604.06802)

[^41]: Balunović, M., et al. (2025). MathArena: Evaluating LLMs on uncontaminated math competitions. arXiv:2505.23281. [https://arxiv.org/abs/2505.23281](https://arxiv.org/abs/2505.23281)

[^42]: As of this writing, the MathArena website lists 30 problems for March and 41 for April in the ArXivMath benchmark, which is where these scores are reported.

[^43]: GPT-5.5 and Gemini 3.1 Pro Preview scores are taken from the MathArena leaderboard for the same releases.

[^44]: Zhu, M., et al. (2025). Probing the critical point (CritPt) of AI reasoning: A frontier physics research benchmark. arXiv:2509.26574. [https://arxiv.org/abs/2509.26574](https://arxiv.org/abs/2509.26574)

