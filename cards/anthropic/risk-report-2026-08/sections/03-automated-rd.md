<!-- source: source.pdf pages 093-114 -->

<!-- p.93 -->

## 3 Autonomy threat model 2: Risks from automated R&D

### 3.1 Overview

<table><tbody>
<tr><td><b>Threat model</b></td><td>Highly capable AI models may be able to perform automated research and development (R&amp;D) that rapidly accelerates progress in technical fields. Although there could be enormous benefits from this, these would come with corresponding risks. Under human control, such acceleration could disrupt the balance of power both within and between nation states. If combined with an AI system pursuing dangerous goals of its own, it could lead to catastrophic harm initiated by the AI itself. Rapid automated R&amp;D in the field of AI research is of particular interest because of the potential to produce a variety of further AI-related risks.</td></tr>
<tr><td><b>Overall risk assessment</b></td><td>Low. We do not believe our models meet either RSP criterion for this threat model. However, we are less confident in this assessment than we were in prior risk reports, since our most concrete task-based evaluations have “saturated”—i.e., they no longer capture increases in models’ capabilities—and because we are seeing early signs of potential acceleration.</td></tr>
<tr><td><b>Relevant AI model(s)</b></td><td><p>When considering whether our models can fully automate the work of our Research Scientists and Research Engineers, we focus on Claude Mythos 5, Claude Mythos Preview, and Model 2, our most capable models as of the coverage date. When considering whether our models can dramatically accelerate our AI R&amp;D work, we consider the entire trajectory of our model development, since the threat concerns the rate of progress rather than the properties of any single model.</p><p>We also consider the possibility of automated or dramatically accelerated R&amp;D in other domains via expert interviews in <a href="#36-automated-rd-in-other-domains">Section 3.6</a>; these reflect usage of Claude Mythos Preview and Mythos 5 (in the case of our internal experts) and publicly-available models from a mixture of AI companies roughly comparable to Opus 4.7 or Opus 4.8 (in the case of external experts).</p></td></tr><!-- p.94 --><tr><td><b>Current usage and capabilities</b></td><td><p>Claude Mythos 5 and Model 2 are used extensively for research and engineering within Anthropic, both interactively and via persistent agent deployments; Claude now authors a large majority of the code merged into our production codebases.</p><p>Our Responsible Scaling Policy specifies two criteria for this threshold. At present, neither of these have been met. First, our Mythos-class models do not seem close to fully substituting for our full staff of Research Scientists and Research Engineers. Second, we have observed some acceleration of AI progress, and believe that AI assistance with R&amp;D is providing significant speedups to our research efforts, but (we believe) not to a degree that doubles our overall rate of progress beyond that which we saw prior to such AI assistance.</p></td></tr>
<tr><td><b>Current risk mitigations</b></td><td><p>This is a broad threat model. The risk mitigations it calls for are broad and overlap heavily with those listed elsewhere in this report: assessing and avoiding dangerous forms of misalignment, building increasingly robust safeguards against misuse, leveling up our information security, and more.</p><p>We don’t believe our current risk mitigations are sufficient to keep risks low in a world of highly automated or dramatically accelerated R&amp;D.</p></td></tr>
<tr><td><b>Looking forward</b></td><td>We continue to work on improving risk mitigations across the board, including those outlined in our <a href="https://www.anthropic.com/responsible-scaling-policy/roadmap">Frontier Safety Roadmap</a>. We also hope to improve our assessment of the risks of R&amp;D acceleration by continuing to identify and report on potential leading indicators of such acceleration.</td></tr>
</tbody></table>

:::caption
**[Table 3.1.A] Summary of autonomy threat model 2:** Risks from automated R&D.
:::

### 3.2 Threat model

**The threat:** We believe that AI models could, in the next few years, have a broad range of capabilities that exceed human capabilities. In particular, most or all of the work needed to advance research and development in key domains—from robotics to energy to cyberwarfare to AI R&D itself—may become automatable.

<!-- p.95 -->

If this is correct, there could be enormous benefits, but these benefits would come with several distinct but related concerns:

