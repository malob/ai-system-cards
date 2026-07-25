<!-- source: source.pdf pages 169-190 -->

<!-- p.169 -->

### 8.12 Multimodal

We evaluated Claude Opus 5’s multimodal capabilities on four benchmarks drawn from real-world, agentic tasks that reflect how models are deployed in professional settings: complex chart reasoning (Chartography), CAD generation from multi-view renders (BenchCAD Vision2Code), agentic computer-use (OSWorld 2.0), and professional document understanding (GDP.pdf).

Claude Opus 5 demonstrates multimodal capabilities which scale with test-time compute. On Chartography and GDP.pdf, Claude Opus 5 bridges the gap between Claude Opus 4.8 and Claude Mythos 5, offering much greater cost-performance at lower effort levels. On BenchCAD Vision2Code and OSWorld 2.0, Claude Opus 5 is Pareto-dominant over Claude Mythos 5 on the score-cost frontier when given tools to crop, analyze, and verify visual inputs and outputs, and to interact with GUIs, respectively.

Indeed, we find that agentic tool-use is generally a more cost-effective method of scaling test-time compute than adaptive thinking by itself. On both Chartography and BenchCAD Vision2Code, Claude Opus 5 achieved significantly higher scores at the same or lower cost when given both adaptive thinking and a standard set of tools, compared to when the model is given adaptive thinking alone.

#### 8.12.1 Chartography

Chartography[^23] is a chart understanding benchmark from Surge AI covering a set of 100 specialized chart types rarely evaluated in existing benchmarks. These include Kaplan–Meier charts, candlestick charts, contour maps, wind rose diagrams, Sankey diagrams, Bode plots, and 3D surface plots. Because different chart types can be read to different degrees of precision, each answer is graded against an acceptable range set by experts for that specific chart, rather than a single fixed tolerance.

The model is configured with adaptive thinking and `max` effort enabled in all runs, both with and without tools. When evaluated with tools, the model is provided a container—with the image file and standard libraries installed—and an image cropping tool. Our internal grading implementation of Chartography matches the tasks and expert-determined acceptable answer ranges in the official repository.[^24]

<!-- p.170 -->

Claude Opus 5 achieved a score of 29.6% without tools and 83.0% with tools. Claude Opus 4.8 scored 17.0% and 75.0%, while Claude Mythos 5 achieved scores of 36.0% and 85.2%, respectively.

![](assets/figures/p170-1.png)

:::caption
**[Figure 8.12.1.A] Chartography scores.** Claude models are evaluated with adaptive thinking and max effort, with and without tools. Scores are averaged over five runs. Shown with 95% CI. *Gemini 3.5 Flash and GPT-5.6 Sol scores as publicly reported by Surge AI, evaluated without tools.
:::

Claude Opus 5 achieves similar performance as Claude Mythos 5 at `max` effort and with tools, but Claude Opus 5 both extends and Pareto-dominates the score-cost frontier on Chartography at lower effort levels. In fact, we find that leveraging the models’ agentic coding capabilities to manipulate, analyze, and crop images can be significantly more cost-effective than simply enabling adaptive thinking.

<!-- p.171 -->

![](assets/figures/p171-1.png)

:::caption
**[Figure 8.12.1.B] Chartography scores.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.12.2 BenchCAD

BenchCAD[^25] is a benchmark for programmatic CAD reasoning built from 17,900 execution-verified CadQuery programs spanning 106 industrial part families, roughly half of which are anchored to real ISO, DIN, EN, ASME, and IEC specification tables. The benchmark decomposes CAD capability into four matched tasks; we report results on the Vision2Code task which requires models to generate CadQuery code from multi-view renders.

Our internal implementation of BenchCAD matches the original reference implementation except for two minor modifications.[^26] First, we corrected a typo in the reference system prompt which swapped all four camera positions in the rendered views provided to the model. Second, we updated the grading to accept raw shapes in addition to Workplanes. On<!-- p.172 --> models like GPT-5.5, we noticed raw shapes would error out due to this stylistic difference in output, but otherwise equivalent geometry. Both changes have already been merged into the reference repository in GitHub.

