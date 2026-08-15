<!-- source: source.pdf pages 148-168 -->

<!-- p.148 -->

## 8 Capabilities

### 8.1 Evaluation summary

Claude Opus 5 is meaningfully more intelligent than Opus 4.8 and achieves state of the art performance on many benchmarks.

<table><tbody>
<tr><th colspan="2">Evaluation</th><th colspan="3">Claude models</th><th>Other models</th></tr>
<tr><td></td><td></td><th>Opus 5</th><th>Opus 4.8</th><th>Fable 5</th><th>GPT 5.6 Sol</th></tr>
<tr><th colspan="2">SWE-bench Pro</th><td>79.2</td><td>69.2</td><td><b>80</b></td><td>64.6</td></tr>
<tr><th colspan="2">SWE-bench Multilingual</th><td><b>89.5</b></td><td>84.4</td><td>86.6</td><td>-</td></tr>
<tr><th colspan="2">SWE-bench Multimodal</th><td><b>59.4</b></td><td>38.4</td><td>54.1</td><td>-</td></tr>
<tr><th colspan="2">DeepSWE v1.1</th><td>68.8</td><td>59.0</td><td>69.7</td><td><b>72.7</b></td></tr>
<tr><th colspan="2">FrontierCode 1.1 (Main)</th><td>53.4</td><td>46.5</td><td><b>53.5</b></td><td>47.5</td></tr>
<tr><th colspan="2">FrontierBench v0.1</th><td><b>43.3</b></td><td>18.7</td><td>33.7</td><td>37.5<br><small>(Codex)</small></td></tr>
<tr><th colspan="2">BrowseComp</th><td><b>90.8</b></td><td>84.3</td><td>87.4</td><td>90.4</td></tr>
<tr><th rowspan="2">Humanity’s Last Exam</th><td><i><b>No tools</b></i></td><td>56.3</td><td>49.8</td><td><b>56.5</b></td><td>-</td></tr>
<tr><td><i><b>With tools</b></i></td><td><b>64.7</b></td><td>57.9</td><td>63.9</td><td>-</td></tr>
<tr><th colspan="2">OSWorld 2.0</th><td><b>70.6</b></td><td>55.7</td><td>66.1</td><td>62.6</td></tr>
<tr><th colspan="2">HealthBench Professional</th><td>59.8</td><td>57.4</td><td><b>66.0<sup>[^11]</sup></b></td><td>60.5</td></tr>
<tr><th colspan="2">GDPval-AA v2</th><td><b>1861</b></td><td>1593</td><td>1747</td><td>1736</td></tr>
<tr><th colspan="2">AA-Briefcase</th><td><b>1720</b></td><td>1346</td><td>1574</td><td>1505</td></tr>
<tr><th colspan="2">AutomationBench</th><td><b>26.0</b></td><td>17.0</td><td>17.4</td><td>18.1</td></tr>
<tr><th colspan="2">ARC-AGI-1</th><td><b>97.5</b></td><td>92.5</td><td>-</td><td><b>97.5</b> <small>(xhigh)</small></td></tr><!-- p.149 --><tr><td colspan="2"><b>ARC-AGI-2</b></td><td>90.4</td><td>72.1</td><td>-</td><td><b>92.5</b></td></tr>
<tr><th colspan="2">ARC-AGI-3</th><td><b>30.2</b> <small>(high)</small></td><td>1.5</td><td>-</td><td>7.8</td></tr>
</tbody></table>

:::caption
**[Table 8.1.A] Capability evaluation summary.** Unless otherwise noted, all Claude Opus 5 results use the following standard configuration: adaptive thinking at max effort, default sampling settings (temperature, top_p), averaged over 5 trials. Context window sizes are evaluation-dependent and do not exceed 1M tokens. The best score in each row is **bolded**. Competitor figures are drawn from the respective developers’ published system cards or benchmark leaderboards. See the [Claude Fable 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf) for evaluation details of earlier Claude models.
:::

### 8.2 SWE-bench Verified, Pro, Multilingual, and Multimodal

SWE-bench (Software Engineering Bench) tests AI models on real-world software engineering tasks. We report four variants, where each score is an average over five trials:

- SWE-bench **Verified**[^12] is a 500-problem subset, each verified by human engineers as solvable. Claude Opus 5 achieved 96.0%.
- SWE-bench **Pro**[^13] is a harder variant composed of problems drawn from actively-maintained repositories with larger, multi-file diffs and reduced public ground-truth leakage. Claude Opus 5 achieved 79.2%.
- SWE-bench **Multilingual** extends the format to 300 problems across 9 programming languages. Claude Opus 5 achieved 89.5%.
- SWE-bench **Multimodal**[^14] adds visual context (screenshots, design mockups) to the issue descriptions (see [Section 9.3](#93-swe-bench-multimodal-test-harness) for details on the internal harness). Claude Opus 5 achieved 59.4%.

### 8.3 DeepSWE v1.1

DeepSWE is a set of 113 long-horizon software engineering tasks built to measure the capabilities of frontier coding agents. The tasks are diverse, reflect real-world complexity, and are written from scratch to avoid benchmark contamination. Claude Opus 5 scored an average of 68.8% over five trials.

<!-- p.150 -->

![](assets/figures/p150-1.png)

:::caption
**[Figure 8.3.A] DeepSWE v1.1** score versus average cost per task across reasoning-effort levels.
:::

### 8.4 FrontierCode

FrontierCode is an agentic coding benchmark of 150 software engineering tasks created by Cognition. Tasks are derived from real pull requests in open-source repositories, e.g. fixing websocket bugs in `aiohttp`, hardening Prisma’s browser bundle, or extending JSON schema linting rules. Each task gives the agent a checked-out repository and a single issue description; the agent then works autonomously in a containerized environment to produce a final patch, with no human intervention and no timeout information. Patches are graded against blocking functional criteria (primarily held-out unit tests) plus weighted rubric criteria, including model-graded checks for required test coverage and prohibited implementation patterns. Tasks were authored by maintainers of the underlying repositories and individually reviewed by Cognition researchers, with a random subset manually solved to verify fairness. We report FrontierCode’s overall score, a composite measure that grades each patch on blocking functional criteria (held-out unit tests) together with weighted code-quality rubric criteria, as mean@5.

Opus 5 ranks 2nd on FrontierCode (Main) with a 53.4% score (each model at its best reasoning effort), improving on Claude Opus 4.8 (46.5%) and leading GPT-5.6 Sol (47.5%).

<!-- p.151 -->

Opus 5 also ranks 2nd on FrontierCode (Extended) with a 63.6% score, improving on Claude Opus 4.8 (59.6%) and leading GPT-5.6 Sol (60.6%).

![](assets/figures/p151-1.png)

:::caption
**[Figure 8.4.A] FrontierCode (main set).** Scores of Claude Opus 5, Claude Opus 4.8, Claude Fable 5, and GPT-5.6 Sol on the main set of FrontierCode v1.1, a coding evaluation run and scored by Cognition, at each model’s five reasoning-effort settings. Claude Opus 5 reaches its best main-set score, 53.4, at medium effort.
:::

![](assets/figures/p151-2.png)

:::caption
**[Figure 8.4.B] FrontierCode (extended set).** Scores of Claude Opus 5, Claude Opus 4.8, Claude Fable 5, and GPT-5.6 Sol on the extended set of FrontierCode v1.1, a coding evaluation run and scored by Cognition, at each model’s five reasoning-effort settings. Claude Opus 5 reaches its best extended-set score, 63.6, at medium effort.
:::

<!-- p.152 -->

### 8.5 FrontierBench v0.1

FrontierBench v0.1 is a successor to Terminal-Bench 2.1 developed by the same team. It’s a refreshed set of 74 harder tasks, with a larger emphasis on science and engineering problems like computational biology, physics simulation, CAD, formal proofs, and GPU performance work. It tests AI models on real-world work in terminal and command-line containerized environments. To run it, we used [mini-SWE-agent](https://github.com/swe-agent/mini-swe-agent) harness on a GKE backend.

On FrontierBench v0.1, Claude Opus 5 achieved a 44.4% mean reward, averaged over 5 attempts for each one of the 74 unique tasks, using `xhigh` effort (best result – `max` scored similarly and within noise, landing at 43%). `high` effort achieves 39% mean reward for 19% fewer output tokens on average, while `low` effort achieves 25% mean reward for 64% fewer output tokens on average.

We also ran the benchmark on Claude Fable 5, which achieved 33.7% at `max` effort, Claude Sonnet 5, 17% mean reward, and Claude Opus 4.8, which achieved 18.7%.

Opus 5 safety classifiers flagged and refused 5% of the API calls, in 4% of the total trials, falling back to Opus 4.8. Fable safety classifiers flagged 42% API calls on 26% of trials, also falling back to Opus 4.8.

We’re also reporting 37.5% mean reward for GPT-5.6 Sol, run at `max` reasoning effort (its best result), also using `mini-swe-agent` and also using the same GKE setup from all other tests - [to keep the comparison fair](https://www.anthropic.com/engineering/infrastructure-noise). GPT-5.6 Sol never triggers safety classifiers in this eval, and thus no fallback model was configured or needed.

### 8.6 IMO 2026

The International Mathematical Olympiad (IMO) is a six-problem, two-day proof-based competition for pre-university students. It is the final stage of the mathematical olympiad track, sitting above national olympiads such as the United States of America Mathematical Olympiad (USAMO), on which earlier Claude models were evaluated. The 2026 IMO took place on July 15–16, 2026.

Because IMO solutions are proofs rather than short answers, grading can be challenging and subjective. For each problem, we had a model write a rubric, which we checked against publicly available reference solutions. Each of Claude Opus 5’s solutions was then judged independently against these rubrics by a panel of three frontier models (Gemini 3.1 Pro,<!-- p.153 --> Claude Opus 4.6, and Claude Mythos Preview). An answer counted as correct only when all three judges agreed.

We prompted Claude Opus 5 to solve each IMO 2026 problem without using any agent harness or tools, instructing it to provide a rigorous, self-contained proof. We set a 256,000-token output limit and used adaptive thinking at `max` effort. Attempts that exhausted the output limit were resampled at lower thinking efforts; one of the solutions required this remedy.

We had Opus 5 generate four independent solutions to each of the six problems. The panel of models judged all 24 solutions to be correct. To corroborate the panel’s scoring, we had human experts grade one pre-specified solution per problem (the first in the packet). These experts also judged each solution to be correct, giving each a score of 7 out of 7 according to the IMO rubric. Opus 5’s final score of 42/42 corresponds to gold-medal performance, well above the 2026 gold-medal cutoff score of 29/42 points.

### 8.7 RiemannBench

RiemannBench is a private benchmark of 25 problems[^15] developed by Surge AI that spans research-level topics in mathematics. Problems are written by mathematics professors, graduate students, and PhD-holding IMO medalists and are designed to require sustained, multi-step theoretical reasoning beyond the scope of competition mathematics. Each problem has a unique, closed-form answer verified programmatically.

<!-- p.154 -->

![](assets/figures/p154-1.png)

:::caption
**[Figure 8.7.A] RiemannBench** scores with and without tools across Claude models. All models run on max effort.
:::

### 8.8 ArxivMath

ArXivMath is a final-answer benchmark of research-level mathematics maintained by MathArena. Problems are extracted monthly from recent arXiv paper abstracts, then filtered through automated and manual checks to ensure they are self-contained, non-trivial, and verifiable. Because problems are drawn from active research, the benchmark is more realistic and more closely connected to mathematical research than contest or olympiad benchmarks.

We evaluated Claude Opus 5 using the June 2026 release (49 problems total) to avoid contamination with Opus’s training data. Claude Opus 5 with `max` effort scored 90.8% without tools and 91.3% with tools, averaged over four runs per problem. In comparison, GPT-5.6 Sol (max) scored 86.73% and Gemini 3.1 Pro Preview 65.99%, per the MathArena leaderboard (both without tools).

<!-- p.155 -->

![](assets/figures/p155-1.png)

:::caption
**[Figure 8.8.A] ArxivMath (June 2026) accuracy scores.** Claude Opus 5, Claude Mythos 5, and Claude Opus 4.8 were evaluated internally with max effort; other scores are from the MathArena leaderboard.[^16] Except for Claude Opus 5 (with tools), other scores are without access to tools.
:::

### 8.9 Long context

#### 8.9.1 Programbench

ProgramBench[^17] is a long context agentic coding benchmark of 200 program-reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using internet access or decompilation tools. Tasks range from small terminal utilities (jq, ripgrep) to large systems (FFmpeg, SQLite, the PHP interpreter). Submissions are graded against execution-based behavioral tests—247,000+ across the benchmark, generated via agent-driven fuzzing.

<!-- p.156 -->

We excluded 34 tasks for which the reference binary itself scores below 0.9 on the hidden test suite (indicating test flakiness), leaving 166 tasks, and within those tasks we score only against tests the reference binary passes. We report the hidden test pass rate across 5 episodes, each continuing from the previous episode’s codebase with a fresh context budget of up to 1M tokens. On this set, Claude Opus 5 scored 83% after the first episode, increasing to 93% by the fifth episode. For reference, Claude Opus 4.8 scored 80% on the first episode rising to 90% on the 5th, while Mythos 5 scored 84% and 93%. We believe ProgramBench is a strong measure of long context coding performance: Opus 5 episodes cover a range of context lengths up to the full 1M token window, and the tasks test long context capabilities that closely align with practical downstream use cases.

### 8.10 Agentic search

#### 8.10.1 HLE

Humanity’s Last Exam (HLE)[^18] is a multi-modal benchmark comprising 2,500 questions across dozens of subjects designed to be difficult for even domain specialists to answer and not quickly answered via internet search.

We tested Claude Opus 5 in two configurations: (1) reasoning-only without tools, and (2) with web search, web fetch, programmatic tool calling, and code execution. In all runs, thinking was set to auto and the total tokens used across contexts was capped at 1M. Context compaction was not used for these results. Claude Opus 4.6 served as the model grader.

To guard against result contamination in the tools variant, we blocklist known sources we know discuss HLE for both the searcher and fetcher (see Appendix 9.1). We also use Claude Opus 4.8 to review all transcripts and flag any that appear to have retrieved answers from HLE-specific sources; confirmed cases are re-graded as incorrect.

Claude Opus 5 outperforms every other Claude model at a given price point.

<!-- p.157 -->

![](assets/figures/p157-1.png)

:::caption
**[Figure 8.10.1.A] Humanity’s Last Exam (HLE) [with tools] reasoning-effort scaling**. Accuracy on HLE as reasoning efforts from low to max, against average billed cost per task (log scale). Claude Opus 5 costs are billed API actuals. Comparison-model costs are billed actuals where available, cache-hit estimates otherwise.
:::

<!-- p.158 -->

![](assets/figures/p158-1.png)

:::caption
**[Figure 8.10.1.B] Humanity’s Last Exam (HLE) [no tools] reasoning-effort scaling**. Accuracy on HLE as reasoning efforts from low to max, against average billed cost per task (log scale). Claude Opus 5 costs are billed API actuals. Comparison-model costs are billed actuals where available, cache-hit estimates otherwise.
:::

#### 8.10.2 BrowseComp

BrowseComp[^19] tests an agent’s ability to find hard-to-locate information on the open web. We ran Claude Opus 5 with web search, web fetch, programmatic tool calling, and code execution. To extend beyond the 1M-token context window, we used context compaction, triggered at 200k tokens. We use Claude Opus 4.7 as the model grader.

Claude Opus 5 outperforms every other Claude model at a given price point.

<!-- p.159 -->

![](assets/figures/p159-1.png)

:::caption
**[Figure 8.10.2.A] BrowseComp, token budget scaling.** Accuracy on BrowseComp as the per-task token budget grows from 1M to 10M, against average billed cost per task (log scale). Claude Opus 5 costs are billed API actuals. Comparison-model costs are billed actuals where available, cache-hit estimates otherwise. Opus 5 was run with an unreleased effort configuration; comparison models were run at max effort.
:::

<!-- p.160 -->

![](assets/figures/p160-1.png)

:::caption
**[Figure 8.10.2.B] BrowseComp at a 10M-token budget, reasoning-effort scaling.** Accuracy on BrowseComp at a fixed 10M-token budget as reasoning efforts from low to max, against average billed cost per task (log scale). Claude Opus 5 costs are billed API actuals. Comparison-model costs are billed actuals where available, cache-hit estimates otherwise.
:::

#### 8.10.3 DeepSearchQA

DeepSearchQA[^20] is “a 900-prompt benchmark for evaluating agents on difficult multi-step information-seeking tasks across 17 different fields”. Its tasks require the model to conduct extensive searches to compile a list of exhaustive answers.

Claude models were run with web search, web fetch, programmatic tool calling and adaptive thinking enabled. We used a 1M token budget and did not use context compaction.

<!-- p.161 -->

![](assets/figures/p161-1.png)

:::caption
**[Figure 8.10.3.A] DeepSearchQA reasoning effort scaling**. Mean F1 on DeepSearchQA (900 multi-hop web-research questions) at a 980k-token budget, at reasoning efforts from low to max, against average billed cost per task (log scale). Claude Opus 5 costs are billed API actuals; comparison-model costs are billed actuals where available, cache-hit estimates otherwise.
:::

#### 8.10.4 DRACO

Deep Research Accuracy, Completeness, and Objectivity (DRACO[^21]) is a deep research benchmark from Perplexity that aims to evaluate how well models perform at the type of complex research questions that real users would ask. DRACO consists of 100 curated tasks derived from real user queries across a variety of domains. The questions are graded using expert written rubrics that cover four categories: factual accuracy, breadth and depth of analysis, presentation quality, and citation quality.

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution and a 1M token limit.

<!-- p.162 -->

**Grading methodology**

The original DRACO paper uses Gemini 3 Pro, which is no longer available, as the primary judge model. For our evaluations, we used Opus 4.6 to grade responses against the per-task rubrics using the same binary MET/UNMET verdicts, aggregated into a normalized score per the paper’s §4.2 formula. We follow the paper’s protocol of five independent grading runs per response and report the mean. Our judge prompt is taken from the paper’s [Appendix C.5](https://arxiv.org/abs/2602.11685). The paper’s Appendix A shows judge choice can shift absolute scores by 10–25 points while preserving system ordering, so our scores are not directly comparable to the paper’s headline numbers.

Aside from the change in the judge model, the only other difference from the original paper is that we instructed the model to write its complete final report to a file in its execution environment and grade only that file’s contents, rather than grading the full agent transcript; this isolates the deliverable from intermediate tool output. Earlier Claude evaluations marked the report span with `<result>` tags instead; at `high` reasoning effort, models occasionally omitted the tags, causing complete reports to score as empty. The file-based protocol removes that dependency, and control runs showed it recovers those losses without otherwise affecting scores.

![](assets/figures/p162-1.png)

:::caption
**[Figure 8.10.4.A] DRACO reasoning-effort scaling**. Normalized score on DRACO (agentic data analysis) at a 980k-token budget, at reasoning efforts from low to max, against average billed cost per task (log scale). Claude<!-- p.163 --> Opus 5 costs are billed API actuals; comparison-model costs are billed actuals where available, cache-hit estimates otherwise.
:::

### 8.11 Multi-Agent

We evaluated Claude Opus 5 in a variety of multi-agent configurations. In these setups, several instances of the model collaborate on a single task. Below, we highlight our results across two benchmarks: BrowseComp (§8.11.1) and ProgramBench (§8.11.2), and describe the harnesses we tested (§8.11.3) and the measurement methodology (§8.11.4).

#### 8.11.1 Multi-Agent BrowseComp

BrowseComp tests an agent’s ability to find hard-to-locate information on the open web. We ran multi-agent BrowseComp using the two harness types described in [Section 8.11.3](#8113-multi-agent-harnesses) and analyzed the results using the methodology described in [Section 8.11.4](#8114-evaluation-methodology). Figure 8.11.1.A and Figure 8.11.1.B present multi-agent BrowseComp results alongside single-agent ones. Here are some key findings:

![](assets/figures/p163-1.png)

:::caption
**[Figure 8.11.1.A] Accuracy vs. latency for BrowseComp across both single-agent and multi-agent configurations.** As described in the methodology section, the scores presented in this chart were gathered on a pre-release configuration of Claude Opus 5, and as a result the single-agent numbers differ slightly from the previous section.
:::

<!-- p.164 -->

**Multi-agent harnesses achieve the highest scores and Pareto-dominate the score-latency frontier.** Every multi-agent variant matches or exceeds the best single-agent variant, with the 10-agent team reaching our highest score of 93.6%, +3.1pp over best single-agent baseline. Latency improves alongside accuracy as agents are added: relative to the single-agent 10M-token baseline, the N-agent team achieves speedups of 5.6×, 5.9× for N=5 and 10 agents respectively, with the async-subagent team also scoring +2.8pp higher than that baseline.

![](assets/figures/p164-1.png)

:::caption
**[Figure 8.11.1.B] Accuracy vs. cost for BrowseComp across both single-agent and multi-agent configurations.** As described in the methodology below, the scores presented in this chart were gathered on a pre-release configuration of Claude Opus 5, and as a result the single-agent numbers differ slightly from the previous section.
:::

On the score-cost frontier, multi-agent extends this frontier up and to the right: Figure 8.11.1.B shows cost rising with agent count alongside score, demonstrating that multi-agent configurations can productively absorb additional token budget by distributing work across agents. Taken together, multi-agent harnesses offer a latency–cost trade-off: when latency matters, N-agent team or async subagents can reach a given score faster, at higher cost.

<!-- p.165 -->

#### 8.11.2 Multi-Agent ProgramBench

ProgramBench[^22] is an agentic benchmark of 200 program-reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using internet access or decompilation tools. Single-agent results were presented in [Section 8.9.1](#891-programbench); we present the multi-agent ProgramBench results in this section.

We evaluated the 5-agent team and async-subagents harnesses on ProgramBench against a single-agent baseline, with the same per-agent 1M-token limit. As outlined in [Section 8.9.1](#891-programbench), we exclude the 34 tasks whose reference binary scores below 0.9 on the hidden test suite, leaving 166 “golden” tasks. We grade at a series of intermediate snapshots and use the resulting per-task trajectories of score, latency, and tokens to construct the cumulative curves in Figures 8.10.2.A and 8.10.2.B.

<!-- p.166 -->

![](assets/figures/p166-1.png)

:::caption
**[Figure 8.11.2.A] Score vs. latency for the full set of 166 “golden” ProgramBench tasks.** A point on the curve reads as the average fraction of hidden tests passed if every problem were stopped at that number of seconds. Shaded regions give the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve. As described in the methodology section, the scores presented in this chart were gathered on a pre-release configuration of Claude Opus 5.
:::

From Figure 8.11.2.A, on the full golden set, both 5-Agent Team and Async Subagents show latency improvement at the same score compared to single-agent. In particular, the 5-agent team achieves a 2.2x latency improvement over the single-agent to reach the same score of 0.6. The async-subagent curve largely sits between the two, improving on the single agent but by a smaller margin than the 5-agent team, before taking the lead to get the highest final score.

<!-- p.167 -->

![](assets/figures/p167-1.png)

:::caption
**[Figure 8.11.2.B] Score vs. tokens for the full set of 166 “golden” ProgramBench tasks.** A point on the curve reads as the average fraction of hidden tests passed if every problem were stopped at this amount of token usage. Shaded regions give the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve. As described in the methodology section, the scores presented in this chart were gathered on a pre-release configuration of Claude Opus 5.
:::

Figure 8.11.2.B shows the same latency–cost trade-off described in [Section 8.11.1](#8111-multi-agent-browsecomp). The latency gain comes from working on the problem concurrently and spending more tokens.

#### 8.11.3 Multi-Agent Harnesses

We evaluated two multi-agent harnesses. Both share a common set of tools: web search, web fetch, programmatic tool calling (code execution and bash) for search tasks, and the bash tool for coding tasks. Every agent has a 1M token limit.

**N-agent team**. A team of N=5 or 10 peer agents works on the task concurrently. One agent is designated the lead and is responsible for coordination and submitting the final answer if needed, but all agents have identical tools and all see the full task description. In addition to the task tools, every agent has two messaging tools: Send Message, which delivers a message to one or more teammates (inserted following the recipient’s next tool result), and<!-- p.168 --> Wait for Message, which blocks sampling until an incoming message arrives. On ProgramBench, each agent works in its own checkout of the task repository and can share code with other agents via Git.

This harness is designed to mirror real-world settings in which multiple agents collaborate on a shared task, and to reduce latency by letting peers work in parallel.

**Async subagents**. In this harness, we start with a lead agent which can spawn asynchronous, long-lived subagents while retaining direct access to the task tools. The spawning tool returns immediately with a confirmation rather than waiting on subagent execution. Each subagent sees only the instructions provided by the lead, not the original task description, and subagents can message any other agent and the lead. A subagent’s final response is delivered to the lead as a message, after which the subagent idles until the lead wakes it with new instructions. Subagents have the task tools and the same communication tools as in the N-agent team (namely Send Message and Wait for Message); the lead additionally has tools to create subagents, delete subagents (freeing concurrency slots), and to check subagent status (working, idle, or terminated). For search tasks, only the lead agent’s final submission is graded. There is no cap on the number of subagents that can be spawned.

#### 8.11.4 Evaluation Methodology

We present results that focus on comparing the difference between single- and multi-agent harnesses, including score, latency, token usage, and cost. In particular, token usage is calculated as the total number of tokens consumed across all agents on a task; cost is calculated based on token usage and per-token API pricing, assuming perfect cache hits; and latency is reported as a derived per-task latency rather than raw wall-clock time. We divide each agent’s input and output token counts by fixed reference prefill and decode rates, add its measured tool-execution time, and subsequently take the maximum of all agent latencies. This isolates the structural latency of the harness (e.g., how much sequential model work and tool time it requires) from serving-side variance (e.g., batching, queuing, hardware), so harnesses are compared on equal footing.

Scores in this section, for both single-agent and multi-agent BrowseComp and ProgramBench, were gathered on a pre-release configuration of Claude Opus 5, with an unreleased effort configuration and without safeguards classifiers. They are helpful for understanding the relative, but not absolute, performance of multi-agent harnesses.

BrowseComp runs were scanned after the fact with a verifier Claude and an automated pipeline to identify answer leakage; any problems flagged were counted as incorrect.
[^11]: Mythos 5

[^12]: Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? arXiv:2310.06770. [https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770)

[^13]: Deng, X., et al. (2025). SWE-bench Pro: Can AI agents solve long-horizon software engineering tasks? arXiv:2509.16941. [https://arxiv.org/abs/2509.16941](https://arxiv.org/abs/2509.16941)

[^14]: Yang, J., et al. (2024). SWE-bench Multimodal: Do AI systems generalize to visual software domains? arXiv:2410.03859. [https://arxiv.org/abs/2410.03859](https://arxiv.org/abs/2410.03859)

[^15]: During evaluation we identified and corrected minor issues in the reference answers and grading; all results are graded against the corrected setup. Scores are the mean over 4 attempts per problem.

[^16]: Our internal evaluation produces a score higher than the MathArena leaderboard for Claude Opus 4.8.

[^17]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^18]: Phan, L., et al. (2025). Humanity’s Last Exam. arXiv:2501.14249. [https://arxiv.org/abs/2501.14249](https://arxiv.org/abs/2501.14249)

[^19]: Wei, J., et al. (2025). BrowseComp: A simple yet challenging benchmark for browsing agents. arXiv:2504.12516. [https://arxiv.org/abs/2504.12516](https://arxiv.org/abs/2504.12516)

[^20]: Gupta, N., et al. (2026). DeepSearchQA: Bridging the Comprehensiveness Gap for Deep Research Agents. arXiv:2601.20975. [https://arxiv.org/abs/2601.20975](https://arxiv.org/abs/2601.20975)

[^21]: Zhong, J., et al. (2026). DRACO: a cross-domain benchmark for Deep Research Accuracy, Completeness, and Objectivity. arXiv:2602.11685. [https://arxiv.org/abs/2602.11685](https://arxiv.org/abs/2602.11685)

[^22]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. https://arxiv.org/abs/2605.03546