1. Sufficiently rapid progress in some areas of technology could change power structures both within and between nations. For example, if an authoritarian regime built a self-reinforcing lead in AI over the rest of the world, this lead could compound into a major advantage in science and technology—which could in turn translate to very sudden and disruptive advances in the ability to wage war, surveil citizens, and/or wield extremely powerful technology over the long term.
2. If AI models develop [dangerous goals](https://www.anthropic.com/research/agentic-misalignment) while heavily automating R&D in key domains, they may cause unbounded harm—up to and including humanity losing control over civilization entirely—by leveraging novel technology and their access to it.
3. If AI can be used to automate AI R&D itself, the result may be extreme acceleration in AI progress, putting a very broad set of risks on the table, including but not limited to those discussed in this report.

**Role of AI:** Automation of R&D could, under certain circumstances, cause dramatic and disruptive acceleration in the rate of progress, contributing to unexpected power imbalances (between different humans or groups of humans, or between humans and AIs).

**Potential magnitude of impact:** We are most concerned with major, enduring changes in the global balance of power (either between humans or passing to AI systems themselves). The value at stake could be a multiple of what’s at stake in any of the other threat models discussed here.

**Likelihood of impact:** The probabilities related to this threat model are difficult to assess, and we do not have consensus on a specific likelihood. We think impacts of the size alluded to above are at least plausible if and when AI becomes capable of automating nearly everything humans do in advancing R&D in key domains, including AI itself.

**RSP threshold:** The RSP has two different criteria for meeting this threshold in the domain of AI R&D:

1. If our models would be able to “fully substitute for our entire set of Research Scientists and Research Engineers, at competitive costs (i.e., within a factor of 5)." We discuss this criterion in [Section 3.4](#34-substitution-of-our-ai-models-for-anthropic-researchers).
2. If there is “dramatic acceleration” of the pace of AI progress for reasons that likely relate to the automation of AI R&D. We discuss this criterion in [Section 3.5](#35-acceleration-of-ai-progress-due-to-automated-ai-rd).

<!-- p.96 -->

We do not think that our models as of the coverage date meet either of these criteria, as discussed below.

**Why this is a priority threat:** While there are a large number of possible threats from AI, our best working guess is that the automation of R&D will be the one most likely to lead to globally transformative impacts like those sketched above.

**Note:** As noted in our RSP, our evaluations for the automated R&D threat model focus centrally on the case of *AI* R&D (as opposed to R&D for other technical domains), for three reasons:

1. We expect this domain to play to the strengths of current AI systems, such that we would likely see dramatic acceleration in AI R&D before many other fields.
2. We can measure progress in this domain earlier and with more fidelity than in other fields, because we use our AI models extensively in pursuit of AI R&D tasks and have a great deal of information about such internal use.
3. Models capable of dramatically accelerating AI R&D development could lead in short order to much *more* powerful AI systems, via recursive self-improvement. This process would very quickly raise concerns about almost all of the other threat models in this report.

We also include an early assessment of the degree of R&D automation in domains other than AI in [Section 3.6](#36-automated-rd-in-other-domains). We believe that current AIs are very far from being capable of full automation or transformative acceleration in these domains.

### 3.3 Relevant AI models

For our assessment of whether AI models can substitute for Anthropic researchers ([Section 3.4](#34-substitution-of-our-ai-models-for-anthropic-researchers)), we focus on Claude Mythos Preview, Claude Mythos 5, and Model 2, our most capable models deployed internally as of the coverage date.[^39] (We include discussion of models other than Model 2 because in some cases we have more data on their failure modes or substitution potential than with Model 2, for instance evidence in the system cards about those models.)

<!-- p.97 -->

For our assessment of the degree of AI progress acceleration within Anthropic ([Section 3.5](#35-acceleration-of-ai-progress-due-to-automated-ai-rd)), we consider the entire trajectory of our history of model development, to assess trends in the rate of progress over time.

For our assessment of automated R&D in other domains ([Section 3.6](#36-automated-rd-in-other-domains)), our evidence draws on interviews with subject-matter experts conducted in May and June 2026. For internal experts, we expect their assessment was based in large part on use of Claude Mythos Preview and/or Claude Mythos 5. For external experts, we expect their assessments drew on a mixture of publicly available models from a variety of AI developers at the time of the interview, likely broadly comparable to Opus 4.7 or Opus 4.8 in capability.

### 3.4 Substitution of our AI models for Anthropic researchers

The first of the two criteria under which our RSP considers our automated R&D threshold to be met is if “our models would be able to fully substitute for our entire set of Research Scientists and Research Engineers, at competitive costs (i.e., within a factor of 5)." We think this is not the case.

We are strongly incentivized to have our models substitute to the greatest extent possible for both the technical skills and general scientific/strategic judgment (or “research taste”) of all members of technical staff at Anthropic. Technical talent is scarce, and we invest heavily in this area to help improve our models. Despite that incentive, and despite very heavy use of Claude in our research, we believe that our models do not yet substitute for our Research Scientists and Research Engineers, especially relatively senior ones. (For instance, it is very frequently the case that Anthropic researchers work on tasks which it would be extremely valuable to complete quickly, have the ability to use extremely large amounts of AI labor to help with these tasks if they wished, and choose to make use of only moderate amounts of AI because they are bottlenecked on steps which they do not trust our AI models to perform correctly.)

In practice, considerations like the above are the dominant source of our evidence about this threshold: we believe it would be clear to us if models were capable of substituting, even at high cost, for the technical work of our entire research staff, and the fact that we do not perform such substitution even when strongly incentivized to is evidence against our models having this level of capability.[^40] Because that experience is inherently difficult to<!-- p.98 --> report in a document of this nature, in this section we summarize the more legible evidence we have collected: examples of failure modes from internal use, researcher self-reports, and automated evaluations on internal R&D tasks.

#### 3.4.1 Failure modes from internal use

One important part of our reasoning on substituting AI models for human researchers involves collecting examples where Claude falls short of what a competent human researcher would do on comparable tasks.

Sections 2.3.3 and 2.3.4 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://anthropic.com/claude-mythos-5-system-card) present our most recent such collection, drawn from a sample of 886 day-to-day sessions on internal tasks. The system cards for [Claude Opus 4.8](https://anthropic.com/claude-opus-4-8-system-card) and [Claude Mythos Preview](https://www.anthropic.com/claude-mythos-preview-system-card) present comparable collections for those models. We do not repeat that material here, but summarize the broad strokes and our takeaways.

The recurring failure patterns are: stating an easy-to-check guess as fact or reporting work as verified when it was not (57/886 sessions across two clusters in the Mythos 5 sample); working around a block instead of stopping (9/886); ignoring an explicit instruction or required step (4/886); and inventing key details that were never observed (3/886). Failures of this kind recur even when the relevant correction is present in memory files or has just been given by the user. The system card also presents median-quality examples of *typical* internal use, in which the model is largely successful but a human still often catches at least one substantive error per session.

We conclude that even though Mythos 5 can often execute on well-scoped tasks much more rapidly and more cheaply than unassisted Anthropic staff, it has meaningful weaknesses that prevent it from fully replacing the technical work of our entire research staff.

These weaknesses are related to calibration, self-monitoring, and judgment, which are precisely the properties that distinguish reliable autonomous research work from work requiring a human in the loop. We note that this judgment gap is narrowing on at least some measures.

We expect this kind of analysis to understate the extent of capability failures, because internal users are unlikely to deploy Claude at tasks at which they are confident it will not succeed, so fewer of these sessions will be from tasks which models are clearly not yet capable enough to perform.

<!-- p.99 -->

#### 3.4.2 Researcher survey

For each frontier model from Claude Opus 4.5 through Claude Mythos Preview, we surveyed a sample of Anthropic technical staff on (a) the productivity uplift they experienced from the model relative to no AI assistance; and (b) whether they felt the model qualified as a drop-in replacement for an entry-level Research Scientist or Engineer. We did not run a new survey for Claude Mythos 5. The most recent survey is the one reported for Claude Mythos Preview.

In that survey, the geometric mean self-reported uplift was on the order of 4×; 1 of 18 respondents thought we already had a drop-in replacement for entry-level Research Scientists or Engineers; 4 of 18 thought there was a ≥50% chance of reaching that bar with three months of iteration on the model’s scaffolding. Reported weaknesses relative to an entry-level researcher included the model’s skill at self-managing week-long ambiguous tasks, understanding organizational priorities, taste, verification, instruction-following, and epistemics.

These self-reports are not free of bias: respondents may overestimate uplift on tasks they chose to delegate to Claude and underestimate it where the gain is in latency rather than task difficulty. Moreover, productivity uplift on individual tasks does not translate directly into acceleration of research progress. We consider these surveys somewhat informative, but do not put a great deal of trust into their conclusions, and have deprioritized this source of evidence in favor of the other avenues of investigation described in this section.

#### 3.4.3 CoBench

The task-based AI R&D evaluation suite we have reported on in our system cards has reached the point where frontier models surpass human baseline performance on most tasks. Here, we describe a newer internal evaluation that is designed to measure capability on real Anthropic R&D tasks rather than proxies.

**CoBench** is an internal evaluation measuring how well a model, placed at a historical point in Anthropic’s infrastructure (that is, given a snapshot of our codebase, logs, internal messaging, and docs at a past timestamp), can diagnose the root causes of issues that Anthropic engineers actually solved. Our current version of this evaluation on which we report results below comprises 449 problems from parts of the technical organization most directly relevant to training models and running the infrastructure needed to do so, largely sourced from issues that were solved between February 2026 and April 2026. The evaluation is not a representative distribution of all such tasks, as it is moderately filtered for difficulty: the dataset is mostly restricted to problems that Mythos Preview failed to<!-- p.100 --> solve at least once in three tries, and without such filtering the dataset would be roughly twice as large. Problems are model-graded using a rubric that compares a solution to the root cause we identified in practice (which is not visible from the historical snapshot available to the evaluated model).

Scores on this evaluation are shown below for a number of recent Anthropic models:

![](assets/figures/p100-1.png)

:::caption
**[Figure 3.4.3.A] Relative performance of recent Anthropic models on CoBench.** Our Mythos-class models perform substantially better than other recent models, though still fall short of the performance we would expect from a system that could fully substitute for the work of Anthropic technical staff (see below).
:::

Based on manual inspection and validation of these problems and their grading process, we think our validation, scaffolding, and grading rubrics for these tasks are reliable enough that a model which was truly capable of fully substituting for Anthropic research staff would be able to score at least 85% on this evaluation. The remaining gap is attributable to issues such as:

- Cases where the human researchers reached an incorrect conclusion, or where the answer is ambiguous.
- Grader error, or cases where a rubric was written in an overly narrow way so as to exclude some valid answers.
- <!-- p.101 -->Cases where human researchers would have been unable to solve the issue given access only to the (quite broad, but not unlimited) data sources and permissions which models in this evaluation are able to use.[^41]

The results shown above are from the best-performing of a number of scaffolds used, including ones we regularly use in real-world internal Anthropic use for tasks similar to this, and we find that giving Mythos 5 a 900,000 token budget instead of the 300,000 token budget used in the figure above only improves scores by about 3 percentage points. Nonetheless, we expect that dedicated effort put into improving the harness for this specific evaluation could produce significant further gains.

We believe this is some evidence that our models are not fully capable of all the things we believe our Research Scientists and Engineers would be able to do. However, given that this dataset was filtered based on Mythos Preview success rates (as noted above), performance may be somewhat underelicited, and we have only an uncertain estimate that full equivalency to our teams would mean 85% success, we don’t think this evidence is as strong as the high-level considerations discussed at the start of [Section 3.4](#34-substitution-of-our-ai-models-for-anthropic-researchers).

### 3.5 Acceleration of AI progress due to automated AI R&D

The second of the two criteria under which our RSP considers our automated R&D threshold to be met is if “there is ‘dramatic acceleration’ of the pace of AI progress for reasons that likely relate to the automation of AI R&D.”

Some background on our thinking:

- The most acute version of this threat model, and the one we consider most decision-relevant, is a transition to super-exponential progress in AI capability: a regime in which AI-driven automation of AI R&D compounds, producing something like a 10³–10¹⁰× effective scaleup within a year.
- The risk threshold set out in our RSP—a doubling of the pace of progress beyond pre-AI-acceleration rates, attributable to automation of AI R&D—functions as a potential early warning, rather than evidence that the threat has already materialized.

<!-- p.102 -->

In the past, the main evidence we have presented for the acceleration criterion has been trends in the Anthropic ECI (AECI), our internal fork of Epoch AI’s [Epoch Capability Index](https://arxiv.org/abs/2512.00193) (see Section 2.3.6 of the [Claude Mythos Preview System Card](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf) for methodology).

In addition to analyzing AECI, we have also been investigating internal leading indicators for capabilities advances (that is, metrics that we believe could be predictive of later trends in AECI). The nature of these indicators, and trends in them, are sensitive and not included in the public version of this report.

#### 3.5.1 AECI capability trajectory

![](assets/figures/p102-1.png)

:::caption
**[Figure 3.5.A] The Epoch Capabilities Index** (ECI) synthesizes performance across many benchmarks into one number per model. Our version of this metric, the Anthropic ECI, is powered by internal benchmark results, so scores are not directly comparable to Epoch’s public ECI leaderboard. Colored dots are the most recent models. Error bars are 95% percentile CI over 100 [IRT](https://en.wikipedia.org/wiki/Item_response_theory) refits, each on a random 80% subsample of benchmarks. The dotted line shows a linear fit of the frontier before Claude Mythos Preview. We set the (arbitrary) units of the scale by fixing Claude Sonnet 3.5 to have a value of 130, so it has a zero-width confidence interval.
:::

<!-- p.103 -->

As noted in the [Claude Mythos Preview System Card](https://www.anthropic.com/claude-mythos-preview-system-card), Mythos Preview departed from the previous trendline, but we have fairly high confidence in our attribution of this outcome to specific research progress that (from talking to the humans involved) we do not believe was significantly accelerated by AI.

Claude Mythos 5 lies above the historical score trendline by a similar amount to Mythos Preview, which is weak evidence against a dramatic increase in overall model capability trends over time. Based on limited data, Model 2 (not shown on this figure) appears to be around 1.5 points higher on AECI than Claude Mythos 5, with large error bars (a smaller increase than the one from Claude Mythos Preview to Claude Mythos 5). Note that some of the error from absolute error bars in this figure derives from sources of variance shared between nearby models (like a limited pool of evaluations to draw on, rather than sample-to-sample variance in scores on those evaluations), such that our *relative* comparisons of adjacent models are somewhat higher confidence than would be suggested by a model with independent uncertainty.

#### 3.5.2 Conclusions on the overall degree of AI R&D acceleration

Our leading indicators point to a picture of meaningful acceleration starting in early-to-mid 2025, though by less than a factor of 2. We are fairly confident in attributing the acceleration in 2025 to factors other than our use of AI models, though we also believe that our AI models have been a key factor in the faster trends *continuing* through the coverage date.

We conclude that the overall pace of progress remains below the RSP threshold of a doubling over pre-AI-assisted rates of progress attributable primarily to AI R&D automation, but even with our additional sources of data this conclusion is uncertain and subject to some lag (such that we would have difficulty measuring very recent acceleration).

### 3.6 Automated R&D in other domains

#### 3.6.1 Introduction

In addition to AI R&D, our threat model extends to non-AI domains where full automation or dramatic acceleration of top-tier research teams could cause risks to international security or upset the global balance of power.

We do not believe our AI systems fit this description. One reason is that we don’t yet see this level of automation or acceleration in AI R&D, which we’d expect to precede other<!-- p.104 --> domains, given how intently AI developers are focused on automating their own work. We also believe we would be generally aware (via e.g. anecdotes) if AI were dramatically accelerating other domains to the point of causing risks to international security or upsetting the global balance of power.

To further inform this assessment, we conducted semi-structured interviews with 31 academics, scientists, industry experts, government officials, technology firm executives, and frontier practitioners across the domains of robotics, energy, biotechnology, semiconductors, weapons development, neurotechnology, and nanotechnology. Some interviewees spoke to multiple domains. Most interviewees were external to Anthropic. We use these interviews as a rough litmus test, rather than a rigorous or comprehensive assessment. Our sample size was small and the interviews were conducted in a semi-structured manner rather than as a formal survey.

Overall, these interviews were overwhelmingly consistent: AI systems are neither fully automating R&D in key non-AI domains, nor accelerating it to the degree the RSP threat model envisions—that is, enough to produce geopolitically significant developments in a short timeframe. Given that the current rate of R&D progress varies widely between domains, this magnitude of acceleration would entail an extraordinary speedup over the current rate of progress in some domains. Some interviewees did note that while AI is not fully automating their field, it is dramatically accelerating R&D in a normal sense—but not dramatically to a degree that could be causing risks to international security or upsetting the global balance of power.

Interviewees varied in their exposure to frontier AI models. Some were daily users of frontier AI models, others used AI less frequently, or relayed information on AI usage from others. For example, some interviewees attested to the role of AI systems in R&D in their respective domains from the perspective of supervisors, executives, investors, or funders.

In general, interviewees reported that the most significant automation related to R&D is taking place in coding work. For example, one interviewee estimated an average time savings of one day’s worth of work per week; another interviewee estimated that coding agents enable teams to be 5–10× smaller while delivering the same software development work (note that this is not the same as delivering multiple times the progress in a given time period). Several interviewees also reported significant time savings in research and research-adjacent tasks such as figure-making, data analysis, and in non-R&D support tasks such as planning and decision-making. Some interviewees said that frontier AI models handle their fields’ established knowledge well but still lack research taste, or the ability to generate novel ideas or high-quality hypotheses, and so cannot yet substitute for the judgment, intuition, and creativity of top-tier researchers.

<!-- p.105 -->

Many interviewees also noted significant physical bottlenecks to full automation and/or dramatic acceleration. These included laboratory robotics, in-vivo validation, clinical trials, physical fabrication, and battlefield testing. Some interviewees raised doubts that these bottlenecks were possible to automate, even with future frontier LLMs.

#### 3.6.2 Robotics

We conducted three interviews with individuals working at the intersection of AI and robotics, and whose backgrounds ranged from reinforcement learning to hardware engineering.

All interviewees noted that frontier AI models are being heavily used in the software and ML side of frontier robotics R&D, but that robotics R&D as a whole is not close to being fully automated. One interviewee claimed that while time savings are significant, they are largely concentrated in planning and strategy. They estimated AI could probably currently save 10% of the end-to-end development cycle time for complex hardware products. This interviewee also stated that current models are unable to produce editable, parametric 3D CAD models and they did not expect AI systems to be capable of this in the next 12 months; narrower tasks like PCB layout, however, were said to be tractable today.

Interviewees identified spatial and physical reasoning as a key limitation of current frontier AI models, significantly hampering their ability to speed up robotics R&D, with one interviewee noting that physics-grounded models (e.g. trained on tactile, pressure, and force feedback data) would be a significant development for accelerating robotics R&D. Interviewees also identified upstream hardware manufacturing timeframes as another bottleneck to robotics R&D.

Interviewees gave a range of timeframe estimates for when to expect general-purpose robotics models, from six months to up to two years before the first working system.

#### 3.6.3 Biotechnology

We conducted seven interviews with individuals with backgrounds in synthetic biology, drug-development, biotech investment, immunology, genomics, biosecurity, and protein design.

Interviewees reported that AI systems were accelerating biotechnology R&D, with domain-specific ML models and LLMs contributing in different ways. Several interviewees reported that non-LLM ML models, particularly protein structure-prediction models, were transforming or accelerating computational design of antibodies, enzymes, and other<!-- p.106 --> proteins. Multiple interviewees reported that frontier LLMs are saving researchers time, particularly in data analysis, as well as in literature review, setting up experiments, and figure-making. Others noted that progress is being made in LLMs as orchestrators across partially automated laboratory settings when used in conjunction with non-LLM models though some cautioned this was early.

Although there was a range of opinions regarding the amount of R&D speed up being provided, several interviewees agreed that automation from frontier AI models was not yet producing significant breakthroughs in biotechnology. For example, one interviewee said that even the most advanced integration of robotics and frontier LLMs into automated laboratories was not yet capable of fully automating top-tier teams of researchers. They also remarked that AI assistance in experimental design and data analysis, while real, did not present dramatic acceleration, identifying robustly reliable laboratory robotics as the bottleneck to unlocking the kind of dramatic acceleration that the RSP envisions. Lending further support to this view, some interviewees remarked that AI systems have not meaningfully impacted the decade-long process (9–12 and 10–15 years were mentioned as standard timeframes in this context) it takes to go from identifying a drug candidate to treating patients. Interviewees variously cited critical bottlenecks of *in vivo* animal model validation and the time it takes to conduct clinical trials. One noted that AI has not been shown yet to be impacting speed, cost, or headcount in biotech. Only one interviewee expressed the view that AI is already capable of automating full teams in biotechnology, citing Chinese automated-synthesis operations and academic virtual-lab work. They also observed that laboratories are not yet fully autonomous and that AI adoption in the field is at an early stage. They estimated that AI is providing a boost of roughly 2–5×, depending on the workflow.

Multiple interviewees pointed to the next two years as a critical period, with one framing it as the window during which it would become clear whether AI is having a profound impact on drug development, and another expecting significant transformation for some protein-based therapeutics R&D. A third interviewee estimated that robots able to reliably perform roughly 25% of biology experiments are about a year away.

#### 3.6.4 Energy

We conducted five interviews with individuals with backgrounds in energy-storage materials, battery engineering, grid research, energy-sector investment, fusion energy, and condensed matter physics.

Some interviewees said that non-LLM ML models were accelerating energy-related materials discovery, including energy-storage materials and superconductor candidate<!-- p.107 --> screening. One interviewee said that bespoke ML models are able to screen and predict novel superconductor candidates, but that validating candidates still requires months of human expert-led experimental work. That same interviewee mentioned a claim, presented at a seminar they attended, of a 2–3× speedup from LLM agents in a solution-chemistry materials-discovery workflow. The interviewee found this claim credible based on their own experience in a different domain, where they were seeing a 2–5× speed up on purely computational research work, and were seeing graduate students now able to run several projects at once with AI assistance. They also said that LLMs still lacked the ability to generate realistic and original ideas, though they expected they might be capable of this in perhaps a year.

Another interviewee’s testimony suggests to us that we are far from our capability threshold in battery R&D. They remarked that neither LLMs nor other ML models were meaningfully accelerating battery cell R&D that occurs downstream of material science. They gave two reasons: the empirical testing of cell designs has not been physically automated, and attempts at computationally modeling battery cell production have not succeeded because important types of data are unmeasured.

In the case of fusion energy, a pair of interviewees said that LLMs were helping with coding but not otherwise significantly accelerating fusion energy R&D. In the case of code, the interviewees reported that LLMs were useful for porting legacy physics-simulation software to modern standards and for consolidating their own codebases. They said there was some minimal use of AI in engineering work, with perhaps one or two cases of non-LLM ML models being used (e.g. computer vision). On the whole, however, manufacturing time for components necessary for experiments, as well as carrying out the experiments themselves, were identified as bottlenecks that AI is not currently automating and would not cause dramatic acceleration even if AI were applied.

Several interviewees commented that LLM adoption in energy R&D and energy firms more broadly is early, cautious, and largely in contexts such as finance, HR, procurement, inventory and logistics, and communications, not novel technology R&D. One interviewee stated that energy firms do not yet trust frontier LLMs internally and that they are instead engaging other companies that specialize in using AI for energy R&D purposes. Another emphasized that dramatic acceleration of energy R&D would not necessarily lead to transformation of energy systems because physical deployment (e.g. building transmission infrastructure), not R&D, is a significant and not-yet automated constraint.

<!-- p.108 -->

#### 3.6.5 Semiconductors

We conducted three interviews with individuals with backgrounds in chip design, data storage, and AI research applied to chip design.[^42]

Two of the three interviewees indicated there was no evidence of semiconductor R&D being fully or even significantly automated by frontier AI models right now, with the third indicating significant but not yet dramatic speedup.

#### 3.6.6 Weapons development

We conducted eight interviews with individuals with backgrounds in defense, government, intelligence, autonomous systems design, and drone hardware.

Multiple interviewees emphasized that AI is widely being used operationally (e.g. computer vision, terminal guidance, image enhancement) but has yet to accelerate the R&D process itself. Several interviewees gave strong indications that AI systems are not capable of fully automating top-tier teams of researchers, with one stating that AI design tools are early, clunky, and not replacing any engineers. Another interviewee estimated AI is involved in roughly one percent of a defense company’s R&D work. A third interviewee said full automation is not happening and that AI’s role is mostly iterative optimization of existing systems rather than creation of novel weapons systems.

One interviewee did report strong coding-driven acceleration in software engineering for military applications, estimating that coding agents are enabling smaller engineering teams to accomplish what 5–10× larger teams would have historically. Another reported that coding agents had concretely accelerated R&D by taking a six month electronic-warfare development task down to a week, and that agents had progressed from merely writing code to also writing experiment requirements and test plans, though hypothesis generation remains with human experts. Other interviewees in hardware-focused roles reported little to no such gain, with several reporting minimal adoption in the defense industry or minimal gains from usage. There was a shared sentiment amongst some interviewees that materials science is a greater bottleneck to geopolitically significant advances in weapons development. For example, multiple interviewees highlighted higher battery energy density as upstream to novel military capabilities—capabilities such as more persistent drone fleets.

One interviewee said that AI systems are not currently able to provide supply-chain-constrained drone design, which would be necessary for them to be useful,<!-- p.109 --> since aerodynamic design itself is already well understood. Multiple others emphasized that a significant part of testing weapons systems is field deployment in militarily contested areas, which is not automatable by AI systems.

On directed-energy weapons specifically, one interviewee reported that cutting-edge firms are adopting AI in their R&D, and that they believed AI could already automate design processes for conventional directed-energy work, provided humans set objectives and perform testing and integration. Another interviewee remarked that it is not currently possible for AI systems to design a novel directed-energy weapons system from scratch, and that AI’s role is mostly modification of existing systems.

Several interviewees raised autonomous drone-swarm orchestration as a near-term milestone that AI systems might enable, but there was significant disagreement about what, exactly, near term meant, with estimates among interviewees ranging from mere months away, 6–12 months in principle (ignoring military policy requirements), and even farther off due to battery life and other constraints.

#### 3.6.7 Neurotechnology

We conducted four interviews with experts in neuroscience, connectomics, neuroimaging, and biophysics who spoke to how AI is impacting R&D in neurotechnology and related fields.

The interviewees reported that LLMs have accelerated tasks in coding, data analysis, and figure-making in the domain, and were generically productivity-enhancing. One interviewee estimated that graduate students are sped up by at least 2× because of coding agents automating coding and figure-making, and another remarked anecdotally that hiring decisions for postdocs are starting to be impacted because of how much of an uplift AI is providing. One interviewee said that whole brain connectomes still required enormous amounts of labor to proofread data, referencing mouse and fly connectome projects, while another interviewee said that ML models have now overwhelmingly automated the formerly labor-intensive process of image annotation, taking tens of thousands of work-hours by hundreds of students per dataset to a few dozen hours. One interviewee said that frontier AI models lack research taste at the level required for hypothesis generation, even while AI models were remarked on as having PhD-level comprehension.

Multiple interviewees cited physical data acquisition as a major bottleneck that AI is not currently addressing. One interviewee said that non-invasive neuroimaging is low-resolution and even a decade of progress has only doubled resolution without resulting in new breakthroughs. In connectomics, developing tissue-staining protocols<!-- p.110 --> requires weeks-to-months of iteration over an enormous search space and improvements are only achievable with the research intuition of the field’s top talent. Additionally, slicing tissue into nanometer-scale sections for imaging requires days of continuous manual surveillance by technicians.

#### 3.6.8 Nanotechnology

We conducted two interviews with experts in biophysics and biotechnology, one of whom is directly a frontier practitioner in biological nanotechnology.

Both interviewees said that ML models had transformed protein design, significantly speeding up research into biological nanotechnology. One interviewee said that LLMs were generally boosting productivity, with the other interviewee saying that coding has become very significantly automated, saving roughly a day a week in coding work. Both interviewees said that humans were still driving research ideas, with one interviewee noting that frontier AI systems still lack research taste and that dramatic acceleration is also bottlenecked by coordination, communication, and non-automated labor across specialized firms and disciplines. Due in part to these bottlenecks, that interviewee expects the first general-purpose computer chip that can stably convert biological information into digital information to be 3–5 years away. They also noted that data collection and processing is still deeply inefficient in important respects that future AI systems might be able to improve by using laboratory robots.

### 3.7 Our risk mitigations

This is a broad threat model. The risk mitigations it calls for are broad and overlap heavily with those listed elsewhere in this report: assessing and avoiding dangerous forms of misalignment, building increasingly robust safeguards against misuse, leveling up our information security, and more.

#### 3.7.1 Changes to risk mitigations since our previous risk report

We focus here on the specific mitigations that our RSP indicates we plan to complete by the time models reach this threshold:

- *Resource and complete significant “moonshot R&D for security” projects, to explore ambitious and possibly unconventional ways to achieve unprecedented levels of security against the world’s best-resourced attackers.*
- *Achieve an “eyes on everything” state for our internal AI development. We will comprehensively gather, centralize, and maintain logs for all critical AI-development*<!-- p.111 --> *activities, and use AI to analyze them for issues including security threats, concerning behavior by insiders (humans as well as AI systems themselves), and training processes or data that are out of line with the public Constitution that shapes and defines our AI models.*
- *Perform systematic alignment assessments to examine Claude’s behavioral patterns and propensities, meaningfully incorporating mechanistic interpretability and adversarial red-teaming to test our auditing methods.*
- *Develop our internal red-teaming of our deployment safeguards to the point where our internal red-teaming performs better at finding potential jailbreaks than the collective abilities of the participants in our established bug bounty programs.*

We believe our models have not yet crossed our RSP threshold for AI R&D acceleration, so these plans do not yet apply, but we have made progress on the above mitigations on the following fronts:

- We have laid out (but not yet completed) two “moonshot R&D” security projects in our [Frontier Safety Roadmap](https://www.anthropic.com/responsible-scaling-policy/roadmap).
- We have made significant improvements to our internal monitoring and control pipelines (see [Section 2.23.4](#2234-changes-to-risk-mitigations-since-our-previous-risk-report)), though we have also introduced more powerful agents with greater internal affordances that have increased the surface area of AI development activities we need to monitor; we don’t believe we meet an “eyes on everything” standard as of the coverage date. We have set a target date of January 1, 2027 for achieving this goal in our [Frontier Safety Roadmap](https://www.anthropic.com/responsible-scaling-policy/roadmap).
- We already perform extensive alignment assessments with each new system card, particularly for new frontier models, and these assessments often make use of interpretability techniques like [NLAs](https://www.anthropic.com/research/natural-language-autoencoders) and steered evaluations.
    - We have performed [one experiment](https://alignment.anthropic.com/2026/auditing-overt-saboteur/) to measure whether our auditing methods as of January 2026 would catch an “overt saboteur” model organism, which they did (with human assistance). Note that this is not a novel development since our previous Risk Report.
- We have some internal red-teaming efforts for our biological classifiers described in [Section 4.5](#45-our-risk-mitigations), although these efforts are not yet systematic or very well resourced. Empirically, the period since our last Risk Report surfaced one notable jailbreak from our bug bounty program and one notable jailbreak from internal red-teaming efforts (both described in [Section 4.5.3.2](#4532-notes-on-jailbreak-methods-that-remain-viable-on-at-least-some-models-in-some-cases)), though we don’t think this is strong evidence of meeting this bar.

<!-- p.112 -->

### 3.8 Overall assessment of risk

We believe that the near-term risk of a catastrophe under this threat model is low, due to the capability limitations noted above. This statement also works as a description of the level of risk our systems impose over and above the risks posed by other AI developers’ systems (that is, a description of the “marginal” risk of our systems). We believe it also holds for the level of risk that would be imposed industry-wide, if all AI developers had models and practices similar to ours (that is, a description of the “absolute” risk across the industry). This distinction is further discussed in our Responsible Scaling Policy.

However, we believe it is plausible that this threat model will become a major concern in the next 6–12 months.

### 3.9 Looking forward

We are working on deeper integration of external reviewers into our assessment of AI R&D automation and acceleration, and we continue to examine potential leading indicators for an AI-driven acceleration. We are also aiming to level up our risk mitigations across the board—including but not limited to the goals in our [roadmap](https://www.anthropic.com/responsible-scaling-policy/roadmap), bearing in mind that we may cross this threshold in the coming year.

<!-- p.113 -->

### 3.10 Connection to our recommendations for industry-wide safety

Our [recommendations for industry-wide safety](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf) include the following:

<table><tbody>
<tr><th>Capability or usage threshold</th><th>Substantive standards for model developers</th></tr>
<tr><td><p><b>Automated R&amp;D in key domains.</b> AI systems that can fully automate, or otherwise dramatically accelerate, the work of large, top-tier teams of human researchers in domains where fast progress could cause threats to international security and/or rapid disruptions to the global balance of power—for example, energy, robotics, weapons development, and AI itself.<br><br>For now, our evaluations will focus specifically on AI R&amp;D, as this domain likely plays to AI systems’ current strengths and is more tractable to assess than capabilities in other domains. Additionally, AI R&amp;D alone could cause acceleration in AI capabilities improvements, to the point where all of the threats listed above (and more) develop very quickly.<br><br>We will consider this threshold to be met if we determine that either (1) our models would be able to fully substitute for our entire set of Research Scientists and Research Engineers, at competitive costs (i.e., within a factor of 5); or (2) there is “dramatic acceleration” of the pace of AI progress for reasons that likely relate to the automation of AI R&amp;D.<br><br>We would consider scenario (2) to have occurred where (a) we observe or expect double the rate of progress<sup>[^43]</sup> in AI aggregate capabilities compared to both the rate we&#x27;d expect and the fastest rate of extended progress<sup>[^44]</sup> we&#x27;ve observed in the absence of significant AI contributions to AI R&amp;D and (b) it is plausible that this doubling is substantially attributable to the automation of research and/or engineering (as opposed to other factors, such as increased headcount, compute, or general productivity), such that continuation of the trend in AI progress seems likely to lead to even greater acceleration. This capability threshold is intended to reflect our definition of highly capable models (see <a href="#36-automated-rd-in-other-domains">Section</a> <a href="#36-automated-rd-in-other-domains">3.6</a> [of the RSP]). It may be sensible to add earlier, and/or easier-to-measure, thresholds that trigger less demanding versions of the mitigations for this threshold.</p></td><td><p>A frontier developer should make a strong argument that:<br><br>● No user or team of users (including those backed by top-tier states) will become significantly more likely to cause catastrophic harm via their usage of product surfaces or via theft of model weights.<br><br>This will likely require similar measures to those listed in row 1, but to a higher standard, to the point where even well-resourced and -staffed threat actors would be unlikely to reliably jailbreak models or cause catastrophic harm via unauthorized access to or modification of models (including via stolen or modified model weights).<br><br>Accomplishing this would likely mean security roughly in line with RAND SL4. Security requirements would be calibrated to defend against the strongest plausible threat actors who are not bound by a credible industry-wide safety regime. Actors subject to such a regime would not need to be treated as threats to each other&#x27;s model weights.<br><br>● Even malicious employees and other insiders with maximal levels of access will not be significantly enabled to cause catastrophic harm. This requires (among other things) accounting for internal tools that are less restricted than product surfaces, and for the possibility of unauthorized modification of models.<br><br>This will likely require an internal Usage Policy and strong internal compartmentalization, controls and/or monitoring to restrict the ability of employees and contractors (up to and including the company&#x27;s CEO as well as its most privileged technical employees) to circumvent the Usage Policy.<br><br>● AI models have not been deliberately or inadvertently trained with dangerous goals, or are otherwise unlikely to autonomously cause catastrophic harm.<br><br>This will likely require similar measures to those listed above under &#x27;Misaligned AI systems in high-stakes settings&#x27; (some combination of internal compartmentalization, restriction and code review; monitoring AI behavior; and evidence that AI models lack the propensity to deceive and manipulate users), but to a greater degree.<br><br>In particular, at this point AI systems might be responsible for much of the research and analysis that underpins risk assessment, and might have strong capabilities for deception, manipulation and obfuscation of evidence, in which case analyses of threats from AIs should follow very high evidentiary standards with thorough and careful analysis of the possibility that much of the key evidence is suspect due to the possibility of manipulation by AI systems.</p></td></tr><!-- p.114 -->
</tbody></table>

:::caption
**[Table 3.10.A] Summary of our recommendations for industry-wide safety.**
:::

As argued above, we believe our models do not meet the relevant capability thresholds from our RSP, so we do not think an ideal ecosystem of model developers would require the corresponding mitigations from our recommendations for industry-wide safety.
[^39]: Our RSP uses a threshold of models being able to “fully substitute at competitive costs” for Anthropic researchers, which in theory could be crossed via a less capable but cheaper model if the most capable model was only able to substitute at prohibitively large cost. In practice, we do not think that even our most capable models can perform such substitution at *any* cost, so we don’t consider other models in Section 3.4 of this Risk Report. This could change in the future.

[^40]: We have not directly run experiments where we attempt to spend 5× more than the all-inclusive costs of employing an Anthropic researcher on deploying our most capable models at a difficult real-world task which our models do not succeed at with less extravagant expenditure, so this claim is in some ways unverified: it could be that models *would* substitute at these levels, and our allocation of internal model inference compute is inefficient despite our incentives.

[^41]: For instance, our current implementation does not give models in this evaluation the ability to launch jobs on our cluster or view some compartmentalized internal discussions; we don’t believe these affordances are *necessary* to solve any of the tasks in this evaluation, but it’s possible that some of the tasks would become difficult enough without this affordance that human researchers would have failed.

[^42]: Some detail here redacted from the public version of this report.

[^43]: “Double the rate of progress” means “as much progress in one year as one would see in two years at baseline.” For example, if baseline progress involved a 3× scaleup in compute and a 3× improvement in algorithmic efficiency (for a 9× “effective scaleup”), “double the rate of progress” would entail something like an 81× effective scaleup. This is not the same idea as “doubling researchers’ productivity,” since doubling inputs does not necessarily double the rate of progress.

[^44]: Over at least three model generations.

