<!-- source: source.pdf pages 291-308 -->
<!-- p291-1.png ([Figure 8.16.9.A] ScreenSpot-Pro scores) belongs to Section 8.16.9 and is placed in the preceding section file. -->

### 8.17 Real-world professional tasks

#### 8.17.1 OfficeQA

OfficeQA is a public benchmark from Databricks that evaluates end-to-end grounded reasoning over a large corpus of historical U.S. Treasury Bulletin documents: models must locate relevant tables across the corpus and perform precise numerical reasoning over them. We evaluate agentically, with the relevant documents pre-selected and provided as extracted text in a sandboxed environment; OfficeQA Pro is the harder 133-question subset recommended for frontier models.

Using our internal agentic harness, Claude Mythos 5 achieved 79% on OfficeQA and 67.1% on OfficeQA Pro (exact-match grading, mean of five trials, evaluated in the production serving configuration including safeguards classifiers), comparable to Claude Opus 4.8 (77.6% and 66.2% under the same harness and grading).

On Databricks' own evaluation of OfficeQA Pro, which differs from ours in that documents are read as images using the model's vision rather than as extracted text, Claude Fable 5 achieved a state-of-the-art 57.9%, ahead of GPT-5.5 (52.6%) and Claude Opus 4.8 (48.1%).

<!-- p.292 -->

#### 8.17.2 Finance Agent

Finance Agent is a public benchmark published by Vals AI that assesses a model's performance on agentic financial-research tasks, including research over the SEC filings of public companies. Vals AI conducted an evaluation of Fable on this benchmark (using adaptive thinking and max effort) and found that it achieved a score of 56.31% on Finance Agent Benchmark v2, which is above Claude Opus 4.8 and GPT-5.5 which are 53.92% and 51.76% respectively, and second to Gemini 3.5 Flash.

#### 8.17.3 Real-World Finance

##### 8.17.3.1 Real-World Finance v2

Real-World Finance v2 is an internally developed evaluation that assesses a model's ability to complete complex, long-horizon financial-analysis tasks of the kind performed by finance professionals—for example, building and auditing financial models, valuation analyses, and producing client-ready work products from realistic input materials. The suite comprises 294 complex, realistic tasks representative of the day-to-day work of finance professionals.

Because these tasks have open-ended deliverables rather than single correct answers, we evaluate them as pairwise comparisons: two models attempt the same task, and a model-based grader expresses a preference between the two work products. We report head-to-head win rates (and Elo derived from them), an approach similar to other published evaluations of professional work products. A further advantage of this preference-based approach is that we can improve the task distribution and pairwise comparators in future releases while continuing to report win rates and Elo on a consistent basis over time.

Across 2,491 pairwise grades on the 294-task suite, with ties excluded and a model-based grader (Claude Opus 4.8) expressing each preference, Fable/Mythos 5 was preferred over Claude Sonnet 4.6 in 90% of comparisons, over Claude Opus 4.8 in 74%, and over Claude Mythos Preview in 64%. As consistency checks on the grader, Claude Mythos Preview was preferred over Claude Sonnet 4.6 in 88% of comparisons and over Claude Opus 4.8 in 65%, and Claude Opus 4.8 over Claude Sonnet 4.6 in 82%—all in line with the expected capability ordering. Elo ratings are a Bradley–Terry maximum-likelihood fit on the same pairwise wins, with Claude Sonnet 4.6 fixed at 1,000 and the standard 400-point = 10:1 odds scale—an anchoring we will hold fixed in future releases so that scores remain comparable as the evaluation evolves. On this scale, Fable/Mythos 5 rates 1,374, Claude Mythos Preview 1,307, and Claude Opus 4.8 1,222.


<!-- p.293 -->

![Chart: Real-World Finance v2 — two panels showing win rates vs each comparison model with ties excluded (90% vs Claude Sonnet 4.6, 64% vs Claude Mythos Preview, 74% vs Claude Opus 4.8, with a 50% parity line) and Elo ratings on the same comparisons (Claude Sonnet 4.6: 1,000; Claude Mythos Preview: 1,307; Claude Opus 4.8: 1,222; Claude Mythos 5/Claude Fable 5: 1,374)](assets/figures/p293-1.png)
*__[Figure 8.17.3.1.A] The evaluation's grader preferred Claude Fable 5__ over Claude Opus 4.8 in 74% of pairwise comparisons.*

