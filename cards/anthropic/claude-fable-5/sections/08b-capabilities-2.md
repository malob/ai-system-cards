<!-- source: source.pdf pages 264-278 -->
<!-- p264-1.png (Figure 8.12.A, CritPt accuracy scores) belongs to §8.12 and is transcribed in the preceding section file. -->

### 8.13 Long context: GraphWalks

| Evaluation (F1 Score)          | Claude Mythos 5 | Claude Mythos Preview | Claude Opus 4.8 | GPT-5.5 |
| ------------------------------ | --------------- | --------------------- | --------------- | ------- |
| GraphWalks BFS 256K subset     | **91.1**        | 85.7                  | 85.9            | 73.7    |
| GraphWalks BFS 1M subset       | **79.4**        | 74.3                  | 68.1            | 45.4    |
| GraphWalks Parents 256K subset | **99.96**       | 99.9                  | 99.3            | 90.1    |
| GraphWalks Parents 1M subset   | **97.5**        | 95.5                  | 83.3            | 58.5    |

*__[Table 8.13.A] F1 scores for Claude family model results are an average over 5 trials with default sampling settings.__ GPT-5.5 was evaluated using xhigh thinking as reported in "[Introducing GPT-5.5.](https://openai.com/index/introducing-gpt-5-5/)" The best score for each evaluation is __bolded__.*

<!-- p.265 -->
GraphWalks[^45] is a multi-hop long-context reasoning benchmark: the context window is filled with a directed graph of hexadecimal-hash nodes, and the model must perform a breadth-first search (BFS) or identify parent nodes from a random starting node.

Claude Mythos 5 scored 91.1% on the BFS 256K subset and 99.96% on the parents 256k subset, averaged over 5 trials. On the same subset, Opus 4.8 scored 85.9% on BFS and 99.3% on parents. We report a 99.96% F1 score for the parents 256K subset as 4 of the runs scored 99.95% and 1 run scored 100.0% where 4 runs missed 1 node for a single common problem. 1M context subset results are not reproducible via the public API, as the problems exceed its 1M token limit. Claude Mythos 5 scored 79.4% on the BFS 1M subset and 97.5% on the parents 1M subset, averaged over 5 trials.