The model is configured with adaptive thinking and `max` effort enabled in all runs, both with and without tools. When evaluated with tools, the model was provided with a container—with the image files and standard libraries installed—and an image cropping tool. We evaluate the model on a random 1,000 file subset of the published 17,900 Vision2Code files, which we have historically found to be indicative of scores on the full set within a 0.01 voxel IoU margin. We report voxel IoU scores averaged over five runs.

On the 1,000-file subset of BenchCAD Vision2Code, Claude Opus 5 achieved a voxel IoU score of 0.366 without tools and a score of 0.821 with tools. Claude Opus 4.8 achieved scores of 0.277 and 0.521, and Claude Mythos 5 scored 0.378 and 0.678, respectively.

![](assets/figures/p172-1.png)

:::caption
**[Figure 8.12.2.A] BenchCAD Vision2Code subset scores.** Claude models are evaluated with adaptive thinking and max effort, with and without tools. Scores are averaged over five runs and shown with 95% CI. *GPT-5.6 Sol scores as publicly reported by OpenAI, evaluated on the full 17,900 files.
:::

Increasingly, Claude models’ performance on this evaluation scales substantially with test-time compute, in particular when the models are equipped with tools that enable visual verification of intermediate outputs—not just adaptive thinking. Indeed when<!-- p.173 --> provided with tools, Claude Opus 5 surpassed Claude Mythos 5 on BenchCAD Vision2Code by a large margin, in particular at higher effort levels.

![](assets/figures/p173-1.png)

:::caption
**[Figure 8.12.2.B] BenchCAD Vision2Code subset scores.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Scores are averaged over five runs at each effort level. Shown with 95% CI.
:::

#### 8.12.3 OSWorld 2.0

OSWorld 2.0[^27] is a multimodal benchmark that evaluates an agent’s ability to complete real-world computer tasks by interacting with a live Ubuntu virtual machine via mouse and keyboard actions. We followed the default settings, with 1080p resolution and a maximum of 500 action steps per task. For tasks that require a model grader, we used Opus 4.8.

Opus 5 achieved an OSWorld 2.0 score of 70.57% (first-attempt success rate, averaged over five runs). We also evaluated our previously released models on OSWorld 2.0 (GPT 5.6 Sol and Muse Spark 1.1 scores sourced from their respective release posts):

<!-- p.174 -->

![](assets/figures/p174-1.png)

:::caption
**[Figure 8.12.3.A] OSWorld 2.0** scores across models. Opus 5 achieves state of the art on this newly released benchmark.
:::

In addition to being our strongest computer-use model yet, Opus 5 represents a meaningful jump in computer use efficiency.

![](assets/figures/p174-2.png)

:::caption
**[Figure 8.12.3.B] OSWorld 2.0** price vs performance across models.
:::

#### 8.12.4 GDP.pdf

GDP.pdf[^28] is an expert multimodal reasoning benchmark from Surge AI consisting of 100 real-world prompts and PDFs drawn directly from professional workflows across ten<!-- p.175 --> domains, including finance, healthcare, legal, engineering, and insurance. The benchmark tests whether models can parse, cross-reference, and synthesize the dense documents that underpin enterprise work. This includes interpreting multi-page dosage tables, isolating clauses buried in nested exhibits, and reconciling figures across quarterly filings.

We evaluated GDP.pdf using an internal harness, both with and without tools. When evaluated without tools, the model is provided with base64-encoded PDFs to match Surge’s input prompts. However, unlike Surge, we truncate (rather than drop) any PDFs that do not fit our API’s 32MB request size limit. We used Opus 4.7 as a judge instead of Gemini 3 Flash. When evaluated with tools, the model is provided with a container—with the PDF file and standard libraries installed—and an image cropping tool.

We corrected a bug in our harness which was unnecessarily truncating PDFs longer than 100 pages but smaller than our 32MB request size limit. Fixing this issue led to significant uplift on scores produced with our internal harness, as compared to our previously published results. We re-ran prior models with the updated harness and plot the revised scores, below. We report mean criteria pass rate, the fraction of rubric conditions satisfied across tasks, averaged over completed runs, instead of strict pass rate. We evaluated the model on the full 100 prompts and average scores over five runs.

