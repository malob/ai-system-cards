<!-- source: source.pdf pages 174-188 -->

<!-- p.174 -->

## 8 Capabilities

### 8.1 Evaluation summary

<table><tbody>
<tr><th colspan="2" rowspan="2">Evaluation</th><th colspan="3">Claude family models</th><th>Other models</th></tr>
<tr><th>Claude Opus 5.5</th><th>Claude Opus 5</th><th>Claude Fable 5.1</th><th>GPT-6 Astra</th></tr>
<tr><th colspan="2">SWE-bench Pro</th><td><b>89.9</b></td><td>79.2</td><td>81.2</td><td>–</td></tr>
<tr><th colspan="2">SWE-bench Multilingual</th><td><u><b>93.9</b></u></td><td>89.5</td><td>89.1</td><td>-</td></tr>
<tr><th colspan="2">SWE-bench Multimodal</th><td><u><b>61.4</b></u></td><td>59.4</td><td>54.7</td><td>-</td></tr>
<tr><th colspan="2">FrontierCode v1.1 (Main)</th><td><b>54.4</b></td><td>48.0</td><td>50.3</td><td>53.3</td></tr>
<tr><th colspan="2">Terminal-Bench 4.0</th><td><b>66.4</b></td><td>52.3</td><td>55.8</td><td>57.9</td></tr>
<tr><th colspan="2">Terminal-Bench-Science 0.1</th><td>58.7</td><td>29.0</td><td>52.6</td><td><b>64.6</b></td></tr>
<tr><th rowspan="2">Humanity’s Last Exam</th><td><i><b>No tools</b></i></td><td><b>64.4</b></td><td>56.6</td><td>60.9</td><td>–</td></tr>
<tr><td><i><b>With tools</b></i></td><td><b>67.7</b></td><td>63.6</td><td>65.6</td><td>57.2</td></tr>
<tr><th colspan="2">OSWorld 2.0 (partial/strict)</th><td><b>81.8/48.7</b></td><td>74.0/37.2</td><td>80.7/42.8</td><td>–</td></tr>
<tr><th colspan="2">HealthBench Professional</th><td><b>65.6</b></td><td>59.8</td><td>62.1</td><td>63.4</td></tr>
<tr><th colspan="2">GDPval-AA v2.1</th><td><b>1846</b></td><td>1708</td><td>1735</td><td>1542</td></tr>
<tr><th colspan="2">AA-Briefcase v1.1</th><td><b>1822</b></td><td>1673</td><td>1678</td><td>1569</td></tr>
<tr><th colspan="2">AutomationBench</th><td>40.0</td><td>26.9</td><td>31.4</td><td><b>41.4</b></td></tr>
</tbody></table>

:::caption
**[Table 8.1.A] Capability evaluation summary.** Unless otherwise noted, all Claude Opus 5.5 results use the following standard configuration: adaptive thinking at `max` effort, default sampling settings (temperature, top_p), averaged over five trials. Terminal-Bench 4.0 score is reported at `xhigh` effort. Context window sizes are evaluation dependent and do not exceed 1M tokens. The best score in each row is **bolded**. Competitor figures are drawn from the respective developers’ published system cards or benchmark leaderboards. See the [Claude Opus 5 System Card](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf) for evaluation details of earlier Claude models.
:::

<!-- p.175 -->

### 8.2 SWE-bench Pro, Multilingual, and Multimodal

SWE-bench tests AI models on real-world software engineering tasks. We report three variants, where each score is an average over five trials:

- **SWE-bench Pro**[^16] is composed of problems drawn from actively maintained repositories with large, multi-file diffs. Claude Opus 5.5 achieved 89.9%.
- **SWE-bench Multilingual** extends the format to 300 problems across nine programming languages. Opus 5.5 achieved 93.9%.
- **SWE-bench Multimodal**[^17] adds visual context (screenshots and design mockups) to the issue descriptions. Opus 5.5 achieved 61.4%.

### 8.3 DeepSWE v1.1