As with prior Claude models, our scoring corrects an ambiguity in the published F1 metric (empty ground-truth sets score 1.0 on an empty prediction rather than 0) and clarifies the BFS prompt to request nodes at exactly depth N rather than up to depth N. See the [Claude Opus 4.6 System Card](https://www.anthropic.com/claude-opus-4-6-system-card) for detail.

![Chart: GraphWalks BFS F1 scores for Claude models and GPT-5.5 on the 256K and 1M subsets](assets/figures/p265-1.png)
*__[Figure 8.13.B] Claude Mythos 5 on long context reasoning__ measured by GraphWalks BFS scores.*

<!-- p.266 -->

![Chart: GraphWalks Parents F1 scores for Claude models and GPT-5.5 on the 256K and 1M subsets](assets/figures/p266-1.png)
*__[Figure 8.13.C] Claude Mythos 5 on long context reasoning__ measured by GraphWalks Parents scores.*

### 8.14 Agentic search

#### 8.14.1 HLE

Humanity's Last Exam (HLE)[^46] is a multi-modal benchmark at the frontier of human knowledge, comprising 2,500 questions.

We tested Mythos 5 in two configurations: (1) reasoning-only without tools, and (2) with web search, web fetch, programmatic tool calling, and code execution. In all runs, thinking was set to auto and the total tokens used across contexts was capped at 1M. Context compaction was not used for these results. Claude Opus 4.6 served as the model grader. "No tools" results are not reproducible via the Public API as some problems exceed its 1 hour sampling limit.

To guard against result contamination in the tools variant, we blocklist known HLE-discussing sources for both the searcher and fetcher (see Appendix 9.2). We also use Claude Opus 4.6 to review all transcripts and flag any that appear to have retrieved answers from HLE-specific sources; confirmed cases are re-graded as incorrect.

<!-- p.267 -->

![Chart: HLE accuracy scores for Claude, Gemini, and GPT models with and without tools](assets/figures/p267-1.png)
*__[Figure 8.14.1.A] HLE accuracy scores__. Gemini and GPT model scores are taken from published results.*

![Chart: HLE scores plotted across reasoning effort levels for Claude models](assets/figures/p267-2.png)
*__[Figure 8.14.1.B] HLE scores at varying reasoning effort levels__. Each datapoint represents a single run per model up to 1M total tokens used at various effort levels.*

<!-- p.268 -->
#### 8.14.2 BrowseComp

BrowseComp[^47] tests an agent's ability to find hard-to-locate information on the open web. We ran Claude Mythos 5 and Claude Fable 5 with web search, web fetch, programmatic tool calling, and code execution. Mythos 5 scored 88.0% using adaptive thinking at maximum effort with a 10M-token limit. To extend beyond the 1M-token context window, we used context compaction, triggered at 200k tokens.

Claude Mythos 5 significantly improves over Claude Opus 4.8 in accuracy at a given cost per task, and is cheaper than Claude Mythos Preview at comparable accuracy.

![Chart: BrowseComp score versus average cost per task curves for Claude models across token budgets](assets/figures/p268-1.png)
*__[Figure 8.14.2.A] BrowseComp score versus average cost per task__ across various token budgets.*

#### 8.14.3 DeepSearchQA

DeepSearchQA[^48] is a 900-prompt benchmark for evaluating agents on difficult multi-step information-seeking tasks across 17 different fields. Its tasks require the model to conduct extensive searches to compile a list of exhaustive answers.

<!-- p.269 -->
Claude models were run with web search, web fetch, programmatic tool calling, max reasoning effort, and adaptive thinking enabled. We used a 1M token budget and did not use context compaction.

![Chart: DeepSearchQA F1 scores for Claude models](assets/figures/p269-1.png)
*__[Figure 8.14.3.A] DeepSearchQA F1 scores__.*

| Model                     | F1          | Fully Correct | Fully Incorrect | Correct w/ Excessive Answers |
| ------------------------- | ----------- | ------------- | --------------- | ---------------------------- |
| **Claude Mythos 5**       | 94.2% ±1.3% | 87.0% ±2.2%   | 3.2% ±1.2%      | 3.8% ±1.3%                   |
| **Claude Mythos Preview** | 94.4% ±1.3% | 86.9% ±2.2%   | 3.1% ±1.1%      | 4.7% ±1.4%                   |
| **Claude Opus 4.8**       | 93.1% ±1.4% | 84.8% ±2.4%   | 3.9% ±1.3%      | 4.3% ±1.3%                   |

*__[Table 8.14.3.B] DeepSearchQA results for Claude models,__ broken down by outcome category.*

**Reasoning effort**

We ran DeepSearchQA against all reasoning effort levels available for Mythos 5, Mythos Preview and Opus 4.8. We used a 1M token budget and did not use context compaction for these runs.

<!-- p.270 -->

![Chart: DeepSearchQA score versus average cost per task across reasoning-effort levels](assets/figures/p270-1.png)
*__[Figure 8.14.3.B] DeepSearchQA__ score versus average cost per task across reasoning-effort levels.*

#### 8.14.4 DRACO

Deep Research Accuracy, Completeness, and Objectivity (DRACO[^49]) is a deep research benchmark from Perplexity that aims to evaluate how well models perform at various complex research questions. DRACO consists of 100 curated tasks derived from user queries across domains from finance to medicine. The questions are graded using expert written rubrics that cover four categories: factual accuracy, breadth and depth of analysis, presentation quality, and citation quality.

We evaluated Claude models with web search, web fetch, and code execution tools with programmatic tool calling. All Claude models were evaluated with adaptive thinking at max effort and a 1M token limit. We used a task budget of 980k tokens with no compaction, given that it does not significantly help for this task. Claude Mythos 5 achieved 86.4% at max reasoning effort.

**Grading methodology**

The original DRACO paper uses Gemini-3-Pro as the primary judge model, which is no longer available. For our evaluations, we use Claude Opus 4.6 as the LLM judge to grade<!-- p.271 -->  responses against the per-task rubrics using the same binary MET/UNMET verdicts aggregated into a normalized score per the paper's Section 4.2 formula. We follow the paper's protocol of 5 independent grading runs per response and report the mean. Our judge prompt is taken from the paper's Appendix C.2. Appendix A shows judge choice can shift absolute scores by 10–25 points while preserving system ordering, so our scores are not directly comparable to the paper's headline numbers.

Aside from the change in the judge model, our only other difference from the original paper is that we instruct the model to enclose its final report in `<result>` tags and grade only that span, rather than grading the full agent transcript; this isolates the deliverable from intermediate tool output.

![Chart: DRACO score versus average cost per task across reasoning-effort levels](assets/figures/p271-1.png)
*__[Figure 8.14.4.A] DRACO__ score versus average cost per task across reasoning-effort levels.*

### 8.15 Multi-Agent

We evaluated Claude Mythos 5 in a variety of multi-agent configurations. In these setups, several instances of the model collaborate on a single task. Below, we highlight our results across two benchmarks: BrowseComp (§8.15.1) and ProgramBench (§8.15.2), and describe the harnesses we tested (§8.15.3) and the measurement methodology (§8.15.4).

<!-- p.272 -->
#### 8.15.1 Multi-Agent BrowseComp

BrowseComp[^50] tests an agent's ability to find hard-to-locate information on the open web. We ran multi-agent BrowseComp using the three harness types described in Section 8.15.3 and analyzed the results using the methodology described in Section 8.15.4. Figure 8.15.1.A and Figure 8.15.1.B present multi-agent BrowseComp results alongside single-agent ones. Here are some key findings:

![Chart: BrowseComp accuracy plotted against latency for single-agent and multi-agent configurations](assets/figures/p272-1.png)
*__[Figure 8.15.1.A] Accuracy vs. latency for BrowseComp__ across both single-agent and multi-agent configurations.*

**Multi-agent harnesses achieve the highest scores and Pareto-dominate the score-latency frontier**. Every multi-agent variant scores above the best single-agent variant, with the *async subagents* reaching our highest score of 93.3%. Latency improves alongside accuracy as agents are added: relative to the single-agent 10M-token baseline,<!-- p.273 -->  the fixed-agent team achieves speedups of 2.2×, 2.7×, and 2.7× for three, five, and ten agents respectively, with the ten-agent team also scoring +4.2pp higher than that baseline.

These gains come at the cost of tokens. Figure 8.15.1.B shows token usage rising with agent count alongside score, demonstrating that multi-agent configurations can productively absorb additional token budget by distributing work across agents. **Taken together, multi-agent harnesses offer a latency–cost trade-off**: when latency matters, fixed-agent team or async subagents can reach a given score faster, at the cost of higher token consumption.

**Among the multi-agent harnesses, the non-blocking harnesses (fixed-agent team and async-subagents) together outperform the blocking harness on both latency and token usage**. At every target accuracy, at least one of the two reaches it faster and with fewer tokens. The latency advantage comes from removing the synchronization barrier: in the blocking harness the orchestrator must wait for every dispatched subagent to return before continuing, so each round is gated by its slowest subagent, whereas the other two let agents proceed independently. The token advantage likely comes from context persistence: their agents are long-lived and retain context across the whole problem, whereas the blocking harness spawns a fresh subagent for each subtask and spends tokens re-establishing context each time.

<!-- p.274 -->

![Chart: BrowseComp accuracy plotted against total token usage for single-agent and multi-agent configurations](assets/figures/p274-1.png)
*__[Figure 8.15.1.B] Accuracy vs. total token usage for BrowseComp__ across both single-agent and multi-agent configurations. The total token usage includes both input and output tokens.*

To understand where the latency gains come from, Figure 8.15.1.C breaks the aggregate improvement down into per-problem speedups, plotted against problem difficulty. We use the average pass rate across prior Claude model runs (10 variants across 3 model families, not including Claude Mythos 5) as a difficulty proxy, and find that speedup increases with problem difficulty in both the per-problem and summed sense. On the easier problems (pass rate >= 50%), the median per-problem speedup is 0.8×, as coordination overhead roughly offsets the parallelism gain on problems that are already fast, but summed latency across the bucket still drops 2.0×, because the sum is dominated by the bucket's slowest problems, which do benefit. On the harder problems (pass rate < 50%), the median per-problem speedup rises to 1.6× and the summed latency drops 4.4×. **The overall latency improvement is therefore driven by the hard tail**. The highest-latency problems dominate the average, and those are precisely the problems on which multi-agent strategies help most.

<!-- p.275 -->

![Chart: scatter plot of per-problem multi-agent speedup versus per-problem pass rate on BrowseComp](assets/figures/p275-1.png)
*__[Figure 8.15.1.C] Per-problem speedup of the ten-agent team over a single agent with 10M-token limit, plotted against per-problem empirical pass rate on the full set of 1266 BrowseComp problems.__ The x-axis is per-problem pass rate from prior Claude model runs (10 variants across 3 model families, excluding Claude Mythos 5), used as a proxy for task difficulty. The y-axis is Claude Mythos 5 multi-agent speedup (single-agent latency divided by the ten-agent-team latency), one point per problem, colored by whether the single agent and ten-agent team answered correctly or incorrectly. The solid line is the geometric mean of the multi-agent speedup at every pass rate when the ten-agent team gets the task correct. Points are jittered for better visualization.*

#### 8.15.2 Multi-Agent ProgramBench

ProgramBench[^51] is an agentic benchmark of 200 program-reconstruction tasks. Given only a binary compiled from an open-source project and that project's documentation, the agent must rebuild a codebase that reproduces the original program's behavior without internet access or decompilation tools. Single-agent results were presented in Section 8.6 and we present the multi-agent ProgramBench results in this section.

We evaluated the fixed-agent team and async-subagents harnesses on ProgramBench against a single-agent baseline, with the same per-agent 1M-token limit. As outlined in Section 8.6, we exclude the 34 tasks whose reference binary scores below 0.9 on the<!-- p.276 -->  hidden test suite, leaving 166 "golden" tasks. We grade at a series of intermediate checkpoints and use the resulting per-task trajectories of score, latency, and tokens to construct the cumulative curves in Figures 8.15.2.A and 8.15.2.B.

![Chart: ProgramBench score versus latency curves for single-agent and multi-agent harnesses with confidence bands](assets/figures/p276-1.png)
*__[Figure 8.15.2.A] Score vs. latency for the full set of 166 "golden" ProgramBench tasks.__ Shaded regions give the 95% confidence interval, computed from score variance across the tasks.*

**Both multi-agent harnesses achieve a higher score with significant speedup, at the cost of more token usage**. From Figure 8.15.2.A, on the full golden set, the five-agent team achieves a final score +7.9pp higher than the single agent. Notably, this comes with a 3.2× speedup to reach a 60% hidden-test pass rate. Figure 8.15.2.B shows the same latency–cost trade-off described in Section 8.15.1: the score improvement and latency gain come from spending more tokens and working on the problem concurrently.

<!-- p.277 -->

![Chart: ProgramBench score versus total token usage curves for single-agent and multi-agent harnesses with confidence bands](assets/figures/p277-1.png)
*__[Figure 8.15.2.B] Score vs. tokens for the full set of 166 "golden" ProgramBench tasks.__ Shaded regions give the 95% confidence interval, computed from score variance across the tasks.*

#### 8.15.3 Multi-Agent Harnesses

We evaluated three multi-agent harnesses. All harnesses run every agent at maximum effort and share a common set of tools: web search, web fetch, and programmatic tool calling (code execution and bash) for search tasks; and the bash tool for coding tasks.

**Orchestrator with blocking subagents.** A single orchestrator coordinates the task by spawning subagents and blocking until all return. The orchestrator has no task tools of its own; its only capability is spawning subagents. Each subagent receives the full set of task tools for the benchmark. Subagents have a 200k-token context window without compaction, whereas the orchestrator uses context compaction triggered at 100k tokens with no overall token cap.

**Fixed-agent team.** A team of three, five, or ten peer agents works on the task concurrently. One agent is designated the lead and is responsible for coordination and submitting the final answer if needed, but all agents have identical tools and all see the full task description. In addition to the task tools, every agent has two messaging tools: Send<!-- p.278 -->  Message, which delivers a message to one or more teammates (inserted following the recipient's next tool result), and Wait for Message, which blocks sampling until an incoming message arrives. Every agent has the same 1M-token total limit. On ProgramBench, each agent works in its own checkout of the task repository and can share code with other agents via Git.

This harness is designed to mirror real-world settings in which multiple agents collaborate on a shared task, and reduce latency by letting peers work in parallel.

**Async subagents.** This is similar to the blocking-subagents harness, but in this variant, the lead agent can spawn asynchronous, long-lived subagents while retaining direct access to the task tools. Unlike the blocking design, spawning returns immediately with a confirmation rather than waiting on subagent execution. Each subagent sees only the instructions provided by the lead, not the original task description, and subagents can message any other agent and the lead. A subagent's final response is delivered to the lead as a message, after which the subagent idles until the lead wakes it with new instructions. Both the lead agent and the subagents operate with a 1M-token limit without compaction.

Subagents have the task tools and the same communication tools as in the fixed-agent team (namely Send Message and Wait for Message); the lead additionally has tools to create subagents, to delete subagents (freeing concurrency slots), and to check subagent status (working, idle, or terminated). For search tasks, only the lead agent's final submission is graded. For BrowseComp, there is no cap on the number of subagents that can be used; for ProgramBench, resource limits cap this harness at four concurrent subagents and 20 subagents in total.

#### 8.15.4 Evaluation Methodology

We present results that focus on comparing the delta between single- and multi-agent harnesses, including score, latency, and token usage. In particular, token usage is calculated as the total number of input and output tokens consumed across all agents on a task. Latency is reported as a derived per-task latency rather than raw wall-clock time: we divide each agent's input and output token counts by fixed reference prefill and decode rates, add measured tool-execution time, and take the critical-path latency across concurrent agents. This isolates the structural latency of the harness (e.g., how much sequential model work and tool time it requires) from serving-side variance (e.g., batching, queuing, hardware), so harnesses are compared on equal footing.

[^45]: OpenAI. (2025). Introducing GPT-4.1 in the API. [https://openai.com/index/gpt-4-1/](https://openai.com/index/gpt-4-1/)

[^46]: Phan, L., et al. (2025). Humanity's Last Exam. arXiv:2501.14249. [https://arxiv.org/abs/2501.14249](https://arxiv.org/abs/2501.14249)

[^47]: Wei, J., et al. (2025). BrowseComp: A simple yet challenging benchmark for browsing agents. arXiv:2504.12516. [https://arxiv.org/abs/2504.12516](https://arxiv.org/abs/2504.12516)

[^48]: Gupta, N., et al. (2026). DeepSearchQA: Bridging the comprehensiveness gap for deep research agents. arXiv:2601.20975. [https://arxiv.org/abs/2601.20975](https://arxiv.org/abs/2601.20975)

[^49]: Zhong, J., et al. (2026). DRACO: A cross-domain benchmark for deep research accuracy, completeness, and objectivity. arXiv:2602.11685. [https://arxiv.org/abs/2602.11685](https://arxiv.org/abs/2602.11685)

[^50]: Wei, J., et al. (2025). BrowseComp: A simple yet challenging benchmark for browsing agents. arXiv:2504.12516. [https://arxiv.org/abs/2504.12516](https://arxiv.org/abs/2504.12516)

[^51]: Yang, J., et al. (2026). ProgramBench: Can language models rebuild programs from scratch? arXiv:2605.03546. [https://arxiv.org/abs/2605.03546](https://arxiv.org/abs/2605.03546)
