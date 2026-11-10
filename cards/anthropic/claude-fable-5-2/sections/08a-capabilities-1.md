<!-- source: source.pdf pages 207-242 -->

<!-- p.207 -->

## 8 Capabilities

### 8.1 Evaluation summary

<table><tbody>
<tr><th colspan="2" rowspan="2">Evaluation</th><th colspan="3">Our models</th><th>Other</th></tr>
<tr><th>Fable 5.2</th><th>Fable 5.1</th><th>Opus 5.5</th><th>GPT-6 Astra</th></tr>
<tr><th colspan="2">FrontierCode 2.0</th><td><b>49.1</b></td><td>32.4</td><td>45.5</td><td>42.8</td></tr>
<tr><th colspan="2">FrontierSWE v2</th><td><b>69.9</b></td><td>56.3</td><td>62.3</td><td>65.5</td></tr>
<tr><th rowspan="2">Humanity’s Last Exam</th><td><i><b>No tools</b></i></td><td><b>73.2</b></td><td>60.9</td><td>64.4</td><td>–</td></tr>
<tr><td><i><b>With tools</b></i></td><td><b>74.2</b></td><td>65.6</td><td>67.7</td><td>57.2</td></tr>
<tr><th colspan="2">WANDR <i>(Relaxed score)</i></th><td><b>82.1</b></td><td>68.7</td><td>72.3</td><td>-</td></tr>
<tr><th rowspan="2">AA-Briefcase v1.1</th><td><i><b>Rubric</b></i></td><td><b>66.1</b></td><td>61.5</td><td>61.2</td><td>52.0</td></tr>
<tr><td><i><b>ELO</b></i></td><td>1785</td><td>1669</td><td><b>1800</b></td><td>1569</td></tr>
<tr><th colspan="2">OSWorld 2.1 (<i>Offline set, partial</i>)</th><td><b>89.3</b></td><td>83.5</td><td>87.2</td><td>79.5*<sup>[^10]</sup></td></tr>
<tr><th colspan="2">GDPval-AA v2.1</th><td>1831</td><td>1763</td><td><b>1866</b></td><td>1584</td></tr>
<tr><th colspan="2">Remote Labor Index (RLI)</th><td><b>41.3</b></td><td>17.9</td><td>21.3</td><td>20.8</td></tr>
<tr><th colspan="2">AutomationBench</th><td><b>51.4</b></td><td>31.4</td><td>42.5</td><td>41.4</td></tr>
<tr><th colspan="2">De Novo Binder Design <i>(No safeguards)<sup>[^11]</sup></i></th><td><b>85.1</b></td><td>79.1</td><td>82.6</td><td>-</td></tr>
<tr><th rowspan="2">Chartography</th><td><i><b>No tools</b></i></td><td><b>73.4</b></td><td>44.8</td><td>64.4</td><td>71.0</td></tr>
<tr><td><i><b>With tools</b></i></td><td><b>91.6</b></td><td>88.4</td><td>89.0</td><td>–</td></tr>
<tr><th rowspan="3">SWE-bench</th><td><i><b>Pro</b></i></td><td><b>93.0</b></td><td>81.2</td><td>89.9</td><td>–</td></tr>
<tr><td><i><b>Multilingual</b></i></td><td><b>96.6</b></td><td>89.1</td><td>93.9</td><td>–</td></tr>
<tr><td><i><b>Multimodal</b></i></td><td><b>74.1</b></td><td>54.7</td><td>61.4</td><td>–</td></tr><!-- p.208 --><tr><td colspan="2"><b>CVE Rediscovery</b> <i><b>(No safeguards)<sup>[^12]</sup></b></i></td><td><b>89.6</b></td><td>78.3</td><td>81.3</td><td>–</td></tr>
</tbody></table>

:::caption
**[Table 8.1.A] Capability evaluation summary.** Unless otherwise noted, all Claude Fable 5.2 results use adaptive thinking at `max` effort and default sampling settings (temperature, top_p), and are averaged over five trials. FrontierCode 2.0 scores are each model’s best across effort levels: `xhigh` for Fable 5.2 and Claude Fable 5.1, and `max` for Claude Opus 5.5 and GPT-6 Astra. RLI uses default effort settings. Context window sizes are evaluation-dependent and do not exceed 1M tokens. The best score in each row is **bolded**. Competitor figures are drawn from the respective developers’ published system cards or from benchmark leaderboards. This table shows selected evaluations. Full results for these and other evaluations, including some where Fable 5.2 or Claude Mythos 5.2 did not score highest, appear in Sections 8.2 to 8.19.
:::

### 8.2 SWE-bench Pro, Multilingual, and Multimodal

SWE-bench (Software Engineering Bench) tests AI models on real-world software engineering tasks. We report three variants, each scored as the average of five trials:

- SWE-bench **Pro**[^13] is composed of problems drawn from actively maintained repositories with large, multi-file diffs. Claude Fable 5.2 achieved 93.0%.
- SWE-bench **Multilingual** extends the format to 300 problems across nine programming languages. Fable 5.2 achieved 96.6%.
- SWE-bench **Multimodal**[^14] adds visual context (screenshots and design mockups) to the issue descriptions. Fable 5.2 achieved 74.1%.

### 8.3 DeepSWE v1.1

DeepSWE is a set of 113 long-horizon software engineering tasks built to measure the capabilities of frontier coding agents. The tasks are diverse, reflect real-world complexity, and are written from scratch to avoid benchmark contamination. Claude Fable 5.2 averaged 74.3% over five trials.

### 8.4 FrontierCode

