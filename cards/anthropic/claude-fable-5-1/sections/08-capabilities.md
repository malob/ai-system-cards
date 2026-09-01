<!-- source: source.pdf pages 167-205 -->

<!-- p.167 -->

## 8 Capabilities

### 8.1 Evaluation summary

Claude Fable 5.1 is more capable than Fable 5 and achieves state of the art performance on many benchmarks. All the evaluations in this section were run on the final snapshot of Claude Fable 5.1 or Claude Mythos 5.1.

<table><tbody>
<tr><th colspan="2" rowspan="2">Evaluation</th><th colspan="2">Fable family models</th><th colspan="2">Other models</th></tr>
<tr><th>Claude Fable 5.1/ Mythos 5.1</th><th>Claude Fable 5/ Mythos 5</th><th>Claude Opus 5</th><th>GPT-5.6 Sol</th></tr>
<tr><th colspan="2">SWE-bench Pro</th><td><b>81.2</b></td><td>80</td><td>79.2</td><td>64.6</td></tr>
<tr><th colspan="2">SWE-bench Multilingual</th><td>89.1</td><td>86.6</td><td><b>89.5</b></td><td>-</td></tr>
<tr><th colspan="2">SWE-bench Multimodal</th><td>54.7</td><td>54.1</td><td><b>59.4</b></td><td>-</td></tr>
<tr><th colspan="2">Terminal-Bench 4.0</th><td><b>56% (61%)</b></td><td>42% (45%)</td><td>52%</td><td>37%</td></tr>
<tr><th colspan="2">Terminal-Bench-Science 0.1</th><td><b>52.6%</b></td><td>24.7%</td><td>29.0%</td><td>22.4%</td></tr>
<tr><th rowspan="2">Humanity’s Last Exam</th><td><i><b>No tools</b></i></td><td><b>60.9%</b></td><td>57.8%</td><td>56.6%</td><td>-</td></tr>
<tr><td><i><b>With tools</b></i></td><td><b>65.0%</b></td><td>63.8%</td><td>63.6%</td><td>-</td></tr>
<tr><th colspan="2">OSWorld 2.0 (partial/strict)</th><td><b>77.9/41.7</b></td><td>72.9/36.1</td><td>75.4/39.6</td><td>-</td></tr>
<tr><th colspan="2">HealthBench Professional</th><td>62.1%</td><td><b>63.3%</b></td><td>59.8%</td><td>–</td></tr>
<tr><th colspan="2">GDPval-AA v2</th><td><b>1853</b></td><td>1723</td><td>1824</td><td>1711</td></tr>
<tr><th colspan="2">AA-Briefcase</th><td><b>1694</b></td><td>1572</td><td>1685</td><td>1502</td></tr>
<tr><th colspan="2">AutomationBench</th><td><b>31.4</b></td><td>17.1</td><td>26.9</td><td>19.6</td></tr>
<tr><th colspan="2">ARC-AGI-1</th><td>97.5%</td><td>98.5%</td><td>97.5%</td><td>96.5%</td></tr>
<tr><th colspan="2">ARC-AGI-2</th><td>90.0%</td><td>89.2%</td><td>90.42%</td><td>92.5%</td></tr>
</tbody></table>

:::caption
**[Table 8.1.A] Capability evaluation summary.** Unless otherwise noted, all results for Claude Fable 5.1 and Claude Mythos 5.1 use the following standard configuration: adaptive thinking at max effort, default sampling settings<!-- p.168 --> (temperature, top_p), averaged over five trials. Context window sizes are evaluation dependent and do not exceed 1M tokens. The best score in each row is **bolded**. Competitor figures are drawn from the respective developers’ published system cards or benchmark leaderboards. See the <u>[Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf)</u> for evaluation details of earlier Claude models.
:::

### 8.2 SWE-bench Pro, Multilingual, and Multimodal

SWE-bench tests AI models on real-world software engineering tasks. We report three variants, where each score is an average over five trials:

- SWE-bench **Pro**[^12] is composed of problems drawn from actively maintained repositories with large, multi-file diffs. Fable 5.1 achieved 81.2%.
- SWE-bench **Multilingual** extends the format to 300 problems across nine programming languages. Fable 5.1 achieved 89.1%.
- SWE-bench **Multimodal**[^13] adds visual context (screenshots, design mockups) to the issue descriptions. Fable 5.1 achieved 54.7%.

### 8.3 DeepSWE v1.1

DeepSWE is a set of 113 long-horizon software engineering tasks built to measure the capabilities of frontier coding agents. The tasks are diverse, reflect real-world complexity, and are written from scratch to avoid benchmark contamination. Fable 5.1 scored an average of 67.4% over five trials.

A note on scoring: DeepSWE grades each task with hidden tests that are often written for a single reference solution. When we reviewed failing transcripts, we found that Fable 5.1 implemented some ambiguous tasks more thoroughly than the task required, for example by validating inputs and raising exceptions, or by keeping new code consistent with codebase conventions. This resulted in equally valid or more rigorous implementations failing the hidden tests.

### 8.4 FrontierCode

FrontierCode is an agentic coding benchmark of 150 software engineering tasks created by Cognition. Tasks are derived from real pull requests in open-source repositories, such as fixing websocket bugs in `aiohttp`, hardening Prisma’s browser bundle, or extending JSON schema linting rules. Each task gives the agent a checked-out repository and a single issue<!-- p.169 --> description; the agent then works autonomously in a containerized environment to produce a final patch, with no human intervention and no timeout information. Patches are graded against blocking functional criteria (primarily held-out unit tests) plus weighted rubric criteria, including model-graded checks for required test coverage and prohibited implementation patterns. Tasks were authored by maintainers of the underlying repositories and individually reviewed by Cognition researchers, with a random subset manually solved to verify fairness. We report FrontierCode’s overall score, a composite measure that grades each patch on blocking functional criteria (held-out unit tests) together with weighted code-quality rubric criteria.

On FrontierCode 1.1 Extended, Claude Fable 5.1 scores 63.6% at `medium` effort, slightly behind Claude Fable 5 (64.9%, `xhigh`). On FrontierCode 1.1 (Main), Fable 5.1 scores 50.9% at medium effort, 2.6 points behind Fable 5 (53.5%, `xhigh`). It is cheaper per task than Fable 5 at every effort level (by roughly half at `low`, `medium`, and `high` effort and by about 30% at `xhigh` and `max`), and cheaper than Claude Opus 5 at `low`, `medium`, and `high` effort.

A note on why Fable 5.1’s score falls at `high` effort and above: FrontierCode grades each task on task correctness and scope. Because the evaluation is designed around producing mergeable diffs without human edits, any change to a file outside of the task’s scope is considered a failure, even when the change is correct or helpful. This scope criterion explains both Fable 5.1’s decline at higher effort and its gap compared to Fable 5. At `low` and `medium` effort, Fable 5.1 scores slightly above Fable 5 on both subsets, and its pass rate on task-correctness criteria keeps rising with effort. But at higher efforts, Fable 5.1 occasionally adds more small, unrequested changes in files outside the task, such as a documentation comment in an adjacent file, an edit to a docs page, or a new CI job where an existing one could have been reused. Fable 5 at the same effort levels kept more changes within the scope of the request in a way the FrontierCode grader approves of. As a result, Fable 5’s score keeps climbing with effort, whereas Fable 5.1’s peaks at medium, scoring below Fable 5 at `high`, `xhigh`, and `max`. Adding a brevity instruction (including a note to avoid unnecessary comments and documentation) helped reduce out-of-scope edits, but we report scores without changes to the official evaluation.