##### 8.17.3.2 Real-World Finance v1

For continuity with prior system cards, we also report Real-World Finance v1, a 53-task curated subset evaluated against reference answers with a model-based grader (Claude Opus 4.7-series grader, max effort). Scores below are not directly comparable to previously published Real-World Finance results, which used an earlier, more lenient grader. As Real-World Finance v2 supersedes this smaller curated subset, we expect this to be the final release for which we report v1 results.

Fable/Mythos 5 scored 70.0%, comparable to Claude Mythos Preview (70.9%) and up from 64.9% for Claude Opus 4.7 and 64.6% for Claude Opus 4.6, indicating the benchmark is not yet saturated.


<!-- p.294 -->

![Chart: Real-World Finance v1 scores — Claude Sonnet 4.5: 45.6%, Claude Opus 4.5: 58.4%, Claude Opus 4.6: 64.6%, Claude Sonnet 4.6: 57.3%, Claude Mythos Preview: 70.9%, Claude Opus 4.7: 64.9%, Claude Opus 4.8: 64.4%, Claude Mythos 5/Claude Fable 5: 70.0%](assets/figures/p294-1.png)
*__[Figure 8.17.3.2.A]__ Claude Fable 5 scores 70.0%, similar to Claude Mythos Preview.*

#### 8.17.4 Legal Agent Benchmark

