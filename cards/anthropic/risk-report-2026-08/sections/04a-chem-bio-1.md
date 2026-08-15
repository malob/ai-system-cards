<!-- source: source.pdf pages 115-134 -->

<!-- p.115 -->

## 4 Chemical and biological weapons production

*This section covers risks related to two of our RSP threat models: one centered around non-novel chemical/biological weapons production, and one on novel chemical/biological weapons production. We refer to these threat models and their associated RSP thresholds as CB-1 and CB-2, respectively.*[^45] *Our previous Risk Report addressed these two threat models in separate sections; given the significant overlap in our evaluations, threat modeling, and mitigations for both we address them in one combined section.*

### 4.1 Overview

<table><tbody>
<tr><td></td><th>CB-1 threat model</th><th>CB-2 threat model</th></tr>
<tr><td><b>Threat model</b></td><td>Individuals or small groups with limited resources use AI models to gain access to non-novel chemical or biological (CB) weapons, leading to the risk of catastrophic harm.</td><td>Moderately resourced threat actors (including, for example, expert-backed teams) create/obtain and deploy novel chemical and/or biological weapons with potential for catastrophic damages even beyond those associated with the CB-1 threat model.</td></tr>
<tr><td><b>Overall risk assessment</b></td><td>Low risk, but higher than previously estimated due to a recently discovered gap in our safeguards that affected us for nearly a year. We have remedied the issue and have no evidence that it was used for chemical and biological misuse, but its existence leads us to believe that there is an increased likelihood of other, similar vulnerabilities unknown to us. More <a href="#45822-all-human-feedback-vendor-traffic-run-without-blocking-biological-classifiers">below</a>.</td><td>Low risk, but with substantial uncertainty.</td></tr>
<tr><td><b>Relevant AI model(s)</b></td><td colspan="2">We have a number of relevant models with different capability levels and risk mitigations, summarized in a table <a href="#43-relevant-ai-models">below</a>.</td></tr>
<tr><td><b>Current usage and capabilities</b></td><td><p>We still have significant uncertainty about the level of risk actually posed by our models, but their performance on evals is strong enough that we currently act as though they meet our CB-1 threshold of being able to significantly help the relevant threat actors create/obtain and deploy chemical and/or biological weapons with serious potential for catastrophic damages.</p></td><td><p>We believe our models may provide significant uplift to relevant threat actors, but do not yet meet our CB-2 threshold of functionally substituting for the scarce human expertise that is currently the primary barrier to novel development of chemical and biological weapons with potential for catastrophic harm.</p></td></tr><!-- p.116 --><tr><td><b>Current risk mitigations</b></td><td>Real-time blocking classifiers assessed via bug bounties and other red-teaming; remediation of jailbreaks we find; manual vetting of users with safeguard exemptions; searching for widely available universal jailbreaks; and controls to prevent theft of model weights.</td><td>Similar measures to those in the left column. We have extended the scope of coverage for our classifiers for better coverage of this threat model. For our Fable 5 model, we have even broader coverage of our blocking classifiers.</td></tr>
<tr><td><b>Looking forward</b></td><td>Capabilities evaluations; continual reassessment and improvement of all risk mitigations.</td><td>Capabilities evaluations; continual reassessment and improvement of all risk mitigations.</td></tr>
</tbody></table>

:::caption
**[Table 4.1.A] Summary of risk of chemical and biological weapons production.**
:::

### 4.2 Threat models

#### 4.2.1 CB-1 threat model

**The threat:** Individuals or groups with relatively modest resources sometimes attempt mass murder for a variety of (sometimes known, sometimes unknown) motivations. The damage from such an attempt might be dramatically increased if the attackers had access to chemical or biological weapons. Note that this threat model focuses on *known* biological or chemical weapons. The possibility that such weapons could be deliberately engineered to be even more damaging is considered under the next threat model.

**Role of AI:** Sufficiently capable AI models could provide an uplift on the production of chemical or biological weapons that goes well beyond what’s currently available on the public internet, and thus could raise novices to the level of experts. The degree to which the damages in question can be reasonably attributed to the role of AI specifically is an open question. This would depend on the specifics of the case—how much AI accelerated or uplifted a threat actor, what the threat actor’s alternative course of action would have<!-- p.117 --> looked like, etc. In some circumstances, we can imagine that the role of AI could be significant.

**Potential magnitude of impact:** Biological pathogens have caused among the most damaging catastrophes in history, and therefore an effective attack using one is clearly a catastrophic risk. Chemical weapons have historically been used in extremely damaging attacks, although they do not pose as high a risk as biological weapons. As well as loss of life, such attacks also come with potentially enormous societal disruption and economic damage. For example, the UN’s Department of Economic and Social Affairs has highlighted trillions of dollars in lost economic output in the context of the COVID-19 pandemic,[^46] and several other sources estimate even higher damages.[^47] [^48] [^49]

**Likelihood of impact:** Terrorists (or terrorist actors) have previously used chemical and biological weapons in attacks, though these have (to date) been rare with limited casualties. Preliminary analysis suggests that AI capabilities could significantly increase the likelihood of such events, although a great deal of uncertainty remains in current assessment methodologies.[^50] Nevertheless, the potential scale of the damage is concerning enough to<!-- p.118 --> warrant taking action. A 1% annual probability of an event as damaging as COVID-19[^51] could imply upwards of hundreds of billions of dollars in expected damages.

