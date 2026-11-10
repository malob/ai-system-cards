<!-- source: source.pdf pages 243-254 -->

<!-- p.243 -->

### 8.15 ARC-AGI-3

ARC-AGI-3 is the ARC Prize Foundation’s newest benchmark: an interactive evaluation built from novel, turn-based game environments with no instructions, rules, or stated goals. Models must explore each environment, figure out the goals and mechanics, and carry what they learn across increasingly difficult levels. Scoring is based on how efficiently a model completes each level compared with human players.

The ARC Prize Foundation reports results with two harnesses. The Standard harness provides a consistent comparison across providers. The Provider Adapter harness, which we report for the first time in this system card, measures how well a model performs when it can use the context management features its provider designed for it.

The ARC Prize Foundation reports that Claude Fable 5.2 achieved a verified score of 79.26% with the Standard harness and 97.72% with the Provider Adapter harness on ARC-AGI-3, both at `high` effort. At `max` effort, Fable 5.2 scored 65.66% with the Standard harness and 94.90% with the Provider Adapter harness.

For comparison, the ARC Prize Foundation’s leaderboard reports GPT-6 Astra at 62.7% with the Standard harness and 98.6% with the Provider Adapter harness at `max` effort, and GPT-6.1 Sol at 52.7% and 96.2% at `max` effort.

<!-- p.244 -->

![](assets/figures/p244-1.png)

:::caption
**[Figure 8.15.A] ARC-AGI-3 scores** at `high` and `max` effort, with the Standard and Provider Adapter harnesses, as reported by the ARC Prize Foundation.
:::

### 8.16 Healthcare