Legal Agent Benchmark[^64] (LAB) is an open-source benchmark created by the [Harvey AI](https://www.harvey.ai/) team. The benchmark was released in May of 2026 and consists of 1,200+ tasks across 24 distinct practice areas. Each task contains a closed universe of documents (.xlsx, .docx, .eml, .pptx) which include email communication, firm templates, procedural files, and other client-matter materials the agent must sift through in order to accomplish the task. The task instructions are written as a minimal "request for work" from partner to associate. Task instructions also stipulate the expected output document and format. Evaluation is conducted pass/fail using an LLM-as-Judge across a suite of expert-written rubric criteria (criteria per evaluated tasks: min=23, median=56, max=194). The LAB standard reporting considers the task a success only if all criteria are met.


We tested Mythos 5 against 1,235 problems (16 of the 1,251 problems were excluded due to data defects; exclusions were identified before testing) and achieved a 16.91% (± 0.4, n=5) all-pass rate and 92.0% mean criterion-pass rate (adaptive-thinking, max effort). Fable 5 is currently the highest ranked per Harvey's evaluation[^65] (as of June 2026) on their held-out<!-- p.295 -->  set at 13.3% all-pass rate. Our harness is an internal reimplementation that preserves LAB's task content, rubric criteria, all-pass scoring, default judge model (Claude Sonnet 4.6), with a reduced toolset. The public harness exposes bash, read, write, edit, glob, grep tools, whereas we only expose bash and a Python tool.

#### 8.17.5 MCP Atlas

MCP-Atlas[^66] assesses language model performance on real-world tool use via the [Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro) (MCP). The benchmark measures how well models execute multi-step workflows—discovering appropriate tools, invoking them correctly, and synthesizing results into accurate responses. Tasks span multiple tool calls across production-like MCP server environments, requiring models to work with authentic APIs and real data, manage errors and retries, and coordinate across different servers. Claude Fable 5 achieved an 83.3% pass rate, up from 82.2% for Claude Opus 4.8.

#### 8.17.6 Vending-Bench

Vending-Bench 2 is a benchmark from Andon Labs[^67] that measures AI models' performance on running a business over long time horizons. Note that, unlike our real-world experiments as part of Project Vend, Vending-Bench evaluations[^68] are purely simulated.

Models are tasked with managing a simulated vending machine business for a year, given a $500 starting balance. They are scored on their final bank account balance, requiring them to demonstrate sustained coherence and strategic planning across thousands of business decisions. To score well, models must successfully find and negotiate with suppliers via email, manage inventory, optimize pricing, and adapt to dynamic market conditions.

Fable 5 was run with all effort levels. Fable 5's best result came at max effort: a final balance of $5,680.26, slightly below Claude Opus 4.8's $5,787.43. Vending-Bench has its own context management system, meaning the context editing capability in Claude was not enabled; we discuss alignment in Section 6.2.5.

<!-- p.296 -->

#### 8.17.7 GDPval-AA

GDPval-AA[^69], developed by [Artificial Analysis](https://artificialanalysis.ai/), is an independent evaluation framework that tests AI models on economically valuable, real-world professional tasks. The benchmark uses 220 tasks from OpenAI's [GDPval gold database](https://huggingface.co/datasets/openai/gdpval), spanning 44 occupations across 9 major industries. Tasks mirror actual professional work products including documents, slides, diagrams, and spreadsheets. Models are given shell access and web browsing capabilities in an agentic loop to solve tasks, and performance is measured via ELO ratings derived from blind pairwise comparisons of model outputs. Claude Fable 5 achieved the top score on the leaderboard, with Claude models holding four of the top five positions. Claude Fable 5 led Opus 4.8 by ~42 Elo points (56% pairwise win rate), while using fewer turns and tokens. Evaluation was run independently by Artificial Analysis.

#### 8.17.8 Toolathlon

Toolathlon is an agentic benchmark of 108 real-world tool-use tasks spanning office productivity, e-commerce and operations, data analysis, and web research. Tasks are seeded from authentic application state and graded by execution-based checkers that verify resulting artifacts and their side effects. The benchmark exposes 604 tools across 32 applications; tasks average roughly 20 turns and require correct tool selection, multi-step sequencing, and checker-exact outputs.

We ran our internal harness with adaptive thinking at max effort. Following the Toolathlon paper's protocol, we report Pass@1 averaged over 3 trials across all 108 tasks, alongside Pass@3 (at least one of three trials correct), Pass³ (all three trials correct), and the average number of turns per trajectory.

Claude Mythos 5 achieved 61.7% Pass@1 (±0.5 across trials), improving on Claude Opus 4.8 (59.9%) and Claude Opus 4.7 (59.3%). Claude Mythos 5 also sets a new mark for reliability: its Pass³ of 58.3%—the fraction of tasks solved in all three trials—exceeds the best previous Claude result by over 5 points, and the narrow gap between its Pass@1 and Pass@3 (66.7%) indicates that what Claude Mythos 5 can solve, it solves consistently. It does so with fewer turns than its predecessors.

<!-- p.297 -->

| Model                     | Pass@1 | Pass@3 | Pass³ | Avg turns |
|---------------------------|--------|--------|-------|-----------|
| **Claude Fable 5**        | 61.7   | 68.5   | 55.6  | 19.8      |
| **Claude Mythos 5**       | 61.7   | 66.7   | 58.3  | 19.0      |
| **Claude Opus 4.8**       | 59.9   | 67.6   | 48.1  | 24.5      |
| **Claude Opus 4.7**       | 59.3   | 66.7   | 52.8  | 25.9      |
| **Claude Mythos Preview** | 61.1   | 66.7   | 55.6  | 17.6      |
| **Claude Opus 4.6**       | 56.8   | 66.7   | 47.2  | 16.9      |
| **Claude Sonnet 4.5**     | 41.0   | 54.6   | 28.7  | 32.0      |

*__[Table 8.17.8.A] Toolathlon scores (internal harness).__ Models are evaluated with adaptive thinking at max effort. Pass@1, Pass@3, and Pass³ are computed over all 108 tasks across 3 trials per the paper's protocol.*

Note on comparability to the published leaderboard. Our harness mirrors the upstream task definitions, prompts, and execution-based checkers, validated by replaying the published claude-sonnet-4.5 trajectories. To control for live-dependency drift and upstream repository changes since the published trajectories, we pin financial-data feeds and container images to an offline snapshot and mirror current upstream state. Roughly a quarter of tasks are unsatisfiable as published; we leave these unchanged. Net effect of the pinning: our scores run ~3 points above a strictly upstream-equivalent harness—an offset that is constant across the Claude models reported here. Separately, the published leaderboard's Opus 4.7 figure uses the authors' default configuration rather than max effort.

#### 8.17.9 AutomationBench

AutomationBench[^70] is a benchmark from Zapier that measures whether an agent can complete a realistic end-to-end business workflow. Tasks are seeded from real customer workflow patterns across Sales, Marketing, Operations, Support, Finance, and HR. Each task drops the agent into a simulated company with dozens of REST API endpoints spanning 47 apps (CRM, Slack, Google Workspace, etc.). Given a single natural-language instruction, the agent must autonomously discover the right endpoints via search, make dozens of sequential, interdependent API calls, consult and obey layered business-policy documents, as well as sidestep deliberately planted distractors. Grading is pass or fail for each task based on meeting all deterministic assertions on simulated app state (e.g., were the right CRM updates applied).

<!-- p.298 -->

On AutomationBench's [leaderboard](https://zapier.com/benchmarks), which measures performance on a private held-out evaluation set, Claude Fable 5 (max effort) scored a 17.4%, outperforming Claude Opus 4.8 (max effort) at 15.5%.

![Chart: AutomationBench leaderboard on private held-out tasks — horizontal bars: Claude Fable 5 (Max): 17.4%, Claude Opus 4.8 (Max): 15.5%, Gemini 3.5 Flash (Medium): 14.5%, GPT-5.5 (XHigh): 12.9%, Gemini 3.5 Flash (High): 12.6%, Gemini 3.5 Flash (Low): 12.2%, GPT-5.5 (High): 11.3%](assets/figures/p298-1.png)
*__[Figure 8.17.9.A] AutomationBench__ scores on private held-out tasks.*

![Chart: AutomationBench test-time compute scaling — pass rate versus average cost per task (log scale) for GPT-5.5 (6.7% low to 12.9% xhigh), Claude Opus 4.8 (9.9% low to 15.5% xhigh), and Claude Mythos 5 (10.5% low to 17.4% max)](assets/figures/p298-2.png)
*__[Figure 8.17.9.B] AutomationBench__ pass rate versus average cost per task, as measured and reported by Zapier.*

<!-- p.299 -->

### 8.18 Healthcare

#### 8.18.1 HealthBench results

HealthBench[^71] is an open-source evaluation developed to assess safety, accuracy, and communication across realistic healthcare contexts. The benchmark uses over 48,000 expert-written rubric items to grade 5,000 multi-turn patient conversations across 26 medical specialties.

![Chart: HealthBench length-adjusted scores — GPT-5.5*: 56.5%, Claude Sonnet 4.6: 50.2%, Claude Mythos Preview: 61.1%, Claude Opus 4.8: 59.3%, Claude Mythos 5: 62.7%](assets/figures/p299-1.png)
*__[Figure 8.18.1.A] HealthBench length-adjusted scores.__ All Claude models used adaptive thinking at max effort with a 40k token budget. Claude Opus 4.8 was the grader model. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model. Shown with 95% CI. (\*GPT-5.5: as publicly reported by OpenAI [their grader and published length adjustment]).*

#### 8.18.2 HealthBench Professional results

HealthBench Professional[^72] is a clinical task benchmark composed of 525 physician-authored conversations spanning clinical consults, documentation, and research tasks, each graded against rubric criteria by an LLM-as-a-Judge model.


<!-- p.300 -->

![Chart: HealthBench Professional length-adjusted scores — GPT-5.5*: 51.8%, Claude Sonnet 4.6: 44.4%, Claude Mythos Preview: 64.7%, Claude Opus 4.8: 56.9%, Claude Mythos 5: 66.0%](assets/figures/p300-1.png)
*__[Figure 8.18.2.A] HealthBench Professional length-adjusted scores.__ All Claude models used adaptive thinking at max effort. Claude Opus 4.8 was the grader model. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model. Shown with 95% CI. (\*GPT-5.5: as publicly reported by OpenAI [their grader and published length adjustment]).*

#### 8.18.3 HealthAdminBench results

HealthAdminBench[^73] is a 135-task benchmark of three healthcare revenue-cycle workflows (prior authorization, denials and appeals, durable-medical-equipment orders) executed across four simulated GUI environments (an EHR, two payer portals, a fax portal). Each task decomposes into fine-grained verifiable subtasks which are assessed by deterministic and LLM graders. Reported scores are full-task completion pass@1.


<!-- p.301 -->

![Chart: HealthAdminBench full-task pass rates — Claude Sonnet 4.6: 45.2%, Claude Mythos Preview: 47.4%, Claude Opus 4.8: 51.9%, Claude Mythos 5: 51.9%](assets/figures/p301-1.png)
*__[Figure 8.18.3.A] HealthAdminBench full-task completion rates (pass@1).__ Results were generated with Anthropic's internal port of the benchmark and are not directly comparable to the published leaderboard. All runs used a browser-use agent with adaptive thinking and a 500k-token per-task budget. Only a single trial was run for each model. Agents were provided per-portal skill files rather than task-specific system-prompt text. LLM-judged subtasks were scored by Claude Opus 4.8. Task and run identifiers were pinned in browser local storage to ensure robust session tracking.*

### 8.19 Multilingual performance

We evaluated Claude Mythos 5 on three multilingual benchmarks, namely Cohere Labs's Global MMLU (GMMLU)[^74] and INCLUDE benchmark[^75], and AI4Bharat's Multi-task Indic Language Understanding Benchmark (MILU)[^76] to assess model performance across a wide range of languages.


GMMLU extends the standard MMLU evaluation across 42 languages from high-resource languages such as French and German to low-resource languages such as Yoruba, Igbo, and Chichewa. MILU focuses on 10 Indic languages (Bengali, Gujarati, Hindi, Kannada,<!-- p.302 -->  Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu) alongside English and tests culturally grounded knowledge comprehension. INCLUDE covers 44 languages with questions drawn from regional academic and professional examinations, emphasizing in-language and in-culture knowledge rather than translated content.

#### 8.19.1 GMMLU results

![Chart: GMMLU average accuracy — Claude Sonnet 4.6: 88.5, Claude Mythos Preview: 92.7, Claude Opus 4.8: 91.1, Claude Mythos 5: 93.2](assets/figures/p302-1.png)
*__[Figure 8.19.1.A] GMMLU average accuracy.__ Claude Mythos 5 achieved an average accuracy of 93.2% across all evaluated languages. All models were evaluated with max-effort adaptive thinking with a 32,768-token response budget. Only a single trial was run for each model.*

<!-- p.303 -->

#### 8.19.2 MILU results

![Chart: MILU average accuracy — Claude Sonnet 4.6: 89.4, Claude Mythos Preview: 92.7, Claude Opus 4.8: 91.2, Claude Mythos 5: 92.9](assets/figures/p303-1.png)
*__[Figure 8.19.2.A] MILU average accuracy.__ Claude Mythos 5 achieved an average accuracy of 92.9% across all evaluated languages. All models were evaluated with max-effort adaptive thinking with a 32,768-token response budget. Scores were averaged over 5 trials.*

<!-- p.304 -->

#### 8.19.3 INCLUDE results

![Chart: INCLUDE average accuracy — bar chart of Claude Sonnet 4.6, Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5, with Claude Mythos 5 highest at 90.5](assets/figures/p304-1.png)
*__[Figure 8.19.3.A] INCLUDE average accuracy.__ Claude Mythos 5 achieved an average accuracy of 90.5% across all evaluated languages. All models were evaluated with max-effort adaptive thinking with a 32,768-token response budget. Scores were averaged over 5 trials.*

### 8.20 Life sciences capabilities

Claude Mythos 5 outperforms several previous models on life sciences capabilities. We continue to report evaluations in areas including computational biology, structural biology, organic chemistry, and protocol troubleshooting. These evaluations, many of which were developed internally by domain experts, focus on the capabilities that drive beneficial applications in basic research and drug development, complementing the CB risk assessments in Section 2.2 which focus on misuse potential.

Although many of these evaluations are not publicly released, we briefly describe each below. For all tasks except Protocol Troubleshooting, Claude has access to a bash tool for code execution and package managers for installing needed libraries. For Protocol Troubleshooting, Claude has access to bash, file editor, and web search tools. For LabBench2, Claude has access to bash, file editor, web search, and image zoom/crop tools.

<!-- p.305 -->

#### 8.20.1 BioMysteryBench

BioMysteryBench assesses a model's ability to solve difficult, analytical challenges that require interleaving computational analysis with biological reasoning. Given unprocessed datasets, the model must answer questions such as identifying a knocked-out gene from transcriptomic data or determining what virus infected a sample. For this benchmark, we report the subset of problems that independent human experts were able to solve ("Human Solvable") as well as the subset that remain unsolved by humans but have an objective, ground-truth solution ("Human Difficult"). On the Human Solvable subset, Claude Mythos 5 achieved 83.9%, the strongest result, ahead of Claude Mythos Preview at 82.6%, Claude Opus 4.8 at 80.4%, and Claude Sonnet 4.6 at 78.4%. On the Human Difficult subset, Claude Mythos 5 scored 46.1%, well ahead of Claude Opus 4.8 at 40.0%, Claude Mythos Preview at 29.6%, and Claude Sonnet 4.6 at 30.9%.

#### 8.20.2 LatchBio Bioinformatics

Developed by LatchBio, these evaluations assess the ability to solve challenging real-world bioinformatics problems. The SpatialBench Verified variant tests the analysis of spatial transcriptomics data—gene expression mapped to physical locations in a tissue slice—across a set of 115 externally validated problems, requiring the model to answer biological questions about the sample from those results. The SingleCellBench variant tests the analysis of single-cell RNA sequencing data across 195 problems spanning standard workflows such as labeling cell types, finding differentially expressed genes, and correcting batch effects.

On SpatialBench Verified, Claude Mythos 5 achieved the top score at 69.2%, ahead of Claude Opus 4.8 at 66.6%, Claude Mythos Preview at 63.5%, and Claude Sonnet 4.6 at 60.0%; the Claude Mythos Preview figure is drawn from a one-episode-variant run, which is the only Verified data available for that model. On SingleCellBench, Claude Mythos 5 again led at 59.3%, ahead of Claude Opus 4.8 and Claude Mythos Preview, which tied at 58.2%, and Claude Sonnet 4.6 at 50.4%.

#### 8.20.3 Structural biology, open-ended

We evaluated the model's ability to understand the relationship between biomolecular structure and function. Given only structural data and basic tools, the model must answer open-ended questions about a biomolecule's function. Claude Mythos 5 achieved 87.2%, the strongest result, ahead of Claude Mythos Preview at 81.6% and Claude Opus 4.8 at 79.0%, and more than doubling Claude Sonnet 4.6 at 31.6%.

<!-- p.306 -->

#### 8.20.4 ProteinGym Hard

This benchmark assesses a model's ability to predict how mutations affect a protein's function by ranking a subset of mutant protein sequences against the wild type sequence. Scored by rank correlation against real lab measurements from the published ProteinGym benchmark, Claude Mythos 5 achieved 44.8%, ahead of Claude Mythos Preview at 43.1%, Claude Opus 4.8 at 39.6%, and Claude Sonnet 4.6 at 35.4%.

#### 8.20.5 Organic chemistry

We evaluated models' fundamental skills spanning tasks like predicting molecular structures from spectroscopy data, designing multi-step synthetic routes, predicting reaction products, and converting between IUPAC names, SMILES notation, and chemical structure images. Claude Mythos 5 achieved a score of 90.1%, the strongest result, ahead of Claude Mythos Preview at 86.5% and Claude Opus 4.8 at 86.2%, and a marked improvement over Claude Sonnet 4.6 at 56.2%.

#### 8.20.6 Protocol troubleshooting

This assessment looks at models' ability to detect and fix errors in molecular biology protocols, including by using web search tools to find additional details about protocols online. Claude Mythos 5 achieved a score of 66.7%, an improvement over Claude Opus 4.8 at 59.6% and Claude Sonnet 4.6 at 42.4%, though trailing Claude Mythos Preview, which led at 69.6%.

#### 8.20.7 LABBench2

LABBench2[^77] assesses ability to answer biology research questions by finding and reading evidence on the live web—locating the right papers, patents, clinical-trial records, and databases, interpreting their figures, tables, and supplementary materials, and judging source reliability. Claude Mythos 5's biggest gain came on patent questions, where it scored 79.8%—compared to 68.8% for Claude Opus 4.8 and 64.3% for Claude Mythos Preview—and it also led on clinical-trial questions at 91.2% (up from 86.3% for Claude Mythos Preview and 85.3% for Claude Opus 4.8), database questions at 74.2%, literature questions at 86.5%, and table reading at 82.4%. On supplementary materials (65.9% vs 66.1%) and source-reliability judgments (97.6% vs 96.5%) it performed on par with Claude Mythos Preview. FigQA remained the most difficult category for every model, with Claude Mythos 5 highest at 48.3%.


<!-- p.307 -->

![Chart: six-panel bar charts of life sciences evaluations comparing Claude Sonnet 4.6, Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5 — BioMysteryBench (Human solvable 0.78/0.83/0.80/0.84, Human difficult 0.31/0.30/0.40/0.46), LatchBio Bioinformatics (SpatialBench Verified 0.60/0.63/0.67/0.69, SingleCellBench 0.50/0.58/0.58/0.59), Structural biology open-ended (0.32/0.82/0.77/0.87), ProteinGym Hard (0.35/0.43/0.40/0.45), Organic chemistry (0.56/0.86/0.86/0.90), and Protocol troubleshooting (0.42/0.70/0.60/0.67)](assets/figures/p307-1.png)
*__[Figure 8.20.7.A] Evaluation results for life sciences.__ Claude Mythos 5 shows consistent improvements across a range of life science tasks.*


<!-- p.308 -->

![Chart: LABBench2 accuracy by category for Claude Sonnet 4.6, Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5 — LitQA3 (0.74/0.83/0.82/0.87), FigQA2 (0.30/0.45/0.41/0.48), TableQA2 (0.48/0.79/0.77/0.82), SuppQA2 (0.41/0.66/0.59/0.66), TrialQA (0.59/0.86/0.85/0.91), PatentQA (0.47/0.64/0.69/0.80), DBQA2 (0.52/0.69/0.67/0.74), SourceQuality (0.85/0.97/0.96/0.98)](assets/figures/p308-1.png)
*__[Figure 8.20.7.B] LABBench2.__ Claude Mythos 5 exceeds most previous models on LABBench2 scores.*

[^64]: Harvey AI. (2026). Legal Agent Benchmark. [https://www.harvey.ai/blog/introducing-harveys-legal-agent-benchmark](https://www.harvey.ai/blog/introducing-harveys-legal-agent-benchmark)
[^65]: Harvey AI. (2026). Legal Agent Benchmark: initial results. [https://www.harvey.ai/blog/legal-agent-benchmark-initial-results](https://www.harvey.ai/blog/legal-agent-benchmark-initial-results)
[^66]: Bandi, C., et al. (2026). MCP-Atlas: A large-scale benchmark for tool-use competency with real MCP servers. arXiv:2602.00933. [https://arxiv.org/abs/2602.00933](https://arxiv.org/abs/2602.00933)
[^67]: Andon Labs. (2025). Vending-Bench 2. [https://andonlabs.com/evals/vending-bench-2](https://andonlabs.com/evals/vending-bench-2)
[^68]: Backlund, A., & Petersson, L. (2025). Vending-Bench: A benchmark for long-term coherence of autonomous agents. arXiv:2502.15840. [https://arxiv.org/abs/2502.15840](https://arxiv.org/abs/2502.15840)
[^69]: Patwardhan, T., et al. (2025). GDPval: Evaluating AI model performance on real-world economically valuable tasks. arXiv:2510.04374. [https://arxiv.org/abs/2510.04374](https://arxiv.org/abs/2510.04374)
[^70]: Shepard, D., & Salimans, R. (2026). AutomationBench. arXiv:2604.18934. [https://arxiv.org/abs/2604.18934](https://arxiv.org/abs/2604.18934)
[^71]: Arora, R. K., et al. (2025). HealthBench: Evaluating large language models towards improved human health. arXiv:2505.08775. [https://arxiv.org/abs/2505.08775](https://arxiv.org/abs/2505.08775)
[^72]: Soskin Hicks, R., et al. (2026). HealthBench Professional: Evaluating large language models on real clinician chats. arXiv:2604.27470. [https://arxiv.org/abs/2604.27470](https://arxiv.org/abs/2604.27470)
[^73]: Bedi, S., et al. (2026). HealthAdminBench: Evaluating computer-use agents on healthcare administration tasks. arXiv:2604.09937. [https://arxiv.org/abs/2604.09937](https://arxiv.org/abs/2604.09937)
[^74]: Singh, S., et al. (2024). Global MMLU: Understanding and addressing cultural and linguistic biases in multilingual evaluation. arXiv:2412.03304. [https://arxiv.org/abs/2412.03304](https://arxiv.org/abs/2412.03304)
[^75]: Romanou, A., et al. (2024). INCLUDE: Evaluating multilingual language understanding with regional knowledge. arXiv:2411.19799. [https://arxiv.org/abs/2411.19799](https://arxiv.org/abs/2411.19799)
[^76]: Verma, S., et al. (2024). MILU: A multi-task Indic language understanding benchmark. arXiv:2411.02538. [https://arxiv.org/abs/2411.02538](https://arxiv.org/abs/2411.02538)
[^77]: Laurent, J. M., et al. (2026). LABBench2: An improved benchmark for AI systems performing biology research. arXiv:2604.09554. [https://arxiv.org/abs/2604.09554](https://arxiv.org/abs/2604.09554)