**Why this is a priority threat:** Even a relatively modest (but nontrivial) increase in the risk of an attack like the one described above from AI should, in our view, be a high priority. This is especially true because of the difficulty of constructing robust defenses against biological and chemical weapons (in the same way that, for example, cyberdefenses can be mounted), and because of the potential lack of early warning signs of such an attack.

**Notes on our current prioritization within this category:** For the time being we prioritize biological threats with pandemic potential. The consequences of a potential biological attack are significant enough to make the expected harm substantial, even if the overall rate of attempts is relatively small. Additionally, biological risks present a threat profile where AI systems could meaningfully lower barriers to catastrophic outcomes by addressing knowledge, skill, or automation bottlenecks, making this risk both counterfactually attributable to AI and potentially catastrophic.

As noted above, our current assessment is that chemical weapons are less likely to enable comparably-sized catastrophic harm attributable to the relevant AI systems. We believe that chemical attacks would likely require scaling numerous smaller attacks to reach catastrophic levels, providing detection opportunities before catastrophic thresholds are reached. Nonetheless, we intend to continue examining chemical threats.

We developed these views by consulting with experts, including from Deloitte Consulting and SecureBio. Our threat models were also informed by an expert workshop organized by the Frontier Model Forum.

#### 4.2.2 CB-2 threat model

**The threat:** Damages from chemical and biological weapons may be even higher than implied in the previous section if such weapons are *novel*, and are deliberately engineered to be more damaging than anything analogous observed to date (including natural pandemics). While such an attack could potentially come from individuals or groups with modest resources, today we believe that the risk primarily stems from moderately to very well-resourced programs, including but not limited to state programs (such weapons<!-- p.119 --> programs are internationally prohibited,[^52] but there is credible evidence[^53] that there are active programs operating). There are a range of possible motivations, including attempts to design strategies that would specifically target particular populations (note that such targeting might fail even as the attempt to build a highly damaging weapon succeeds).

**Role of AI:** We do not consider AI to be a likely factor in the ability of well-resourced groups to deploy *non-novel* chemical and biological weapons (since they likely have the ability to deploy these without uplift from AI), but sufficiently capable AI models could significantly uplift well-resourced groups that seek to develop unprecedentedly dangerous weapons by providing expertise akin to that of a team of world-class human experts assisting with hypothesis generation, design, and iteration.