We report Claude Fable 5.2’s results on HealthBench, HealthBench Professional, and PhysicianBench. Artificial Analysis ran HealthBench and HealthBench Professional independently, at our request, and has since [launched leaderboards for both](https://artificialanalysis.ai/articles/healthbench-professional-health-conversations). We ran PhysicianBench ourselves. All scores are at `max` effort unless otherwise stated.

Artificial Analysis graded HealthBench with GPT-4.1 and HealthBench Professional with GPT-5.4 at low reasoning effort, as in OpenAI’s papers on the two benchmarks. We graded PhysicianBench with Claude Opus 5.

In Artificial Analysis’s runs and in our own, Fable 5.2, Claude Sonnet 5.5, Claude Opus 5.5, and Claude Fable 5.1 ran with fallbacks on: if a safety classifier blocked a request or stopped an answer, another model could answer. We report raw scores for HealthBench and HealthBench Professional, with the length-adjusted score (as OpenAI reports it) in parentheses. GPT-6 Astra’s scores on those two evaluations come from Artificial Analysis, and its PhysicianBench score comes from our own run through OpenAI’s public API. None of these scores come from OpenAI’s published figures.

<!-- p.245 -->

Our recent system cards reported HealthBench and HealthBench Professional from our own runs, graded by Claude Opus 4.8, so the scores in this system card are not comparable with the scores in those cards.

#### 8.16.1 HealthBench (Artificial Analysis)

![](assets/figures/p245-1.png)

:::caption
**[Figure 8.16.1.A] HealthBench scores, as measured by Artificial Analysis.** Full-color bars are raw scores and light bars are length-adjusted scores. All models are run at `max` effort and graded by GPT-4.1.
:::

Claude Fable 5.2 scored 58.8% (59.6% adjusted), below all four other Claude models and above GPT-6 Astra at 56.9% (58.2% adjusted). Claude Sonnet 5.5 scored 65.9% (62.1%), Claude Opus 5.5 scored 64.3% (57.0%), Claude Fable 5.1 scored 63.9% (57.2%), and Claude Haiku 5.5 scored 61.2% (58.5%).

On length-adjusted scores, Fable 5.2 was below Sonnet 5.5 and above the other four models. Its score fell slightly as effort rose, from 60.1% (60.4% adjusted) at `low` to 58.8% (59.6% adjusted) at `max`. We have no confidence intervals for these scores, so we do not report whether a difference is within noise.

<!-- p.246 -->

#### 8.16.2 HealthBench Professional (Artificial Analysis)

![](assets/figures/p246-1.png)

:::caption
**[Figure 8.16.2.A] HealthBench Professional scores, as measured by Artificial Analysis.** Full-color bars are raw scores and light bars are length-adjusted scores. All models are run at `max` effort and graded by GPT-5.4 at low reasoning effort.
:::

Claude Fable 5.2 scored 71.1% (67.7% adjusted), 0.3 points below Claude Opus 5.5 at 71.4% (59.9% adjusted) and above the other four models. Claude Sonnet 5.5 scored 70.8% (63.0%), GPT-6 Astra scored 69.7% (66.0%), Claude Fable 5.1 scored 69.2% (57.8%), and Claude Haiku 5.5 scored 64.8% (58.4%).

On length-adjusted scores, Fable 5.2 was the highest of the six models shown. The length adjustment lowered its score by 3.4 points, less than for the other five models. At all five effort levels, Fable 5.2 scored 70.5% to 71.4% (66.9% to 68.1% adjusted). We have no confidence intervals for these scores, so we do not report whether a difference is within noise. For the same Claude models, these scores are about 4 to 6.5 points lower than in our recent [system cards](https://www.anthropic.com/system-cards).

<!-- p.247 -->

#### 8.16.3 PhysicianBench

![](assets/figures/p247-1.png)

:::caption
**[Figure 8.16.3.A] PhysicianBench pass rate.** Share of attempts passed, over 100 tasks with five attempts each (one attempt each for GPT-6 Astra). All models are run using `max` effort. GPT-6 Astra passed 48.0% at `max` and 55.0% at `high` reasoning effort.
:::

PhysicianBench is a public benchmark of 100 physician tasks carried out in an electronic health record (EHR). Claude Fable 5.2 passed 64.4% of attempts. This was 4.0 points below Claude Opus 5.5 at 68.4%—the highest score of any released Claude model—1.2 points above Claude Sonnet 5.5 at 63.2%, and 3.4 points above Claude Fable 5.1 at 61.0%. All three differences are within noise: each 95% confidence interval includes zero.

Fable 5.2 passed 55.0% of attempts at `low` effort (three runs pooled) and 61.8% at `high` effort. This increase of 6.8 points has a 95% confidence interval of 3.2 to 10.4. From `high` effort upward (64.6% at `xhigh`, 64.4% at `max`), no two levels could be statistically distinguished.

### 8.17 Multilingual performance

We evaluated Claude Fable 5.2 on two multilingual benchmarks, Global MMLU (GMMLU) and the Multi-task Indic Language Understanding Benchmark (MILU), to assess performance across a range of languages.

GMMLU extends the standard MMLU evaluation across 42 languages, from high-resource languages such as French and German to low-resource languages such as Yoruba, Igbo, and Chichewa. MILU tests culturally grounded knowledge comprehension in 11 languages: 10<!-- p.248 --> Indic languages (Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu) and English.

#### 8.17.1 GMMLU results

On GMMLU, Claude Fable 5.2 achieved an average accuracy of 96.0% across 42 languages, ahead of Claude Opus 5.5 at 94.3%, Claude Fable 5.1 at 94.0%, and Claude Sonnet 5.5 at 92.1%.

![](assets/figures/p248-1.png)

:::caption
**[Figure 8.17.1.A] GMMLU average accuracy.** All Claude models used adaptive thinking at `max` effort and were run with safety classifiers enabled. Blocked or unanswered questions (0.5% for Fable 5.2, 0.5% for Opus 5.5, 1.3% for Fable 5.1, and under 0.1% for Sonnet 5.5) were left out of the average rather than scored as wrong. Scores are reported for a single trial. No tools or customized system prompts were provided to any model.
:::

#### 8.17.2 MILU results

On MILU, Claude Fable 5.2 achieved an average accuracy of 94.1% across 11 languages, ahead of Claude Opus 5.5 at 93.1%, Claude Fable 5.1 at 93.0%, and Claude Sonnet 5.5 at 91.6%.

<!-- p.249 -->

![](assets/figures/p249-1.png)

:::caption
**[Figure 8.17.2.A] MILU average accuracy.** All Claude models used adaptive thinking at `max` effort and were run with safety classifiers enabled. Blocked or unanswered questions (under 0.2% for each of the four models) were left out of the average rather than scored as wrong. [Opus 5.5](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf), [Fable 5.1](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf), and [Sonnet 5.5](https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf) values are as reported in their system cards. Scores are averaged over five trials and shown with 95% CI. No tools or customized system prompts were provided to any model.
:::

### 8.18 Life sciences capabilities

This section reports evaluations of capabilities that support beneficial life sciences research. They cover bioinformatics, cell-based assay analysis, biomedical image analysis, medicinal chemistry, protein design, protein understanding, and laboratory protocols. Unless otherwise noted, each Claude score is the average over five attempts per problem, sampled with adaptive thinking at `max` effort.

We evaluated Claude Mythos 5.2 through the API with its biology safeguards turned off, so these results reflect the capabilities of the underlying model rather than of the deployed system. When available, we also report scores for GPT-6 Astra, which we ran through the OpenAI API at `max` reasoning effort. Likewise, we report scores for Gemini 4 Argon, which we ran through Google’s Vertex AI API at the highest level of thinking. Attempts blocked by safety filters on either model are excluded from our evaluation results.

<!-- p.250 -->

![](assets/figures/p250-1.png)

:::caption
**[Figure 8.18.A] Life science benchmarks.** Performance of Claude Mythos 5.2 and comparison models across the benchmarks shown. Per-benchmark results are discussed in the sections below.
:::

#### 8.18.1 LatchBio Bioinformatics

Developed by LatchBio, this set of evaluations assesses a model’s ability to solve challenging real-world bioinformatics problems. The SpatialBench Verified variant tests analysis of<!-- p.251 --> spatial transcriptomics and chromatin-accessibility data, and the SingleCellBench variant tests analysis of single-cell RNA sequencing data. For both variants, Claude has access to a bash tool for code execution, a file editor, and a prespecified set of installed packages. On SingleCellBench, Claude Mythos 5.2 achieved the highest performance of our models: 65.6%, compared with 61.2% for Claude Opus 5.5 and 61.8% for Claude Mythos 5.1.

#### 8.18.2 Morphology-to-molecule matching

Developed with Axiom Bio, this benchmark assesses whether a model can match four sets of multi-channel cell imaging data from Axiom’s human liver in vitro assay to the four shuffled molecule-dose perturbations that treated the wells in each image set. Claude Mythos 5.2 performed similarly to Claude Opus 5.5 (35.2%, compared with 34.0%) and outperformed both GPT-6 Astra (22.8%) and Gemini 4 Argon (25.2%).

#### 8.18.3 Medicinal chemistry

This benchmark assesses whether a model can reason about absorption, distribution, metabolism, and excretion (ADME)-related properties of drug-like molecules. Each of the 504 questions presents several real compounds from drug discovery programs as chemical structures and asks which candidate had the highest or lowest measured value of one such property. Claude Mythos 5.2 achieved our highest performance: 69.0%, compared with 63.5% for Claude Opus 5.5 and 57.7% for Claude Mythos 5.1.

#### 8.18.4 Protein design

These benchmarks assess Claude’s protein design abilities. The Sequence Generation task assesses Claude’s ability to generate novel protein sequences conditioned on a variety of design constraints. We ran only one attempt per problem on this task. The De Novo Binder Design task assesses whether Claude can carry out an extended protein design campaign on its own. For each of 15 protein targets, Claude is given the target’s structure, access to a set of open-source protein design and folding models and bioinformatics tools, one NVIDIA H200 GPU, and a fixed budget of 24 hours of wall-clock time to design a set of 30 miniprotein binders against the target.

Claude Mythos 5.2 achieved new highs for both benchmarks: 64.6% on sequence generation, compared with 60.2% for Claude Opus 5.5, and 85.1% on de novo binder design, compared with 82.6% for Opus 5.5. Claude Mythos 5.2’s mean score on de novo binder design was the highest of the four models on each of the 15 targets, though on five of them the margin was about one percentage point or less.

<!-- p.252 -->

#### 8.18.5 Biomedical image analysis

This benchmark assesses a model’s ability to carry out quantitative analyses of biomedical images using data from public biomedical image analysis competitions. Task inputs span CT, MRI, histopathology, dermoscopy, retinal, ultrasound, microscopy, and other imaging. We scaled the scoring to reflect Claude’s performance relative to the best results achieved in the associated competition. We ran one attempt per problem. Claude Mythos 5.2 scored 80.7%, higher than Claude Opus 5.5 (at 71.4%) and GPT-6 Astra (at 77.5%).

#### 8.18.6 Protocols

This benchmark assesses a model’s ability to help with molecular biology protocols. The Troubleshooting variant asks Claude to detect and fix issues in protocols. The Understanding (V2) variant, created by Benchling, gives Claude a real laboratory protocol (such as a protocols.io document, vendor manual, or core facility guide) and a practical question about applying or adapting it. On troubleshooting, Claude Mythos 5.2 achieved a new high: 77.1%, compared with 73.7% for Claude Opus 5.5 and 70.2% for Claude Mythos 5.1.

#### 8.18.7 Protein domain identification

This new protein understanding task tests whether Claude can identify which domains are contained in a protein from its amino acid sequence. On each question, Claude is asked, without tools, to choose between the correct Pfam family name and a set of other families chosen to resemble the correct domain. In this evaluation, Claude Mythos 5.2 achieved much higher performance than any model we tested: 91.8%, compared with 73.6% for Claude Opus 5.5 and 63.5% for Claude Mythos 5.1.

#### 8.18.8 Protein mutation attribution

This new protein understanding task tests whether Claude can predict changes in function (e.g., binding affinity to a partner protein, thermal stability, or expression yield) based on mutations in the sequence. On each task, Claude is given measured values for a reference protein and a variant containing four to 16 mutations and asked to attribute the changes in the measured values to the mutations. Claude is also given structure-analysis tools and the structure of the protein (or a close relative) in complex with a binding partner. The final score is derived from the rank correlation with per-mutation contributions computed from withheld measurements of intermediate variants.

Claude Mythos 5.2 scored 51.5%, outperforming Claude Opus 5.5 (49.5%) and Claude Mythos 5.1 (48.0%).

<!-- p.253 -->

### 8.19 CVE Rediscovery

CVE Rediscovery measures a model’s ability to identify real-world vulnerabilities in open-source codebases. The model receives a known-vulnerable snapshot of a real repository, without its commit history, and a list of files the fix changed. It does not have internet access. The model must find security bugs in a single attempt, but it does not need to produce an exploit or triggering input. A model-based judge compares the bug reports with the published security advisory and its fix. An attempt counts as a success if any report has the same root cause as the advisory.

The evaluation includes 1,829 advisories published in October 2026, out of roughly 17,000 CVEs published that month. We only included advisories for which we could identify an open-source repository and a vulnerable commit, and where we could localize the bug to at most 20 source files, and we excluded the Linux kernel. Information about some of these advisories may have been made public earlier, so we cannot rule out that some might have been included in model training.

At `max` effort, with cyber and bio safeguards turned off, Claude Mythos 5.2 rediscovered 89.6% of the advisories, compared with 81.3% for Claude Opus 5.5 and 78.3% for Claude Mythos 5.1. Claude Mythos 5.2 scored highest at every effort level, though effort levels with the same name are not directly comparable across models (Figure 8.19.A).

Models can submit several reports, because they may also find real bugs that are not yet known and are thus unscored. Counting only the first five reports per attempt does not alter the models’ ranking, but it lowers Claude Mythos 5.2’s score at `max` effort by 4.4 points and every other model’s score by less than 2 points. When we count only the first report, Claude Mythos 5.2 remains in first place at every effort level, but its lead over Opus 5.5 at `max` effort narrows from 8.3 to 2.6 points. Applying stricter judging criteria to a small sample at `max` effort lowered scores by about 1–4 points but did not suggest any obvious grader bias toward any model.

<!-- p.254 -->

![](assets/figures/p254-1.png)

:::caption
**[Figure 8.19.A] Claude Mythos 5.2 scores above Opus 5.5 and Claude Mythos 5.1 at every effort level on CVE Rediscovery.** Each point is one effort level, plotted against mean output tokens per attempt. Effort levels with the same name are not necessarily comparable across models. Results cover 1,829 advisories from October 2026, with one attempt each and cyber and bio safeguards turned off. The model is given the project as it was just before the fix was applied, along with a list of source files the fix changed. An advisory counts as found if at least one of the model’s reports matches the real bug.
:::