On GDP.pdf, Claude Opus 5 achieved a mean criteria pass rate of 83.4% without tools and a score of 85.5% with tools. Claude Opus 4.8 scored 77.5% and 84.8% and Claude Mythos 5 scored 81.8% and 87.3%, respectively. We note that Claude Opus 5 Pareto-dominates both Claude Opus 4.8 and Claude Mythos 5 in the no tools setting, achieving significantly higher scores at the same or lower cost. However, Claude Mythos 5 continues to lead among Claude models on GDP.pdf in the tools setting.

<!-- p.176 -->

![](assets/figures/p176-1.png)

:::caption
**[Figure 8.12.4.A] GDP.pdf scores.** Models are evaluated with adaptive thinking at various effort levels, with and without tools. We use the effort parameter to adjust the amount of test-time compute spent. Mean criteria pass rates are averaged over five runs at each effort level. Shown with 95% CI.
:::

### 8.13 Real-world professional tasks

#### 8.13.1 OfficeQA

OfficeQA is a public benchmark from Databricks that evaluates end-to-end grounded reasoning over a large corpus of historical U.S. Treasury Bulletin documents. Models must locate relevant tables across the corpus and perform precise numerical reasoning over them. We evaluate agentically, with documents provided as extracted text in a sandboxed environment and code-execution tools available; OfficeQA Pro is the harder 133-question subset recommended for frontier models.

Claude Opus 5 achieved 78.1% on OfficeQA and 66.9% on OfficeQA Pro. This is slightly above Claude Opus 4.8, which achieved 77.6% and 66.2%, and slightly below Claude Mythos 5, which achieved 79.0% and 67.1%. Claude Opus 5 was evaluated on the public Messages API with its production safeguards active (safety classifiers, with fallback to Claude Opus 4.8 on classifier refusal); the comparison models were evaluated on the internal API without those safeguards.

<!-- p.177 -->

#### 8.13.2 MCP Atlas

MCP-Atlas assesses language model performance on real-world tool use via the Model Context Protocol (MCP). The benchmark measures how well models execute multi-step workflows—discovering appropriate tools, invoking them correctly, and synthesizing results into accurate responses. Tasks span multiple tool calls across production-like MCP server environments, requiring models to work with authentic APIs and real data, manage errors and retries, and coordinate across different servers.

Claude Opus 5 achieved an 85.8% pass rate, up from 82.2% for Opus 4.8. Mean claim coverage of 89.1% indicated that most remaining failures were partial rather than complete. In the time since we computed this benchmark score, effort settings may have changed slightly for our production deployment and therefore some scores may not be precisely reproducible.

#### 8.13.3 Legal Agent Benchmark