[FrontierCode](https://cognition.com/frontiercode) is an agentic coding benchmark created by [Cognition](https://cognition.com/). Tasks are derived from real pull requests in open-source repositories. Tasks were authored by maintainers of the underlying repositories and individually reviewed by Cognition researchers. A random subset was solved manually to assess fairness.

<!-- p.209 -->

Each task gives the agent a checked-out repository, an issue description, and the repository’s testing, lint, and style guidelines. The agent then works autonomously in a containerized environment with internet access, but without human intervention or timeout information, to produce a final patch. (Runs that consult solution-bearing sources, such as the original pull request, are scored zero.) Patches are graded against blocking functional criteria (primarily held-out unit tests, plus scope and performance blockers) and weighted rubric criteria, including model-graded checks for required test coverage and prohibited implementation patterns.

We report results on FrontierCode 2.0, a rebuilt suite of 132 tasks (FrontierCode 1.1 had 150) with updated scope grading, so scores on the two versions are not comparable. We report the overall score, a composite measure of the functional and rubric criteria, as mean@5.

The evaluation assesses whether models can write mergeable code diffs that do not need to be edited by a human. Its grading still penalizes out-of-scope changes, though FrontierCode 2.0 loosened its scope criteria to accept more reasonable changes beyond the task Claude Fable 5.2’s scores use the official evaluation, without any changes.

At `max` effort, Fable 5.2 scored 45.7% on FrontierCode 2.0, compared with 45.5% for Claude Opus 5.5, 42.8% for GPT-6 Astra, and 31.7% for Claude Fable 5.1. Fable 5.2’s `max` effort score includes the graded scores of 22 attempts (out of 660) that timed out. If those attempts were counted as zero, its score would be 44.4%, below Opus 5.5 at 45.5%. None of its attempts timed out at lower effort levels. Each score is a single result from Cognition with no uncertainty interval, so small differences, such as the 0.2 points between Fable 5.2 and Opus 5.5 at `max` effort, may not be meaningful.

Across the five effort settings, Fable 5.2 scored 34.2% at `low`, 37.6% at `medium`, 45.3% at `high`, 49.1% at `xhigh`, and 45.7% at `max` (Figure 8.4.A). Its score peaked at `xhigh`, compared with top scores of 45.5% for Opus 5.5 (at `max`), 42.8% for GPT-6 Astra (at `max`), and 32.4% for Fable 5.1 (at `xhigh`).

The average cost per task for Fable 5.2 rose from $2.10 at `low` effort to $2.48 at medium, $6.72 at high, $14.19 at `xhigh`, and $44.70 at `max`. Opus 5.5’s best score cost $12.82 per task, GPT-6 Astra’s cost $6.68, and Fable 5.1’s cost $8.68. Like Cognition’s public leaderboard, Table 8.1.A shows each model at its best-performing effort.

<!-- p.210 -->

![](assets/figures/p210-1.png)

:::caption
**[Figure 8.4.A] FrontierCode 2.0** score and average cost per task across reasoning effort levels (`low`, `medium`, `high`, `xhigh`, and `max`). Cognition ran the evaluation for every model shown and reported the results. Claude models were run in Claude Code, GPT-6 Astra in Codex CLI, and Gemini 4 Carbon in Antigravity CLI. The y-axis begins at 10%, so differences between points are visually magnified.
:::

### 8.5 Terminal-Bench 4.0

Terminal-Bench 4.0[^15] tests models on real-world work in containerized terminal and command-line environments. Its 66 tasks emphasize science-adjacent and frontier engineering problems, such as computational biology, physics simulation, CAD, formal proofs, and GPU performance work.

Previous Terminal-Bench versions were highly sensitive to timeouts and resource limits. Version 4.0 largely addresses this by increasing timeouts and adaptively raising both RAM and CPU in a few tasks that could benefit. The sandboxing provider might still be a confounding factor in a few tasks, but we expect it to play a significantly smaller role than it did in previous versions. We also found that the upgrade reduced the confounding effect of harness differences (e.g., CLI memory footprint, compaction strategy, and container communication protocol), making Terminal-Bench a more stable and rigorous evaluation.

<!-- p.211 -->

Claude Fable 5.2 scored 67.6% with safeguards enabled. Requests flagged by the safeguards were answered by a fallback model following the default server-side fallback policy (2.5% of requests, affecting 10% of trials; two attempts stopped instead of replying).

We ran the evaluation for Fable 5.2 with no internet access. Based on historical run logs, we preemptively cached the resources the model needed to operate and rebuilt the images accordingly. On most tasks, the agent also had offline web search and web fetch tools that could access only a frozen index. In principle, blocking internet access could lower scores if the model wanted to use online resources it could not reach. We have not rigorously measured the size of this effect for Fable 5.2, but we believe it did not move the final score outside the noise intervals.

For comparison, Claude Opus 5.5 scored 66.4% (with 2.5% of requests flagged by safeguards, affecting 10% of trials), and Claude Fable 5.1 scored 55.8%.

Scores are averaged over 10 trials per task for Fable 5.2 (660 trials), five for Opus 5.5 (330 trials), and 15 for Fable 5.1 (990 trials). When trials are treated as independent, the standard error is ±1.8 points for Fable 5.2, ±2.6 points for Opus 5.5, and ±1.6 points for Fable 5.1. All reported numbers use Claude Code in --bare mode at `max` thinking effort, except Opus 5.5, which is reported at `xhigh` effort as in its own system card.

The public leaderboard reports GPT-6 Sol at 49.4% ± 3.2% and GPT-6.1 Sol at 58.2% ± 3.1% (intervals are as reported by the leaderboard), both scored with the Codex CLI at `max` thinking effort. To our knowledge, OpenAI has not reported its own Terminal-Bench 4.0 scores for these two models. OpenAI reported GPT-6 Astra’s final Terminal-Bench 4.0 score as 57.9%, scored at high thinking effort (in its reporting, the model performed slightly better at `high` effort than at `max` effort, so we used the highest score). The public leaderboard reports GPT-6 Astra’s score as 58.2% ± 2.8% with the Codex CLI at `max` thinking effort.

Evaluated without safeguards, Claude Mythos 5.2 scored 70.5% (660 trials, standard error ±1.8 points).

### 8.6 Terminal-Bench-Science 0.1

Terminal-Bench-Science[^16] is a Stanford-led community benchmark of 70 tasks drawn from scientific research workflows, authored and reviewed by scientists and researchers across<!-- p.212 --> the life, physical, earth, mathematical, and engineering sciences. Scientific advisors to the project are from MIT, Princeton, the University of Washington, Genentech, and Stanford.

For each task, an agent CLI works in a self-contained environment from natural-language instructions. The artifacts it produces are graded against hidden, task-specific tests.

Claude Fable 5.2 scored 74.6% on Terminal-Bench-Science with safeguards enabled. Requests flagged by the safeguards were answered by a fallback model, following the default server-side fallback policy (1.3% of requests, affecting 4.1% of trials). Evaluated without these safeguards, Claude Mythos 5.2 scored 75.3%. Claude Opus 5.5 scored 58.7%, and Claude Fable 5.1 scored 52.6%. Scores are averaged over 10 trials per task (700 trials). Clustered by task, the standard error is ±4.3 points for Fable 5.2 and Claude Mythos 5.2 and ±4.8 points for Opus 5.5.

We ran the evaluation for Fable 5.2 and Claude Mythos 5.2 with the same no-internet-access setup as for Terminal-Bench 4.0 ([Section 8.5](#85-terminal-bench-40)). The reported numbers use Claude Code in --bare mode at `max` thinking effort.

OpenAI reported scores of 68.1% for GPT-6 Astra, 57.0% for GPT-6.1 Sol, and 27.6% for GPT-6 Sol, all at `max` thinking effort.

### 8.7 FrontierSWE v2

FrontierSWE v2[^17] is a Proximal benchmark of 34 ultra-long-horizon engineering and research tasks spanning system implementation, performance optimization, scientific computing, AI research, and visual reasoning. Examples include reimplementing the core of Quantum ESPRESSO’s pw.x in Rust, building an OpenGL scene renderer that can run a flight simulator, and post-training an LLM to play an interactive puzzle game. Each trial has a 20-hour budget. The leading public models average about 11–16 hours per trial and remain far from saturating the benchmark. Every model runs at `max` reasoning effort in Proximal’s own agent harness, and the reported score is the mean across five trials per task.

Claude Fable 5.2 scored 69.9% on FrontierSWE v2, first among the models Proximal evaluated. It was ahead of GPT-6 Astra (65.5%), Claude Opus 5.5 (62.3%), Claude Sonnet 5.5 (61.9%), Claude Fable 5.1 (56.3%), and Gemini 4 Argon (55.0%). Fable 5.2 scored highest or tied for highest on 20 of the 34 tasks. Its gains over Opus 5.5 were greatest for performance optimization, scientific computing, and visual reasoning.

<!-- p.213 -->

### 8.8 CursorBench 4.0

[CursorBench 4.0](https://cursor.com/cursorbench) is Cursor’s agentic coding benchmark. Its tasks are drawn from real-world Cursor usage and executed end to end in Cursor’s production agent harness. Cursor measured and reported all scores independently. Output token counts for Claude Fable 5.2 are from the result files Cursor sent us.

Fable 5.2 scored 60.0% at `max` effort, 56.3% at `xhigh`, 56.9% at `high`, 54.8% at `medium`, and 53.2% at `low`. Its `max` effort score was 2.2 points above Claude Opus 5.5 (57.8%), 8.2 points above Claude Fable 5.1 (51.8%), and 13.4 points above Claude Opus 5 (46.6%), each at `max` effort.

Much of Fable 5.2’s performance is available below `max` effort. At `high` effort, its score was 56.9%, within one point of Opus 5.5 at `max` effort. It used about 99,000 output tokens per task at `high` effort, compared with about 353,000 at `max`. Each score is a single result reported by Cursor with no uncertainty interval, so small differences between neighboring settings, such as the 0.6 points between `high` and `xhigh`, may not be meaningful. As of November 7, Cursor’s public leaderboard did not list any GPT-6 models (its newest OpenAI entry was GPT-5.6 Sol, at 41.7%), so we do not show any GPT-6 results in Figure 8.8.A.

The [Opus 5.5](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf) and [Claude Sonnet 5.5](https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf) System Cards also reported CursorBench 4.0. However, Cursor attributes part of Fable 5.2’s score to additional prompt and harness improvements, so its score may not be directly comparable with the scores in those system cards.

<!-- p.214 -->

![](assets/figures/p214-1.png)

:::caption
**[Figure 8.8.A] CursorBench 4.0 score and average cost per task across reasoning effort levels.** Cursor executed the evaluation end to end in its production agent harness and independently measured and reported the scores. Fable 5.2 scored 53.2% at `low`, 54.8% at `medium`, 56.9% at `high`, 56.3% at `xhigh`, and 60.0% at `max`. Opus 5.5 scored 57.8% at `max`, and Fable 5.1 scored 51.8% at `max`. Fable 5.2’s cost is computed at its list price from the token counts in the result files Cursor sent us. The other costs are Cursor’s own. Gemini 4 Argon is shown only at `medium` effort, its default in Cursor (52.8%, at $4.39 per task). The x-axis is logarithmic; each score is a single result, so no uncertainty intervals are shown. The y-axis begins at 40%, so differences between points are visually magnified.
:::

### 8.9 STEM professor bench

STEM Professor Bench is an internal set of unpublished research problems written by professional scientists, each representing about a month of research work with colleagues. We report the results on a 64-problem subset. Most problems are in theoretical physics, including string theory and holography, condensed matter, high-energy theory, and astrophysics. The rest cover computational and data analysis physics, materials science, neuroscience, and mathematics.

Each model worked as a single agent with Python, bash, and a file editor, within the time and compute limits set by each problem’s author. For 58 of the 64 problems, all models could also search a fixed index of arXiv papers published up to December 1, 2025. Claude Opus 5 graded 56 of the problems by comparing the final answer with the author’s answer key or rubric. The other eight were graded by a checking program or procedure written by<!-- p.215 --> the author or by comparing an output file with the author’s reference. Models can receive partial credit on a few problems; the rest are scored pass or fail. We ran nine attempts per problem.

![](assets/figures/p215-1.png)

:::caption
**[Figure 8.9.A] Mean score on STEM Professor Bench** at `max` effort, over up to nine attempts on each of the 64 problems. Error bars show ±1 standard error of the variation between attempts.
:::

### 8.10 Long context

#### 8.10.1 ProgramBench

ProgramBench is a long-context agentic coding benchmark of 200 program reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using the internet or decompilation tools. Tasks range from small terminal utilities (jq, ripgrep) to large systems (FFmpeg, SQLite, the PHP interpreter). Submissions are graded against more than 247,000 execution-based behavioral tests generated via agent-driven fuzzing.

We excluded 34 tasks for which the reference binary itself scored below 0.9 on the hidden test suite (indicating test flakiness), leaving 166 tasks. On those tasks, we scored only<!-- p.216 --> against tests the reference binary passes. We report the hidden-test pass rate using the same mini-swe-agent harness that the upstream repo uses, without the six-hour time limit. On this set, Claude Fable 5.2 scored 85.6%, compared with Claude Fable 5.1 at 87.6% and Claude Opus 5.5 at 91.2%.

The harness gives the model a single 1M-token context window with no indication of how much remains. Fable 5.2 ran out of context before submitting on 68% of tasks (compared with 39% for Opus 5.5 and 28% for Fable 5.1). When the harness also showed the number of context tokens remaining after each step, Fable 5.2 scored 91.6% (up from 85.6%), compared with Fable 5.1 at 86.8% and Opus 5.5 at 91.1%.

We believe ProgramBench is a strong measure of long-context coding performance: Fable 5.2’s episodes cover a range of context lengths up to the full 1M-token window, and the tasks test long-context capabilities that closely align with real-world use cases.

### 8.11 Agentic search

#### 8.11.1 HLE

Humanity’s Last Exam (HLE)[^18] is a multimodal benchmark of 2,500 questions spanning dozens of subjects. The questions were written and reviewed by subject-matter experts, kept only if frontier LLMs could not answer them, and designed so that they cannot be answered quickly via internet search.

We tested Claude Fable 5.2 in two configurations: (1) reasoning-only, without tools; and (2) with web search, web fetch, programmatic tool calling, and code execution. In all runs, thinking was set to auto, and each attempt had a 980k-token task budget. Context compaction was not used for these results. Claude Opus 4.6 served as the model grader.

To guard against contamination in the tools variant, we blocklisted sources known to discuss HLE for both web search and web fetch (see [Appendix 9.2](#92-blocklist-used-for-humanitys-last-exam)). We also screened every correctly answered transcript with text-matching rules for signs of HLE-specific sources, and Claude Opus 5 reviewed each flagged transcript. Confirmed cases of cheating were regraded as incorrect.

<!-- p.217 -->

![](assets/figures/p217-1.png)

:::caption
**[Figure 8.11.1.A] Humanity’s Last Exam (HLE, with tools) reasoning effort scaling**. Accuracy on HLE as reasoning effort scales from `low` to `max`, plotted against average cost per task (log scale). Costs assume a perfect cache hit rate, with web search fees excluded.
:::

<!-- p.218 -->

![](assets/figures/p218-1.png)

:::caption
**[Figure 8.11.1.B] Humanity’s Last Exam (HLE, no tools) test-time compute scaling.** Accuracy on HLE as reasoning effort scales from `low` to `max`, plotted against average cost per task (log scale). Costs assume a perfect cache hit rate.
:::

#### 8.11.2 DRACO

Deep Research Accuracy, Completeness, and Objectivity (DRACO[^19]) is a deep research benchmark from Perplexity that evaluates how well models perform at complex research questions that real users would ask. DRACO consists of 100 curated tasks derived from user queries across a variety of domains. Responses are graded using expert-written rubrics covering factual accuracy, breadth and depth of analysis, presentation quality, and citation quality.

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution, and a 980k-token task budget.

The DRACO paper’s original judge model, Gemini 3 Pro, is no longer available. We used Claude Opus 4.6 to grade responses against the per-task rubrics, with the same binary MET/UNMET verdicts aggregated into a normalized score, per the paper’s formula in<!-- p.219 --> Section 4.2. Following the paper’s protocol, we ran five independent grading runs per response and recorded the mean. Our judge prompt is taken from the paper’s Appendix C.5. The paper’s Appendix A shows that judge choice can shift absolute scores by 10 to 25 points while preserving system ordering, so our scores are not directly comparable with the paper’s headline numbers.

In addition to changing the judge model, we used our own agent harness (no Appendix C.4 system prompt; web search, web fetch, programmatic tool calling, and code execution with a 980k-token budget). We instructed the model to write its final report to a file in its execution environment and graded only that file’s contents, rather than the full agent transcript, to isolate the deliverable from intermediate tool output.

![](assets/figures/p219-1.png)

:::caption
**[Figure 8.11.2.A] DRACO score** and average cost per task across reasoning effort levels. Normalized score on DRACO at a 980k-token task budget as reasoning effort rises from `low` to `max`, plotted against average cost per task (log scale). Costs assume a perfect cache hit rate, with web search fees excluded.
:::

#### 8.11.3 WANDR

[WANDR (Wide ANd Deep Research)](https://www.perplexity.ai/hub/blog/wandr-benchmark-evaluating-research-agents-that-must-search-wide-and-deep) is a benchmark from Perplexity intended as a wide-search counterpart to the DRACO deep research benchmark. It comprises 500 tasks in which the model must search for tens to hundreds of entities, find facts about each, and<!-- p.220 --> list these facts along with citations in structured records. We ran a modified version of this evaluation, and we describe the differences in methodology below.

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution, and a 980k-token task budget. Tasks are graded with a judge model that has access to the same web fetch tool as the model being evaluated. The grader re-fetches the cited URLs; the judge model then determines whether the references support the solution.

The primary metric is “soft F1,” which balances precision (how much of the model’s solution is verified) against recall (how much of the requested fact collection it completed). Partial credit is awarded when only some of the required facts can be verified. Results are averaged over the 500 tasks. Individual entity rows that fail format validation are dropped without failing the entire task.

In our evaluations, the models were given offline web search and web fetch tools that could access only a frozen index. By contrast, Perplexity’s version uses the live web. We judged Claude models with Claude Opus 4.6, whereas Perplexity uses GPT-5.4. Our prompts also differed slightly. Because our tools and grading logic differed from those in Perplexity’s harness, our results are not directly comparable to reported numbers for competitor models.

<!-- p.221 -->

![](assets/figures/p221-1.png)

:::caption
**[Figure 8.11.3.A] WANDR soft F1 score** and average cost per task across reasoning effort levels at a 980k-token task budget (log scale). Costs assume a perfect cache hit rate, with web search fees excluded.
:::

### 8.12 Multi-agent

We evaluated Claude Fable 5.2’s performance in multi-agent configurations. Below, we highlight the advantages of small teams over a single agent on ProgramBench ([Section 8.12.1](#8121-multi-agent-programbench)) and DRACO ([Section 8.12.2](#8122-multi-agent-draco)) and discuss the increasing potential of large teams coordinating to solve more ambitious problems ([Section 8.12.3](#8123-large-agent-teams)). We also describe the harnesses we used for these results ([Section 8.12.4](#8124-multi-agent-harnesses)) and the measurement methodology ([Section 8.12.5](#8125-evaluation-methodology)).

The serving speeds of Fable 5.2 in these evaluations may differ from what external users experience, so the absolute scores and token counts reported within a particular time window may not generalize.

<!-- p.222 -->

#### 8.12.1 Multi-agent ProgramBench

ProgramBench[^20] is an agentic benchmark of 200 program reconstruction tasks. Each task involves rebuilding a codebase to reproduce a program’s behavior, using only the program’s compiled binary and documentation as a reference (more details in [Section 8.10.1](#8101-programbench)).

We compared two small-scale multi-agent harness configurations with the single-agent baseline: a fixed five-agent team and dynamically spawned asynchronous subagents (details in [Section 8.12.4](#8124-multi-agent-harnesses)). We provided each harness with the same four-hour time budget for every task. Once the time budget had elapsed, the run was given notice and one final turn to finish. We graded at a series of intermediate snapshots, and we used the resulting per-task trajectories of score, latency, and tokens to construct the cumulative curves in Figures 8.12.1.A and 8.12.1.B.

![](assets/figures/p222-1.png)

:::caption
**[Figure 8.12.1.A] Score versus latency for the full set of 166 “golden” ProgramBench tasks.** Each point on the curve is the average fraction of hidden tests passed if every problem were stopped at that number of seconds. Shaded regions represent the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still running at that point on the curve.
:::

<!-- p.223 -->

As Figure 8.12.1.A shows, both the five-agent team and async subagents reached the same score as the single agent on these tasks, at a lower latency. In particular, the five-agent team reached a score of 0.6 in half the time it took the single agent. The async subagent curve lies largely between the two, improving on the single agent but by a smaller margin than the five-agent team.

![](assets/figures/p223-1.png)

:::caption
**[Figure 8.12.1.B] Score versus tokens for the full set of 166 “golden” ProgramBench tasks.** Each point on the curve is the average fraction of hidden tests passed if every problem were stopped at this amount of token usage. Shaded regions represent the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still running at that point on the curve.
:::

Together, Figures 8.12.1.A and 8.12.1.B demonstrate the latency–cost trade-off of multi-agent harnesses. When latency matters, five-agent teams and async subagents can productively absorb additional token budget by distributing work across agents, reaching a given score faster, but at a higher cost.

#### 8.12.2 Multi-agent DRACO

We also evaluated small multi-agent teams on DRACO, a deep research benchmark consisting of 100 curated tasks derived from user queries across a variety of domains (more details in [Section 8.11.2](#8112-draco)). These problems consist of upfront web research followed by report generation and are much shorter in duration than ProgramBench tasks. We<!-- p.224 --> compared the same three harnesses as in the previous section at time budgets of 15, 30, and 60 minutes. Figure 8.12.2.A shows the relationship between the score achieved and the average latency.

![](assets/figures/p224-1.png)

:::caption
**[Figure 8.12.2.A] Score versus latency for the DRACO tasks.** Multi-agent teams dominate the score–latency Pareto frontier. Latency is the mean derived latency per task (see [Section 8.12.5](#8125-evaluation-methodology)).
:::

Figure 8.12.2.A demonstrates that multi-agent teams dominated the score–latency Pareto frontier at increasingly tight time budgets. The five-agent team with a 15-minute budget exceeded the performance of a single agent with a 60-minute budget. Figure 8.12.2.B shows the relationship between score and total tokens.

<!-- p.225 -->

![](assets/figures/p225-1.png)

:::caption
**[Figure 8.12.2.B] Score versus tokens for the DRACO tasks.** Tokens count everything that entered each agent’s context window once: new input (task prompt, tool results, messages from other agents) plus all generated output, thinking included, summed over agents.
:::

Figure 8.12.2.B highlights the consistent relationship between score and tokens across harnesses on these tasks. Multi-agent teams outscored single agents because they were able to produce and consume a larger number of tokens within the same time window.

#### 8.12.3 Large agent teams

Many high-value tasks may exceed what a single agent can accomplish, instead requiring large teams of agents that decompose the work, coordinate, and communicate. We measure this with the large agent team evaluations introduced in the [Claude Opus 5.5 System Card](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf#page=83.26).

For this system card, we added a new task to the evaluation set: proving Fermat’s Last Theorem in Lean from fixed statements, with intermediate theorems as weighted milestones and a score of 1.0 for a complete proof. The agent teams started with definitions and supporting lemmas from [our earlier formalization](https://www.anthropic.com/research/formalizing-fermats-last-theorem). We ran teams of one, 10, 30, and 100 agents. Each lead and its N−1 helpers worked concurrently for 18 hours, each in its own<!-- p.226 --> sandbox, with no internet access. They shared a Git repository and a SQL database for communication. We report the best score that each team reached within 18 hours.

On this task, Claude Fable 5.2 scored 0.12 with a single agent, compared with 0.09 for Opus 5.5. With 100 agents, Fable 5.2 scored 0.35, compared with Opus 5.5 at 0.21 (Figure 8.12.3.A).

![](assets/figures/p226-1.png)

:::caption
**[Figure 8.12.3.A] Fermat’s Last Theorem in Lean: score by agent team size.** Each point is the best score a team reached within 18 hours, averaged over three runs. The score is the weighted proportion of 60 theorems whose proofs our grader accepted, using only Lean’s standard axioms (0–1 range). Fable 5.2 ran one week after Opus 5.5, with a shorter task brief. This task uses a different theorem from the Lean task in the [Claude Opus 5.5 System Card](https://www.anthropic.com/document/claude-opus-5-5-system-card), so the scores are not comparable across the two system cards.
:::

We also ran one team of 1,000 agents with an earlier snapshot of Fable 5.2, and one with Opus 5.5. After 18 hours, the earlier snapshot’s team had reached 0.86, compared with 0.26 for the Opus 5.5 team. We then resumed each team’s work with an additional 12-hour budget. By hour 30, the earlier snapshot’s team had a complete Lean proof of Fermat’s Last Theorem that our grader accepted (Figure 8.12.3.B).

<!-- p.227 -->

![](assets/figures/p227-1.png)

:::caption
**[Figure 8.12.3.B] Fermat’s Last Theorem in Lean: score over 30 hours with 1,000 agents.** Each line shows the best score one team had reached each hour, from a single run per model. At the dashed line (18 hours), both teams resumed from their last save with 12 more hours.
:::

#### 8.12.4 Multi-agent harnesses

##### 8.12.4.1 Fixed team

This harness is designed to mirror real-world settings in which multiple agents collaborate on a shared task, and to reduce latency by letting peers work in parallel. A fixed team of peer agents works on the task concurrently. All agents have identical tools and see the full task description. Depending on the task, one agent may be designated the lead.

On DRACO, the run ends when the lead finishes, and the report is graded as it stands at that point. On ProgramBench, there is no lead. The agents are peers given the same prompt, the shared repository’s main branch is graded, and the run ends when every agent has finished. On both evaluations, how the work is divided is left to the agents.

In addition to the task tools, every agent has two messaging tools: Send Message, which delivers a message to one or more teammates (inserted following the recipient’s next tool result), and Wait for Message, which pauses the agent until an incoming message arrives. On ProgramBench, each agent works in its own checkout of the task repository and can<!-- p.228 --> share code with other agents via Git. DRACO has no repository. Its agents share one container’s filesystem.

##### 8.12.4.2 Async subagents

This harness is initialized with a lead agent that can spawn asynchronous, long-lived subagents at will while retaining direct access to the task tools.

The spawning tool returns immediately rather than waiting for the subagent to finish. Each subagent sees only the instructions provided by the lead, not the original task description. Subagents can message the lead and any other subagent that is still working. A subagent’s final response is delivered to the lead as a message, after which the subagent idles until the lead wakes it with new instructions. Subagents have access to the task tools and Send Message; the lead also has access to Wait for Message, along with tools to create and terminate subagents and check subagent status (working, idle, queued, or terminated).

The single-agent baseline uses the same task tools and grader as the multi-agent configurations. It also uses context compaction alongside a 20M-token budget to ensure that the larger token expenditure of multi-agent teams does not act as a confounder. Because of this setup, its scores are not directly comparable with those reported for the same datasets in previous sections.

#### 8.12.5 Evaluation methodology

We compare single-agent and multi-agent harnesses on score, latency, and token usage.

Token usage is counted in the same way that token limits are enforced. Every token that enters an agent’s context window, input and output alike, is counted once per context window rather than once per model request. The counts are summed over all agents on a task.

Latency is reported as a derived per-task latency rather than raw wall-clock time. We calculate the latency of each agent trajectory by dividing the agent’s input and output token counts by fixed reference prefill and decode rates and adding its measured tool execution time. We account for agent idleness by carrying clocks across hand-offs. A spawned agent starts at its spawner’s clock, and an agent that receives a message or a result moves its clock forward to the sender’s clock at the time of sending, if that clock is later than its own. End-to-end latency is measured differently on each benchmark. On ProgramBench, it is the longest agent trajectory (the largest clock over all agents at each grading point). On<!-- p.229 --> DRACO, it is the lead agent’s final clock, because the task ends when the lead agent answers.

Derived latency isolates the latency of the harness (e.g., how much sequential model work and tool time it requires) from serving-side variance (e.g., batching, queuing, hardware), so harnesses are compared at the same model speed across time. Tool execution time is reported as measured, and so it still reflects conditions at the time of the run.

### 8.13 Multimodal

#### 8.13.1 Chartography

Chartography[^21] is a chart-understanding benchmark from Surge AI with 100 tasks on specialized chart types rarely evaluated in existing benchmarks, including Kaplan–Meier charts, candlestick charts, contour maps, wind rose diagrams, Sankey diagrams, Bode plots, and 3D surface plots. Because different chart types can be read to different degrees of precision, each answer is graded against an acceptable range set by experts for that specific chart, rather than against a single fixed tolerance.

We configured the model with adaptive thinking at `max` effort unless otherwise noted, with and without tools. With tools, the model was given a container, with the image file and standard libraries installed, and an image cropping tool. Our implementation of Chartography uses the tasks and expert-determined acceptable answer ranges from the official repository.[^22] To ensure comparable grading across models, we followed the Surge AI Leaderboard in using Gemini 3.5 Flash as a grader. Some previous [system cards](https://www.anthropic.com/system-cards) showed slightly lower scores because they used Claude Sonnet 4.6 as the grader for Claude models only.

Claude Fable 5.2 scored 73.4% without tools and 91.6% with tools. Claude Opus 5.5 scored 64.4% without tools and 89.0% with tools, and Claude Fable 5.1 scored 44.8% without tools and 88.4% with tools.

<!-- p.230 -->

![](assets/figures/p230-1.png)

:::caption
**[Figure 8.13.1.A] Chartography scores.** Claude models are evaluated with adaptive thinking at `max` effort, with and without tools. Scores are averaged over five runs. Shown with 95% CI. Claude scores are from our own runs. Scores for Gemini 4 Argon, GPT-6 Sol, and GPT-6 Astra are as publicly reported by Surge AI.
:::

Without tools, Fable 5.2 outperformed Opus 5.5 and Fable 5.1 at all effort levels. Its lowest-effort score matched Opus 5.5’s highest at less than a tenth of the cost per task. With tools, it was within noise of Opus 5.5 at lower effort levels at matched cost and scored slightly higher at higher effort levels.

<!-- p.231 -->

![](assets/figures/p231-1.png)

:::caption
**[Figure 8.13.1.B] Chartography scores by cost per task.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

Most Chartography figures come from public sources, and Fable 5.2 can answer some questions from memory of underlying raw data. To check the effect on scores, we redrew the charts for all 100 tasks with new data and answers, creating several novel tasks of roughly equivalent difficulty for each original task, and ran five models on both sets without tools. Fable 5.2 scored 74.3% on the original charts and 76.4% on the redrawn ones. These runs are separate from those in Figure 8.13.1.A.

Over all 100 tasks, all five models scored higher on the redrawn charts. Fable 5.2’s increase (2.1 points) was comparable to those of Opus 5.5 (2.8), GPT-6 Astra (3.2), and Gemini 4 Argon (4.6); Claude Sonnet 5.5’s was larger (7.4). Fable 5.2’s score on the original charts was within the range of scores from picking one redrawn version of each task at random. However, because the redrawn charts may differ in difficulty, this check can neither fully show nor rule out an effect of memory.

<!-- p.232 -->

![](assets/figures/p232-1.png)

:::caption
**[Figure 8.13.1.C] Chartography scores on original and redrawn charts, without tools.** Charts are redrawn with new data and answers, in runs separate from those in Figure 8.13.1.A. Claude models are evaluated with adaptive thinking at `max` effort. GPT-6 Astra was run by Anthropic through OpenAI’s API at `max` reasoning effort, and Gemini 4 Argon through Google’s Vertex AI API at the `high` thinking level. These scores are not comparable to those reported by Surge AI or in Figures 8.13.1.A and 8.13.1.B. Scores are averaged over five runs. Shown with 95% CI across runs.
:::

#### 8.13.2 BenchCAD 2.1

BenchCAD 2.1[^23] tests whether models can rebuild parts, assemblies, and circuit boards from engineering drawings and rendered images. Problems are scored with partial credit, and we report the mean score over its Core set of 100 problems. Scores are not comparable with the BenchCAD 1.0 results in previous [system cards](https://www.anthropic.com/system-cards).

We configured the model with adaptive thinking at `max` effort unless otherwise noted. Without tools, we used our own implementation of the benchmark’s protocol, in which the model writes code, sees its output and renders, and can revise for up to 60 rounds and 500,000 output tokens. With tools, the model was provided with a shell, a file editor, and an<!-- p.233 --> image zoom tool, with thinking-block clearing enabled and no limit on rounds or total tokens. Both settings use the benchmark’s official scorer.

Claude Fable 5.2 scored 75.4% without tools and 83.5% with tools. Claude Opus 5.5 scored 49.0% without tools and 65.3% with tools, and Claude Fable 5.1 scored 36.3% without tools and 44.4% with tools.

![](assets/figures/p233-1.png)

:::caption
**[Figure 8.13.2.A] BenchCAD 2.1 Core scores.** Models are evaluated with adaptive thinking at `max` effort, with and without tools. Scores are averaged over five runs. Shown with 95% CI.
:::

At lower effort levels, Fable 5.2 scored similarly to Opus 5.5 at matched cost. At higher effort levels, it pulled ahead. In both settings, Fable 5.2 at `high` effort outperformed Fable 5.1 at `max` effort, at about half the cost without tools and under a third with tools.

<!-- p.234 -->

![](assets/figures/p234-1.png)

:::caption
**[Figure 8.13.2.B] BenchCAD 2.1 Core scores by estimated API cost per task.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.13.3 OSWorld 2.1 offline set

[OSWorld 2.1](https://github.com/xlang-ai/OSWorld-V2/releases/tag/osworld-v2.1) is a benchmark of 108 long-horizon computer use tasks in which an agent operates a live Ubuntu virtual machine via screenshots and mouse and keyboard actions. As in previous [system cards](https://www.anthropic.com/system-cards), we report two metrics: the partial score (mean per-task credit across checkpoints) and the strict pass rate (the fraction of tasks with every checkpoint satisfied), each as Pass@1 averaged over five independent attempts per task. We used the benchmark’s default settings (1080p resolution and a maximum of 500 action steps per task) and Claude Opus 4.8 for tasks that require a model grader.

We report the benchmark’s official offline set: the 82 (of 108) tasks on the benchmark’s offline task list, in which the agent’s virtual machine has no internet access. All Anthropic models in this section were evaluated with the same configuration. We ran GPT-6 Astra and GPT-6.1 Sol on the same 82 tasks through OpenAI’s API, with OpenAI’s own context compaction.

<!-- p.235 -->

Claude Fable 5.2 achieved a partial score of 89.3% and a strict pass rate of 54.6%. Re-evaluated under the same conditions, Claude Opus 5.5 scored 87.2% partial and 53.2% strict pass, and Claude Fable 5.1 scored 83.5% partial and 47.6% strict pass.

![](assets/figures/p235-1.png)

:::caption
**[Figure 8.13.3.A] OSWorld 2.1 (offline set) scores across models.** Bars show the partial score and strict pass rate at `max` effort, with 95% confidence intervals over the five attempts per task; pale outlined bars are GPT models.
:::

<!-- p.236 -->

![](assets/figures/p236-1.png)

:::caption
**[Figure 8.13.3.B] OSWorld 2.1 (offline set) price and performance** for Fable 5.2, Opus 5.5, Fable 5.1, GPT-6 Astra, and GPT-6.1 Sol. Each point on a line is one reasoning effort setting (`low` to `max`, from left to right), positioned at its mean cost per task, with partial-credit scores averaged over five attempts per task. Thin gray lines are GPT models.
:::

<!-- p.237 -->

![](assets/figures/p237-1.png)

:::caption
**[Figure 8.13.3.C] OSWorld 2.1 (offline set) price and strict pass rate** for Fable 5.2, Opus 5.5, and Fable 5.1, with GPT-6 Astra and GPT-6.1 Sol. Strict pass rate counts an attempt as passed when it satisfies every checkpoint, averaged over five attempts per task. All other details are the same as in Figure 8.13.3.B.
:::

### 8.14 Real-world professional tasks

#### 8.14.1 OfficeQA

OfficeQA is a public benchmark from Databricks that evaluates end-to-end grounded reasoning over a large corpus of historical U.S. Treasury Bulletin documents. Most questions require models to find the right tables within the documents they are given and perform precise numerical reasoning over them. We ran the evaluation agentically, with the relevant documents preselected and provided as extracted text. OfficeQA Pro is the harder 133-question subset recommended for frontier models.

Claude Fable 5.2 scored 83.4% on OfficeQA and 72.9% on OfficeQA Pro (`max` effort, mean of five runs), ahead of Claude Fable 5.1, which scored 80.2% and 69.0%, and Claude Opus 5.5, which scored 78.9% and 67.7%.

<!-- p.238 -->

#### 8.14.2 Legal Agent Benchmark

Legal Agent Benchmark (LAB) is an open-source benchmark created by [Harvey AI](https://www.harvey.ai/). It consists of more than 2,010 tasks across 27 distinct practice areas. Each task contains a closed universe of documents, including email communication, firm templates, procedural files, and other client matter materials the agent must sift through to accomplish the task. The task instructions are written as a minimal “request for work” from a partner to an associate and stipulate the expected output document and format. Grading is pass/fail, using an LLM as a judge across a suite of expert-written rubric criteria. Standard LAB reporting considers a task a success only if all criteria are met.

Harvey also maintains a held-out set of 120 problems that is not publicly released. [Artificial Analysis](https://artificialanalysis.ai/evaluations/harvey-lab-aa) independently reports results on this held-out set, using a harness maintained by the Artificial Analysis team ([more on their methodology here](https://artificialanalysis.ai/methodology/intelligence-benchmarking#harvey-lab-aa)).

We report Artificial Analysis’s Harvey LAB-AA v1.1, released in October 2026. Version 1.1 runs on Harvey’s updated private task set and grades each deliverable criterion by criterion with a panel of three judge models. It also introduces a new headline metric, the hallucination-gated all-pass rate. A task is credited only when its deliverables satisfy every rubric criterion and contain no material hallucination against the task’s source documents. The rate is averaged across the three judges and over tasks.

At `max` effort, Claude Fable 5.2 achieved a 7.2% hallucination-gated all-pass rate on the held-out set (a 10.8% all-pass rate before the hallucination check). On the same metric and setting, Claude Fable 5.1 scored 6.4% and Claude Opus 5.5 scored 4.2%. Artificial Analysis reports scores of 8.6% for GPT-6 Astra, 6.9% for GPT-6.1 Sol, and 3.6% for GPT-6 Sol. Artificial Analysis states that v1.1 supersedes v1.0 and that scores are not comparable across versions, so these figures are not comparable with the all-pass rates reported in our earlier [system cards](https://www.anthropic.com/system-cards). As in our previous system cards, scores for every model are measured by Artificial Analysis so that every model is compared on the same harness.

#### 8.14.3 GDPval-AA v2.1

GDPval-AA v2.1, developed by [Artificial Analysis](https://artificialanalysis.ai/), is an independent evaluation framework that tests AI models on economically valuable, real-world professional tasks. It uses 220 tasks from OpenAI’s [GDPval gold database](https://huggingface.co/datasets/openai/gdpval),[^24] spanning 44 occupations across nine major industries. Tasks mirror actual professional work products, including documents, slides, diagrams, and spreadsheets. Models solve tasks in an agentic loop with shell access and<!-- p.239 --> web browsing. Performance is measured via Elo ratings derived from blind pairwise comparisons of model outputs, anchored to DeepSeek-V4.1-Flash (`max`) at 1600.

At `max` effort, Claude Fable 5.2 scored an Elo of 1831. It trailed Claude Opus 5.5 (1866) and Muse Wonder Full (1857) and was ahead of Claude Fable 5.1 (1763), GPT-6.1 Sol (1609), and GPT-6 Astra (1584). At `xhigh` effort, it scored 1751 while using about 57% fewer output tokens than at `max`. Evaluations were run independently by Artificial Analysis.

#### 8.14.4 AA-Briefcase v1.1

[AA-Briefcase](https://artificialanalysis.ai/articles/aa-briefcase) v1.1, developed by Artificial Analysis, is a benchmark built by industry experts to measure long-horizon knowledge work on complex projects. Models work through multi-week projects with many linked tasks and thousands of input source files. Grading combines rubric scoring and pairwise judging via a panel of frontier models to measure verifiable task success, analytical quality, and presentation quality.

At `max` effort, Claude Fable 5.2 scored an Elo of 1785, behind Claude Opus 5.5 (1800) and ahead of Muse Wonder Full (1729), Claude Fable 5.1 (1669), GPT-6 Astra (1569), and GPT-6.1 Sol (1555). At `xhigh` effort, it scored 1738 while using about 48% fewer output tokens than at `max` effort. On rubric pass rate, Fable 5.2 scored 66.1%, ahead of all other models, including Fable 5.1 (61.5%) and Opus 5.5 (61.2%). Evaluations were run independently by Artificial Analysis.

<!-- p.240 -->

#### 8.14.5 AutomationBench

![](assets/figures/p240-1.png)

:::caption
**[Figure 8.14.5.A] AutomationBench: test-time compute scaling.** Scores are from Zapier’s runs on its private AutomationBench 1.0.6 set (657 tasks per effort level), with both Claude models run with the API’s default fallbacks. Claude Fable 5.2’s scores and costs come from Zapier’s October 8, 2026 run. We calculated its cost per task from the token counts Zapier recorded, priced at Fable 5.2’s list price with prompt caching ($8/$40 per million input/output tokens, cache reads $0.20, five-minute cache writes $10). Claude Opus 5.5’s and GPT-6 Astra’s scores and costs are as published on Zapier’s leaderboard. The score axis starts at 20%.
:::

AutomationBench[^25] is a benchmark from Zapier that measures whether an agent can complete a realistic end-to-end business workflow. Tasks are derived from real customer workflow patterns across sales, marketing, operations, support, finance, and HR. The benchmark spans roughly 500 REST API endpoints across 47 apps (CRM, Slack, Google Workspace, etc.). Given a single natural-language instruction, the agent must autonomously discover the right endpoints via search; make dozens of sequential, interdependent API calls; consult and obey layered business policy documents; and avoid deliberately planted distractions. Each task is graded pass/fail, based on whether it meets all of the deterministic assertions on simulated app state (e.g., the correct CRM updates were all applied).

<!-- p.241 -->

Zapier evaluated Fable 5.2 on AutomationBench’s private held-out set, where it scored 51.4% at `max` effort. On AutomationBench’s leaderboard, which measures performance on the same set, Opus 5.5 at `max` effort scored 42.5% (the [Claude Opus 5.5 System Card](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf#page=83.26) reported 40.0%, from Zapier’s earlier run without fallbacks). Both models were run with the API’s default fallbacks. Raising the effort level took Fable 5.2 from 39.7% at `low` effort to 51.4% at `max` effort, at an estimated $1.30 to $4.64 per task at its list price.

#### 8.14.6 Real-World Finance v2

Real-World Finance v2 is an internally developed evaluation of complex, long-horizon financial analysis tasks of the kind performed by finance professionals, such as building and auditing financial models and producing client-ready work products. Two models attempt the same task, a model-based grader compares the two attempts and states which it prefers, and we report head-to-head win rates and Elo ratings derived from them. For this release, each model made one attempt at 123 tasks.

At `max` effort, Claude Fable 5.2 scored an Elo of 1637, ahead of Claude Opus 5.5 (1571) and Claude Fable 5.1 (1493). The grader preferred Fable 5.2’s work to Opus 5.5’s in 74% of comparisons and to Fable 5.1’s in 91%.

Since earlier system cards, we have moved to a new grader built on Opus 5.5 and now give models more time and context per task. On the same stored outputs from earlier models, the new grader produced Elo gaps about 2.6 times as large as the earlier grader did. We therefore divided its Elo gaps by 2.61 to keep ratings on the same scale as in earlier system cards.

<!-- p.242 -->

![](assets/figures/p242-1.png)

:::caption
**[Figure 8.14.6.A] Real-World Finance v2 Elo.** Each model made one attempt at each of 123 tasks at `max` effort, and a grader built on Opus 5.5 compared pairs of attempts at the same task. To keep ratings on the scale of earlier system cards (where Claude Sonnet 4.6 = 1000), we anchored the Bradley-Terry ratings to Claude Fable 5’s published score of 1374 and divided the grader’s Elo gaps by 2.61. This matches the scale of the earlier grader, which was built on Claude Opus 4.8. Fable 5.2 is about 66 points above Opus 5.5 (95% CI: 41 to 95). Fable 5.2 did not finish six of the 123 tasks within the three-hour limit, while Opus 5.5 completed all 123. Counting those six as Fable 5.2’s losses reduces the gap to about 43 points. Shown with 95% CI.
:::

#### 8.14.7 Remote Labor Index

[Remote Labor Index (RLI)](https://www.remotelabor.ai/), created by the Center for AI Safety and Scale AI, measures how well AI agents complete real freelance projects. It has 240 projects covering work such as game development, product design, architecture, and data analysis, most sourced from online freelance platforms. Each project includes a brief, input files, and a deliverable produced by a human professional. Human evaluators compare the agent’s deliverable with the professional’s. The automation rate is the percentage of projects for which the agent’s deliverable is judged to complete the project at least as well as the professional’s.

Claude Fable 5.2 achieved an automation rate of 41.3% (99 of 240 projects), ahead of Claude Opus 5.5 (21.3%), GPT-6 Astra (20.8%), and Claude Fable 5.1 (17.9%). Scale AI ran Claude models with the default configurations: `high` effort, a 200k-token context window, and a limit of 32k tokens per response.
[^10]: We ran GPT-6 Astra on the same 82 tasks through OpenAI’s API, using OpenAI’s own context compaction.

[^11]: Results are from Claude Mythos 5.2, Claude Mythos 5.1, and Claude Opus 5.5 without safeguards.

[^12]: Results are from Claude Mythos 5.2, Claude Mythos 5.1, and Claude Opus 5.5 without safeguards.

[^13]: Deng, X., et al. (2025). SWE-bench Pro: Can AI agents solve long-horizon software engineering tasks? arXiv:2509.16941. [https://arxiv.org/abs/2509.16941](https://arxiv.org/abs/2509.16941)

[^14]: Yang, J., et al. (2024). SWE-bench Multimodal: Do AI systems generalize to visual software domains? arXiv:2410.03859. [https://arxiv.org/abs/2410.03859](https://arxiv.org/abs/2410.03859)

[^15]: Merrill, M., et al. (2026). Terminal-Bench: Benchmarking agents on hard, realistic tasks in command line interfaces. arXiv:2601.11868. [https://arxiv.org/abs/2601.11868](https://arxiv.org/abs/2601.11868)

[^16]: Terminal-Bench-Science Team (2026). Terminal-Bench-Science: Evaluating AI agents on research workflows across scientific domains. [https://doi.org/10.5281/zenodo.22110253](https://doi.org/10.5281/zenodo.22110253)

[^17]: Proximal (2026). FrontierSWE v2. [https://www.frontierswe.com/blog/v2](https://www.frontierswe.com/blog/v2)

[^18]: Phan, L., et al. (2025). Humanity’s Last Exam. arXiv:2501.14249. [https://arxiv.org/abs/2501.14249](https://arxiv.org/abs/2501.14249)

[^19]: Zhong, J., et al. (2026). DRACO: A cross-domain benchmark for Deep Research Accuracy, Completeness, and Objectivity. arXiv:2602.11685. [https://arxiv.org/abs/2602.11685](https://arxiv.org/abs/2602.11685)

[^20]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^21]: Surge AI (2026). Chartography: A benchmark for professional chart understanding. [https://surgehq.ai/blog/chartography](https://surgehq.ai/blog/chartography)

[^22]: Surge AI (2026). Chartography. [https://github.com/surge-ai/chartography](https://github.com/surge-ai/chartography)

[^23]: BenchCAD Team (2026). BenchCAD 2.0: Benchmarking programmatic CAD on real engineering work. We use release v2.1: [https://github.com/BenchCAD-org/benchcad-2-main/releases/tag/v2.1](https://github.com/BenchCAD-org/benchcad-2-main/releases/tag/v2.1)

[^24]: Patwardhan, T., et al. (2025). GDPval: Evaluating AI model performance on real-world economically valuable tasks. arXiv:2510.04374. [https://arxiv.org/abs/2510.04374](https://arxiv.org/abs/2510.04374)

[^25]: Shepard, D., and Salimans, R. (2026). AutomationBench. arXiv:2604.18934. [https://arxiv.org/abs/2604.18934](https://arxiv.org/abs/2604.18934)