DeepSWE is a set of 113 long-horizon software engineering tasks built to measure the capabilities of frontier coding agents. The tasks are diverse, reflect real-world complexity, and are written from scratch to avoid benchmark contamination. Claude Opus 5.5 scored an average of 74.2% over five trials.

### 8.4 FrontierCode

FrontierCode is an agentic coding benchmark of 150 software engineering tasks created by Cognition. Tasks are derived from real pull requests in open-source repositories, such as fixing websocket bugs in `aiohttp`, hardening Prisma’s browser bundle, or extending JSON schema linting rules. Each task gives the agent a checked-out repository, an issue description, and the repository's testing, lint, and style guidelines; the agent then works autonomously in a containerized environment with internet access to produce a final patch, with no human intervention and no timeout information. Patches are graded against blocking functional criteria (primarily held-out unit tests, plus scope and performance blockers) plus weighted rubric criteria, including model-graded checks for required test coverage and prohibited implementation patterns. Tasks were authored by maintainers of the underlying repositories and individually reviewed by Cognition researchers, with a random subset manually solved to verify fairness. We report FrontierCode’s overall score, a composite measure that grades each patch on blocking functional criteria (held-out unit tests) together with weighted code-quality rubric criteria, as mean@5.

<!-- p.176 -->

Note: There is a decline in model performance on FrontierCode (Main and Extended) above `medium` effort. The evaluation is designed around writing mergeable code diffs without requiring human edits, so its grading penalizes out-of-scope changes that may be unnecessary, even if they are high quality or helpful. We report the Claude Opus 5.5 scores on this benchmark without any changes to the official evaluation.

Opus 5.5 ranks first on FrontierCode (Main) with a 54.6% score (each model at its best reasoning effort), improving on Claude Opus 5 (53.4%) and leading Claude Fable 5 (53.5%), GPT-6 Astra (53.3%), and Claude Fable 5.1 (52.8%). Opus 5.5 also ranks first on FrontierCode (Extended) with a 65.3% score, improving on Claude Opus 5 (63.6%) and leading Claude Fable 5 (64.9%), GPT-6 Astra (64.5%), and Claude Fable 5.1 (63.6%). Opus 5.5’s highest FrontierCode scores—54.6% on Main and 65.3% on Extended—are at `medium` effort. Scores decline above `medium` effort but mostly recover at `max`, as the note above describes. At `max` effort, Opus 5.5 scores 54.4% on Main and 63.6% on Extended.

![](assets/figures/p176-1.png)

:::caption
**[Figure 8.4.A] FrontierCode v1.1 Main score** versus average output tokens per task across reasoning effort levels (`low`, `medium`, `high`, `xhigh`, and `max`; GPT-6 Astra also at none). Cognition ran the evaluation for every model shown and reported the results; Claude models were run in Claude Code and GPT models were run in Codex CLI. Cognition’s result files report token counts and no cost, so the x-axis shows average output tokens per task on a logarithmic scale. The result files carry no uncertainty intervals, so none are shown; Cognition's published plots report error bars. Note that the y-axis begins at 33%, not at zero, so differences between points are visually magnified.
:::

<!-- p.177 -->

![](assets/figures/p177-1.png)

:::caption
**[Figure 8.4.B] FrontierCode v1.1 Extended score** versus average output tokens per task across reasoning effort levels (`low`, `medium`, `high`, `xhigh`, and `max`; GPT-6 Astra also at none). Cognition ran the evaluation for every model shown and reported the results; Claude models were run in Claude Code and GPT models were run in Codex CLI. Cognition’s result files report token counts and no cost, so the x-axis shows average output tokens per task on a logarithmic scale. The result files carry no uncertainty intervals, so none are shown; Cognition's published plots report error bars. Note that the y-axis begins at 48%, not at zero, so differences between points are visually magnified.
:::

### 8.5 Terminal-Bench 4.0

Terminal-Bench 4.0 tests AI models on real-world work in terminal and command line containerized environments. It comprises a set of 66 tasks, with an emphasis on science-adjacent and frontier engineering problems like computational biology, physics simulation, CAD, formal proofs, and GPU performance work.