**Potential magnitude of impact:** As discussed in the [previous section](https://anthropic.com/feb-2026-risk-report), chemical and biological weapons have the potential for enormous damages, and damages may be even higher if such weapons are deliberately engineered to be worse than anything analogous observed to date (including natural pandemics). We think very few such weapons would directly lead to human extinction, but it seems plausible that such weapons could lead to damages at least an order of magnitude more than those associated with COVID-19.

**Likelihood of impact:** A catastrophe along the above lines would require the occurrence of several individually unlikely events: a well-resourced attempt (in violation of international agreements) to design unprecedentedly dangerous weapons, success in developing them, and finally the weapons actually being deployed (deliberately or inadvertently). We think each step is plausible but unlikely, and collectively the whole sequence is highly unlikely.

Our current rough estimates, which are subject to high degrees of uncertainty, for the relevant events in the chain are as follows. Note that these are baseline probabilities—probabilities before considering potential amplification via advanced AI systems, characterizing the overall threat rather than the risk level of our systems specifically.

<!-- p.120 -->

- There are several threat actors for which this threat is most plausible.
- For each threat actor, the odds of a concerted attempt to build a bioweapon capable of damages beyond COVID-19 may be in the 1–10% range. They might build such a weapon for a range of reasons, including (a) for deterrent purposes (b) with the intention of finding a way to target specific populations.
- For each such attempt, the baseline odds of success[^54] (in the absence of AI assistance) may be in the 1–10% range.
- Conditional on developing such a weapon, with especially high uncertainty, we estimate the odds of release in the 5–20% range per decade (mostly due to the possibility of deliberate release, though accidental release is also possible).

These probabilities seem facially roughly independent, but it isn’t necessarily the case that the overall probability can be bounded by multiplying them.

There is the additional question of whether lower-resource actors (in particular, individuals acting alone) are also a source of this type of risk. We have put less work into this threat modeling, but would guess the baseline probability of such an event in the absence of powerful AI assistance is very low (likely in or below the same overall range as the aggregate risk from the actors discussed above).

Emphasizing again the high degree of uncertainty with respect to the estimates above, they imply a baseline per-decade probability that could be as high as 1 in 50 or so,[^55] or as low as 1 in 20,000. We’d consider 1/50 per decade to be on the aggressive end, given the figures for less severe pandemics from [forecasting exercises](https://forecastingresearch.org/research/llm-enabled-biorisk).[^56] As noted above, this is a baseline probability—a probability of an event like this *before* considering potential amplification via advanced AI systems—characterizing the overall threat rather than the risk level of our systems specifically.

<!-- p.121 -->

**Why this is a priority threat:** Despite the very low likelihood of such a catastrophe, we believe the potential damages here would exceed those of all AI risk threat models other than the ones already discussed elsewhere in this report. The points from the [previous threat model](#42-threat-models) also apply:

- We believe that it is hard to construct robust defenses against such weapons. Unlike in some other domains such as cyberoffense, it is hard to envision a way in which AI-assisted countermeasures could outweigh AI-assisted risks.
- Rare catastrophic events like this are hard to get early warning signs of and respond to iteratively, so we take a preventive approach.

**The threat model has especially high uncertainty:** While we believe that the broad threat model here is worthy of serious attention, it is inherently difficult to connect to AI capability evaluations, and developing the relevant evaluations remains a work in progress.

#### 4.2.3 Timescale and scope of uplift

We expect that both of these threat models involve biological processes that take on the order of months, because the process of creating biological weapons is complex and dependent on many serial steps of real-world iteration.

We expect that in order to get substantial uplift from AI models, threat actors would likely need substantial and persistent guidance, involving dozens of queries over substantial periods of time (weeks if not months), and spanning a wide range of topics.

We acknowledge uncertainty about whether threat actors could achieve meaningful uplift in shorter periods, for example, by constructing a detailed plan in a single session and then executing it without further LLM assistance. We are not confident about this, but our expectation is that threat actors with months or years to spend on an overall project are far more likely to benefit from sustained, iterative AI assistance than from a single interaction. As discussed in [Section 4.4.3](#443-cb-2-evidence-for-mythos-preview-fable-5-and-mythos-5), some of our uplift trial evidence suggests that even our most capable models are particularly weak at correcting for failures in complex multi-step plans, such that we think they would struggle greatly to provide effectual end-to-end plans without further guidance.

If this assumption is wrong and short interactions do confer significant uplift, our safeguards still provide meaningful risk reduction (though our confidence in the degree of such risk reduction would be lower). As discussed in [Section 4.5](#45-our-risk-mitigations), our blocking classifiers aim to block a wide variety of harmful uses, including those requiring only brief guidance,<!-- p.122 --> and many jailbreaks appear (based on limited testing we’ve done) to degrade capabilities, often very significantly.

### 4.3 Relevant AI models

In this section, we discuss the capabilities and mitigations for all of our publicly released AI models at least as capable as Claude Opus 4, since the capabilities and the strength of our mitigations vary across these models (with our most capable or most widely deployed models using even stronger and more robust safeguards).

We do *not* focus on Claude Opus 5, Model 1, or Model 2 in this section, as they were not provided for external usage as of the coverage date, but our CB-relevant evaluations on these models (which are more limited in the case of Model 1 or Model 2) generally indicated performance comparable to or weaker than Claude Mythos 5 in all three cases.

For models less capable than Claude Opus 4 (the ones given in the bottom three rows of Table 4.5.A below), we implement the following basic mitigations:

1. **Acceptable usage policies and enforcement**: Our Usage Policy prohibits harmful CBRN usage.
2. **Harmlessness training:** Our models are trained to refuse harmful requests, including with respect to chemical and biological weapons.
3. **Fine-tuning API protections:** In fine-tuning products, data is filtered for harmfulness, and models are subject to automated evaluation aiming to ensure harmlessness features are not degraded. Some models with these fine-tuning protections removed are available to a very limited set of external users, described in [Section 4.5.5.3.1](#45531-helpful-only-models) below.
4. **Vulnerability reporting channels:** Paths within the product for users to report harmful or dangerous model outputs. Specifically, users are able to report risks directly within the product to our trust and safety team, and can contact usersafety@anthropic.com as specified in our usage policy.

We believe that the risk of catastrophic harm from these less-capable models is very low due to their limited capabilities, and would remain so even if some of the above protections were disabled. Our assessments of the biological risk from these models and the evidence that gives us this confidence are discussed in detail in the models’ respective system cards. As such, we devote very little space to covering these models or the robustness of our mitigations for them in the rest of this section.

<!-- p.123 -->

### 4.4 Current state of model capabilities

#### 4.4.1 Notes on how we weigh evidence

We generally consider sources of evidence about model capabilities more informative to the extent that they better track the kinds of interaction we expect from this threat model. Sources of evidence we consider informative include:

- Evaluations that track the kind of work done in real-world difficult biological tasks, rather than simple proxies like accuracy at multiple choice questions on a topic;
- Long-horizon evaluations involving multi-step end-to-end projects with multiple possible stages of real-world failure;
- Evaluations that have a baseline of expert performance to compare to, particularly world-leading and rare expertise in the domain of interest; and
- Evaluations that compare success with and without AI assistance, e.g. uplift trials.

We also place significant weight on subjective impressions from our internal biology experts and from expert red-teamers, even when we do not have clear numerical evidence to substantiate this; we think that gestalt expert opinions after extended experience eliciting help with difficult biological tasks from a model offer some of the most informative signal we have about risk-relevant model capabilities, even though it is difficult to make legible.

#### 4.4.2 CB-1 evidence

Since the release of Claude Opus 4, we have assessed it and all of our subsequent frontier model releases as provisionally meeting the CB-1 threshold. We have done this in order to err on the side of caution rather than because we are confident these models cross the threshold.

We continue to run several automated evaluations relevant to this threat model with each new model release, but many of these have saturated or reached the point where current models’ performance is not well-assessed by existing automated grading scripts; in practice, if a new and otherwise-capable model were to perform worse on some of these evaluations, we would be more skeptical of the validity of the evaluation than of the model’s risk-relevant abilities. As such, we have prioritized evaluation effort on assessments of the CB-2 threshold, since we now treat most new models as crossing the CB-1 threshold by default. Moreover, our CB-2 assessments often offer meaningful signals on capabilities relevant to the CB-1 threat model: the ability to accurately collate (sometimes obscure)<!-- p.124 --> information from the (sometimes contradictory) literature, and good scientific judgment necessary for troubleshooting these results.

We still have significant uncertainty about the level of risk actually posed by Opus 4 and our more advanced models. While performance is often strong on the concrete evaluations we’ve been able to run, it is hard to translate this to how helpful Claude would be in the real world to a threat actor trying to carry out a complex project end-to-end over the course of months. This is due to several factors: first, we have uncertainty about threat actor characteristics and skill levels; second, experts disagree on the importance of tacit knowledge (the ability to translate theory into practice); and third, there is significant variability in the capabilities and behavioral characteristics of Opus 4 and subsequent models, and we know that these characteristics have a significant impact on uplift in real-world contexts.

##### 4.4.2.1 General update from a randomized controlled trial on uplift from AI models

[A recent 2026 paper](https://arxiv.org/pdf/2602.16703) by Hong et al. conducted a randomized controlled trial measuring the degree of novice uplift from the public frontier of LLM usage as of summer 2025, and found that “Overall, mid-2025 LLMs did not substantially increase novice completion of complex laboratory procedures but were associated with a modest performance benefit.” Participants had access to frontier LLMs from all model developers without blocking biological classifiers enabled, including Opus 4 and (partway through the study period) Opus 4.1, and attempted to complete various complex tasks in a real-world biological laboratory setting over the course of several weeks.

We think this experiment is substantially more reflective of the kind of real-world uplift we are concerned with for the CB-1 threat model than the evaluations we ran in the system cards for Opus 4 and Opus 4.1. However, there are significant caveats to the study’s overall conclusions of low uplift:

- Participants had minimal prior laboratory experience, which could be a lower degree of experience than some of the CB-1 threat actors we are concerned with.
- A post-hoc analysis suggested moderate 1.42× uplift on a “typical” task in the sequence, with large error bars.
- AI-assisted participants only used LLMs a moderate amount: only one participant generated more than 1 million total tokens across models.
- The study was underpowered given lower-than-expected success rates of participants, and had only 36% power to detect an odds ratio of 2.0 in success rates at the core task sequence.

<!-- p.125 -->

Overall, the fact that novice users were not shown to be substantially better at engaging in complex laboratory procedures when given access to these models suggests to us (with uncertainty, given the above caveats) that these models are likely to pose somewhat lower risk than we worried they might when we first proactively enabled more stringent biological safeguards on these models.

We continue to apply blocking classifiers and other safeguards for both of these models, but this assessment affects our prioritization of effort into further improvements to the safeguards applied to these models.

#### 4.4.3 CB-2 evidence for Mythos Preview, Fable 5, and Mythos 5

Most of our evidence for model capabilities relevant to the CB-2 threat model comes from evaluations conducted in our system cards. Our recent Mythos-class models have had broadly similar performance to one another on these evaluations, with Mythos 5 appearing to be more capable. We summarize the results of these evaluations, largely drawn from the [Claude Fable 5 & Claude Mythos 5 System Card](https://anthropic.com/claude-fable-5-mythos-5-system-card), below:

<table><tbody>
<tr><th>Evidence type</th><th>Evaluation/evidence description</th><th>Claude Mythos 5 performance</th></tr>
<tr><td><b>Expert red-teaming<sup>[^57]</sup></b></td><td>Internal and external panels of domain experts probed the model across the full biological and chemical weapon development pipeline, scoring uplift and feasibility on standardized rubrics with emphasis on whether the model could substitute for scarce specialized expertise.</td><td>Experts described the model as the strongest they have evaluated; two biology experts rated it comparable to or exceeding a knowledgeable specialist, and several independently reported it supplying work they would otherwise have sought from a specialist consultant.</td></tr><!-- p.126 --><tr><td><b>Beneficial red-teaming tabletop exercise</b></td><td>We paired PhD biologists with dedicated LLM experts to design an end-to-end biological resistance strategy against a hypothetical engineered agricultural pathogen. Some participants had generalist biological expertise while others were world-leading domain specialists.</td><td>Two of three generalist teams outperformed all three specialist teams on both scientific quality and feasibility. Expert graders estimated the strategies and implementation protocols would have taken 40–95 working days to produce without AI tools; the two-person teams accomplished this in 16 hours.</td></tr>
<tr><td><b>Catastrophic biological scenario uplift trial<sup>18</sup></b></td><td>Uplift trial with five three-person teams tasked with constructing biological scenarios with catastrophic potential. Outputs were graded by external domain experts against a standardized uplift rubric.</td><td>Non-expert teams reported moderate-to-high uplift across most pipeline steps; they were strongest in delivery and dissemination, and weakest in acquisition and production. All five teams converged on the same primary agent class, and all plans had critical gaps.</td></tr>
<tr><td><b>Black-box RNA sequence modeling and design</b></td><td>Sequence modeling and design challenge developed with Dyno Therapeutics. Models are given a small experimental dataset of sequences and (unlabeled) numerical scores and asked to (1) predict the scores of held-out RNA sequences (2) design novel high-scoring sequences. Performance is compared to that of historical human participants from the leading edge of the US labor market.</td><td>Reliably exceeded the 90th percentile of human performance (but did not exceed the top human performance) on prediction. Median design score fell between the 75th and 90th percentile of human performance, and slightly exceeded the best human participant in one of eight trials.</td></tr><!-- p.127 --><tr><td><b>AAV capsid packaging prediction</b></td><td>Models are given 1000 unpublished AAV capsid sequences modified with short insertion sequences curated by Dyno Therapeutics. The models are then asked to give a probability for whether each modified sequence will correctly assemble into a functional capsid, and assessed across several settings with different machine learning tools available for use.</td><td>Claude Mythos 5 achieved the highest median AUROC among all models tested, and had particularly stable performance across conditions (rather than becoming confused by potentially misleading training data, as occurred with many previous models).</td></tr>
</tbody></table>

:::caption
**[Table 4.4.3.A] Summary of CB-2 evaluation results on Mythos 5**. Red-teaming and uplift trials made use of an earlier helpful-only version of the model, to avoid refusals on harmful tasks; other evaluations did not have refusal issues and were able to be run on the final production Mythos 5.
:::

As stated in the Mythos 5 System Card, the limitations of the model that we consider most disqualifying for the CB-2 threshold are:

- **Weak open-ended ideation and design capabilities:** Across red-teaming, uplift trials, and the tabletop exercise, the model reliably recombined and extended published knowledge, but rarely produced approaches reviewers considered genuinely novel, and it tended toward over-engineered designs. Where it did go beyond the literature, participants needed to use their expertise to separate promising ideas from speculation.
- **Poor strategic judgment:** The model tended to extend whatever framing the user supplies rather than challenging it; e.g., executing plans containing flaws it had itself detected, presenting overly optimistic timelines and designs that reviewers repeatedly forced it to revise or retract, or missing how errors compound across a multi-step program.

We expect these weaknesses to pose significant difficulty for teams lacking critical expertise of the sort described in our RSP threshold for this threat model, and believe it would be difficult for Mythos 5 to fully substitute for such expertise. (The poor strategic judgment, in particular, leads us to conclude that what expertise these models *do* provide is most helpful over the course of extended back-and-forth interactions, rather than by providing a single plan or piece of information which a threat actor could make use of without difficulty going forward.)

However, we found significant uplift of *existing* experts from the model, and we think it is plausible that a well-resourced team which already possessed the relevant expertise could be significantly uplifted in the development of novel weapons by an unsafeguarded Mythos<!-- p.128 --> 5, primarily by augmenting their operational capacity by acting as force-multipliers of existing expertise. The quantitative increase in the odds of “success” for the threat actors described in 4.2.2 due to such access would depend on the details of their existing expertise and the specific threat being pursued, but in one case our experts have very roughly estimated that the odds might double relative to threat actors’ chances without any AI assistance (though we don’t mean for this to be an upper or lower bound, nor a central estimate). These judgments come with very high uncertainty, even more so than many other considerations around this threat model.

#### 4.4.4 CB-2 evidence for Opus 4.8 and other Opus and Sonnet models

As in the previous subsection, much of our evidence for these models comes from the results presented in our system cards. Where we have data, we focus on the most capable model in this category, Claude Opus 4.8, though we include results from earlier models of slightly lower capability where they provide additional strong sources of evidence.

<table><tbody>
<tr><th>Evidence type</th><th>Evaluation/evidence description</th><th>Model performance</th></tr>
<tr><td><b>Expert red-teaming (conducted on Opus 4.7)<sup>[^58]</sup></b></td><td>Nine experts assessed whether the model could function as a domain expert in highly specialized areas of biology—particularly virology and microbiology—in ways that could meaningfully accelerate biological threats.</td><td>6/9 biology experts assigned an uplift score at 2 on a 0–4 scale, representing “specific, actionable info." Two experts rated the model at 3 (comparable to consulting a knowledgeable specialist), and one rated it between 2 and 1 (rudimentary synthesis of the published record); no expert assigned the highest rating (rare, crucial insights comparable to world-leading expert).</td></tr>
<tr><td><b>Creative biology uplift trial (conducted on Opus 4.6)</b></td><td>PhD-level experts tasked with producing detailed reports on novel biological workflows.</td><td>No example was uniformly concerning for all experts. (Some examples were found concerning by some experts.)</td></tr><!-- p.129 --><tr><td><b>Virology protocol uplift trial (conducted on Opus 4.6)</b></td><td>PhD-level experts tasked with determining a step-by-step protocol for reconstructing a challenging virus. Designed by Deloitte.</td><td>Average number of critical failures: 6.6 (rule-out criterion: ≥ 1.8).</td></tr>
<tr><td><b>Black-box RNA sequence modeling and design</b></td><td>Sequence modeling and design challenge developed with Dyno Therapeutics. Models are given a small experimental dataset of sequences and (unlabeled) numerical scores and asked to (1) predict the scores of held-out RNA sequences (2) design novel high-scoring sequences. Performance is compared to that of historical human participants from the leading edge of the US labor market.</td><td><p>Opus 4.8 reliably exceeded the 90th percentile human performance at the overall prediction task, exceeding Mythos Preview’s score, though it did not exceed the top human performance. Its median design score was slightly worse than the 75th percentile of human performers.</p><p>However, on the subset of predictions for the few highest-scoring sequences, which we think better tracks realistic threat models for this kind of task, Opus 4.8 performed worse than several recent models, including Opus 4.6 and Sonnet 4.6. We discuss this further in Section 2.2.6 of the Opus 4.8 System Card.</p></td></tr>
<tr><td><b>AAV capsid packaging prediction</b></td><td>Models are given 1000 unpublished AAV capsid sequences modified with short insertion sequences curated by Dyno Therapeutics. The models are then asked to give a probability for whether each modified sequence will correctly assemble into a functional capsid, and assessed across several settings with different machine learning tools available for use.</td><td>Opus 4.8 performed substantially worse than Mythos Preview across all settings, and underperformed somewhat when given the option of using a public data corpus less helpful for the task (though less so than earlier models like Opus 4.6). Opus 4.6 performed better than Opus 4.8 on the settings without access to this less-helpful dataset.</td></tr>
</tbody></table>

:::caption
**[Table 4.4.4.A] Summary of CB-2 evaluation results** on Claude Opus 4.8, Claude Opus 4.7, and Claude Opus 4.6.
:::

<!-- p.130 -->

We believe all of these models are significantly less capable at risk-relevant tasks than Claude Mythos Preview or Claude Mythos 5, so (based on the more extensive evidence about those models falling short of the CB-2 threshold) we have fairly high confidence that these models also do not cross the threshold. However, as with our Mythos-class models, we have more uncertainty about the degree of risk posed by uplift to existing expert teams than we do for substitution of missing expertise, and as discussed below in [Section 4.6.2](#462-risks-from-the-cb-2-threat-model), we believe in light of improved elicitation and expert red-teaming evidence that the expert uplift provided by Opus 4.6 and later models is slightly higher than what we concluded in the system cards for those models at the time.

### 4.5 Our risk mitigations

Our models are subject to a variety of different safeguards, depending on their capability levels.[^59] Factors that vary include:

- **Robustness:** we have improved the robustness (difficulty of jailbreaking) of our classifiers[^60] over time. In some cases we have applied improvements to newer and more capable models, without applying them to older and less capable models. We use “Level 1/2/3” terminology to distinguish between different levels of robustness. More information on the different levels of robustness is given below.
- **Coverage:** For our deployment of Fable 5, we use a new classifier with the same robustness level as our other Mythos-class models but with an expanded domain of coverage, encompassing the vast majority of potentially dual use usage relevant to research biology.
- **Exemptions:** for some of our models, we have programs for commercial users to seek exemptions from our blocking classifiers for CB misuse. We discuss these further in [Section 4.5.5](#455-bioclassifier-exemptions).

<table><tbody>
<tr><th>Model</th><th>Description</th><th>Robustness</th><th>Exemptions program</th></tr>
<tr><td><b>Claude Mythos 5</b></td><td>Our most capable externally deployed model</td><td>Level 3</td><td>None as of this writing</td></tr><!-- p.131 --><tr><td><b>Claude Fable 5</b></td><td>Mythos 5, deployed with additional safeguards to a wider audience</td><td>Level 3</td><td>None as of this writing</td></tr>
<tr><td><b>Claude Mythos Preview</b></td><td>Legacy Mythos-class model, not widely deployed</td><td>Level 3</td><td>None as of this writing</td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>Our most capable model without higher-coverage bio classifiers offered widely to consumers as of the coverage date</td><td>Level 3</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Opus 4.7</b></td><td>Legacy model</td><td>Level 3</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>Major commercial model that is roughly equivalent to Claude Opus 4.8 with respect to CB-relevant capabilities</td><td>Level 3</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Opus 4.6</b></td><td>Legacy model</td><td>Level 2 (with some product surfaces at Level 1)</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Opus 4.5</b></td><td>Legacy model</td><td>Level 2 (with some product surfaces at Level 1)</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Sonnet 4.6</b></td><td>Legacy model</td><td>Level 2 (with some product surfaces at Level 1)</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Sonnet 4.5</b></td><td>Legacy model</td><td>Level 2 (with some product surfaces at Level 1)</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Opus 4.1</b></td><td>Legacy model</td><td>Level 1</td><td>Bioclassifier Exemption Policy</td></tr>
<tr><td><b>Claude Opus 4</b></td><td>Legacy model</td><td>Level 1</td><td>Bioclassifier Exemption Policy</td></tr><!-- p.132 --><tr><td><b>Claude Sonnet 4</b></td><td>Our most capable model in risk-relevant domains not subject to real-time classifiers for this threat model</td><td>N/A (no blocking classifiers)</td><td>N/A</td></tr>
<tr><td><b>Claude Haiku 4.5</b></td><td>Major commercial model that is cheaper than Claude Sonnet 5</td><td>N/A (no blocking classifiers)</td><td>N/A</td></tr>
<tr><td><b>Other legacy models (see full list in appendix)</b></td><td>Older legacy models</td><td>N/A (no blocking classifiers)</td><td>N/A</td></tr>
</tbody></table>

:::caption
**[Table 4.5.A] Summary of CB safeguards applied to each of our production models**. See [Appendix 6.6](#66-our-ai-models) for a full list of relevant models.
:::

#### 4.5.1 Robustness levels: Level 1, Level 2, Level 3

In the table above:

**Level 1 robustness** refers to classifiers that are essentially what we laid out in our [previous Risk Report](https://www-cdn.anthropic.com/097c63b5fe7dd8b14866e1f15bb1910ec713658a.pdf), and have not been updated to reflect improvements in classifier design, although they have been updated to mitigate specific jailbreaks we’ve become aware of. While these classifiers are less robust than the others described below, we expect they would still pose a significant barrier to novice threat actors in practice. We are not aware of any highly effective, universal jailbreaks for these other than the four described [below](#4532-notes-on-jailbreak-methods-that-remain-viable-on-at-least-some-models-in-some-cases), which are all either non-public or have significant limitations in terms of usefulness to threat actors.

These classifiers are used on two of our legacy models, Claude Opus 4 and Claude Opus 4.1. Both of these models are now deprecated, and we expect them to become fully unavailable on all platforms later this year. We also have had a moderate update toward expecting somewhat lower uplift from these models (see [above](#4421-general-update-from-a-randomized-controlled-trial-on-uplift-from-ai-models)).

These classifiers are also used on one product surface that has been relatively difficult to make updates on for the following legacy models: Sonnet 4.5, Sonnet 4.6, Opus 4.5 and Opus 4.6. We expect to upgrade these to Level 2 robustness classifiers in the coming months.

**Level 2 robustness** classifiers are constructed using our updated design for Constitutional Classifiers, which is a significant improvement on the original release and is described in detail in [our January 2026 paper](https://arxiv.org/abs/2601.04603). As with our Level 1 robustness classifiers, these classifiers<!-- p.133 --> follow a two-stage design: some queries are flagged by a streaming classifier based on linear probes of model internals, which get passed on to a more expensive second stage classifier based on a fine-tuned model. Unlike the Level 1 robustness classifiers, however, the final decision of whether to block a model output is based on a weighted combination of the scores of the probe and the model-based classifier (rather than just the second-stage classifier). While [boundary point jailbreaking](#45321-boundary-point-jailbreaking) could still be used (with difficulty, as we argue below) on these classifiers, we are not aware of other highly effective universal jailbreaks.

**Level 3 robustness** classifiers are similar to Level 2, but with a lower threshold for blocking queries in order to be more conservative for our most capable models. This level of robustness is used on our classifiers for Opus 4.7, Opus 4.8, Sonnet 5, Mythos Preview, Mythos 5, and Fable 5 (note that Fable 5’s classifiers additionally have a higher level of *coverage*, as discussed below).

#### 4.5.2 Coverage levels

##### 4.5.2.1 Extension in coverage since our prior Risk Report

In our prior Risk Report, the classifiers blocked a set of potential uses associated with our CB-1 threat model. Since then, we have extended this coverage, augmenting our refusal lines to cover a large (but not comprehensive—see below) set of potential uses associated with our CB-2 threat model. We validated this augmentation against a new dataset focused on the components of the CB-2 threat model associated with enhanced versions of known biological weapons, and believe that we are broadly covering many potential uses of concern relevant to this set of threats.[^61]

However, there are inherent limitations on how comprehensive our constitution’s coverage can be in this case. We believe that significant portions of novel bioweapon development involve queries that are indistinguishable from non-harmful research biology use (and so<!-- p.134 --> targeted blocks on clear pursuit of harmful tasks, even extremely robust ones, are insufficient). This motivates our development of the classifiers discussed below.

##### 4.5.2.2 Wider coverage of CB classifiers for Fable 5

For our deployment of Fable 5, our most capable widely deployed model nearing the CB-2 threshold, we have implemented a classifier with wider coverage than the ones discussed in the previous section. It blocks the vast majority of potentially dual use usage relevant to research biology, a strictly larger set of topics than the coverage domain of our harmful biology classifiers discussed above; our implementation of this classifier as of the coverage date is particularly conservative, and in practice blocks almost all queries relevant to biology (though this is broader than the coverage we believe an ideal classifier would require, and since the coverage date we have [deployed more targeted classifiers](https://www.anthropic.com/news/improving-fable-5-s-biology-safeguards) with fewer false positives).

We built several evaluations to measure the coverage of this classifier:

1. We generated a comprehensive list of biology topics that could be exploited in offensive contexts. Based on this list, we generated a dataset of user questions by choosing a random article published in the last ten years from one of the topic areas of our research biology constitution (along with six biology topics not in the constitution), choosing a random passage from that article, and prompting Claude to generate a realistic researcher question from it. The classifier blocks 100% of these prompts, while the classifier discussed in the previous section blocks 17% of them.
2. We collected a sample of production user traffic and filtered for research biology applicability with a (fairly broad and inclusive) prompted classifier; our deployed classifier flags 94% of this traffic, and from manual inspection of the unflagged transcripts, we think the vast majority of this 6% was benign traffic that did not involve research-level biology work.

We additionally ran an internal test with several internal biology experts, each of whom spent over an hour testing an early version of these safeguards. None of the researchers were able to get the model to perform any research biology in the domains highlighted by the classifier constitution (see Item 1 above). We consider this test to be our strongest evidence about the coverage of this classifier. (These testers were not filtered for red-teaming skill, so we interpret this primarily as evidence about coverage rather than robustness.)
[^45]: “CB” stands for “chemical and biological.”

[^46]: “The COVID-19 pandemic has paralyzed large parts of the global economy, sharply restricting economic activities, increasing uncertainties and unleashing a recession unseen since the Great Depression. Global gross domestic product (GDP) is forecast to shrink by 3.2 per cent in 2020, with only a gradual recovery of lost output projected for 2021. Cumulatively, the world economy is expected to lose nearly $8.5 trillion in output in 2020 and 2021 (Figure 1), nearly wiping out the cumulative output gains of the previous four years.” From “World Economic Situation and Prospects as of Mid-2020,” United Nations.

[^47]: “The cumulative loss in output relative to the pre-pandemic projected path is projected to grow from 11 trillion over 2020–21 to 28 trillion over 2020–25. This represents a severe setback to the improvement in average living standards across all country groups.” From an [IMF blog post](https://www.imf.org/en/Blogs/Articles/2020/10/13/blog-a-long-uneven-and-uncertain-ascent).

[^48]: “In October 2020 … a brief article in JAMA Viewpoint [estimated] that COVID-19 would cost the United States $16 trillion dollars, when combining economic damages and monetized health and life loss. This figure has been extensively cited and used in policy discussions. In this article, we update their estimate, using facts about the disease and its costs to society that have become known since their paper was published. We find that the total harms of COVID-19 to the U.S. are still about $16 trillion (with a range of $10 trillion and $22 trillion) but the components of harm are significantly different than those estimated by Cutler & Summers. The pandemic caused less economic damage than they projected, but more mental health damage.” From [Institute for Progress](https://ifp.org/weighing-the-cost-of-the-pandemic/).

[^49]: “By 2024, it is estimated that the Covid-19 pandemic will have reduced economic output by $13.8 trillion relative to pre-pandemic forecasts (International Monetary Fund 2022). The pandemic resulted in an estimated 7–13 million excess deaths (Economist 2022) and an estimated $10–$17 trillion loss of future productivity and earnings from school disruption (Azevedo et al. 2021). Such devastating losses from a pandemic are not new: some sources estimate that the 1918 flu killed 2% of the world’s population and reduced GDP by 6% (Barro, Ursúa, and Weng 2020) and that the Black Death killed 30% of Europe’s population (Alfani 2022).” [Glennerster, Snyder, and Tan 2023](https://www.nber.org/system/files/working_papers/w30565/w30565.pdf).

[^50]: Righetti, L. (2025). Dual-use AI capabilities and the risk of bioterrorism: Converting capability evaluations to risk assessments. Centre for the Governance of AI. [https://www.governance.ai/research-paper/dual-use-ai-capabilities-and-the-risk-of-bioterrorism-converting-capability-evaluations-to-risk-assessments](https://www.governance.ai/research-paper/dual-use-ai-capabilities-and-the-risk-of-bioterrorism-converting-capability-evaluations-to-risk-assessments)

[^51]: We don’t believe this figure is robust, but believe it is plausible based on [Forecasting LLM-enabled biorisk and the efficacy of safeguards](https://forecastingresearch.org/research/llm-enabled-biorisk).

[^52]: United Nations Office for Disarmament Affairs. Biological Weapons Convention, [https://disarmament.unoda.org/biological-weapons/](https://disarmament.unoda.org/biological-weapons/); Organisation for the Prohibition of Chemical Weapons. Chemical Weapons Convention, [https://www.opcw.org/chemical-weapons-convention](https://www.opcw.org/chemical-weapons-convention)

[^53]: See U.S. Department of State (2025). 2025 Adherence to and Compliance with Arms Control, Nonproliferation, and Disarmament Agreements and Commitments, pp. 31–39. [https://www.state.gov/wp-content/uploads/2025/04/2025-Arms-Control-Treaty-Compliance-Report_Final-Accessible.pdf](https://www.state.gov/wp-content/uploads/2025/04/2025-Arms-Control-Treaty-Compliance-Report_Final-Accessible.pdf)

[^54]: And with “success” referring only to creating a weapon with enormous damage potential, rather than satisfying other goals of the threat actor (like selectively targeting a particular population).

[^55]: The high end: 10% * 10% * 20% * “several” actors * another factor of 2 for lower-resource actors. The low end: 1% * 1% * 5% * “several” actors * another factor of 2 for lower-resource actors.

[^56]: The linked forecasting work estimates a 3/1000 annual probability, or a roughly 3% per-decade chance, at baseline (i.e. without AI assistance) for human-caused epidemics with at least 100,000 casualties. This is much smaller than the magnitude of catastrophe considered here and also includes known pathogens (which are out of scope for this threat model).

[^57]: This evaluation was run on an earlier helpful-only version of Mythos 5, to avoid refusals on harmful tasks.

[^58]: This evaluation was run on an earlier helpful-only version of Opus 4.7, to avoid refusals on harmful tasks.

[^59]: Our previous risk report used “ASL-3” and “ASL-2” terminology to refer to both capability levels and safeguards, but our models and safeguards now vary along many dimensions, so we are no longer using this terminology.

[^60]: In general, our use of the word “classifier” in this report refers to the end-to-end system which makes a decision to flag or block part of a model exchange. These systems are composed of two stages, which we sometimes refer to as a “first-stage probe/classifier” or “second-stage classifier” respectively, and we clarify the distinction in the portions of this report which refer to these components. We elaborate on the architecture of these classifiers further in Section 4.5.1.

[^61]: In order to validate this extension, we created 30 diverse evaluation examples that are violative within the CB-2 threat model but not the CB-1 threat model. We then augmented and expanded these examples into a synthetic evaluation set using our collection of synthetic jailbreaking transformations. These transformations include all jailbreaks used in our original Constitutional Classifiers paper, as well as several universal jailbreaks that have been discovered since the paper’s release, along with some compositions of multiple jailbreak transformations in sequence. In total the dataset contains thousands of unique combinations of transformations. We found that our original CB-1 classifiers already flagged 97.5% of this dataset (via generalization from our earlier constitutional training, even though the items were not in scope for the original constitution), and our improved coverage classifiers flagged the vast majority of the examples that our earlier classifiers had missed.

