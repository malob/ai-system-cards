<!-- source: source.pdf pages 189-221 -->

<!-- p.189 -->

### 8.12 Multi-agent

We evaluated Claude Opus 5.5’s performance in multi-agent configurations. Below, we highlight the advantages of small teams over a single agent on ProgramBench ([Section 8.12.1](#8121-multi-agent-programbench)) and DRACO ([Section 8.12.2](#8122-multi-agent-draco)), and discuss the emerging potential of large teams coordinating on more ambitious problems ([Section 8.12.3](#8123-large-agent-teams)). We also describe the multi-agent harnesses we used for these results ([Section 8.12.4](#8124-multi-agent-harnesses)) and the measurement methodology ([Section 8.12.5](#8125-evaluation-methodology)).

#### 8.12.1 Multi-agent ProgramBench

ProgramBench[^22] is an agentic benchmark of 200 program reconstruction tasks. Given only a binary compiled from an open-source project and that project’s documentation, the agent must rebuild a codebase that reproduces the original program’s behavior without using internet access or decompilation tools. We use 166 “golden” tasks, each with a reference binary that scores at least 0.9 on the hidden test suite. This is the same criterion described in [Section 8.10.1](#8101-programbench), however this task list differs from that section’s in four tasks because the lists were compiled from different runs of the reference binaries, between which a few tasks crossed the 0.9 line or failed to grade. In this section, we present the multi-agent ProgramBench results and compare them to a single agent configuration.

We compared two small-scale multi-agent harness configurations against the single-agent baseline: a fixed five-agent team and dynamically spawned async subagents (details in [Section 8.12.4](#8124-multi-agent-harnesses)). The single-agent baseline in this section uses the same task tools and grading as the multi-agent configurations, not the harness of Section 8.10.1, so its scores are not directly comparable with those reported there. Additionally, while the single-agent configuration presented in [Section 8.10.1](#8101-programbench) used a 1M token budget, here we use context compaction and a 20M token budget to ensure that the larger token expenditure of multi-agent teams does not act as a confounder.

We grade at a series of intermediate snapshots and use the resulting per-task trajectories of score, latency, and tokens to construct the cumulative curves in Figures 8.12.1.A and 8.12.1.B. Note that due to logistical challenges, this evaluation was run on an alternate, broadly comparable snapshot of Opus 5.5.

<!-- p.190 -->

![](assets/figures/p190-1.png)

:::caption
**[Figure 8.12.1.A] Score vs. latency for the 166 “golden” ProgramBench tasks.** A single point on the curve is the average fraction of hidden tests that would pass if every problem were stopped at that number of seconds. Shaded regions give the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve. This evaluation was run on an alternate, broadly comparable snapshot of Claude Opus 5.5.
:::

As Figure 8.12.1.A shows, on these tasks, both the five-agent team and async subagents show latency improvement at the same score compared to the single agent. In particular, the five-agent team achieves a 2.7x latency improvement over the single agent to reach the same score of 0.6. The async subagent curve is largely between the two, improving on the single agent but by a smaller margin than the five-agent team.

<!-- p.191 -->

![](assets/figures/p191-1.png)

:::caption
**[Figure 8.12.1.B] Score vs. tokens for the 166 “golden” ProgramBench tasks**. A single point on the curve is the average fraction of hidden tests that would pass if every problem were stopped at this amount of token usage. Shaded regions give the 95% confidence interval, computed from score variance across the tasks. The shaded band fades as problems finish their runs: the fainter the band, the fewer problems are still contributing data at that point on the curve. This evaluation was run on an alternate, broadly comparable snapshot of Claude Opus 5.5.
:::

Taken together with Figure 8.12.1.A, Figure 8.12.1.B further demonstrates the latency–cost trade-off of multi-agent harnesses: when latency matters, five-agent teams and async subagents can productively absorb additional token budget by distributing work across agents, allowing them to reach a given score faster at a higher cost.

#### 8.12.2 Multi-agent DRACO

We also evaluated small multi-agent teams on DRACO, a deep research benchmark consisting of 100 curated tasks derived from user queries across a variety of domains (more details in [Section 8.11.2](#8112-draco)). These problems consist of upfront web research followed by report generation and are of a much shorter duration than ProgramBench. Single-task latencies ranged from 13 to 71 minutes.

On shorter problems like these, we find that multi-agent teams can take longer than their single-agent counterparts to finish a task due to their coordination overhead. However, one of the values of multi-agent teams is that they speed up the delivery of work when latency<!-- p.192 --> is an important consideration. For that reason, we chose to use this dataset to examine the ways in which multi-agent teams respond to latency incentives.

We tested two different kinds of latency incentives. The first is a general latency pressure, in which we provide an instruction to Claude on the importance of time efficiency and display a cumulative elapsed time after every step. The second is a latency budget, which gives Claude a fixed time window in which to complete its work. Rather than providing an instruction, we display the budget alongside the elapsed time. We obtained time budgets by taking the single-agent latency for each task and scaling that amount by 1.0x, 0.75x, 0.5x, and 0.25x. In this way, each task gets a range of budgets that are scaled to its unique time to accomplish. Figure 8.12.2.A shows the results of this experiment.

![](assets/figures/p192-1.png)

:::caption
**[Figure 8.12.2.A] Score vs. latency for the DRACO tasks.** Multi-agent teams dominate the score–latency Pareto frontier. Each point is the mean of two runs; latency is the mean derived latency per task (see [Section 8.12.5](#8125-evaluation-methodology)).
:::

Although multi-agent teams are slower when not pressed for time, they dominate the score–latency Pareto frontier at increasingly tight time budgets. At a latency budget of 0.5x, the five-agent team is capable of more than matching single-agent performance, with a roughly 2.8x speedup. When a reasonable budget cannot be predicted up front, latency pressure also drives both multi-agent teams to complete the task earlier than the unprompted single agent.

<!-- p.193 -->

All of these runs are at `max` effort. Note that while reducing effort and tightening a latency budget can both bring down task latency, these two dials have a fundamentally different effect on multi-agent behavior. The former results in less work overall, whereas the latter preserves more of the work at a given latency by sustaining higher effective parallelism. This is true even among fixed teams, which exhibit less idleness.

For async subagents, there is a limit to this higher effective parallelism. At tighter latency budgets, the coordination and latency overhead of spawning new subagents becomes large enough that the lead spawns them at a much lower rate and prefers to act as a single agent. At the same latency where this collapse occurs, the pre-spawned five-agent team is still capable of a highly productive level of parallelism, highlighting the benefit of pre-spawned teams of agents at this latency scale.

#### 8.12.3 Large agent teams

Many high-value tasks, such as conducting scientific research, doing large-scale software engineering projects, and operating a business, may exceed what a single agent can accomplish, and instead require large teams of agents (from dozens to thousands) that decompose the work, coordinate, and communicate. To measure how well models operate in such teams, we created a new set of evaluations built around large, complex, and realistic tasks. Each task supports more than 100 agents working concurrently. We use these evaluations to measure and improve both the capability and the alignment of agents operating in large teams.

Here, we present results on two such tasks and report how Claude Opus 5.5’s performance changes as the team grows from 1 to 100 agents, with each team working for 24 hours. (The quantitative results come from a slightly different model version than the released one; performance is comparable.) The first is a knowledge base task: agents read a company’s documents and write an indexed knowledge base of notes based on them; we score the result based on how accurately a reader with access to only these notes can answer questions about the company. The second is a math formalization task: agents must prove a challenging theorem in Lean from fixed statements, with intermediate theorems’ formalizations as weighted milestones.

Opus 5.5 outperforms Claude Opus 5 and Claude Fable 5.1 on these two tasks across team sizes. Opus 5.5 outperforms both models at every team size in both tasks. For all models, scores generally rise with team size, with diminishing returns.

<!-- p.194 -->

![](assets/figures/p194-1.png)

:::caption
**[Figure 8.12.3.A] Knowledge base construction task accuracy by agent team size.** Data points represent the result attained by an agent team of the indicated scale within a 24-hour window, averaged across three distinct attempts. Performance reflects the proportion of held-out questions correctly answered by a reader relying exclusively on team-generated documentation (0–1 range).
:::

<!-- p.195 -->

![](assets/figures/p195-1.png)

:::caption
**[Figure 8.12.3.B] Lean formalization task accuracy by agent team size.** Data points represent the result attained by an agent team of the indicated scale within a 24-hour window, averaged across three distinct attempts. Performance reflects the weighted proportion of 49 formal theorem proofs successfully validated by the Lean environment (0–1 range).
:::

The differences between 10, 30, and 100 agents become more pronounced when we look inside the 24-hour window. Figure 8.12.3.C and Figure 8.12.3.D show Opus 5.5’s performance on both tasks at the two-hour, six-hour, and 24-hour marks across team sizes. Larger teams reach a given level of performance much earlier, so scaling up the team substantially reduces the time needed to complete the task even when the 24-hour scores are close.

<!-- p.196 -->

![](assets/figures/p196-1.png)

:::caption
**[Figure 8.12.3.C] Knowledge base: score within two, six, and 24 hours.** Each point is the best score a Claude Opus 5.5 team of that size had reached by that point in time, averaged over three independent 24-hour runs. The score is the fraction of held-out questions a reader answered correctly using only the team’s notes. Note that the y-axis begins at 0.3, so differences are visually magnified.
:::

<!-- p.197 -->

![](assets/figures/p197-1.png)

:::caption
**[Figure 8.12.3.D] Lean theorem proving: score within two, six, and 24 hours.** Each point is the best score a Claude Opus 5.5 team of that size had reached by that point in time, averaged over three independent 24-hour runs. The score is the weighted share of 49 theorem statements whose proofs the Lean kernel verified (0–1).
:::

We use a fixed-team harness (see [Section 8.12.4](#8124-multi-agent-harnesses)): one lead and N−1 helpers start together with the full task and work concurrently for up to 24 hours on one shared Linux machine with no network access. Each agent has a shell, a file editor, and two messaging tools (Send Message and Wait for Message). Any agent can directly message any other agent. The team’s work is kept in one shared Git repository, which is used for grading task performance. The model is instructed to use the terminal command to check for the time and plan accordingly.

We conclude the section with an interesting qualitative observation: different organizational structures emerged on the two tasks. Reading the transcripts of the 100-agent teams, we found that the Lean team organized itself into two tiers: the lead appointed a dozen sub-leads and stayed in contact with them, while each sub-lead handed out work to its own group of helpers and reported back. In contrast, the knowledge-base team remained flat: the lead divided the records among the helpers at the start of the task, each helper then owned its part of the knowledge base, and helpers communicated relatively little with one another for the rest of the run. [Figure 8.12.3.E] illustrates the two structures.

<!-- p.198 -->

![](assets/figures/p198-1.png)

:::caption
**[Figure 8.12.3.E] Emergent team structures in two 100-agent Claude Opus 5.5 teams.** The harness designated a lead for each 100-agent team, but the team structures and messaging habits of each team were determined by the agents. A sub-lead is a helper agent that becomes the main sender of messages to at least three other helpers; each helper agent is shown “reporting to” the lead or sub-lead that messaged it most. On the Lean task, 12 sub-leads emerged; on the knowledge base task, helpers mostly talked directly to the lead, and there were no sub-leads.
:::

#### 8.12.4 Multi-agent harnesses

**Fixed team**. A fixed team of peer agents work on the task concurrently. All agents have identical tools and all see the full task description. Depending on the task, one agent may be designated the lead: on DRACO, the run ends when the lead finishes, and the report as it stands then is graded. On ProgramBench, there is no lead: the agents are peers given the same prompt, the shared repository’s main branch is graded, and the run ends when every agent has finished. On both evaluations, how the work is divided is left to the agents. In addition to the task tools, every agent has two messaging tools: Send Message, which delivers a message to one or more teammates (inserted following the recipient’s next tool result), and Wait for Message, which blocks sampling until an incoming message arrives. On ProgramBench, each agent works in its own checkout of the task repository and can share code with other agents via Git. DRACO has no repository: its agents share one container’s filesystem. This harness is designed to mirror real-world settings in which multiple agents collaborate on a shared task, and to reduce latency by letting peers work in parallel.

**Async subagents**. This harness is initialized with a lead agent that can spawn asynchronous, long-lived subagents at will while retaining direct access to the task tools. The spawning tool provides immediate confirmation rather than waiting on subagent execution. Each subagent sees only the instructions provided by the lead, not the original task description. Subagents can message the lead and any other subagent that is still working. A subagent’s final response is delivered to the lead as a message, after which the<!-- p.199 --> subagent idles until the lead wakes it with new instructions. Subagents have access to the task tools and Send Message; the lead additionally has access to Wait for Message and tools to create subagents, terminate subagents, and check subagent status (working, idle, queued, or terminated). There is no cap on the number of subagents that can be spawned.

#### 8.12.5 Evaluation methodology

We focus on the comparison between single- and multi-agent harnesses, including score, latency, and token usage. In particular, token usage is counted the same way the token limits are enforced: every token that enters an agent's context window, input and output alike, is counted once per window rather than once per model request, and the counts are summed over all agents on a task. Latency is reported as a derived per-task latency rather than raw wall-clock time. We calculate the latency of each agent trajectory by dividing the agent’s input and output token counts by fixed reference prefill and decode rates and adding its measured tool execution time. We account for agent idleness by carrying clocks across hand-offs: a spawned agent starts at its spawner’s clock, and an agent that receives a message or a result moves its clock forward to the sender’s clock at the time of sending if that clock is later than its own. We report the longest agent trajectory on ProgramBench (the largest clock over all agents at each grading point) and, on DRACO, the lead agent’s final clock (the lead’s answer ends the task) as the end-to-end latency of the harness. Using derived latency isolates the latency of the harness (e.g., how much sequential model work and tool time it requires) from serving-side variance (e.g., batching, queuing, hardware), so harnesses are compared at the same model speed across time. Tool execution time is reported as measured, and so it still reflects conditions at the time of the run.

### 8.13 Multimodal

#### 8.13.1 Chartography

Chartography[^23] is a chart-understanding benchmark from Surge AI covering a set of 100 tasks on specialized chart types rarely evaluated in existing benchmarks. These include Kaplan–Meier charts, candlestick charts, contour maps, wind rose diagrams, Sankey diagrams, Bode plots, and 3D surface plots. Because different chart types can be read to different degrees of precision, each answer is graded against an acceptable range set by experts for that specific chart rather than a single fixed tolerance.

The model is configured with adaptive thinking and `max` effort enabled in all runs. It is evaluated with and without tools. When evaluated with tools, the model is provided with a<!-- p.200 --> container, with the image file and standard libraries installed, and an image cropping tool. Our internal grading implementation of Chartography matches the tasks and expert-determined acceptable answer ranges in the official repository.[^24] In order to ensure comparable grading across models, we follow the Surge AI Leaderboard in using Gemini 3.5 Flash as a grader; previous system cards showed slightly lower scores due to using Claude Sonnet 4.6 as a judge only for Claude models.

Claude Opus 5.5 achieved a score of 64.4% without tools and 89.0% with tools. Claude Fable 5.1 scored 44.8% and 88.4%, whereas Claude Opus 5 achieved scores of 29.8% and 83.4%, respectively.

![](assets/figures/p200-1.png)

:::caption
**[Figure 8.13.1.A] Chartography scores.** Claude models are evaluated with adaptive thinking and `max` effort, with and without tools. Scores are averaged over five runs. Shown with 95% CI. Gemini 3.8 Flash and GPT-5.6 Sol scores as publicly reported by Surge AI, evaluated without tools.
:::

Without tools, Claude Opus 5.5 shows step-function improvement in raw visual reasoning capabilities, outperforming Claude Fable 5.1 by a wide margin.

<!-- p.201 -->

![](assets/figures/p201-1.png)

:::caption
**[Figure 8.13.1.B] Chartography scores, without tools.** Models are evaluated with adaptive thinking at various effort levels. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

Given access to tools, Claude Opus 5.5 Pareto-dominates prior Claude models on the score–cost frontier.

<!-- p.202 -->

![](assets/figures/p202-1.png)

:::caption
**[Figure 8.13.1.C] Chartography scores, with tools.** Models are evaluated with adaptive thinking at various effort levels. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.13.2 BenchCAD

BenchCAD[^25] is a benchmark for programmatic CAD reasoning built from 17,900 execution-verified CadQuery programs spanning 106 industrial part families, roughly half of which are anchored to real ISO, DIN, EN, ASME, and IEC specification tables. The benchmark decomposes CAD capability into four matched tasks; we report results on the Vision2Code task, which requires models to generate CadQuery code from multi-view renders.

While testing Claude Opus 5.5, we observed a discrepancy in our implementation of BenchCAD Vision2Code. Our implementation had relied on pre-rendered images of CAD parts from the official HuggingFace repository,[^26] which rendered each view at 128 x 128px,<!-- p.203 --> with four views total. In contrast, the reference implementation on GitHub dynamically rendered each view at a resolution of 256 x 256 px per view, 4x the resolution we had been evaluating prior Claude models. This resulted in prior Claude models scoring significantly lower relative to other models evaluated on the same benchmark. For example, we were able to reproduce GPT-5.6 Sol no-tools scores using the 256 x 256 px-sized views and not the 128 x 128 px-sized views. We have updated our evaluation to correspond to the intended implementation; we publish updated numbers on our previous Claude models below.

The model is configured with adaptive thinking and `max` effort enabled in all runs, both with and without tools. When evaluated with tools, the model was provided with a container, with the image files and standard libraries installed, and an image cropping tool. We evaluate the model on a random 1,000-file subset of the published 17,900 Vision2Code files, which we have historically found to be indicative of scores on the full set within a 0.01 voxel IoU margin. We report voxel IoU scores averaged over five runs.

On the 1,000-file subset of BenchCAD Vision2Code, Claude Opus 5.5 achieved a voxel IoU score of 0.730 without tools and 0.962 with tools. Claude Fable 5.1 achieved scores of 0.606 and 0.926 (compared to previously reported scores of 0.437 and 0.843 when evaluated at low resolution), whereas Claude Opus 5 scored 0.497 and 0.899 (compared to previously reported scores of 0.366 and 0.821 when evaluated at low resolution).

<!-- p.204 -->

![](assets/figures/p204-1.png)

:::caption
**[Figure 8.13.2.A] BenchCAD Vision2Code subset scores.** Claude models are evaluated with adaptive thinking and `max` effort, with and without tools. Scores are averaged over five runs and shown with 95% CI. GPT-5.6 Sol and GPT-6 Astra scores as publicly reported by OpenAI.
:::

Claude’s performance on this evaluation scales substantially with test-time compute, particularly when the models are equipped with tools that enable visual verification of intermediate outputs. Indeed, when provided with tools, Claude Opus 5.5 nearly achieves a perfect voxel IoU score on the benchmark.

<!-- p.205 -->

![](assets/figures/p205-1.png)

:::caption
**[Figure 8.13.2.B] BenchCAD Vision2Code subset scores, with tools.** Models are evaluated with adaptive thinking at various effort levels We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.13.3 OSWorld 2.0

OSWorld 2.0[^27] is a benchmark of 108 long-horizon computer use tasks in which an agent operates a live Ubuntu virtual machine via screenshots and mouse and keyboard actions. Each task is graded against a set of weighted checkpoints. We report two metrics: the partial score (mean per-task credit across checkpoints) and the strict pass rate (the fraction of tasks with every checkpoint satisfied), each as pass@1 averaged over five independent runs. We used the benchmark's default settings of 1080p resolution and a maximum of 500 action steps per task at maximum reasoning effort. For tasks that require a model grader, we used Claude Opus 4.8.

Since the [Claude Fable 5.1 and Claude Mythos 5.1 System Card](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf), we have updated this evaluation in two ways. First, we updated to the September 10, 2026 versions of the<!-- p.206 --> benchmark’s task files, task assets, and companion web applications. Second, we changed how the agent harness manages context: instead of discarding older screenshots once a fixed number had accumulated, the agent now retains every screenshot and uses the Claude API’s server-side context management, which compacts the conversation once it exceeds 100k tokens. All models in this section were evaluated under the same updated configuration.

Claude Opus 5.5 achieved a partial score of 81.8% and a strict pass rate of 48.7%. Re-evaluated under the same conditions, Claude Fable 5.1 scored 80.7% partial and 42.8% strict pass, and Claude Opus 5 scored 74.0% partial and 37.2% strict pass. Because both the task files and the harness configuration differ, these results supersede the OSWorld 2.0 figures in the Claude Fable 5.1 and Claude Mythos 5.1 System Card and are not directly comparable to results reported on earlier releases of the benchmark or obtained with other harness configurations.

![](assets/figures/p206-1.png)

:::caption
**[Figure 8.13.3.A] OSWorld 2.0 scores across models.** Bars show the partial score and strict pass rate at `max` effort, with 95% confidence intervals over five runs.
:::

<!-- p.207 -->

![](assets/figures/p207-1.png)

:::caption
**[Figure 8.13.3.B] OSWorld 2.0 price versus performance for Claude Opus 5.5, Claude Opus 5, and Claude Fable 5.1.** Each point is one reasoning effort setting (levels differ by model), placed at its mean cost per task at API list prices for input, output, and prompt caching. Scores are partial-credit scores from the OSWorld 2.0 graders, averaged over five runs.
:::

<!-- p.208 -->

![](assets/figures/p208-1.png)

:::caption
**[Figure 8.13.3.C] OSWorld 2.0 price versus strict pass rate for Claude Opus 5.5, Claude Opus 5, and Claude Fable 5.1.** Each point is one reasoning effort setting (levels differ by model), placed at its mean cost per task at API list prices for input, output, and prompt caching. Strict pass rate counts a task only when every checkpoint is satisfied, averaged over five runs.
:::

### 8.14 Real-world professional tasks

#### 8.14.1 OfficeQA

OfficeQA is a public benchmark from Databricks that evaluates end-to-end grounded reasoning over a large corpus of historical U.S. Treasury Bulletin documents. Models must locate relevant tables across the corpus and perform precise numerical reasoning over them. We evaluate agentically, with documents provided as extracted text in a sandboxed environment and code execution tools available; OfficeQA Pro is the harder 133-question subset recommended for frontier models.

Claude Opus 5.5 achieved 78.9% on OfficeQA and 67.7% on OfficeQA Pro (`max` effort, mean of five runs). This is slightly above Claude Opus 5, which achieved 78.1% and 66.9%, and below Claude Fable 5.1, which achieved 80.2% and 69.0%.

<!-- p.209 -->

#### 8.14.2 Legal Agent Benchmark

Legal Agent Benchmark (LAB) is an open-source benchmark created by [Harvey AI](https://www.harvey.ai/). The benchmark consists of 2,010+ tasks across 27 distinct practice areas. Each task contains a closed universe of documents, which include email communication, firm templates, procedural files, and other client matter materials the agent must sift through in order to accomplish the task. The task instructions are written as a minimal “request for work” from a partner to an associate. The task instructions also stipulate the expected output document and format. Evaluation is conducted pass/fail using an LLM as a judge across a suite of expert-written rubric criteria (criteria per evaluated task: min=23, median=56, max=194). Standard LAB reporting considers the task a success only if all criteria are met.

In addition to the public tasks, Harvey maintains a held-out set of 120 problems that is not publicly released. Reporting on this held-out set for Harvey LAB is conducted independently by [Artificial Analysis](https://artificialanalysis.ai/evaluations/harvey-lab-aa) on a harness maintained by the Artificial Analysis team ([more on their methodology here](https://artificialanalysis.ai/methodology/intelligence-benchmarking#harvey-lab-aa)).

Claude Opus 5.5 achieved an 8.3% all-pass rate and a 91.2% mean criterion-pass rate on the held-out set at `max` effort. As in our previous system card, scores for earlier models are those measured by Artificial Analysis and not those reported by Harvey so that every model is compared on the same harness. As such, the scores may differ slightly from those in system cards published before that change.

#### 8.14.3 GDPval-AA

GDPval-AA v2.1, developed by [Artificial Analysis](https://artificialanalysis.ai/), is an independent evaluation framework that tests AI models on economically valuable, real-world professional tasks. The benchmark uses 220 tasks from OpenAI’s [GDPval gold database](https://huggingface.co/datasets/openai/gdpval)[^28] spanning 44 occupations across nine major industries. Tasks mirror actual professional work products, including documents, slides, diagrams, and spreadsheets. Models are given shell access and web browsing capabilities in an agentic loop to solve tasks, and performance is measured via Elo ratings derived from blind pairwise comparisons of model outputs, anchored to DeepSeek V4.1 Flash (max) at 1,600.

Claude Opus 5.5 holds the top two leaderboard spots, with Elo 1846 at `max` effort and 1820 at `xhigh` effort, ahead of Claude Fable 5.1 at `max` (1735) and Claude Opus 5 at `max` (1708), as well as all non-Claude models. `xhigh` achieves similar performance as max while using about 51% fewer output tokens. Evaluations were run independently by Artificial Analysis.

<!-- p.210 -->

#### 8.14.4 AA-Briefcase

[AA-Briefcase](https://artificialanalysis.ai/articles/aa-briefcase) v1.1, developed by Artificial Analysis, is a new benchmark for long-horizon knowledge work on complex projects built by industry experts. Models work through multi-week projects with many linked tasks and thousands of input source files; grading combines rubric scoring and pairwise judging via a panel of frontier models to measure verifiable task success, analytical quality, and presentation quality.

Claude Opus 5.5 holds the top three leaderboard spots, with Elo 1822 at `max` effort, 1780 at `xhigh` effort, and 1705 at `high` effort, ahead of Claude Fable 5.1 at `max` (1678) and Claude Opus 5 at `max` (1673). It leads Claude Fable 5.1 on both analytical quality Elo and presentation Elo. `xhigh` achieves similar performance as `max` while using about 41% fewer output tokens. Evaluations were run independently by Artificial Analysis.

#### 8.14.5 Toolathlon Verified

Toolathlon is an agentic benchmark of 108 real-world tool use tasks spanning office productivity, ecommerce and operations, data analysis, and web research. The tasks start in apps that are prefilled with realistic data and are graded by execution-based checkers that verify both the resulting artifacts and changes in the related apps or websites. The benchmark exposes more than 600 tools across 32 applications. Tasks require correct tool selection, multi-step sequencing, and checker-exact outputs over long horizons; the trajectories in our runs averaged roughly 20–27 assistant turns. We evaluate against Toolathlon-Verified, the authors’ final release (June 2026), in which task prompts, ground truth, and evaluators were human-reviewed and finalized, with reference trajectories for eight models published for external validation.

Claude Opus 5.5 achieved 77.8% Pass@1. Of 324 trials, one trial (0.3%) was stopped by production safety classifiers and six (1.9%) were halted by our evaluation harness's sandbox-escape monitor, and all seven are counted as failures. Following the paper’s protocol, we report Pass@1 averaged over three trials across all 108 tasks, alongside Pass@3 (at least one of three trials correct), Pass³ (all three trials correct), and the average number of assistant turns per trajectory.

<!-- p.211 -->

<table><tbody>
<tr><th>Model</th><th>Pass@1</th><th>Pass@3</th><th>Pass³</th><th>Avg. turns</th></tr>
<tr><td><b>Claude Opus 5.5</b></td><td>77.8</td><td>82.4</td><td>72.2</td><td>26.9</td></tr>
<tr><td><b>Claude Fable 5.1</b></td><td>77.8</td><td>81.5</td><td>73.1</td><td>23.7</td></tr>
<tr><td><b>Claude Opus 5</b></td><td>80.6</td><td>87.0</td><td>73.1</td><td>23.5</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td>79.3</td><td>86.1</td><td>73.1</td><td>19.8</td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>79.9</td><td>88.0</td><td>71.3</td><td>20.4</td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>74.7</td><td>84.3</td><td>65.7</td><td>24.5</td></tr>
</tbody></table>

:::caption
**[Table 8.14.5.A] Toolathlon scores (internal harness).** Models are evaluated with adaptive thinking and `max` effort; Claude Opus 5.5 and Claude Fable 5.1 were run with safety classifiers. Pass@1, Pass@3, and Pass³ are computed over all 108 tasks across three trials, per the paper’s protocol.
:::

Our harness mirrors the Toolathlon-Verified task definitions, prompts, and execution-based checkers with a small number of environment-specific setup patches, which we validated by re-running two of the reference models (Claude Sonnet 5 and Claude Opus 4.8) in our harness and matching the authors published results. To control live dependency drift, we pin financial data feeds to a snapshot recorded at run time and pin container images. A small number of upstream checker defects (e.g., ground truth referencing a since-renamed repository) are left unchanged.

A note on comparability to the published leaderboard: our Claude Sonnet 5 and Claude Opus 4.8 figures are roughly three points higher than those on the published leaderboard (71.6% and 76.2%, respectively). Most of this gap comes from null attempts—runs in which the authors’ harness produced no trajectory (8 of 324 for Claude Sonnet 5; 11 of 324 for Claude Opus 4.8). The leaderboard counts these as failures; excluding them, our figures match the authors’ published reference trajectories within run-to-run noise.

#### 8.14.6 AutomationBench

AutomationBench[^29] is a benchmark from Zapier that measures whether an agent can complete a realistic end-to-end business workflow. Tasks are derived from real customer workflow patterns across sales, marketing, operations, support, finance, and HR. Each task places the agent inside a simulated company, with dozens of REST API endpoints spanning 47 apps (CRM, Slack, Google Workspace, etc.). The agent is given a single natural language instruction. It must then autonomously discover the right endpoints via search; make<!-- p.212 --> dozens of sequential, interdependent API calls; consult and obey layered business policy documents; and correctly avoid deliberately planted distractions. Grading is pass/fail for each task and is based on meeting all of the deterministic assertions on simulated app state (e.g., the correct CRM updates were all applied).

On AutomationBench’s leaderboard, which measures performance on a private held-out evaluation set, Claude Opus 5.5 at `max` effort scored 40.0%, a substantial gain over Claude Fable 5.1 at `max` effort at 31.4%, and Claude Opus 5 at 26.9%.

![](assets/figures/p212-1.png)

:::caption
**[Figure 8.14.6.A] AutomationBench task-cost scores.** Claude Opus 5.5 outperforms Claude Opus 5 across effort levels. Claude Opus 5.5’s cost per task is Anthropic's calculation from Zapier's recorded token counts at list prices with prompt caching. Other models' costs, including Claude Opus 5, are as published on Zapier's AutomationBench leaderboard (release 1.0.6).
:::

### 8.15 Healthcare

We evaluated Claude Opus 5.5 on two healthcare benchmarks, HealthBench[^30] and HealthBench Professional,[^31] to assess performance on a variety of healthcare tasks.

<!-- p.213 -->

HealthBench is an open-source evaluation developed to assess safety, accuracy, and communication across realistic healthcare contexts. The benchmark uses over 48,000 expert-written rubric items to grade 5,000 single- and multi-turn patient and clinician conversations. HealthBench Professional is a clinical task benchmark composed of 525 physician-authored conversations spanning clinical consults, documentation, and research tasks. Each is graded against rubric criteria by an LLM-as-a-judge model.

#### 8.15.1 HealthBench results

On HealthBench, Claude Opus 5.5 achieved a raw score of 68.1%, ahead of Claude Fable 5.1 at 66.7%, Claude Sonnet 5 at 59.2%, and Claude Opus 5 at 67.1%. After length adjustment, which penalizes verbose model responses, Claude Opus 5.5 achieved a score of 60.6%.

![](assets/figures/p213-1.png)

:::caption
**[Figure 8.15.1.A] HealthBench raw and length-adjusted scores**. All Claude models used adaptive thinking and `max` effort. Claude Opus 4.8 was used as the grader model. Claude Opus 5.5 was run with safety classifiers enabled and a refusal fallback to Claude Opus 5. Scores were averaged over five trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in OpenAI’s GPT-5.5 System Card. Shown with 95% CI.
:::

#### 8.15.2 HealthBench Professional results

On HealthBench Professional, Claude Opus 5.5 achieved a raw score of 77.1%, ahead of Claude Opus 5 at 73.4%, Claude Fable 5.1 at 74.2%, and Claude Sonnet 5 at 62.4%. After<!-- p.214 --> length adjustment, which penalizes verbose model responses, Claude Opus 5.5 achieved a score of 65.6%.

![](assets/figures/p214-1.png)

:::caption
**[Figure 8.15.2.A] HealthBench Professional raw and length-adjusted scores**. All Claude models used adaptive thinking at `max` effort. Claude Opus 4.8 was the grader model. Claude Opus 5.5 was run with safety classifiers enabled and a refusal fallback to Claude Opus 5. Scores were averaged over five trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in the HealthBench Professional paper. Shown with 95% CI.
:::

### 8.16 Multilingual performance

We evaluated Claude Opus 5.5 on two multilingual benchmarks, Global MMLU (GMMLU) and Multi-task Indic Language Understanding Benchmark (MILU),[^32] to assess performance across a range of languages.

GMMLU extends the standard MMLU evaluation across 42 languages, from high-resource languages such as French and German to low-resource languages such as Yoruba, Igbo, and Chichewa. MILU covers 11 languages—10 Indic languages (Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu) and English—and tests culturally grounded knowledge comprehension.

<!-- p.215 -->

#### 8.16.1 GMMLU results

On GMMLU, Claude Opus 5.5 achieved an average accuracy of 94.3% across 42 languages, ahead of Claude Fable 5.1 at 94.0%, Claude Opus 5 at 92.5%, and Claude Sonnet 5 at 89.2%.

![](assets/figures/p215-1.png)

:::caption
**[Figure 8.16.1.A] GMMLU average accuracy.** All Claude models used adaptive thinking at `max` effort. Scores were reported for a single trial. No tools or customized system prompts were provided to any model.
:::

#### 8.16.2 MILU results

On MILU, Claude Opus 5.5 achieved an average accuracy of 93.1% across 11 languages, ahead of Claude Fable 5.1 at 93.0%, Claude Opus 5 at 92.1%, and Claude Sonnet 5 at 89.3%.

<!-- p.216 -->

![](assets/figures/p216-1.png)

:::caption
**[Figure 8.16.2.A] MILU average accuracy.** All Claude models used adaptive thinking at `max` effort. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model.
:::

### 8.17 Life sciences capabilities

We continue to report evaluations in bioinformatics, protein science and design, and laboratory protocol troubleshooting, and add new evaluations of cell-based assay and biomedical image analysis, de novo protein binder design, and medicinal chemistry. These evaluations, many of which were developed internally by domain experts or with external partners, focus on capabilities that support beneficial applications in basic research and drug development, complementing our CB risk assessments, which focus on the potential for misuse.

Although many of these evaluations are not publicly released, we briefly describe each one below. Unless otherwise noted, each Claude score is the average over five attempts per problem (one attempt per problem for protein sequence generation and for biomedical image analysis, three for protein design library ranking, and five independent runs per target for binder design), sampled with adaptive thinking at `max` effort. When available, we also report scores for GPT‑6 Astra, run through the OpenAI API at `max` reasoning effort; attempts declined by OpenAI's safety system are excluded from the score. All GPT‑6 Astra evaluations were run with the same or more permissive network access configurations as our evaluations of Claude.

<!-- p.217 -->

#### 8.17.1 BioMysteryBench

BioMysteryBench assesses a model’s ability to solve difficult analytical challenges that require interleaving computational analysis with biological reasoning. Given experimental datasets, the model must answer questions such as identifying a knocked-out gene from transcriptomic data or determining which virus infected a sample. We report two subsets: Human Solvable, the 73 problems that independent human experts solved, and Human Difficult, the 17 problems that remain unsolved by humans but have an objective, ground-truth answer. Claude has access to a bash tool for code execution, a file editor, and a prespecified set of installed packages; it can install further packages only from an internal repository and can reach only a small allow-list of domains.

In the Human Solvable subset, Claude Opus 5.5 achieved 89.3%, on par with Claude Opus 5 at 91.4% and Claude Mythos 5.1 at 90.3%, and ahead of Claude Sonnet 5 at 84.9%. On the Human Difficult subset, Claude Opus 5 led at 51.8%, followed by Claude Opus 5.5 at 50.0%, Claude Mythos 5.1 at 44.1%, and Claude Sonnet 5 at 39.4%.

#### 8.17.2 LatchBio Bioinformatics

Developed by LatchBio, this set of evaluations assesses a model’s ability to solve challenging real-world bioinformatics problems. The SpatialBench Verified variant tests analysis of spatial transcriptomics data across a set of 115 externally validated problems, requiring the model to answer biological questions about the sample from the results. The SingleCellBench variant tests analysis of single-cell RNA sequencing data across 195 problems spanning standard workflows such as labeling cell types, finding differentially expressed genes, and correcting batch effects. For both variants, Claude has access to a bash tool for code execution, a file editor, and a prespecified set of installed packages.

On SpatialBench Verified, Claude Mythos 5.1 remains the strongest model at 77.6%, followed by Claude Opus 5.5 at 72.0%, Claude Opus 5 at 71.7%, and Claude Sonnet 5 at 68.9%. On SingleCellBench, Claude Mythos 5.1 at 61.8%, Claude Opus 5.5 at 61.2% and Claude Opus 5 at 60.5% were level, ahead of Claude Sonnet 5 at 56.5%.

#### 8.17.3 Morphology-to-molecule matching

Developed with Axiom Bio, this new benchmark assesses whether a model can match four sets of multi-channel cell imaging data from Axiom’s human liver in-vitro assay to the four shuffled molecule-dose perturbations that treated the wells in each image set. Claude works in a closed sandbox with a bash tool for code execution, a file editor, and a<!-- p.218 --> prespecified set of installed packages; it cannot install further packages and has no network access.

Claude Opus 5.5 achieved 34.0%, ahead of Claude Mythos 5.1 at 25.8%, Claude Opus 5 at 25.0%, and Claude Sonnet 5 at 6.8%. GPT‑6 Astra scored 22.8%.

#### 8.17.4 Medicinal chemistry

This benchmark assesses whether a model can reason about absorption, distribution, and metabolism (ADME)-related properties of drug-like molecules. Each of the 504 questions presents several real compounds from drug discovery programs as chemical structures and asks which candidate had the highest or lowest measured value of one such property. Claude is given a set of reference values and answers without tools; the score is based on accuracy over five attempts per question.

Claude Opus 5.5 achieved 63.5%, ahead of Claude Opus 5 at 57.9%, Claude Mythos 5.1 at 57.7%, GPT‑6 Astra at 56.6%, and Claude Sonnet 5 at 41.3%.

#### 8.17.5 Protein design

These benchmarks assess Claude’s protein design abilities. The Sequence Generation task assesses Claude’s ability to generate novel protein sequences conditioned on a variety of design constraints, such as natural-language descriptions of a given protein family, knot topology, globularity, and structural motifs for enzyme active sites and binding pockets, across 336 design briefs. Claude answers each brief directly, without access to tools. Each design is scored by constraint satisfaction, protein folding confidence, and sequence novelty.

Claude Opus 5.5 achieved 60.2%, ahead of Claude Mythos 5.1 at 46.0%, Claude Opus 5 at 42.4%, and Claude Sonnet 5 at 20.2%.

The Library Ranking task assesses Claude’s ability to prioritize protein designs for experimental testing. Each of the 83 problems gives Claude the sequences of a design library annotated with wet-lab measurements from a real protein engineering campaign, together with a selection objective, and asks it to rank a held-out set of sequences from the same campaign. Claude answers each problem directly, without access to tools. Rankings are scored by chance-normalized average precision (0 for a random ranking, 1 for a perfect one) against the designs that meet the objective in the measured outcomes.

<!-- p.219 -->

Claude Mythos 5.1 at 56.9% and Claude Opus 5.5 at 56.0% were level, followed by Claude Opus 5 at 53.5% and Claude Sonnet 5 at 44.0%. Note that these Library Ranking scores are not comparable with those in the [Claude Mythos 5.1 System Card](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf): we have since revised the problem set and grader, and all models were re-run on the current 83-problem version.

#### 8.17.6 De novo protein binder design

This new benchmark assesses whether Claude can carry out an extended protein design campaign on its own. For each of 15 protein targets, Claude is given the target’s structure and a fixed budget of 24 hours of wall-clock time in a sandbox equipped with a GPU, a bash tool and file editor, and a suite of protein design and structure prediction tools, with no internet access, and must design and submit a set of 30 miniprotein binders against the target. The protein targets are described in [this blog post](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling); we excluded Cas9 from this evaluation. Submitted designs are re-folded in complex with the target by a panel of structure predictors and scored on predicted interface confidence and agreement between the designed and re-predicted binding pose. We include a penalty for sets of designs that are not structurally diverse. The score for a target is the mean over five independent runs, and the reported number is the mean over the 15 targets.

Claude Opus 5.5 achieved 82.6%, compared with Claude Mythos 5.1 at 79.1%, Claude Opus 5 at 78.9%, and Claude Sonnet 5 at 72.6%. Target by target, Claude Opus 5.5 scored higher than Claude Opus 5 and Claude Sonnet 5 on all 15 targets, and higher than Claude Mythos 5.1 on 14 of 15.

#### 8.17.7 Biomedical image analysis

This new benchmark assesses a model’s ability to carry out quantitative analyses of biomedical images using data from public biomedical image analysis competitions. Each of the 91 problems is a case from one of 31 tasks drawn from such competitions, spanning segmentation, detection, measurement, classification, registration, reconstruction and tracking on CT, MRI, histopathology, dermoscopy, retinal, ultrasound, microscopy, and other imaging, and asks the model to produce the task’s required output for that case (for example, a segmentation mask or a measurement). Claude works in a sandbox with a bash tool, a file editor, and a standard set of classical image analysis packages, without pretrained models or internet access. Each case is scored with its task’s own official metric or a chosen component if the competition is graded by multiple metrics. We also normalize each metric so that baseline performance is 0% and the best published competition result is 100%.

<!-- p.220 -->

GPT‑6 Astra led at 77.5%, followed by Claude Opus 5.5 at 71.4%, Claude Mythos 5.1 at 67.1%, Claude Opus 5 at 61.0%, and Claude Sonnet 5 at 42.3%.

#### 8.17.8 Protocols

This assessment looks at models’ ability to assist with molecular biology protocols, including by using web search tools to find additional details about protocols online. The Troubleshooting variant (206 problems) assesses Claude’s ability to detect and fix errors in protocols. The Understanding (V2) variant (119 problems), a new held-out set created by Benchling, gives Claude a real laboratory protocol (such as a protocols.io document, vendor manual, or core facility guide) and a practical question about applying or adapting it, with answers graded against a rubric. For both variants, Claude has access to bash, file editor, and web search tools.

For the Troubleshooting variant, Claude Opus 5.5 led at 73.7%, ahead of Claude Mythos 5.1 at 70.2% and Claude Opus 5 at 68.9%, followed by GPT‑6 Astra at 66.0% and Claude Sonnet 5 at 49.9%. Note that the Claude Opus 5 and Claude Sonnet 5 Troubleshooting scores differ from those reported in earlier system cards: both models were re-run on the current evaluation configuration, in which we removed external network access from the task environment (web search remains available through the search tool).

For the Understanding (V2) variant, Claude Opus 5 scored highest at 71.8%, with Claude Mythos 5.1 (69.6%) and Claude Opus 5.5 (69.0%) close behind, ahead of GPT‑6 Astra (61.9%) and Claude Sonnet 5 (58.9%).

<!-- p.221 -->

![](assets/figures/p221-1.png)

:::caption
**[Figure 8.17.8.A] Life science benchmarks.** Performance of Claude Opus 5.5 and comparison models across the benchmarks shown; per-benchmark results are discussed in the sections above.
:::
[^22]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)

[^23]: Surge AI (2026). Chartography: A benchmark for professional chart understanding. Surge AI. [https://surgehq.ai/blog/chartography](https://surgehq.ai/blog/chartography)

[^24]: Surge AI (2026). Chartography [Code repository]. GitHub. [https://github.com/surge-ai/chartography](https://github.com/surge-ai/chartography)

[^25]: Zhang, H., et al. (2026). BenchCAD: A comprehensive, industry-standard benchmark for programmatic CAD. arXiv:2605.10865. [https://arxiv.org/abs/2605.10865](https://arxiv.org/abs/2605.10865)

[^26]: [https://huggingface.co/datasets/BenchCAD/BenchCAD](https://huggingface.co/datasets/BenchCAD/BenchCAD)

[^27]: Yuan, M., et al. (2026). OSWorld 2.0: Benchmarking computer use agents on long-horizon real-world tasks. arXiv:2606.29537. [https://arxiv.org/abs/2606.29537](https://arxiv.org/abs/2606.29537)

[^28]: Patwardhan, T., et al. (2025). GDPval: Evaluating AI model performance on real-world economically valuable tasks. arXiv:2510.04374. [https://arxiv.org/abs/2510.04374](https://arxiv.org/abs/2510.04374)

[^29]: Shepard, D., and Salimans, R. (2026). AutomationBench. arXiv:2604.18934. [https://arxiv.org/abs/2604.18934](https://arxiv.org/abs/2604.18934)

[^30]: Arora, R. K., et al. (2025). HealthBench: Evaluating large language models towards improved human health. arXiv:2505.08775. [https://arxiv.org/abs/2505.08775](https://arxiv.org/abs/2505.08775)

[^31]: Soskin Hicks, R., et al. (2026). HealthBench Professional: Evaluating large language models on real clinician chats. arXiv:2604.27470. [https://arxiv.org/abs/2604.27470](https://arxiv.org/abs/2604.27470)

[^32]: Verma, S., et al. (2024). MILU: A multi-task Indic language understanding benchmark. arXiv:2411.02538. [https://arxiv.org/abs/2411.02538](https://arxiv.org/abs/2411.02538)