Previous Terminal-Bench versions were [very timeout- and resource-sensitive](https://www.anthropic.com/engineering/infrastructure-noise): 4.0 largely addresses these issues by increasing timeouts and adaptively bumping up both RAM and CPU in a few tasks that could benefit from it. The choice of sandboxing provider might still be a confounding factor in a few tasks, but we expect it to play a significantly smaller role than it did in previous versions. We also found that the upgrade has reduced the confounding role of various harnesses (e.g., CLI memory footprint, compaction strategy,<!-- p.178 --> and container communication protocol), ultimately making Terminal-Bench a more stable and rigorous evaluation.

Claude Opus 5.5 scored 66.36% on Terminal-Bench 4.0 with safeguards enabled; requests flagged by the safeguards were answered by a fallback model following the default server-side fallback policy (2.5% of requests, affecting 10% of trials). For comparison, Claude Mythos 5.1 scored 60.9% and Claude Fable 5.1 scored 55.8%, whereas Claude Opus 5 scored 52.3%. Scores are averaged over five trials per task (330 trials) for Opus 5.5, 10 trials per task (660 trials) for Claude Mythos 5.1, and 15 trials per task (990 trials) for Opus 5. Treating trials as independent, the standard error is ±2.6 points for Opus 5.5 and ±1.6-2 points for the other models. The numbers reported use Claude Code in `--bare` mode and `xhigh` thinking effort for Opus 5.5 (which at `max` effort scores *64.8*%, within noise of `xhigh`), and `max` effort for the comparison models.

For reference, the public leaderboard reports Claude Opus 5 at 51.8% (five trials, using the Claude Code harness), within the noise of our internal setup. OpenAI’s GPT-6 Astra reported their final Terminal-Bench 4.0 score at 57.9%, scored at `high` thinking effort (in their reporting `max` effort fared slightly lower than high, so we picked their highest number).

### 8.6 Terminal-Bench-Science 0.1

Terminal-Bench-Science is a Stanford-led community benchmark of 70 tasks drawn from scientific research workflows, authored and reviewed by scientists and researchers across the life, physical, earth, mathematical, and engineering sciences. Scientific advisors to the project are from MIT, Princeton, University of Washington, Genentech, and Stanford.

Tasks are set up as typical agentic problems: an agent CLI works in a self-contained environment from a natural language instruction and is graded against hidden, task-specific tests on the artifacts it produces.

Claude Opus 5.5 scored 58.7% on Terminal-Bench-Science with safeguards enabled; requests flagged by the safeguards were answered by a fallback model following the default server-side fallback policy (3.9% of requests, affecting 5% of trials). It averaged over 10 trials per task (700 trials). Claude Fable 5.1 scored 52.6% (10 trials per task, 700 trials), Claude Opus 5 scored 29.0% (12 trials per task, 840 trials), and Claude Fable 5 scored 24.7% (10 trials per task, 700 trials). The standard error, clustered by task, is ±3.5–4.8 points (±4.8 for Opus 5.5).

<!-- p.179 -->

The numbers reported use Claude Code in `--bare` mode and `max` thinking effort. For reference, the public leaderboard reports Claude Opus 5 at 30.0% and Claude Fable 5 at 21.4% (three trials, using the Claude Code harness), all within expected noise of our internal setup. OpenAI reported GPT-6 Astra at 64.6% with `max` thinking effort.

### 8.7 FrontierSWE v2

FrontierSWE v2[^18] is a Proximal benchmark of 34 ultra-long-horizon engineering and research tasks spanning system implementation, performance optimization, scientific computing, AI research and visual reasoning, such as porting Quantum Espresso from Fortran to Rust, building an OpenGL scene renderer that can run a flight simulator, and post-training an LLM to play an interactive puzzle game. The strongest models often work close to 20 hours per task and remain far from saturating the benchmark. Every model runs at `max` reasoning effort in Proximal’s own agent harness, with five trials per task, and the reported score is the mean across trials.

Claude Opus 5.5 scored 62.3% on FrontierSWE v2, second among the models Proximal evaluated, behind GPT-6 Astra (65.5%) and ahead of Claude Fable 5.1 (56.3%) and GPT-5.6 Sol (32.2%).

### 8.8 CursorBench 4.0

CursorBench 4.0[^19] is Cursor’s agentic coding benchmark. It is composed of coding tasks drawn from real-world Cursor usage, and executed end to end in Cursor’s production agent harness. All scores were measured and reported independently by Cursor; per-task costs for Claude Opus 5.5 are our estimates from Cursor's reported token counts at list prices, and all other costs are as published by Cursor.

Opus 5.5 scored 57.8% on CursorBench at `max` effort, 56.0% at `xhigh` and `high`, and 52.5% at `medium`. This is the highest score on Cursor’s public leaderboard, 6.0 points above Claude Fable 5.1 at `max` effort (51.8% for $17.28 per task), 11.2 points above Claude Opus 5 at `max` effort (46.6% for $11.95), and 16.1 points above GPT-5.6 Sol at `max` effort (41.7% for $8.23).

Notably, most of Opus 5.5’s performance is available well below `max` effort. At `high` effort, Opus 5.5 reaches 56.0% for about $4 per task, above every other model on the leaderboard at roughly a quarter of the cost of Claude Fable 5.1 at `max` effort. At `medium` effort it scores 52.5% for about $3 per task, still above Claude Fable 5.1 at `max` effort and at roughly a<!-- p.180 --> quarter of the cost of Claude Opus 5 at `max` effort. Costs for Opus 5.5 are estimated from the token counts Cursor reported at list prices. All other scores and costs are as published by Cursor.

Note that previous system cards reported older versions of CursorBench, so the scores are not comparable.

![](assets/figures/p180-1.png)

:::caption
**[Figure 8.8.A] CursorBench v4.0 score** versus average cost per task across reasoning effort levels. Cursor executed the evaluation end to end in its production agent harness and independently measured and reported the scores. For models other than Claude Opus 5.5, the scores and costs per task are as Cursor published them on its public leaderboard in September 2026. Opus 5.5’s scores are from a result file Cursor sent directly to us, and its cost per task is computed by us from the mean token counts in that file at list prices ($4 per million uncached input tokens, $5 per million five-minute cache-write tokens, $0.20 per million cache-read tokens, and $20 per million output tokens). Every model is shown at five reasoning effort levels (`low`, `medium`, `high`, `xhigh`, and `max`), except for Grok 4.6, which is shown at four (`low`, `medium`, `high`, and `xhigh`). Neither source includes uncertainty intervals, so none are shown. Note that the y-axis begins at 23%, not at zero, so differences between points are visually magnified.
:::

### 8.9 ArXivMath

ArXivMath is a final-answer benchmark of research-level mathematics maintained by MathArena. Problems are extracted monthly from recent arXiv papers, then filtered through automated and manual checks to ensure they are self-contained, non-trivial, and<!-- p.181 --> verifiable. Because problems are drawn from active research, the benchmark is more realistic and more closely connected to mathematical research than contest or Olympiad benchmarks.

We evaluated Claude Opus 5.5 on the latest ArXivMath release (August 2026, 57 problems). This release is constructed differently from earlier ones: MathArena now prioritizes results that resolve or refute previously stated conjectures, and 25 of the 57 problems come from such results, “formulated so that simply guessing the conjectured value gives the wrong answer.” The set therefore rewards deriving an answer over recalling the prior literature.

Opus 5.5 at max effort scored 91.2% without tools and 96.9% with tools (code execution sandbox, no internet access), averaged over four attempts per problem. For comparison, under the same setup Claude Fable 5.1 scored 82.9% without tools and 92.1% with tools, and Claude Opus 5 scored 78.1% and 90.4%, respectively. Figures 8.9.A and 8.9.B show scores across effort levels against cost per task.

MathArena’s own August leaderboard uses a different setting: each model runs in its vendor’s agentic harness with Python and SageMath, a prompt that asks for a best guess when the model cannot find a solution, two attempts per problem, and an LLM judge. Under that setting, they report GPT-6 Astra (max) at 88.6% and Claude Fable 5.1 (high) at 87.7%. These numbers are closest to our “with tools” results but are not directly comparable.

<!-- p.182 -->

![](assets/figures/p182-1.png)

:::caption
**[Figure 8.9.A] ArXivMath (August 2026) accuracy scores without tools.** Claude Opus 5.5, Claude Fable 5.1, and Claude Opus 5 were evaluated internally, without safeguards classifiers, at various effort levels.
:::

<!-- p.183 -->

![](assets/figures/p183-1.png)

:::caption
**[Figure 8.9.B] ArXivMath (August 2026) accuracy scores with tools.** Claude Opus 5.5, Claude Fable 5.1, and Claude Opus 5 were evaluated internally, without safeguards classifiers, at various effort levels.
:::

### 8.10 Long context

#### 8.10.1 ProgramBench

ProgramBench is a long-context agentic coding benchmark of 200 program reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using the internet or decompilation tools. Tasks range from small terminal utilities (jq, ripgrep) to large systems (FFmpeg, SQLite, the PHP interpreter). Submissions are graded against over 247,000 execution-based behavioral tests generated via agent-driven fuzzing.

We excluded 34 tasks for which the reference binary itself scored below 0.9 on the hidden test suite (indicating test flakiness), leaving 166 tasks. Among those tasks, we score only against tests the reference binary passes. We report the hidden test pass rate using the same mini-swe-agent harness the upstream repo uses, without the six-hour time limit. On this set, Claude Opus 5.5 scored 91.2%, whereas Claude Fable 5.1 scored 87.6% and Claude Opus 5 scored 85.4%.

<!-- p.184 -->

We believe ProgramBench is a strong measure of long-context coding performance: Opus 5.5 episodes cover a range of context lengths up to the full 1M token window, and the tasks test long-context capabilities that closely align with practical downstream use cases.

### 8.11 Agentic search

#### 8.11.1 Humanity’s Last Exam

Humanity’s Last Exam (HLE)[^20] is a multimodal benchmark comprising 2,500 questions across dozens of subjects. The questions were written and reviewed by subject-matter experts, kept only if frontier LLMs could not answer them, and designed not to be quickly answerable via internet search.

We tested Claude Opus 5.5 in two configurations: (1) reasoning-only without tools and (2) with web search, web fetch, programmatic tool calling, and code execution. In all runs, thinking was set to auto and the total tokens used across contexts was capped at 1M. Context compaction was not used for these results. Claude Opus 4.6 served as the model grader.

To guard against result contamination in the tools variant, we blocklist sources known to discuss HLE for both the searcher and fetcher (see Appendix 9.2). We also screen every correctly answered transcript with text rules for signs of HLE-specific sources and use Claude Opus 5 to review each flagged transcript. Confirmed cheating cases are re-graded as incorrect.

<!-- p.185 -->

![](assets/figures/p185-1.png)

:::caption
**[Figure 8.11.1.A] Humanity’s Last Exam (HLE, with tools) reasoning effort scaling**. Accuracy on HLE as reasoning effort scales from `low` to `max` against average cost per task (log scale). Costs are billed assuming a perfect cache hit rate and with web search fees excluded.
:::

<!-- p.186 -->

![](assets/figures/p186-1.png)

:::caption
**[Figure 8.11.1.B] Humanity’s Last Exam (HLE, no tools) test-time compute scaling**. Accuracy on HLE as reasoning effort scales from `low` to `max` against average cost per task (log scale). Costs are billed assuming a perfect cache hit rate and with web search fees excluded.
:::

#### 8.11.2 DRACO

Deep Research Accuracy, Completeness, and Objectivity (DRACO[^21]) is a deep research benchmark from Perplexity that aims to evaluate how well models perform at the types of complex research questions real users would ask. DRACO consists of 100 curated tasks derived from user queries across a variety of domains. The questions are graded using expert-written rubrics that cover four categories: factual accuracy, breadth and depth of analysis, presentation quality, and citation quality.

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution, and a 980k token task budget.

**Grading methodology**

The original DRACO paper uses Gemini 3 Pro, which is no longer available, as the primary judge model. For our evaluations, we used Claude Opus 4.6 to grade responses against the per-task rubrics using the same binary MET/UNMET verdicts aggregated into a normalized<!-- p.187 --> score, per the paper’s formula in Section 4.2. We follow the paper’s protocol of five independent grading runs per response and report the mean. Our judge prompt is taken from the paper’s [Appendix C.5](https://arxiv.org/abs/2602.11685). The paper’s Appendix A shows judge choice can shift absolute scores by 10 to 25 points while preserving system ordering, so our scores are not directly comparable to the paper’s headline numbers.

Beyond the judge model, we also used our own agent harness (no Appendix C.4 system prompt; web search, web fetch, programmatic tool calling and code execution with a 980k-token budget) and instructed the model to write its final report to a file in its execution environment and graded only that file’s contents, rather than grading the full agent transcript; this isolates the deliverable from intermediate tool output.

![](assets/figures/p187-1.png)

:::caption
**[Figure 8.11.2.A] DRACO score** versus average cost per task across reasoning effort levels. Normalized score on DRACO at a 980k task budget as reasoning effort rises from `low` to `max` against average cost per task (log scale). Costs are billed assuming a perfect cache hit rate and with web search fees excluded.
:::

#### 8.11.3 WANDR

[WANDR (Wide ANd Deep Research)](https://www.perplexity.ai/hub/blog/wandr-benchmark-evaluating-research-agents-that-must-search-wide-and-deep) is a benchmark from Perplexity that aims to provide a wide search counterpart to the DRACO deep research benchmark. It comprises 500 tasks in which the model must search for tens to hundreds of entities, find facts about each, and list these facts along with citations in structured records. We ran a modified version of this evaluation; we note the differences in methodology below.

<!-- p.188 -->

We evaluated Claude models with web search, web fetch, programmatic tool calling, code execution, and a 980k token task budget. Tasks are graded using a judge model that has access to the same web fetch tool as the student model. The grader re-fetches the cited URLs; the judge model then determines whether the references support the solution.

The primary metric is “soft F1,” which balances precision (how much of the model’s solution is verified) against recall (how much of the requested fact collection it completed). Partial credit is awarded when only some of the required facts can be verified. Results are averaged over the 500 tasks; individual entity rows that fail format validation are dropped instead of failing the entire task.

In our evals, the models were given offline web search and web fetch tools that could only access to a frozen index; Perplexity’s version uses the live web. Claude models were judged using Claude Opus 4.6, which is different from what Perplexity uses, GPT-5.4. Our prompts differed slightly as well. Since the tools and grading logic differed from Perplexity’s harness, our results are not directly comparable to reported numbers on competitor models.

![](assets/figures/p188-1.png)

:::caption
**[Figure 8.11.3.A] WANDR soft F1 score** versus average cost per task across reasoning effort levels at a 980k token task budget (log scale). Costs are billed assuming a perfect cache hit rate, with web search fees excluded.
:::
[^16]: Deng, X., et al. (2025). SWE-Bench Pro: Can AI agents solve long-horizon software engineering tasks? arXiv:2509.16941. [https://arxiv.org/abs/2509.16941](https://arxiv.org/abs/2509.16941)

[^17]: Yang, J., et al. (2024). SWE-Bench Multimodal: Do AI Systems generalize to visual software domains? arXiv:2410.03859. [https://arxiv.org/abs/2410.03859](https://arxiv.org/abs/2410.03859)

[^18]: Proximal (2026). FrontierSWE v2. [https://www.frontierswe.com/blog/v2](https://www.frontierswe.com/blog/v2)

[^19]: Cursor (2026). CursorBench. [https://cursor.com/cursorbench](https://cursor.com/cursorbench)

[^20]: Phan, L., et al. (2025). Humanity’s Last Exam. arXiv:2501.14249. [https://arxiv.org/abs/2501.14249](https://arxiv.org/abs/2501.14249)

[^21]: Zhong, J., et al. (2026). DRACO: a cross-domain benchmark for Deep Research Accuracy, Completeness, and Objectivity. arXiv:2602.11685. [https://arxiv.org/abs/2602.11685](https://arxiv.org/abs/2602.11685)