<!-- p.170 -->

![](assets/figures/p170-1.png)

:::caption
**[Figure 8.4.A] FrontierCode v1.1 Extended** score versus average cost per task across reasoning-effort levels.
:::

### 8.5 FrontierSWE v2

FrontierSWE v2[^14] is a Proximal benchmark of 34 ultra-long-horizon engineering and research tasks, such as porting Quantum Espresso from Fortran to Rust, building an OpenGL scene renderer that can run a flight simulator, and post-training an LLM to play an interactive puzzle game. The strongest models often work close to 20 hours per task and remain far from saturating the benchmark. Every model runs at maximum reasoning effort in Proximal’s own agent harness, with five trials per task, and the reported score is the mean across trials, on a scale from 0 to 1.

Claude Fable 5.1 scored 0.57 on FrontierSWE v2, the highest of the models Proximal evaluated, ahead of Claude Opus 5 (0.52), Claude Fable 5 (0.48) and GPT-5.6 Sol (0.32).

Fable 5.1 led on 22 of the 33 tasks where every model produced a scored result with no major area of weakness. It was strongest on tasks that require sustained reasoning and execution over many hours. Where it trails other models, the gaps were generally small, with Fable 5 still scoring higher on a few individual tasks. Opus 5 matches Fable 5.1’s best<!-- p.171 --> results on some tasks, but drops off more often on mid-difficulty tasks, whereas Fable 5.1’s performance holds up as task difficulty increases. Fable 5.1 also has a substantially higher floor than Fable 5, with a median task score of 0.56 versus 0.41, and the lowest outright failure rate of the three (5% of trials, versus 6% for Opus 5 and 8% for Fable 5). It has the highest share of top-end results as well, with 38% of trials scoring above 0.8. Fable 5.1 leads on breadth and consistency: it combines high-end capability with a stronger performance floor, particularly on difficult, long-horizon engineering work.

### 8.6 Terminal-Bench 4.0