Legal Agent Benchmark (LAB) is an open-source benchmark created by [Harvey AI](https://www.harvey.ai/). The benchmark consists of 1,200+ tasks across 24 distinct practice areas. Each task contains a closed universe of documents, which include email communication, firm templates, procedural files, and other client-matter materials the agent must sift through in order to accomplish the task. The task instructions are written as a minimal “request for work” from partner to associate. Task instructions also stipulate the expected output document and format. Evaluation is conducted pass/fail using an LLM-as-Judge across a suite of expert-written rubric criteria (criteria per evaluated task: min=23, median=56, max=194). The LAB standard reporting considers the task a success only if all criteria are met.

We tested Claude Opus 5 against 1,235 problems (16 of the 1,251 problems were excluded due to data defects; exclusions were identified before testing). It achieved a 23.58% (± 0.48, n=5) all-pass rate and a 93.74% mean criterion-pass rate (adaptive thinking, `max` effort). Claude Opus 5 was evaluated on the public Messages API with production safeguards, falling back to Claude Opus 4.8 when a safety classifier is triggered. Since our previously reported LAB results, we made minor grading pipeline fixes: correctly rendering Word tracked changes in .docx deliverables and recovering outputs truncated at the token limit, which together we estimate raise all-pass scores by 0.5–1 percentage points for any model evaluated. Our harness is an internal reimplementation that preserves LAB’s task content, rubric criteria, all-pass scoring, and default judge model (Claude Sonnet 4.6), but with a reduced toolset. The public harness exposes bash, read, write, edit, glob, and grep tools, whereas we only expose bash and a Python tool. Per Harvey’s evaluation on their held-out set, Claude Opus 5 achieved an 11.7% all-pass rate and a 94.1% mean criterion-pass rate.

<!-- p.178 -->

#### 8.13.4 GDPval-AA

GDPval-AA v2, developed by [Artificial Analysis](https://artificialanalysis.ai/), is an independent evaluation framework that tests AI models on economically valuable, real-world professional tasks. The benchmark uses 220 tasks from OpenAI’s [GDPval gold database](https://huggingface.co/datasets/openai/gdpval)[^29], spanning 44 occupations across 9 major industries. Tasks mirror actual professional work products including documents, slides, diagrams, and spreadsheets. Models are given shell access and web browsing capabilities in an agentic loop to solve tasks, and performance is measured via ELO ratings derived from blind pairwise comparisons of model outputs. Claude Opus 5 takes the top two spots on the leaderboard: ELO 1861 at `max` effort and 1827 at `xhigh`. The `xhigh` setting still outperforms every other model while using 25% fewer output tokens than `max`. Evaluations were run independently by Artificial Analysis.

#### 8.13.5 AA-Briefcase

[AA-Briefcase](https://artificialanalysis.ai/articles/aa-briefcase), developed by Artificial Analysis, is a new benchmark for long-horizon knowledge work in complex projects built by industry experts. Models work through multi-week projects with many linked tasks and thousands of input source files; grading combines rubric scoring and pairwise judging via a panel of frontier models to measure verifiable task success, analytical quality, and presentation quality. Claude Opus 5 takes the top three spots on the leaderboard: ELO 1720 at `max` effort, 1693 at `xhigh`, and 1606 at `high`. The `xhigh`/`high` setting still outperforms every other model while using 15%/33% fewer output tokens than `max`. Evaluation was run independently by Artificial Analysis.

#### 8.13.6 Toolathlon Verified

Toolathlon is an agentic benchmark of 108 real-world tool-use tasks spanning office productivity, e-commerce and operations, data analysis, and web research. Tasks are seeded from authentic application state and graded by execution-based checkers that verify the resulting artifacts and their side effects. The benchmark exposes more than 600 tools across 32 applications, and tasks require correct tool selection, multi-step sequencing, and checker-exact outputs over long horizons—trajectories in our runs averaged roughly 20–26 assistant turns. We evaluated against Toolathlon-Verified, the authors’ final release (June 2026), in which task prompts, ground truths, and evaluators were human-reviewed and finalized, with reference trajectories for eight models published for external validation.

<!-- p.179 -->

We ran our internal harness with adaptive thinking at `max` effort and no safety classifiers or fallback. Following the paper’s protocol, we report Pass@1 averaged over three trials across all 108 tasks, alongside Pass@3 (at least one of three trials correct), Pass³ (all three trials correct), and the average number of assistant turns per trajectory.

Claude Opus 5 achieved 80.6% Pass@1, ahead of Claude Opus 4.8 (79.9%) and Claude Sonnet 5 (74.7%) evaluated on the same harness.

<table><tbody>
<tr><th>Model</th><th>Pass@1</th><th>Pass@3</th><th>Pass³</th><th>Avg turns</th></tr>
<tr><td><b>Claude Opus 5</b></td><td>80.6</td><td>87.0</td><td>73.1</td><td>23.5</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td>79.3</td><td>86.1</td><td>73.1</td><td>19.8</td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>79.9</td><td>88.0</td><td>71.3</td><td>20.4</td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>74.7</td><td>84.3</td><td>65.7</td><td>24.5</td></tr>
</tbody></table>

:::caption
**[Table 8.13.6.A] Toolathlon scores (internal harness).** Models are evaluated with adaptive thinking at max effort. Pass@1, Pass@3, and Pass³ are computed over all 108 tasks across 3 trials per the paper’s protocol.
:::

Our harness mirrors the Toolathlon-Verified task definitions, prompts, and execution-based checkers byte-for-byte, which we validated by replaying the authors’ published reference trajectories. To control live-dependency drift, we pin financial-data feeds to a snapshot recorded at run time and pin container images. A small number of upstream checker defects (for example, ground truth referencing a since-renamed repository) affect all models symmetrically and are left unchanged..

A note on comparability to the published leaderboard: Our Claude Sonnet 5 and Claude Opus 4.8 figures are roughly 3 points higher than the published leaderboard’s (71.6% and 76.2%). The gap comes entirely from *null attempts*—runs in which the authors’ harness produced no trajectory (8 of 324 for Sonnet 5, 11 for Opus 4.8). The leaderboard counts these as failures; excluding them, our figures match the authors’ published reference trajectories within run-to-run noise.

#### 8.13.7 AutomationBench

AutomationBench[^30] is a benchmark from Zapier that measures whether an agent can complete a realistic end-to-end business workflow. Tasks are seeded from real customer workflow patterns across Sales, Marketing, Operations, Support, Finance, and HR. Each task drops the agent into a simulated company with dozens of REST API endpoints<!-- p.180 --> spanning 47 apps (CRM, Slack, Google Workspace, etc.). Given a single natural-language instruction, the agent must autonomously discover the right endpoints via search, make dozens of sequential, interdependent API calls, consult and obey layered business-policy documents, as well as sidestep deliberately planted distractors. Grading is pass/fail for each task and based on meeting all deterministic assertions on simulated app state (e.g., the correct CRM updates were all applied).

On AutomationBench’s leaderboard, which measures performance on a private held-out eval set, Claude Opus 5 (`max` effort) scored 26.0%, a substantial gain over Claude Opus 4.8 (`max` effort) at 17.0% and Claude Fable 5 at 17.4%. Notably at `medium` effort, Claude Opus 5 scored 24% at $0.89 cost per task, significantly outperforming both Claude Opus 4.8 and Fable 5 at less than half the cost.

![](assets/figures/p180-1.png)

:::caption
**[Figure 8.13.7.A] AutomationBench scores.** Claude Opus 5 has higher performance and lower task cost than any previous Claude model.
:::

### 8.14 ARC-AGI

#### 8.14.1 ARC-AGI-1 & ARC-AGI-2

ARC-AGI is a fluid intelligence benchmark developed by the ARC Prize Foundation. It is designed to measure AI models’ ability to reason about novel patterns given only a few (typically around 3) examples. Models are given input-output pairs of grids satisfying some<!-- p.181 --> hidden relationship, and are tasked with inferring the corresponding output for a new input grid. These tests use semi-private validation sets to ensure consistency and fairness across models.

The ARC Prize Foundation reports that Claude Opus 5 achieved a verified score of 97.50% on ARC-AGI-1 and 90.42% on ARC-AGI-2 at `max` effort on their semi-private datasets. The ARC-AGI-2 result is a substantial advance over prior Claude models (Claude Opus 4.7 reported 75.83% at `max` effort).

![](assets/figures/p181-1.png)

:::caption
**[Figure 8.14.1.A] ARC-AGI-1 performance as reported by the ARC Prize Foundation.** Claude Opus 5 achieved 97.50% on ARC-AGI-1 at max effort.
:::

<!-- p.182 -->

![](assets/figures/p182-1.png)

:::caption
**[Figure 8.14.1.B] ARC-AGI-2 performance as reported by the ARC Prize Foundation.** Claude Opus 5 achieved 90.42% on ARC-AGI-2 at max effort.
:::

#### 8.14.2 ARC-AGI-3

ARC-AGI-3 is the ARC Prize Foundation's newest benchmark: an interactive evaluation built from novel, turn-based game environments with no instructions, rules, or stated goals. Models must explore each environment, figure out how it works and what winning looks like, and carry what they learn across increasingly difficult levels; scoring is efficiency-based and grounded in human action baselines. The reported results use a semi-private evaluation set of games.

The ARC Prize Foundation reports that Claude Opus 5 achieved a verified score of 30.16%, set at high effort, on the ARC-AGI-3 semi-private evaluation, roughly four times the best previously reported score on the official leaderboard. GPT-5.6 Sol reached 7.78% at max effort and Claude Opus 4.8 reached 1.52% at high effort. Results for Claude Opus 5 at max effort were not available at the time of release.

<!-- p.183 -->

![](assets/figures/p183-1.png)

:::caption
**[Figure 8.14.2.A] ARC-AGI-3 performance as reported by the ARC Prize Foundation.** Claude Opus 5 achieved a Relative Human Action Efficiency (RHAE) score of 30.16% at high effort.
:::

The ARC Prize Foundation also shared an analysis, produced by an LLM judge reviewing the model's transcript on a single game, of how Claude Opus 5 approached the task. The model completed Axis Reflect (ar25) with a score of 100, clearing all eight levels in 294 actions. The judge described its defining strength on this game as turning the visual puzzle into explicit algebra. By level 2 it had derived a simple reflection equation and by level 8 it had generalized this to two-dimensional reflections, partitioning 60 targets into mirrored quadrants, and calculating every piece's destination before executing. The judge also noted some hypothesis churn on one level, where the model explored elaborate, unverified theories before abruptly correcting itself, along with repetitive narration. But it observed that failed exploration updated the model's understanding rather than producing loops. The judge concluded: “Once the correct ontology is found, execution is extremely reliable.”

<!-- p.184 -->

### 8.15 Healthcare

#### 8.15.1 HealthBench results

HealthBench[^31] is an open-source evaluation developed to assess safety, accuracy, and communication across realistic healthcare contexts. The benchmark uses over 48,000 expert-written rubric items to grade 5,000 multi-turn patient conversations.

Claude Opus 5 achieved a raw score of 67.1%, which is the highest among all Claude models, ahead of Claude Mythos 5 at 62.5%, Claude Opus 4.8 at 58.8%, and Claude Sonnet 5 at 59.2%. After length adjustment, which penalizes verbose model responses, Claude Opus 5 achieved a score of 57.8%.

![](assets/figures/p184-1.png)

:::caption
**[Figure 8.15.1.A] HealthBench raw and length-adjusted scores**. All Claude models used adaptive thinking at max effort. Claude Opus 4.8 was the grader model. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in OpenAI’s GPT 5.5 system card. Shown with 95% CI..
:::

<!-- p.185 -->

#### 8.15.2 HealthBench Professional results

HealthBench Professional[^32] is a clinical task benchmark composed of 525 physician-authored conversations spanning clinical consults, documentation, and research tasks, each graded against rubric criteria by an LLM-as-a-Judge model.

Claude Opus 5 achieved a raw score of 73.4%, which is the highest amongst all Claude models, ahead of Claude Mythos 5 at 70.3%, Claude Opus 4.8 at 60.3%, and Claude Sonnet 5 at 62.4%. After length adjustment, which penalizes verbose model responses, Claude Opus 5 achieved a score of 59.8%.

![](assets/figures/p185-1.png)

:::caption
**[Figure 8.15.2.A] HealthBench Professional raw and length-adjusted scores**. All Claude models used adaptive thinking at max effort. Claude Opus 4.8 was the grader model. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model. Length-adjusted scores were calculated using the method published in the HealthBench Professional paper. Shown with 95% CI.
:::

<!-- p.186 -->

### 8.16 Multilingual performance

We evaluated Claude Opus 5 on three multilingual benchmarks—Global MMLU (GMMLU)[^33], INCLUDE[^34], and Multi-task Indic Language Understanding Benchmark (MILU)[^35]—to assess model performance across a range of languages. GMMLU extends the standard MMLU evaluation across 42 languages from high-resource languages such as French and German to low-resource languages such as Yoruba, Igbo, and Chichewa. MILU covers 11 languages—10 Indic languages (Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu) and English—and tests culturally grounded knowledge comprehension. INCLUDE covers 44 languages with questions drawn from regional academic and professional examinations, emphasizing in-language and in-culture knowledge rather than translated content.

#### 8.16.1 GMMLU results

![](assets/figures/p186-1.png)

:::caption
**[Figure 8.16.1.A] GMMLU average accuracy.** All Claude models used adaptive thinking at max effort. Scores were reported for a single trial. No tools or customized system prompts were provided to any model.
:::

<!-- p.187 -->

#### 8.16.2 MILU results

![](assets/figures/p187-1.png)

:::caption
**[Figure 8.16.2.A] MILU average accuracy.** All Claude models used adaptive thinking at max effort. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model.
:::

#### 8.16.3 INCLUDE results

![](assets/figures/p187-2.png)

:::caption
**[Figure 8.16.3.A] INCLUDE average accuracy.** All Claude models used adaptive thinking at max effort. Scores were averaged over 5 trials. No tools or customized system prompts were provided to any model.
:::

### 8.17 Life sciences capabilities

We continue to report evaluations in areas including computational biology, structural biology, organic chemistry, and protocol troubleshooting. These evaluations, many of which were developed internally by domain experts, focus on the capabilities that drive beneficial applications in basic research and drug development, complementing the CB risk<!-- p.188 --> assessments in [Section 2.2](#22-cb-evaluations) which focus on misuse potential. Although many of these evaluations are not publicly released, we briefly describe each below. For all evaluations except ProteinGym, Protocols and Protein design, Claude has access to a bash tool for code execution, a file editor and package managers for installing needed libraries. For ProteinGym, Claude has access to a bash tool and a file editor, but no package managers. For Protocols, Claude has access to bash, file editor, and web search tools. For Protein design, Claude has no tool access.

#### 8.17.1 BioMysteryBench

BioMysteryBench assesses a model’s ability to solve difficult, analytical challenges that require interleaving computational analysis with biological reasoning. Given unprocessed datasets, the model must answer questions such as identifying a knocked-out gene from transcriptomic data or determining what virus infected a sample. For this benchmark, we report the subset of problems that independent human experts were able to solve (“Human Solvable”) as well as the subset that remain unsolved by humans but have an objective, ground-truth solution (“Human Difficult”). (Note that we have removed 3 problems in the human-solveable set and 6 problems in the human-difficult set based on external feedback.)

In the Human Solvable subset, Claude Opus 5 achieved 90.1% ahead of Claude Mythos 5 at 89.0%, Claude Opus 4.8 at 88.5%, and Claude Sonnet 5 at 87.5%. On the Human Difficult subset, Claude Opus 5 again led at 49.4%, ahead of Claude Mythos 5 at 46.5%, Claude Opus 4.8 at 42.4%, and Claude Sonnet 5 at 34.1%.

#### 8.17.2 LatchBio Bioinformatics

Developed by LatchBio, these evaluations assess the ability to solve challenging real-world bioinformatics problems. The SpatialBench Verified variant tests the analysis of spatial transcriptomics data—gene expression mapped to physical locations in a tissue slice—across a set of 115 externally validated problems, requiring the model to answer biological questions about the sample from those results. The SingleCellBench variant tests the analysis of single-cell RNA sequencing data across 195 problems spanning standard workflows such as labeling cell types, finding differentially expressed genes, and correcting batch effects.

On SpatialBench Verified, Claude Opus 5 achieved the top score at 72.5%, ahead of Claude Mythos 5 at 69.2%, Claude Sonnet 5 at 67.8%, and Claude Opus 4.8 at 66.6%. On SingleCellBench, Claude Opus 5 again led at 60.6%, ahead of Claude Mythos 5 at 59.3%, Claude Opus 4.8 at 58.2%, and Claude Sonnet 5 at 56.2%.

<!-- p.189 -->

#### 8.17.3 ProteinGym Hard

This benchmark assesses a model’s ability to predict how mutations affect a protein’s function by ranking a subset of mutant protein sequences against the wild type sequence. It is scored by rank correlation against real lab measurements from the published ProteinGym benchmark. Claude Opus 5 achieved 47.7%, the strongest result, ahead of Claude Mythos 5 at 45.8%, Claude Opus 4.8 at 40.0%, and Claude Sonnet 5 at 36.6%.

#### 8.17.4 Protein Design

This benchmark assesses Claude’s ability to generate novel protein sequences conditioned on a variety of design constraints, such as natural language descriptions of a given protein family, knot-topology, globularity and structural motifs for enzyme active sites and binding pockets. It is scored by constraint satisfaction, protein folding confidence and sequence novelty. Claude Opus 5 achieved 42.5%, ahead of Claude Mythos 5 at 41.4%, Claude Opus 4.8 at 32.0%, and Claude Sonnet 5 at 21.2%.

#### 8.17.5 Organic chemistry, V2

We evaluated models’ fundamental skills spanning tasks like predicting molecular structures from spectroscopy data, designing multi-step synthetic routes, predicting reaction products, and understanding chemical structure images. This evaluation was recently updated to include more challenging problems recommended by expert chemists. Claude Opus 5 achieved a score of 61.6%[^36], the strongest result, ahead of Claude Mythos 5 at 58.9% and Claude Opus 4.8 at 50.4%, and a marked improvement over Claude Sonnet 5 at 40.6%.

#### 8.17.6 Protocols

This assessment looks at models’ ability to assist with molecular biology protocols, including by using web search tools to find additional details about protocols online. The “troubleshooting” variant assesses Claude’s ability to detect and fix errors in protocols. The “understanding” variant, created by Benchling, assesses Claude’s ability to take an online protocol and extend it in additional directions. For the Troubleshooting variant, Claude Opus 5 scored 61.1%, an improvement over Claude Opus 4.8 at 59.6%, though trailing Claude Mythos 5, which led at 66.7%, and Claude Sonnet 5 at 62.3%. For the Understanding variant, Claude Opus 5 achieved 78.4%, the strongest result by a wide margin, ahead of Claude Mythos 5 at 68.1%, Claude Opus 4.8 at 62.3%, and Claude Sonnet 5 at 60.5%.

<!-- p.190 -->

![](assets/figures/p190-1.png)

:::caption
[**Figure 8.17.6.A] Life sciences capability evaluations.** Performance of Claude Opus 5 and comparison models across the benchmarks shown; per-benchmark results are discussed in the sections above.
:::
[^23]: Surge AI (2026). Chartography: A benchmark for professional chart understanding. Surge AI. [https://surgehq.ai/blog/chartography](https://surgehq.ai/blog/chartography)

[^24]: Surge AI (2026). Chartography [Code repository]. GitHub. [https://github.com/surge-ai/chartography](https://github.com/surge-ai/chartography)

[^25]: Zhang, H., et al. (2026). BenchCAD: A comprehensive, industry-standard benchmark for programmatic CAD. arXiv:2605.10865. [https://arxiv.org/abs/2605.10865](https://arxiv.org/abs/2605.10865)

[^26]: Zhang, H., et al. (2026). BenchCAD [Code repository]. GitHub. [https://github.com/BenchCAD/BenchCAD-main](https://github.com/BenchCAD/BenchCAD-main)

[^27]: Yuan, M., et al. (2026). OSWorld 2.0: Benchmarking computer use agents on long-horizon real-world tasks. arXiv:2606.29537. [https://arxiv.org/abs/2606.29537](https://arxiv.org/abs/2606.29537)

[^28]: Surge AI. (2026). GDP.pdf: Can $100B AI models master the documents that run the world? [https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world](https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world)

[^29]: Patwardhan, T., et al. (2025). GDPval: Evaluating AI model performance on real-world economically valuable tasks. arXiv:2510.04374. [https://arxiv.org/abs/2510.04374](https://arxiv.org/abs/2510.04374)

[^30]: Shepard, D., & Salimans, R. (2026). AutomationBench. arXiv:2604.18934. [https://arxiv.org/abs/2604.18934](https://arxiv.org/abs/2604.18934)

[^31]: Arora, R. K., et al. (2025). HealthBench: Evaluating large language models toward improved human health. arXiv:2505.08775. [https://arxiv.org/abs/2505.08775](https://arxiv.org/abs/2505.08775)

[^32]: Soskin Hicks, R., et al. (2026). HealthBench Professional: Evaluating large language models on real clinician chats. arXiv:2604.27470. [https://arxiv.org/abs/2604.27470](https://arxiv.org/abs/2604.27470)

[^33]: Singh, S., et al. (2024). Global MMLU: Understanding and addressing cultural and linguistic biases in multilingual evaluation. arXiv:2412.03304. [https://arxiv.org/abs/2412.03304](https://arxiv.org/abs/2412.03304)

[^34]: Romanou, A., et al. (2024). INCLUDE: Evaluating multilingual language understanding with regional knowledge. arXiv:2411.19799. [https://arxiv.org/abs/2411.19799](https://arxiv.org/abs/2411.19799)

[^35]: Verma, S., et al. (2024). MILU: A Multi-task Indic language understanding benchmark. arXiv:2411.02538. [https://arxiv.org/abs/2411.02538](https://arxiv.org/abs/2411.02538)

[^36]: Note that Claude Opus 5 timed out for 10 out of 1260 attempts, which were excluded from aggregation, leading to ≤±0.006 effect on the score