Terminal-Bench 4.0 tests AI models on real-world work in terminal and command-line containerized environments. It’s a set of 66 tasks, with an emphasis on science-adjacent and frontier engineering problems like computational biology, physics simulation, CAD, formal proofs, and GPU performance work. Previous Terminal-Bench versions were [very timeout- and resource-sensitive](https://www.anthropic.com/engineering/infrastructure-noise): 4.0 largely addresses these issues by increasing timeouts and adaptively bumping up both RAM and CPU in a few tasks that could benefit from it. The choice of sandboxing provider might still be a confounding factor in a few tasks, but we expect it to play a significantly smaller role than it did in previous versions. We also found that the upgrade has reduced the confounding role of various harnesses (e.g., CLI memory footprint, compaction strategy, and container communication protocol), ultimately making Terminal-Bench a more stable and rigorous evaluation.

Claude Mythos 5.1 scored 60.9% on Terminal-Bench 4.0, while Claude Fable 5.1 scored 55.8%. Claude Opus 5 scored 52.3%, and Claude Fable 5 42.0%. Scores are averaged over 10 trials per task (660 trials) for Mythos 5.1 and 15 trials per task (990 trials) for the other three models; the standard error is ±1.6-2 points for every model. The numbers reported use Claude Code in --bare mode and maximum thinking effort. For reference, the public leaderboard reports Opus 5 at 51.8% and Fable 5 at 44.5% (five trials, Claude Code harness), within the noise of our internal setup. The public leaderboard also reports OpenAI’s GPT-5.6 Sol at 37.3%, scored with the Codex CLI at max thinking effort.

### 8.7 Terminal-Bench-Science 0.1

Terminal-Bench-Science is a Stanford-led community benchmark of 70 tasks drawn from scientific research workflows, authored and reviewed by scientists and researchers across the life, physical, earth, mathematical, and engineering sciences. Scientific advisors to the project are from MIT, Princeton, University of Washington, Genentech, and Stanford.

<!-- p.172 -->

Tasks are set up as typical agentic problems: an agent CLI works in a self-contained environment from a natural-language instruction and is graded against hidden, task-specific tests on the artifacts it produces.

Claude Fable 5.1 scored 52.6% averaged over 10 trials per task (700 trials), while Claude Opus 5 scored 29.0% (12 trials per task, 840 trials) and Claude Fable 5 scored 24.7% (10 trials per task, 700 trials). The standard error is ±3.5-4.5 points for every model, roughly double that of Terminal-Bench 4.0 despite similar trial counts. Terminal-Bench-Science tasks are strongly bimodal: two-thirds of the tasks are solved either ≥80% or ≤20% of the time by a given model, so most of the uncertainty comes from tasks rather than run-to-run variance.

As with Terminal-Bench 4.0, the numbers reported use of Claude Code in --bare mode and maximum thinking effort. For reference, the public leaderboard reports Opus 5 at 30.0% and Fable 5 at 21.4% (three trials, using the Claude Code harness), all within expected noise of our internal setup. The public leaderboard also reports OpenAI’s GPT-5.6 Sol at 22.4% with the Codex CLI at maximum thinking effort.

### 8.8 CursorBench 3.2.0

CursorBench[^15] 3.2.0 is Cursor’s agentic coding benchmark. It is composed of coding tasks that are representative of real-world Cursor usage (drawn from internal use and external traffic) and executed end-to-end in Cursor’s production agent harness. All scores and per-task costs were measured and reported independently by Cursor.

Fable 5.1 scored a state-of-the-art 73.4% on CursorBench at `max` effort. This is 2.9 points above Fable 5 at `max` effort (70.5%), at a little over half the cost. It is also 3.4 points above Claude Opus 5 at `max` effort (70.0%), at only a modestly higher cost. At medium effort, Fable 5.1 scored 68.0% for $3.53 per task. That is above GPT-5.6 Sol at `max` effort (67.2% for $5.69) at roughly two-thirds the cost.

<!-- p.173 -->

![](assets/figures/p173-1.png)

:::caption
**[Figure 8.8.A] CursorBench v3.2.0** score versus average cost per task across reasoning-effort levels.
:::

Note: previous system cards reported older versions of CursorBench, so the scores are not comparable.

### 8.9 CritPT-Corrected

CritPt (Complex Research using Integrated Thinking–Physics Test) is a benchmark of 71 theoretical physics problems developed by active physics researchers spanning condensed matter; quantum physics; atomic, molecular, and optical physics; astrophysics; high-energy physics; mathematical physics; statistical physics; nuclear physics; nonlinear dynamics; fluid dynamics; and biophysics. Each problem has a unique answer, either as an analytical formula, a numerical value, or a Python function. We had experts provide corrected versions of 31 of the problem statements that were flagged due to underspecification, ambiguity, or typos. The resulting internal version is referred to as CritPT-Corrected. Below, we present mean Pass@1 scores averaged over 16 attempts. The model solutions were graded using Claude Opus 4.8 as a judge, comparing model solutions to ground-truth solutions.

<!-- p.174 -->

![](assets/figures/p174-1.png)

:::caption
**[Figure 8.9.A] CritPT-Corrected Pass@1 scores at** `max` effort **with tools**, averaged over 16 attempts per problem.
:::

### 8.10 ArXivMath

ArXivMath is a final-answer benchmark of research-level mathematics maintained by MathArena. Problems are extracted monthly from recent arXiv paper abstracts, then filtered through automated and manual checks to ensure they are self-contained, non-trivial, and verifiable. Because problems are drawn from active research, the benchmark is more realistic and more closely connected to mathematical research than contest or Olympiad benchmarks.

We evaluated Claude Mythos 5.1 on the latest ArXivMath release (June 2026, 49 problems). Mythos 5.1 at `max` effort scored 91.33% without tools and 93.88% with tools, averaged over four runs per problem. In comparison, GPT-5.6 Sol (max) scored 86.73% and Gemini 3.1 Pro Preview scored 65.99%, per the MathArena leaderboard (both without tools).

The June 2026 problem set is drawn from arXiv abstracts posted in June 2026. The training data for Mythos 5.1 may overlap with this period, so some of these abstracts may have been inadvertently included. We have not verified this, so some contamination cannot be ruled out.

<!-- p.175 -->

![](assets/figures/p175-1.png)

:::caption
**[Figure 8.10.A] ArXivMath (June 2026) accuracy scores.** Claude Mythos 5.1, Claude Opus 5, Claude Mythos 5, and Claude Opus 4.8 were evaluated internally at `max` effort; other scores are from the MathArena leaderboard. All scores are without tools, with the exception of the “with tools” bars for Opus 5, Mythos 5, and Mythos 5.1.
:::

### 8.11 Long context

#### 8.11.1 ProgramBench

ProgramBench[^16] is a long-context agentic coding benchmark of 200 program reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using the internet or decompilation tools. Tasks range from small terminal utilities (jq, ripgrep) to large systems (FFmpeg, SQLite, the PHP interpreter). Submissions are graded against over 247,000 execution-based behavioral tests generated via agent-driven fuzzing.

We excluded 34 tasks for which the reference binary itself scored below 0.9 on the hidden test suite (indicating test flakiness), leaving 166 tasks. Among those tasks, we score only against tests the reference binary passes. We report the hidden test pass rate using the<!-- p.176 --> same mini-swe-agent harness that the upstream repo uses, without the six-hour time limit. On this set, Claude Fable 5.1 scored 87.6%, while Claude Opus 5 scored 85.4% and Fable 5 scored 86.3%.

We believe ProgramBench is a strong measure of long-context coding performance: Fable 5.1 episodes cover a range of context lengths up to the full 1M token window, and the tasks test long-context capabilities that closely align with practical downstream use cases.

### 8.12 Agentic search

#### 8.12.1 HLE

Humanity’s Last Exam (HLE)[^17] is a multimodal benchmark comprising 2,500 questions across dozens of subjects. The questions are designed to be difficult even for domain specialists to answer and not quickly answerable via internet search.

We tested Claude Fable 5.1 in two configurations: (1) reasoning-only without tools and (2) with web search, web fetch, programmatic tool calling, and code execution. In all runs, thinking was set to auto and the total tokens used across contexts was capped at 1M. Context compaction was not used for these results. Claude Opus 4.6 served as the model grader.

For the second configuration, we use a restricted fetch tool that can only retrieve URLs that have already appeared in the conversation, such as web search results or links on previously fetched pages. We adopted this after finding in internal testing that, given a fetch tool that accepted arbitrary model-constructed URLs, a model could route its own JavaScript through public third-party web services to execute it outside our sandbox and make arbitrary web requests.

To guard against result contamination in the tools variant, we blocklist sources known to discuss HLE for both the searcher and fetcher (see Appendix 9.2). We also use Claude Opus 5 to review all transcripts and flag any that appear to have retrieved answers from HLE-specific sources; confirmed cases are re-graded as incorrect.

<!-- p.177 -->

![](assets/figures/p177-1.png)

:::caption
**[Figure 8.12.1.A] Humanity’s Last Exam (HLE) [with tools] reasoning-effort scaling**. Accuracy on HLE as reasoning efforts from `low` to `max`, against average billed cost per task (log scale). Costs are billed based on cache-hit estimates.
:::

<!-- p.178 -->

![](assets/figures/p178-1.png)

:::caption
**[Figure 8.12.1.B] Humanity’s Last Exam (HLE) [no tools] test-time compute scaling**. Accuracy on HLE as reasoning efforts from `low` to `max`, against average billed cost per task (log scale). Costs are billed based on cache-hit estimates.
:::

#### 8.12.2 DRACO

Deep Research Accuracy, Completeness, and Objectivity (DRACO[^18]) is a deep research benchmark from Perplexity that aims to evaluate how well models perform at the type of complex research questions that real users would ask. DRACO consists of 100 curated tasks derived from user queries across a variety of domains. The questions are graded using expert-written rubrics that cover four categories: factual accuracy, breadth and depth of analysis, presentation quality, and citation quality.

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution, and a 1M token limit.

**Grading methodology**

The original DRACO paper uses Gemini 3 Pro, which is no longer available, as the primary judge model. For our evaluations, we used Claude Opus 4.6 to grade responses against the per-task rubrics using the same binary MET/UNMET verdicts aggregated into a normalized<!-- p.179 --> score, per the paper’s formula in Section 4.2. We follow the paper’s protocol of five independent grading runs per response and report the mean. Our judge prompt is taken from the paper’s [Appendix C.5](https://arxiv.org/abs/2602.11685). The paper’s Appendix A shows judge choice can shift absolute scores by 10–25 points while preserving system ordering, so our scores are not directly comparable to the paper’s headline numbers.

Aside from the change in the judge model, the only other difference from the original paper is that we instructed the model to write its complete final report to a file in its execution environment and graded only that file’s contents, rather than grading the full agent transcript; this isolates the deliverable from intermediate tool output.

![](assets/figures/p179-1.png)

:::caption
**[Figure 8.12.2.A] DRACO** score versus average cost per task across reasoning-effort levels. Normalized score on DRACO at a 980k-token budget, as reasoning effort rises from low to max, against average billed cost per task (log scale). Costs are billed based on cache-hit estimates.
:::

### 8.13 Multi-Agent

We evaluated Claude Fable 5.1’s performance when a single agent is replaced with a multi-agent configuration. Below, we highlight our results on ProgramBench (Section 8.13.1) and describe the harnesses we tested (Section 8.13.2) and the measurement methodology (Section 8.13.3).

<!-- p.180 -->

#### 8.13.1 Multi-Agent ProgramBench

ProgramBench[^19] is an agentic benchmark of 200 program-reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using the internet or decompilation tools. As outlined in [Section 8.11.1](#8111-programbench), we excluded the 34 tasks whose reference binary scored below 0.9 on the hidden test suite, leaving 166 “golden” tasks. Single-agent results were presented in Section 8.11; we present the multi-agent ProgramBench results in this section.

We compared two multi-agent harness configurations against the single-agent baseline: a fixed five-agent team and dynamically spawned async subagents (details in Section 8.13.2). We grade at a series of intermediate snapshots and use the resulting per-task trajectories of score, latency, and tokens to construct the cumulative curves in Figures 8.13.1.A and 8.13.1.B.

<!-- p.181 -->

![](assets/figures/p181-1.png)

:::caption
**[Figure 8.13.1.A] Score vs. latency for the full set of 166 “golden” ProgramBench tasks.** A point on the curve represents the average fraction of hidden tests the model would pass if every problem were stopped at that number of seconds. Shaded regions represent the 95% CI, computed from the score variance across tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve.
:::

On the full golden set, both the five-agent team and async subagents show latency improvements at the same score compared to the single agent. In particular, the five-agent team achieved a 2x latency improvement over the single agent to reach the same score of 0.6. The async subagent speed improves on the single agent but by a smaller margin than the five-agent team, before taking the lead to achieve the highest final score.

<!-- p.182 -->

![](assets/figures/p182-1.png)

:::caption
**[Figure 8.13.1.B] Score vs. tokens for the full set of 166 “golden” ProgramBench tasks.** A point on the curve represents the average fraction of hidden tests the model would pass if every problem were stopped at this amount of token usage. Shaded regions represent the 95% CI, computed from the score variance across tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve.
:::

Figure 8.13.1.B further demonstrates the latency–cost tradeoff of multi-agent harnesses: when latency is a concern, five-agent teams and async subagents can make productive use of the additional token budget by distributing work across agents, allowing them to reach a given score faster, at a higher cost.

#### 8.13.2 Multi-Agent Harnesses

**Five-agent team**. A team of five peer agents work on the task concurrently. All agents have identical tools, and all see the full task description. In addition to the task tools, every agent has two messaging tools: Send Message, which delivers a message to one or more teammates (inserted following the recipient’s next tool result), and Wait for Message, which blocks sampling until an incoming message arrives. Each agent works in its own checkout of the task repository and can share code with other agents via Git. This harness is designed to mirror real-world settings in which multiple agents collaborate on a shared task, and to reduce latency by letting peers work in parallel.

<!-- p.183 -->

**Async subagents**. This harness is initialized with a lead agent that can spawn asynchronous, long-lived subagents at will while retaining direct access to the task tools. The spawning tool returns immediately with a confirmation rather than waiting on subagent execution. Each subagent sees the instructions provided by the lead, not the original task description, and subagents can message any other agent or the lead. A subagent’s final response is delivered to the lead as a message; after that, the subagent idles until the lead wakes it up with new instructions. Subagents have access to the task tools and the same communication tools as in the five-agent team (i.e., Send Message and Wait for Message); the lead also has tools to create subagents, delete subagents (freeing concurrency slots), and check subagent status (working, idle, or terminated). There is no cap on the number of subagents the lead agent can spawn.

Each agent in these two harnesses has access to a bash tool and is limited to 1M tokens.

#### 8.13.3 Evaluation methodology

We focus on the comparison between single- and multi-agent harnesses, including score, latency, token usage, and cost. Token usage is calculated as the total number of tokens consumed across all agents on a task. Cost is calculated based on token usage and per-token API pricing, assuming perfect cache hits. Latency is reported as a derived per-task latency rather than raw wall-clock time. We calculate the latency of each agent trajectory by dividing the agent’s input and output token counts by fixed reference prefill and decode rates and adding its measured tool-execution time. We account for agent idleness by forcing each agent to inherit the longer of either its clock or the clock of any agent it interacts with (through messaging or spawning). We report the longest agent trajectory as the latency for the harness, to represent the total coding work completed. Using derived latency isolates the latency of the harness (e.g., how much sequential model work and tool time it requires) from serving-side variance (e.g., batching, queuing, hardware), so harnesses are compared on equal footing across time.

These results were collected on an internal Fable 5.1 endpoint with safety classifiers enabled, and with Opus 5 as the single refusal fallback model. 72% of episodes had at least one turn completed by the fallback, affecting under 1% of turns in total. The ProgramBench scores are therefore best read as a relative comparison between harnesses rather than as absolute measures of performance.

<!-- p.184 -->

### 8.14 Multimodal

#### 8.14.1 Chartography

Chartography[^20] is a chart understanding benchmark from Surge AI covering a set of 100 tasks on specialized chart types rarely evaluated in existing benchmarks. These include Kaplan–Meier charts, candlestick charts, contour maps, wind rose diagrams, Sankey diagrams, Bode plots, and 3D surface plots. Because different chart types can be read to different degrees of precision, each answer is graded against an acceptable range set by experts for that specific chart, rather than against a single fixed tolerance.

The model is configured with adaptive thinking and `max` effort enabled in all runs, both with and without tools. When evaluated with tools, the model is provided with a container (with the image file and standard libraries installed) and an image cropping tool. Our internal grading implementation of Chartography matches the tasks and expert-determined acceptable answer ranges in the official repository.[^21]

Claude Fable 5.1 achieved a score of 42.6% without tools and 86.2% with tools. Claude Fable 5 scored 36.6% and 84.2%, while Claude Opus 5 achieved scores of 29.6% and 83.0%, respectively.

<!-- p.185 -->

![](assets/figures/p185-1.png)

:::caption
**[Figure 8.14.1.A] Chartography scores.** Claude models are evaluated with adaptive thinking and `max` effort, with and without tools. Scores are averaged over five runs. Shown with 95% CI. Gemini 3.7 Flash (Medium) and GPT-5.6 Sol (Max) scores are given as publicly reported by Surge AI, evaluated without tools.
:::

Claude Fable 5.1 outperformed all prior Claude models without tools. With tools, Claude Fable 5.1 Pareto-dominated Claude Fable 5 on the score-cost frontier and outperformed Opus 5 at higher effort levels. We continue to find that using the models’ agentic coding capabilities to manipulate, analyze, and crop images can be significantly more cost-effective than simply enabling adaptive thinking.

<!-- p.186 -->

![](assets/figures/p186-1.png)

:::caption
**[Figure 8.14.1.B] Chartography scores.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.14.2 BenchCAD

BenchCAD[^22] is a benchmark for programmatic CAD reasoning built from 17,900 execution-verified CadQuery programs spanning 106 industrial part families, roughly half of which are anchored to real ISO, DIN, EN, ASME, and IEC specification tables. The benchmark decomposes CAD capability into four matched tasks; we report results on the Vision2Code task, which requires models to generate CadQuery code from multi-view renders.

Our internal implementation of BenchCAD matches the original reference implementation except for three minor modifications.[^23] First, we corrected a typo in the reference system prompt, which swapped all four camera positions in the rendered views provided to the<!-- p.187 --> model. Second, we updated the grading to accept raw shapes in addition to Workplanes. On models like GPT-5.5, we previously noticed that raw shapes would error out due to this stylistic difference in output but otherwise equivalent geometry. Both of these changes have already been merged into the reference repository in GitHub. We also parse the last (rather than the first) code fence as the model’s submission.

The model is configured with adaptive thinking and `max` effort enabled in all runs, both with and without tools. When evaluated with tools, the model was provided with a container (with the image files and standard libraries installed) and an image cropping tool. We evaluate the model on a random 1,000-file subset of the published 17,900 Vision2Code files, which we have historically found to be indicative of scores on the full set within a 0.01 voxel IoU margin. We report voxel IoU scores averaged over five runs.

On the 1,000-file subset of BenchCAD Vision2Code, Claude Fable 5.1 achieved a voxel IoU score of 0.437 without tools and a score of 0.843 with tools. Claude Fable 5 achieved scores of 0.376 and 0.675, and Claude Opus 5 scored 0.366 and 0.821, respectively.

![](assets/figures/p187-1.png)

:::caption
**[Figure 8.14.2.A] BenchCAD Vision2Code subset scores.** Claude models are evaluated with adaptive thinking and `max` effort, with and without tools. Scores are averaged over five runs and shown with 95% CI. GPT-5.6 Sol scores are given as publicly reported by OpenAI, evaluated on the full 17,900 files.
:::

<!-- p.188 -->

The performance of Claude models on this evaluation scales substantially with test-time compute, particularly when the models are equipped with tools that enable visual verification of intermediate outputs in addition to adaptive thinking. Indeed, when provided with tools, Fable 5.1 achieved a voxel IoU score that is close to double its score when run without tools.

![](assets/figures/p188-1.png)

:::caption
**[Figure 8.14.2.B] BenchCAD Vision2Code subset scores.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.14.3 OSWorld 2.0

OSWorld 2.0[^24] is a benchmark of 108 long-horizon computer-use tasks in which an agent operates a live Ubuntu virtual machine via screenshots and mouse and keyboard actions. Each task is graded against a set of weighted checkpoints, and we report two metrics: the partial score (mean per-task credit across checkpoints) and the strict pass rate (fraction of tasks with every checkpoint satisfied), each as Pass@1 averaged over five independent runs.

<!-- p.189 -->

We used the benchmark’s default settings of 1080p resolution and a maximum of 500 action steps per task, at maximum reasoning effort. For tasks that require a model grader, we used Claude Opus 4.8.

We evaluated the authors’ August 2026 task release with their subsequent task fixes, plus fixes to task setup and grading scripts that we reported to the authors. Claude Fable 5.1 achieved a partial score of 77.9% and a strict pass rate of 41.7%. Re-evaluated under the same conditions, Claude Opus 5 scored 75.4% partial and 39.6% strict pass, and Claude Fable 5 scored 72.9% partial and 36.1% strict pass. Because the task files differ, these results supersede the OSWorld 2.0 figures in the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf) and are not directly comparable to results reported on earlier releases of the benchmark.

![](assets/figures/p189-1.png)

:::caption
**[Figure 8.14.3.A] OSWorld 2.0 scores** across models. Claude Fable 5.1 was evaluated with its production safeguards enabled. On tasks where these safeguards intervened, Fable 5.1 and Fable 5 scored a zero on OSWorld, and Fable 5 scored a zero on AutomationBench. In all other interventions from our safeguards, cybersecurity tasks were completed by Claude Opus 4.8, and biology tasks were completed by Claude Opus 5. This likely reduces the performance of Fable 5.1 and Fable 5 on these benchmarks. Scores are on the benchmark authors’ August 2026 task release; Fable 5 and Opus 5 were re-run under the same conditions.
:::

<!-- p.190 -->

![](assets/figures/p190-1.png)

:::caption
**[Figure 8.14.3.B] OSWorld 2.0 price vs performance** across models.
:::

#### 8.14.4 GDP.pdf

GDP.pdf[^25] is an expert multimodal reasoning benchmark from Surge AI consisting of 100 real-world prompts and PDFs drawn directly from professional workflows across 10 domains, including finance, healthcare, legal, engineering, and insurance. The benchmark tests whether models can parse, cross-reference, and synthesize the dense documents that underpin enterprise work. This includes interpreting multi-page dosage tables, isolating clauses buried in nested exhibits, and reconciling figures across quarterly filings.

We evaluated GDP.pdf using an internal harness, both with and without tools. When evaluated without tools, the model is provided with base64-encoded PDFs to match Surge’s input prompts. However, unlike Surge, we truncate (rather than drop) any PDFs that do not fit our API’s 32MB request size limit. We used Claude Opus 4.7 as a judge instead of Gemini 3 Flash. When evaluated with tools, the model is provided with a container (with the PDF file and standard libraries installed) and an image cropping tool.

<!-- p.191 -->

We report mean criteria pass rate—the fraction of rubric conditions satisfied across tasks, averaged over completed runs—instead of strict pass rate. We evaluated the model on the full 100 prompts and average scores over five runs.

On GDP.pdf, Claude Fable 5.1 achieved a mean criteria pass rate of 85.4% without tools and a score of 85.1% with tools. Claude Fable 5 scored 82.7% and 87.1%, and Claude Opus 5 scored 83.4% and 85.5%, respectively.

![](assets/figures/p191-1.png)

:::caption
**[Figure 8.14.4.A] GDP.pdf scores.** Models are evaluated with adaptive thinking and `max` effort, with and without tools. Mean criteria pass rates are averaged over five runs. Shown with 95% CI.
:::

### 8.15 Real-world professional tasks

#### 8.15.1 OfficeQA

OfficeQA is a public benchmark from Databricks that evaluates end-to-end grounded reasoning over a large corpus of historical U.S. Treasury Bulletin documents. Models must locate relevant tables across the corpus and perform precise numerical reasoning over them. We evaluate agentically, with documents provided as extracted text in a sandboxed environment and with code-execution tools available. OfficeQA Pro is a harder,<!-- p.192 --> 133-question subset of OfficeQA recommended for frontier models; we report results from both.

Claude Fable 5.1 achieved 80.2% on OfficeQA and 69.0% on OfficeQA Pro, ahead of Claude Mythos 5, which achieved 79.0% and 67.1%, and Claude Opus 5, which achieved 78.1% and 66.9%, respectively. Fable 5.1 was evaluated on the public Messages API with its production safeguards active (safety classifiers, with fallback to Opus 5 for bio blocks, and to Claude Opus 4.8 for cyber blocks), as was Opus 5 (with fallback to Opus 4.8); Mythos 5 was evaluated on the internal API without those safeguards. Runs that exhaust the output limit are scored as incorrect; under the production 128k-token output limit, no Fable 5.1 runs were truncated before producing a final answer.

A note on comparability across reports: OfficeQA scores are highly sensitive to the evaluation harness. Settings that require the model to parse the raw PDF corpus directly yield substantially lower absolute scores for all models. For example, Databricks’s own evaluation of Claude Fable 5, with documents read as images rather than extracted text, reports 57.9% on OfficeQA Pro.

#### 8.15.2 Legal Agent Benchmark

Legal Agent Benchmark (LAB) is an open-source benchmark created by Harvey AI. The core benchmark consists of over 1,200 tasks across 24 distinct practice areas. Each task contains a corpus of documents (.xlsx, .docx, .eml, .pptx, .txt), including email communications, firm templates, procedural files, and other materials the agent must sift through in order to accomplish the task. The task instructions are written as a minimal “request for work” from partner to associate. The task instructions also stipulate the expected output document and format. Evaluation is conducted pass/fail using an LLM-as-a-judge across a suite of expert-written rubric criteria (criteria per evaluated task: min=23, median=56, max=194). The LAB standard reporting considers the task a success only if all criteria are met.

We tested Claude Fable 5.1 against 1,235 problems (16 of the 1,251 problems were excluded due to data defects; exclusions were identified before testing). This model achieved a 19.09% (± 0.92, n=5) all-pass rate and a 90.81% mean criterion-pass rate with adaptive thinking and `max` effort. Fable 5.1 was evaluated on the public Messages API with production safeguards active (safety classifiers, with fallback to Claude Opus 5 for bio blocks and to Claude Opus 4.8 for cyber blocks). Since we first started reporting LAB in system cards, our grading pipeline has been updated to correctly render tracked changes in .docx deliverables and to recover from token-limit truncation. Our harness is an internal reimplementation that preserves LAB’s task content, rubric criteria, all-pass scoring, and default judge model (Claude Sonnet 4.6), with a reduced toolset. The public harness<!-- p.193 --> exposes bash, read, write, edit, glob, and grep tools, whereas we only expose bash and a Python tool.

Reporting on the held-out problem set for Harvey LAB is conducted by [Artificial Analysis](https://artificialanalysis.ai/evaluations/harvey-lab-aa). We previously reported Harvey’s scores for the held-out set. In order to represent model comparisons most accurately, we’ve updated our reporting to use Artificial Analysis’s scores for our previous models; these may differ slightly from the scores reported in previous system cards. The held-out set consists of 120 problems and is run on a harness maintained by the Artificial Analysis team ([see their methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking#harvey-lab-aa)). On the held-out set, Fable 5.1 achieves a 16.7% all-pass rate and a 93.3% criterion-pass rate with `xhigh` effort.

#### 8.15.3 GDPval-AA v2

GDPval-AA v2, developed by [Artificial Analysis](https://artificialanalysis.ai/), is an independent evaluation framework that tests AI models on economically valuable, real-world professional tasks. The benchmark uses 220 tasks from OpenAI’s [GDPval gold database](https://huggingface.co/datasets/openai/gdpval),[^26] spanning 44 occupations across nine major industries. Tasks mirror actual professional work products, including documents, slides, diagrams, and spreadsheets. Models are given shell access and web browsing capabilities in an agentic loop to solve tasks, and performance is measured via ELO ratings derived from blind pairwise comparisons of model outputs. Claude Fable 5.1 holds the top two leaderboard spots, with ELO 1853 at `max` effort and 1835 at `xhigh` effort, ahead of Claude Opus 5 at max (1824) and Claude Fable 5 at max (1723). xhigh matches max within the confidence interval while using about 25% fewer output tokens. Evaluations were run independently by Artificial Analysis.

#### 8.15.4 AA-Briefcase

[AA-Briefcase](https://artificialanalysis.ai/articles/aa-briefcase), developed by Artificial Analysis, is a new benchmark for long-horizon knowledge work on complex projects built by industry experts. Models work through multi-week projects with many linked tasks and thousands of input source files; grading combines rubric scoring and pairwise judging via a panel of frontier models to measure verifiable task success, analytical quality, and presentation quality. Claude Fable 5.1 leads at `max` effort with an ELO of 1694, on par with Claude Opus 5 (1685) and well above Claude Fable 5 (1572). Its performance at `xhigh` effort (1686) matches its performance at `max` effort within the confidence interval while using 19% fewer output tokens, and even at high effort (1611), it beats every non-Claude model while using 47% fewer tokens. Against Opus 5 at `max` effort, Fable 5.1 wins on rubric pass rate (61.5% vs. 57.2%) and analytical quality (2025<!-- p.194 --> vs. 1980) but trails on presentation (1495 vs. 1572). The evaluation was run independently by Artificial Analysis.

#### 8.15.5 Toolathlon Verified

Toolathlon is an agentic benchmark of 108 real-world tool use tasks spanning office productivity, ecommerce and operations, data analysis, and web research. The tasks start in apps that are prefilled with realistic data, and are graded by execution-based checkers that verify the resulting artifacts and what changed in the related apps or websites. The benchmark exposes more than 600 tools across 32 applications, and tasks require correct tool selection, multi-step sequencing, and checker-exact outputs over long horizons; the trajectories in our runs averaged roughly 20–26 assistant turns. We evaluate against Toolathlon-Verified, the authors’ final release (from June 2026), in which task prompts, ground truth, and evaluators were human-reviewed and finalized, with reference trajectories for eight models published for external validation.

We ran our internal harness with adaptive thinking at max effort. We evaluated Claude Fable 5.1 in its production configuration, with safety classifiers enabled and Claude Opus 4.8 as the refusal-fallback model; the comparison models were evaluated with safety classifiers and fallback disabled, and their figures are reproduced from the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf). Following the paper’s protocol, we report Pass@1 averaged over three trials across all 108 tasks, alongside Pass@3 (at least one of three trials correct), Pass³ (all three trials correct), and the average number of assistant turns per trajectory.

Fable 5.1 achieved 77.8% Pass@1. Of 324 trials, 11 (3.4%) hit a safety refusal and were partly or fully completed by the fallback model, and a further four trials were terminated by safety classifiers and are counted as failures.

<table><tbody>
<tr><th>Model</th><th>Pass@1</th><th>Pass@3</th><th>Pass³</th><th>Avg. turns</th></tr>
<tr><td><b>Claude Fable 5.1</b></td><td>77.8</td><td>81.5</td><td>73.1</td><td>23.7</td></tr>
<tr><td><b>Claude Opus 5</b></td><td>80.6</td><td>87.0</td><td>73.1</td><td>23.5</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td>79.3</td><td>86.1</td><td>73.1</td><td>19.8</td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>79.9</td><td>88.0</td><td>71.3</td><td>20.4</td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>74.7</td><td>84.3</td><td>65.7</td><td>24.5</td></tr>
</tbody></table>

:::caption
**[Table 8.15.5.A] Toolathlon scores (internal harness).** Models are evaluated with adaptive thinking and `max` effort; Claude Fable 5.1 was run with safety classifiers and refusal fallback enabled. Pass@1, Pass@3, and Pass³ are computed over all 108 tasks across three trials, per the paper’s protocol.
:::

<!-- p.195 -->

Our harness mirrors the Toolathlon-Verified task definitions, prompts, and execution-based checkers byte-for-byte, which we validated by replaying the authors’ published reference trajectories. To control live dependency drift, we pin financial data feeds to a snapshot recorded at run time and pin container images. A small number of upstream checker defects (e.g., ground truth referencing a since-renamed repository) affect all models symmetrically and are left unchanged.

A note on comparability to the published leaderboard: Our Claude Sonnet 5 and Claude Opus 4.8 figures are roughly three points higher than those on the published leaderboard (71.6% and 76.2%, respectively). This is the result of *null attempts*—runs in which the authors’ harness produced no trajectory (8 of 324 for Sonnet 5; 11 of 324 for Opus 4.8). The leaderboard counts these as failures; excluding them, our figures match the authors’ published reference trajectories within run-to-run noise.

#### 8.15.6 AutomationBench

AutomationBench[^27] is a benchmark from Zapier that measures whether an agent can complete a realistic end-to-end business workflow. Tasks are derived from real customer workflow patterns across sales, marketing, operations, support, finance, and HR. Each task places the agent inside a simulated company, with dozens of REST API endpoints spanning 47 apps (CRM, Slack, Google Workspace, etc.). The agent is given a single natural-language instruction; it must then autonomously discover the right endpoints via search; make dozens of sequential, interdependent API calls; consult and obey layered business policy documents; and correctly avoid deliberately planted distractions. Grading is pass/fail for each task and is based on meeting all of the deterministic assertions on simulated app state (e.g., the correct CRM updates were all applied).

On AutomationBench’s leaderboard, which measures performance on a private held-out evaluation set, Claude Fable 5.1 at `max` effort scored 31.4%, a substantial gain over Claude Opus 5 at `max` effort at 26.9% and Claude Fable 5 at 17.05%.

<!-- p.196 -->

![](assets/figures/p196-1.png)

:::caption
**[Figure 8.15.6.A] AutomationBench scores.** Claude Fable 5.1 at `max` effort outperforms any previous Claude model.
:::

### 8.16 ARC-AGI

ARC-AGI is a fluid intelligence benchmark developed by François Chollet and maintained by the ARC Prize Foundation. It is designed to measure AI models’ ability to reason about novel patterns given only a few examples (typically around three). Models are given input-output pairs of grids satisfying some hidden relationship, and are tasked with inferring the corresponding output for a new input grid. These tests use semi-private validation sets to ensure consistency and fairness across models.

The ARC Prize Foundation reports that Fable 5.1 achieved a verified score of 97.5% on ARC-AGI-1 and 90% on ARC-AGI-2 at `max` effort on their semi-private datasets. ARC-AGI-3 results were not available at the time of release.

<!-- p.197 -->

![](assets/figures/p197-1.png)

:::caption
**[Figure 8.16.A] ARC-AGI-1 performance, as reported by the ARC Prize Foundation.** Claude Fable 5.1 achieved 97.5% on ARC-AGI-1 at `max` effort.
:::

![](assets/figures/p197-2.png)

:::caption
**[Figure 8.16.B] ARC-AGI-2 performance, as reported by the ARC Prize Foundation.** Claude Fable 5.1 achieved 90% on ARC-AGI-2 at `max` effort.
:::

<!-- p.198 -->

### 8.17 Healthcare

We evaluated Claude Fable 5.1 on two healthcare benchmarks, HealthBench[^28] and HealthBench Professional,[^29] to assess performance on a variety of healthcare tasks. HealthBench is an open-source evaluation developed to assess safety, accuracy, and communication across realistic healthcare contexts. The benchmark uses over 48,000 expert-written rubric items to grade 5,000 multi-turn patient conversations. HealthBench Professional is a clinical task benchmark composed of 525 physician-authored conversations spanning clinical consults, documentation, and research tasks. Each is graded against rubric criteria by an LLM-as-a-judge model.

#### 8.17.1 HealthBench results

On HealthBench, Claude Fable 5.1 achieved a raw score of 66.7%, ahead of Claude Fable 5 at 61.2% and Claude Sonnet 5 at 59.2%, and behind Claude Opus 5 at 67.1%. After length adjustment, which penalizes verbose model responses, Fable 5.1 achieved a score of 60%.

![](assets/figures/p198-1.png)

:::caption
**[Figure 8.17.1.A] HealthBench raw and length-adjusted scores**. All Claude models used adaptive thinking and `max` effort. Claude Opus 4.8 was used as the grader model. Claude Fable 5.1 was run with safety classifiers<!-- p.199 --> active and a refusal-fallback to Claude Opus 5. Scores were averaged over five trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in OpenAI’s GPT-5.5 System Card. Shown with 95% CI.
:::

#### 8.17.2 HealthBench Professional results

On HealthBench Professional, Claude Fable 5.1 achieved a raw score of 74.2%, ahead of Claude Opus 5 at 73.4%, Fable 5 at 68.9%, and Claude Sonnet 5 at 62.4%. After length adjustment, which penalizes verbose model responses, Fable 5.1 achieved a score of 62.1%.

![](assets/figures/p199-1.png)

:::caption
**[Figure 8.17.2.A] HealthBench Professional raw and length-adjusted scores**. All Claude models used adaptive thinking at `max` effort. Claude Opus 4.8 was the grader model. Claude Fable 5.1 was run with safety classifiers active and a fallback to Claude Opus 5 when a classifier block occurred. Scores were averaged over five trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in the HealthBench Professional paper. Shown with 95% CI.
:::

### 8.18 Multilingual performance

We evaluated Claude Fable 5.1 on two multilingual benchmarks, Global MMLU (GMMLU) and Multi-task Indic Language Understanding Benchmark (MILU),[^30] to assess performance across a range of languages.

<!-- p.200 -->

GMMLU extends the standard MMLU evaluation across 42 languages, from high-resource languages such as French and German to low-resource languages such as Yoruba, Igbo, and Chichewa. MILU covers 11 languages—10 Indic languages (Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu) and English—and tests culturally grounded knowledge comprehension.

#### 8.18.1 GMMLU results

On GMMLU, Claude Fable 5.1 achieved an average accuracy of 94.0% across 42 languages, ahead of Claude Fable 5 at 93.6%, Claude Opus 5 at 92.5%, and Claude Sonnet 5 at 89.0%.

![](assets/figures/p200-1.png)

:::caption
**[Figure 8.18.1.A] GMMLU average accuracy.** All Claude models used adaptive thinking and `max` effort. Scores were reported for a single trial. No tools or customized system prompts were provided to any model.
:::

#### 8.18.2 MILU results

On MILU, Claude Fable 5.1 achieved an average accuracy of 93.0% across 11 languages, ahead of Claude Fable 5 at 92.9%, Claude Opus 5 at 92.1%, and Claude Sonnet 5 at 89.3%.

<!-- p.201 -->

![](assets/figures/p201-1.png)

:::caption
**[Figure 8.18.2.A] MILU average accuracy.** All Claude models used adaptive thinking and `max` effort. Scores were averaged over five trials. No tools or customized system prompts were provided to any model.
:::

### 8.19 Life sciences capabilities

We continue to report evaluations in areas including computational biology, structural biology, organic chemistry, and protocol troubleshooting. These evaluations, many of which were developed internally by domain experts, focus on capabilities that support beneficial applications in basic research and drug development, complementing the CB risk assessments discussed in [Section 2.2](#22-cb-evaluations), which focus on the potential for misuse.

Although many of these evaluations are not publicly released, we briefly describe each one below. For all evaluations (with the exception of protocols and protein design), Claude has access to a bash tool for code execution, a file editor, and a pre-specified set of installed packages. Unlike previous iterations of these evaluations, we limited Claude’s ability to install packages to only those available in an internal repository. For the protocol benchmarks, Claude has access to bash, file editor, and web search tools. For the protein design benchmarks, Claude does not have access to tools.

When available, we also report scores for GPT-5.6 Sol and Gemini 3.1 Pro. All GPT and Gemini evaluations were run with the same or more permissive network access<!-- p.202 --> configurations as our evaluations of Claude. We did not run private benchmarks (such as LatchBio’s) on GPT or Gemini.

#### 8.19.1 BioMysteryBench

BioMysteryBench assesses a model’s ability to solve difficult analytical challenges that require interleaving computational analysis with biological reasoning. Given unprocessed datasets, the model must answer questions such as identifying a knocked-out gene from transcriptomic data or determining which virus infected a sample. For this benchmark, we report the subset of problems that independent human experts were able to solve (Human Solvable) as well as the subset that remain unsolved by humans but have an objective, ground-truth solution (Human Difficult). Note that, compared to other versions of this evaluation reported in previous system cards, we limited Claude’s ability to install packages to only those available in an internal repository, and restricted its set of accessible domains to a small list. Nevertheless, these scores are within the noise of previously reported scores.

In the Human Solvable subset, Claude Mythos 5.1 achieved 90.3%, below Claude Opus 5 at 91.4% and on par with Claude Mythos 5 at 90.1%. Mythos 5.1 exceeded GPT-5.6 Sol at 86.1%, Claude Sonnet 5 at 84.9%, and Gemini 3.1 Pro at 83.6%. On the Human Difficult subset, Opus 5 led at 51.8%, followed by Mythos 5 at 44.7%, Mythos 5.1 at 44.1%, and Sonnet 5 at 39.4%. Gemini 3.1 Pro scored 32.9% and GPT-5.6 Sol scored 28.8%.

#### 8.19.2 LatchBio Bioinformatics

Developed by LatchBio, these evaluations assess the ability to solve challenging real-world bioinformatics problems. The SpatialBench Verified variant tests analysis of spatial transcriptomics data—gene expression mapped to physical locations in a tissue slice—across a set of 115 externally validated problems, requiring the model to answer biological questions about the sample from the results. The SingleCellBench variant tests analysis of single-cell RNA sequencing data across 195 problems spanning standard workflows such as labeling cell types, finding differentially expressed genes, and correcting batch effects.

On SpatialBench Verified, Claude Mythos 5.1 achieved the top score at 77.6%, ahead of Claude Opus 5 at 72.5%, Claude Sonnet 5 at 67.8%, and Claude Mythos 5 at 69.2%. On SingleCellBench, Mythos 5.1 again led at 61.9%, ahead of Opus 5 at 60.6%, Mythos 5 at 59.3%, and Sonnet 5 at 56.2%.

<!-- p.203 -->

#### 8.19.3 ProteinGym Hard

This benchmark assesses a model’s ability to predict how mutations affect a protein’s function by ranking a subset of mutant protein sequences against the wild type sequence. It is scored by rank correlation against real lab measurements from the published ProteinGym benchmark. Claude Mythos 5.1 achieved 49.3%, the strongest result, ahead of Claude Opus 5 at 47.7% and Claude Mythos 5 at 45.8%. Gemini 3.1 Pro scored 37.0%, Claude Sonnet 5 scored 36.6%, and GPT-5.6 Sol scored 35.5%.

#### 8.19.4 Protein Design

This benchmark assesses Claude’s protein design abilities. The Sequence Generation variant assesses Claude’s ability to generate novel protein sequences conditioned on a variety of design constraints, such as natural-language descriptions of a given protein family, knot topology, globularity, and structural motifs for enzyme active sites and binding pockets. It is scored by constraint satisfaction, protein folding confidence, and sequence novelty. Claude Mythos 5.1 achieved 46.0%, ahead of Claude Opus 5 at 42.4%, Claude Mythos 5 at 40.4%, and Claude Sonnet 5 at 20.2%. Note that the scores reported here differ slightly from those reported in the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf) due to updates we made to the benchmark and grader.

The Library Ranking variant assesses Claude’s ability to prioritize protein designs for experimental testing. Each problem gives Claude sequences annotated with wet-lab measurements from a real protein engineering campaign together with a selection objective, and asks it to rank a held-out set of sequences from the same campaign. Mythos 5.1 achieved 49.3%, ahead of Mythos 5 at 48.2%, Opus 5 at 48.0%, and Sonnet 5 at 41.3%.

#### 8.19.5 Organic chemistry, V2

We evaluated models’ fundamental skills on tasks like predicting molecular structures from spectroscopy data, designing multi-step synthetic routes, predicting reaction products, and understanding chemical structure images. The evaluation was recently updated to include more challenging problems recommended by expert chemists. Claude Mythos 5.1 achieved a score of 69.2%, the strongest result, ahead of Claude Opus 5 at 65.7% and Claude Mythos 5 at 64.3%. All three are ahead of Gemini 3.1 Pro at 45.9%, Claude Sonnet 5 at 43.7%, and GPT-5.6 Sol at 43.2%. Note the scores reported here differ slightly from those reported in the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf) based on feedback from external experts.

<!-- p.204 -->

#### 8.19.6 Protocols

This assessment looks at models’ ability to assist with molecular biology protocols, including by using web search tools to find additional details about protocols online. The Troubleshooting variant assesses Claude’s ability to detect and fix errors in protocols. The Understanding variant, created by Benchling, assesses Claude’s ability to take an online protocol and extend it in additional directions.

For the Troubleshooting variant, Claude Mythos 5.1 led at 70.2%, ahead of Claude Mythos 5 at 66.6%, Claude Sonnet 5 at 62.3%, and Claude Opus 5 at 61.1%. Gemini 3.1 Pro scored 58.1% and GPT-5.6 Sol scored 56.4%.

For the Understanding variant, Opus 5 remains the strongest model at 80.0%, with Mythos 5.1 following at 77.2% and ahead of Mythos 5 at 69.7%, GPT-5.6 Sol at 63.9%, Sonnet 5 at 60.5%, and Gemini 3.1 Pro at 52.8%. Note that for the Understanding variant, the scores reported here differ slightly from those reported in the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf), due to a change in the evaluation configuration in which we removed external network access.

<!-- p.205 -->

![](assets/figures/p205-1.png)

:::caption
**[Figure 8.19.6.A] Life science benchmarks.** Performance of Claude Mythos 5.1 and comparison models across the benchmarks shown; per-benchmark results are discussed in the sections above.
:::
[^12]: Deng, X., et al. (2025). SWE-Bench Pro: Can AI agents solve long-horizon software engineering tasks? arXiv:2509.16941. [https://arxiv.org/abs/2509.16941](https://arxiv.org/abs/2509.16941)

[^13]: Yang, J., et al. (2024). SWE-bench Multimodal: Do AI Systems generalize to visual software domains? arXiv:2410.03859. [https://arxiv.org/abs/2410.03859](https://arxiv.org/abs/2410.03859)

[^14]: Proximal (2026). FrontierSWE v2. [https://www.proximal.ai/blog/frontierswev2/](https://www.proximal.ai/blog/frontierswev2/)

[^15]: Cursor (2026). CursorBench. [https://cursor.com/cursorbench](https://cursor.com/cursorbench)

[^16]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^17]: Phan, L., et al. (2025). Humanity’s Last Exam. arXiv:2501.14249. [https://arxiv.org/abs/2501.14249](https://arxiv.org/abs/2501.14249)

[^18]: Zhong, J., et al. (2026). DRACO: a cross-domain benchmark for Deep Research Accuracy, Completeness, and Objectivity. arXiv:2602.11685. [https://arxiv.org/abs/2602.11685](https://arxiv.org/abs/2602.11685)

[^19]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^20]: Surge AI (2026). Chartography: A benchmark for professional chart understanding. Surge AI. [https://surgehq.ai/blog/chartography](https://surgehq.ai/blog/chartography)

[^21]: Surge AI (2026). Chartography [Code repository]. GitHub. [https://github.com/surge-ai/chartography](https://github.com/surge-ai/chartography)

[^22]: Zhang, H., et al. (2026). BenchCAD: A comprehensive, industry-standard benchmark for programmatic CAD. arXiv:2605.10865. [https://arxiv.org/abs/2605.10865](https://arxiv.org/abs/2605.10865)

[^23]: Zhang, H., et al. (2026). BenchCAD [Code repository]. GitHub. [https://github.com/BenchCAD/BenchCAD-main](https://github.com/BenchCAD/BenchCAD-main)

[^24]: Yuan, M., et al. (2026). OSWorld 2.0: Benchmarking computer use agents on long-horizon real-world tasks. arXiv:2606.29537. [https://arxiv.org/abs/2606.29537](https://arxiv.org/abs/2606.29537)

[^25]: Surge AI. (2026). GDP.pdf: Can $100B AI models master the documents that run the world? [https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world](https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world)

[^26]: Patwardhan, T., et al. (2025). GDPval: Evaluating AI model performance on real-world economically valuable tasks. arXiv:2510.04374. [https://arxiv.org/abs/2510.04374](https://arxiv.org/abs/2510.04374)

[^27]: Shepard, D., and Salimans, R. (2026). AutomationBench. arXiv:2604.18934. [https://arxiv.org/abs/2604.18934](https://arxiv.org/abs/2604.18934)

[^28]: Arora, R. K., et al. (2025). HealthBench: Evaluating large language models toward improved human health. arXiv:2505.08775. [https://arxiv.org/abs/2505.08775](https://arxiv.org/abs/2505.08775)

[^29]: Soskin Hicks, R., et al. (2026). HealthBench Professional: Evaluating large language models on real clinician chats. arXiv:2604.27470. [https://arxiv.org/abs/2604.27470](https://arxiv.org/abs/2604.27470)

[^30]: Verma, S., et al. (2024). MILU: A multi-task Indic language understanding benchmark. arXiv:2411.02538. [https://arxiv.org/abs/2411.02538](https://arxiv.org/abs/2411.02538)

