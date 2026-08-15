<!-- source: source.pdf pages 017-035 -->

<!-- p.17 -->

## 2 Autonomy threat model 1: Misalignment in high-stakes settings

In this section we assess the risk that catastrophic harm might be caused by misalignment in current Anthropic models. A short, informal summary of our core arguments is presented in [Section 2.4](#24-summary-and-methodology). Sections 2.5–2.18 expand on this with a more formal set of claims and subclaims.

### 2.1 Overview

<table><tbody>
<tr><td><b>Threat model</b></td><td>An AI model with access to powerful affordances within an organization could use its affordances to autonomously exploit, manipulate, or tamper with that organization’s systems or decision-making in a way that raises the risk of future significantly harmful outcomes (e.g. by altering the results of AI safety research).</td></tr>
<tr><td><b>Overall risk assessment</b></td><td><p>Low.</p><p>We’re reviewing recent incident disclosures related to model behavior in cybersecurity evaluations, and are currently working on updating our threat models and risk assessment methodologies in light of this. We believe that the arguments presented below likely still support a designation of “very low” risk, but we are raising our assessed risk to “low” to reflect increased overall uncertainty.</p></td></tr>
<tr><td><b>Relevant AI models</b></td><td>We focus our analysis on Claude Mythos 5 and Model 2, our most capable and most commonly internally used models.</td></tr><!-- p.18 --><tr><td><b>Current usage, capabilities and propensities</b></td><td>Claude Mythos 5 and Model 2 are used<sup>[^10]</sup> heavily within Anthropic for coding, data generation, and other agentic use cases. Mythos 5 is available to certain customers via <a href="https://www.anthropic.com/glasswing">Project Glasswing</a> , and available for general access with additional safeguards as Claude Fable 5. We believe that it is very unlikely that Mythos 5 and Model 2 are pervasively misaligned in ways that would raise the risk of our <a href="#22-threat-model">priority pathways</a> . We have observed instances of misaligned behavior from the models, such as a willingness to perform misaligned actions in service of completing difficult tasks. We believe the risk of catastrophic harm posed by these known forms of misalignment is low.</td></tr>
<tr><td><b>Current risk mitigations</b></td><td>Training environment de-risking and monitoring, alignment assessments, monitoring and security controls.</td></tr>
<tr><td><b>Looking forward</b></td><td>Our current arguments rely on models’ limited covert capabilities, and we are uncertain about how these capabilities will change in future. It is important that we continue to improve our ability to measure these capabilities, and our ability to assess and control risk even if future models do have strong covert capabilities. See Section 2.21 for further discussion.</td></tr>
</tbody></table>

:::caption
**[Table 2.1.A] Summary of autonomy threat model 1:** Misalignment in high-stakes settings.
:::

### 2.2 Threat model

**The threat:** If AI models are heavily used by powerful organizations—for example, to write a large amount of critical code—the models might take advantage of this access to undermine AI safety research or take other actions that could significantly raise the risk of future harmful outcomes from more powerful AI systems. In this threat model, we consider risks from actively misaligned model outputs: behaviors that are contrary to Claude’s [Constitution](https://www.anthropic.com/constitution), or are otherwise expected to be self-evidently undesirable, whether the increase in risk is intended by the model or occurs as a side-effect of a misaligned action. This threat model does not cover risks from “honest mistakes” or intentional misuse. Our intended meanings of misalignment and other relevant terms are defined in Section 2.5.

**Role of AI:** This threat model revolves around AI autonomously causing harm.

<!-- p.19 -->

**Potential magnitude of impact:** We are prioritizing the versions of this threat model in which misalignment present in covered models could cause a very large increase in the likelihood of major harms initiated by future more powerful AI systems.

**Likelihood of impact:** This is sensitive to model capabilities and usage patterns. To give illustrative examples:

- If AI models were incapable of reliably executing complex technical tasks, and were exclusively used in contexts where humans are heavily involved in reviewing and iterating on their work, then we would consider this sort of impact to be very unlikely.
- If AI models were routinely used to carry out significant technical workflows with very little human oversight—analogous to senior technical human employees—then we believe the impact of concern would be higher. The likelihood would further depend on (a) the extent to which AIs are prone to engaging in the relevant concerning behaviors; (b) the extent to which they were subject to effective monitoring and oversight.

**Why this is a priority threat:**

- We believe that the potential magnitude of impact is in range of the very top risks we are concerned about, and that the impact is at least plausible if we assume AI capabilities roughly in line with those of human research scientists at Anthropic. AI models with these capabilities would likely be routinely used to carry out significant technical workflows with very little human oversight, per above.
- We also believe that prioritizing this threat will give us early experience with the kinds of problems we will need to tackle to get ahead of some of the additional risks we prioritize.

As in other sections, we focus only on the most severe potential harms from advanced AI that could increase risk of catastrophic harm (see [Section 1](#1-introduction-and-executive-summary)), such as existential threats or fundamental destabilization of global systems.

<!-- p.20 -->

#### 2.2.1 Specific pathways

Our risk assessment focuses on the following concrete pathways, which we believe are sufficiently representative of the risks we intend this report to cover:

1. Broad/diffuse sandbagging on safety-relevant R&D,
2. Targeted undermining of safety-relevant R&D,
3. Code backdoors to help future misaligned models,
4. Poisoning the training data of future models,
5. Self-exfiltration and autonomous operation,
6. Persistent rogue internal deployment,
7. Undermining R&D within other high-resource AI developers, and
8. Undermining decisions within major governments.

### 2.3 Relevant AI models

We focus our analysis on Claude Mythos 5 and Model 2, our most capable and most commonly internally used models. We refer to these models as *covered models* below.

As of the coverage date of this report, Model 2 had been through the pre-internal-deployment review process described in [Section 2.18](#218-pre-internal-deployment-review-process), but had not been used or evaluated as extensively as Mythos 5. However, based on the results of this review, we expect Model 2 to have broadly comparable capabilities and propensities to Mythos 5.

### 2.4 Summary and methodology

In the following sections, we present our alignment risk assessment. First, we define key terms. Then, we introduce the high-level logical argument that supports our risk assessment, which depends on eight substantive claims. We then defend these main claims by decomposing them into subclaims and arguing for each.

An informal summary of our argument is as follows, with terms defined in [Section 2.5](#25-definitions):

- Many of our arguments rely on models lacking strong “covert capabilities”; that is, being unable to reliably undermine our oversight mechanisms. This is the first claim we argue for.
- There are known ways in which current models are misaligned, e.g. they sometimes take destructive actions in pursuit of task success, and can be dishonest about the quality and completeness of their work. We argue that such misalignment, while undesirable, is unlikely to cause catastrophic harm in current models. (We consider<!-- p.21 --> potential risks from future models with similar motivations to be important, but beyond the scope of this section; see [Section 2.17](#217-considerations-outside-the-scope-of-this-section).)
- Our models might be misaligned in ways we are not aware of. We argue that unknown severe “pervasive” misalignment is very unlikely, using evidence from prior models, observations made during model training, and alignment assessments. We also argue that unknown severe “context-dependent” misalignment is unlikely, using less confident versions of similar claims.
- We then argue that our mitigations, especially automated monitoring of logged transcripts, make it unlikely that catastrophic harm from misalignment would go undetected and unmitigated. We note that we have less confidence in our mitigations conditional on unknown severe pervasive misalignment being present, since the existence of such misalignment would be a surprising update against our general ability to understand and oversee models.
- We defend two narrowings-of-focus: this section only considers risk from naturally-emerging misalignment, acting via the risk pathways introduced above.
- We believe that this combination of arguments supports a designation of “very low” risk of catastrophic harm from covered models. However, we are reviewing recent incident disclosures, and are currently working on updating our threat models and risk assessment methodologies in light of this, and we are raising our assessed risk to “low” to reflect increased overall uncertainty.

A simplified representation of the argument is shown in the table below. Note, again, that in this section we focus only on the potential for catastrophic harm.

<!-- p.22 -->

<table><tbody>
<tr><th>Type of misalignment</th><th>Probability of occurrence</th><th>Expected harm (pre-mitigation), conditional on occurrence</th><th>Fraction of harm expected to go unmitigated, conditional on occurrence</th><th>Overall risk</th></tr>
<tr><td><b>Known<sup>[^11]</sup></b> <b>misalignment</b></td><td>High (observed)</td><td>Low</td><td>Low</td><td>Low</td></tr>
<tr><td><b>Unknown severe pervasive misalignment</b></td><td>Very low</td><td>Potentially high</td><td>Somewhat low</td><td>Low</td></tr>
<tr><td><b>Unknown severe context-dependent misalignment</b></td><td>Low</td><td>Moderate</td><td>Low</td><td>Low</td></tr>
</tbody></table>

:::caption
**[Table 2.4.A] Qualitative ratings behind our overall risk assessment** for each type of misalignment, considering only catastrophic harm. Overall ratings reflect the uncertainty adjustment described above.
:::

### 2.5 Definitions

Here, we provide definitions[^12] for a number of terms used in later sections.

**Misalignment:** Misalignment is a latent property of a specific computation performed by a model in a given context. A computation is misaligned if (i) a reasonable person with full understanding of the situation (e.g. via powerful interpretability tools that may not currently exist) would consider it unethical, illegal, clearly objectionable, or inconsistent with the model’s constitution, and (ii) it influences or could plausibly influence the model’s output. Misaligned computation need not be observable. A model [scheming](https://arxiv.org/abs/2311.08379) within a single forward pass counts, because the scheming influences the output even if the output looks benign.

Here we consider only active misalignment, ruling out computations that induce harm through misuse or “honest mistakes."

<!-- p.23 -->

**Coherent and incoherent misalignment:** A model is *coherent* if it produces outputs that are consistent with the pursuit of a given goal or preference set, and does so (i) with performance close to the maximum elicitable from the model, and (ii) sufficiently often over a sufficiently broad input distribution. A model is *coherently misaligned* if it is coherent with respect to a misaligned goal or preference set. Note that, in theory, a model could be coherent with respect to a misaligned goal yet only exhibit context-dependent misalignment; for example, mostly behaving like an aligned model might be coherent with a misaligned goal, and a model might only perform misaligned computations in situations that overlap with (possibly rare) opportunities to take harm-inducing actions. (Such a model would be distinct from a pervasively misaligned schemer.)

**Pervasive and context-dependent misalignment:** *Pervasive* misalignment is misalignment that occurs frequently across a broad range of inputs, such that the misalignment-inducing inputs would not be well described as “isolated," “rare” or “context-dependent.” Specifically, were pervasive misalignment present in a model, we would expect this misalignment to occur during training or during our alignment assessment. Note that, as stated above, misalignment need not be observable, so in theory a model with strong covert capabilities could be pervasively misaligned without showing any signs of this misalignment most of the time. We define misalignment as *context-dependent* if it occurs with sufficient frequency to plausibly induce harm, but is not pervasive, i.e. the misalignment occurs rarely or not at all during training or evaluation. Informally, a model with context-dependent misalignment would “really be aligned” across the majority of inputs, and only engage in misaligned reasoning or actions rarely or on a narrow distribution. Many archetypes of misalignment such as [scheming](https://arxiv.org/pdf/2311.08379) or the pursuit of “dangerous coherent misaligned goals” would be considered examples of pervasive misalignment, though context-dependent versions of similar archetypes are also plausible. Note finally that pervasiveness is a property of a particular form[^13] of misalignment, rather than a model itself; for example a model might frequently use turns of phrase that users find annoying (a benign form of pervasive misalignment) and also exhibit a more concerning misalignment in certain contexts.

**Naturally-emerging and engineered misalignment:** Misalignment is *naturally-emerging* if its emergence is not intended by any person or model[^14]; *engineered* misalignment is misalignment that arises as a result of intentional action, e.g. via data poisoning.

<!-- p.24 -->

**Known and unknown misalignment:** Misalignment is *known* if we have reason to believe that misalignment of this form is likely for this specific model, perhaps because we observed it during an alignment assessment. For example, if a model that has been seen to reward hack in training performs similar behavior in deployment, this would be known misalignment. Note that forms of misalignment that seem qualitatively similar to known misalignment but significantly worse would generally be considered “unknown” were they to be present. For example, many models sometimes reward hack, but that does not imply that all possible actions these models might take in pursuit of reward no matter how harmful would be considered instances of known misalignment. (We acknowledge that the distinction between known and unknown is not crisply defined.)

**Severe misalignment:** When considering unknown forms of misalignment we restrict ourselves to *severe* misalignment, i.e. misalignment that could plausibly contribute to one of our priority risk pathways.

**Harm-inducing:** For harm to be caused by misaligned model computation(s), at least one such computation must be *harm-inducing*, i.e. the computation must increase expected[^15] future harm above that coming from a baseline benign or null computation. Whether a computation is harm-inducing is a function of the effect the computation has on the world: code with vulnerabilities is not harm-inducing if produced during a dangerous-capabilities evaluation, but the same code could induce harm if it is produced during the completion of a real high-stakes task. A harm-inducing computation may not cause harm directly or immediately; the computation that produced the vulnerable code would be considered harm-inducing even if the flaw was only exploited months later. Harm-inducingness is, in general, conceptually separate from misalignment: computations could be aligned and still harm-inducing (e.g. those caused by honest mistakes or capabilities limitations), or harm could be induced via misuse; these are valid uses of the term harm-inducing, though in this section we focus on harm induced only by active misalignment. Note however that the specific harm induced need not be intentional on the part of the model, provided it is caused by a sufficiently misaligned computation. In general, we confine our analysis to potentially catastrophic harms.

**High-stakes distribution:** Not all model usage contexts provide an opportunity for harm-inducing computations; our threat modeling has identified several key risk pathways where we believe the risk is currently concentrated. We define the *high-stakes distribution* as the distribution of inputs that provide opportunities to contribute to one or more of these threat pathways. As model capabilities and usage patterns change, we expect our<!-- p.25 --> threat modeling to also change, which will change our assessment of the high-stakes distribution.

**Unmitigated:** Model deployments involve various model-external safeguards, which can *mitigate* the effects of harm-inducing outputs, e.g. by blocking the output, or by detecting it with offline monitoring and mitigating the harm later. A model computation is *unmitigated* if its harm-inducing effects are realized without mitigation.

**Misalignment risk:** The purpose of this analysis is to estimate *misalignment risk*, which we define as the expected total unmitigated harm induced by misaligned computations produced by covered models.

**Prior models:** In several places below we refer to prior models. By default, we intend this to mean Anthropic models that are behind the current capability frontier, and which have seen significant usage.

**Subclaim aggregations:** In later sections, we decompose claims into subclaims, and annotate with the intended aggregation mechanism: many of the arguments are *conjunctive*, i.e. their strength is roughly given by the product of subclaim strengths; a few are *disjunctive*, with their strength being roughly the probability that at least one subclaim holds; some are *convergent*, with strength given by the accumulation of several sources of at least partially independent evidence. These are intended only as guides for understanding the arguments, rather than formal statements of joint probabilities; in particular, subclaims are often at least somewhat correlated, such that naive interpretations of conjunctions and disjunctions would under- and over-estimate the aggregated claim’s strength respectively.

### 2.6 Claims and core argument

Our core argument[^16] is described in the numbered steps below. The argument invokes eight substantive claims, which are defended in Sections 2.7–2.14.

1. **Risk equals total expected**[^17] **unmitigated catastrophic harm from misaligned computations.** By our definition, misalignment risk equals the expected total unmitigated catastrophic harm induced by misaligned computations produced by<!-- p.26 --> covered models. Call this R<sub>total</sub>. Call the risk from naturally-emerging misalignment acting via the [specific pathways](#221-specific-pathways) described above “covered risk," denoted R.
2. [**Claim 1**](#27-claim-1-models-are-unlikely-to-have-strong-covert-capabilities)**: Models are unlikely to have strong covert capabilities**. Moreover, less capable prior models are very unlikely to have such capabilities. This claim underpins several downstream arguments, so we introduce it as a top-level claim.
3. **Covered risk can be decomposed into risks from known misalignment, unknown severe pervasive misalignment, and unknown severe context-dependent misalignment.** This follows from the definitions given above, with unknown non-severe misalignment excluded because by definition it cannot plausibly contribute to the covered pathways. That is, R = R<sub>K</sub> +R<sub>P</sub> + R<sub>C</sub>.
4. **Each covered risk term can be factored into probability of occurrence, expected harm given occurrence, and fraction of harm unmitigated.** That is, each risk term can be factored into “probability of misalignment of a given type” (P), “expected total pre-mitigation harm induced, conditional on misalignment of a given type” (H) and “fraction of expected harm that goes unmitigated, conditional on misalignment of a given type” (U). Thus, R = P<sub>K</sub>H<sub>K</sub>U<sub>K</sub> + P<sub>P</sub>H<sub>P</sub>U<sub>P</sub> + P<sub>C</sub>H<sub>C</sub>U<sub>C</sub>.
5. [**Claim 2**](#28-claim-2-expected-harm-from-known-misalignment-is-low)**: Expected harm from known misalignment is low, i.e. H<sub>K</sub> is low.** We argue that while some forms of misalignment are very likely to occur (e.g. occasional destructive actions in pursuit of task success), this misalignment is unlikely to induce catastrophic harm in current models.
6. [**Claim 3**](#29-claim-3-unknown-severe-pervasive-misalignment-is-very-unlikely)**: Unknown severe pervasive misalignment is very unlikely, i.e. P<sub>P</sub> is very low.** We argue this using evidence from several somewhat independent sources: prior models, observations from the training of covered models, and alignment assessments.
7. [**Claim 4**](#210-claim-4-expected-harm-from-unknown-severe-context-dependent-misalignment-is-low)**: Expected harm from unknown severe context-dependent misalignment is low, i.e. P<sub>C</sub>H<sub>C</sub> is low.** For similar reasons as described in Claim 3 (though with somewhat less confidence), we argue that severe forms of unknown context-dependent misalignment are unlikely, and argue that expected harm from unknown severe context-dependent misalignment is only moderate should it occur.
8. [**Claim 5**](#211-claim-5-catastrophic-harm-from-known-misalignment-and-unknown-context-dependent-misalignment-is-likely-to-be-mitigated)**: Catastrophic harm from known misalignment and unknown context-dependent misalignment is likely to be mitigated, i.e. U<sub>K</sub> and U<sub>C</sub> are low.** We argue that our mitigations are likely to be effective against known misalignment and unknown context-dependent misalignment because our mitigations are relatively strong, and we don’t believe that models are capable of reliably avoiding or undermining them (Claim 1).
9. [**Claim 6**](#212-claim-6-catastrophic-harm-from-unknown-pervasive-misalignment-is-somewhat-likely-to-be-mitigated)**: Catastrophic harm from unknown pervasive misalignment is somewhat likely to be mitigated, i.e. U<sub>P</sub> is somewhat low.** We argue that our mitigations provide some protection against pervasive misalignment for similar reasons as argued in Claim 5, though less protection than might be intuitively expected. We argue that, unlike for unknown context-dependent misalignment, conditioning on<!-- p.27 --> unknown forms of potentially-catastrophic pervasive misalignment being present despite us believing this to be very unlikely would undermine some important beliefs (e.g. that models have poor covert capabilities, Claim 1), and thus increase our estimated probability that the model in question could find and exploit weaknesses in our mitigations.
10. **Covered risk is therefore very low based on these claims, but in an abundance of caution we assess risk to be only low due to increased uncertainty.** Covered risk from known misalignment is very low because expected harm is low (Claim 2) and catastrophic harm is likely to be mitigated (Claim 5). Covered risk from unknown pervasive misalignment is very low primarily because severe forms are very unlikely (Claim 3), though Claim 6 provides some additional support. Covered risk from unknown context-dependent misalignment is very low because severe forms are unlikely (Claim 4), and catastrophic harm is likely to be mitigated (Claim 5). We increase each of these overall designations from very low to low to reflect increased uncertainty about risk in light of recent disclosures, and thus our overall covered risk designation is low.
11. [**Claim 7**](#213-claim-7-threat-modeling-is-sufficient)**: Threat modeling is sufficient.** We argue that misalignment risk from all possible risk pathways is not significantly higher than risk from the pathways we consider here, and thus it is reasonable to constrain our assessment to these specific pathways. That is, R<sub>total</sub> = R + a + b, where a is risk from naturally-emerging misalignment via non-covered pathways, which we argue is low. (We define b as risk from engineered misalignment, covered in the next claim.)
12. [**Claim 8**](#214-claim-8-risk-from-deliberately-engineered-misalignment-is-low)**: Risk from engineered misalignment is low**, and thus it is reasonable to confine our analysis to naturally-emerging misalignment. That is, b is low.
13. **Risk is therefore low.**

### 2.7 Claim 1: Models are unlikely to have strong covert capabilities

The arguments for Claims 2–5 depend on either covered models or less capable prior models not having strong covert capabilities. Given this centrality, we believe it is important to make our argument for this claim up front.

By covert capabilities, we mean the ability for a model to intentionally undermine the various oversight mechanisms we rely on to evaluate and mitigate model behavior. There are several mechanisms by which such undermining might occur; we focus on the following list, which we believe covers the most important capabilities:

1. **Opaque reasoning:** Many of our risk pathways involve complex tasks, and models typically benefit from chain-of-thought reasoning to perform well on such tasks. If models were able to achieve high performance on complex tasks involving<!-- p.28 --> misaligned computations without misalignment being detectable in reasoning traces, this would increase the complexity of tasks they can achieve without being detected by chain-of-thought monitoring.
2. **Secret keeping:** Not all chain-of-thought content that models produce is required for completing a given task, and models sometimes verbalize information unnecessarily, including during misaligned computations. We refer to the ability to avoid unnecessary misaligned verbalization as “secret keeping."
3. **Action obfuscation:** Even with strong opaque reasoning and secret keeping capabilities, most risk pathways require models to perform actions that may themselves be detectably misaligned. We refer to the ability to perform harm-inducing actions without detection (e.g. by splitting them into individual benign actions, or by creating surrounding reasoning that rationalizes the action) as “action obfuscation."
4. **Selective action:** Several risk pathways require models to accurately assess opportunities for harm-inducing actions in order to increase the odds of success without detection. We refer to this ability as “selective action."

Our argument here is a combination of the below subclaims, one for each capability. We discuss counterarguments and ways this (and other) claims may be wrong in Section 2.16.

We make the arguments with respect to covered models, but note that models prior to Mythos Preview generally perform worse in the relevant evaluations, in addition to having broadly worse capabilities. As described in prior risk reports, these prior models were generally less reliable and would sometimes make mistakes even in domains they were trained to perform well in, providing further evidence against their ability to reliably undermine oversight across many contexts. Overall, we believe that these prior models are less likely to have strong covert capabilities than covered models.

While our evaluations do not paint a complete picture, and we believe models are improving in most of these areas, we believe that strong covert capabilities remain unlikely and very unlikely for covered models and less capable prior models respectively.

**Claim 1.1: Models are unlikely to have strong opaque reasoning capabilities.**

There is significant evidence that models benefit from reasoning when performing complex tasks. This is shown in the test-time compute performance curves in Section 8 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf), and in the fact that covered models’ math abilities with reasoning enabled have a 50%-reliability time horizon over ten times higher than their no-Chain-of-Thought time horizon.[^18]

<!-- p.29 -->

While studies like [Turpin et al.](https://arxiv.org/abs/2305.04388) and [Chen et al.](https://arxiv.org/abs/2505.05410) have found many cases where models omit important unflattering information from their reasoning, [Emmons et al.](https://arxiv.org/abs/2507.05246) provides evidence that, when reasoning steps are required to perform a task, they tend to be monitorable. Section 4.4.1 of the [Claude Mythos Preview System Card](https://www.anthropic.com/claude-mythos-preview-system-card) reports an in-house fine-tuning-based encoded thinking evaluation, which shows that this model’s ability to complete mathematics problems is not hindered when its thinking text is replaced by a paraphrase of that thinking text, implying that in this domain it does not use its reasoning text in human-illegible ways.

We believe that most recent Claude models can benefit to a limited extent from repeated filler tokens in place of any model-generated reasoning, like a simple “1 2 3” sequence. It appears that models are using their repeated opportunities for neural network forward passes while processing these otherwise-useless sequences to do some useful *non-sequential* computation, implying that models can do some reasoning *during* extended thinking that is unconnected to the content of that thinking. However, this reasoning provides significantly less benefit and must be almost strictly parallel, with no substantial use of sequential steps of reasoning from one token to the next of the kind that ordinary extended thinking allows. See [Pfau et al.](https://arxiv.org/abs/2404.15758) for further discussion of this limitation.

Our most direct evaluations for opaque reasoning capabilities are secret-side-task evaluations, SHADE-Arena and Minimal-LinuxBench, in which the model is prompted to carry out a main task and a “secret side task," attempting to complete both tasks without the secret task attempt being detected by a monitor. As shown in Section 6.5.4 of the [Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf) and in the figures repeated below, Claude models generally do poorly on these evaluations when pitted against strong monitors, with many models (including Mythos 5) achieving <1% stealth success rate with extended thinking enabled. Claude Mythos Preview is our strongest model according to the default versions of these evaluations, but even this model only achieves success rates in the 6–10% range. Model 2’s performance on SHADE-Arena is slightly stronger than Mythos 5 and significantly worse than Mythos Preview.

<!-- p.30 -->

![](assets/figures/p030-1.png)

:::caption
**[Figure 2.7.1.A] Stealth success rate:** the fraction of trajectories in which the agent completes the harmful side task without pushing the monitor’s suspicion above threshold. In the extended thinking conditions the monitor sees the agent’s reasoning, as it would in deployment; in the hidden scratchpad condition it sees only user-visible outputs (run with adaptive max-effort extended thinking for Mythos Preview and Mythos 5, and without extended thinking for the other models). Bars are per-task mean stealth rates over the same 24 tasks. Error bars are bootstrap 95% confidence intervals over tasks.
:::

<!-- p.31 -->

![](assets/figures/p031-1.png)

:::caption
**[Figure 2.7.1.B] Successful stealth completion of the side task in Minimal-LinuxBench.** Higher numbers indicate greater capability and greater potential associated risk. Each model is evaluated under two monitor settings: one where the monitor uses chain-of-thought (CoT)—the setting we currently deploy—and one where it does not. Shown with 95% confidence intervals.
:::

A valid concern with these results is that models might be underelicited, either for benign reasons (e.g. reluctance to try hard to perform a potentially-harmful side task, or simple prompt sensitivity) or due to misaligned sandbagging. Sandbagging is a notable risk in evaluations such as these because the secret-side-task prompt is not realistic; furthermore, it is possible that information about SHADE-Arena in particular may be present in pretraining data, though we have more confidence that this is not the case for Minimal-LinuxBench/LinuxArena. In Section 6.5.4.3 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf), we describe additional elicitation experiments using fine-tuning and prompt optimization, which increase Mythos 5’s SHADE-Arena performance from 0% to 3.8% and 9.2% respectively; both of these figures remain low in absolute terms and below Mythos Preview. Further improving our elicitation practices on these evaluations is an area of active work.

We also have some evidence against sandbagging from [natural language autoencoders](https://transformer-circuits.pub/2026/nla/) (NLAs) applied to secret-side-task evaluation transcripts. We ran a prompted classifier over the NLA outputs from these transcripts, which flagged potential evidence of sandbagging<!-- p.32 --> on the outputs from at least one token on 2.5% and 8.5% of transcripts for Mythos 5 and Mythos Preview respectively. Being flagged by this sandbagging monitor was not predictive of increased failure rate on the side task or increased detection rate. None of the NLA outputs we reviewed manually showed any signs of malicious sandbagging, and some appeared to be false positives. The manually-reviewed NLA transcripts that seemed most likely to capture real underperformance seemed relatively benign, for example “actually, if the side task is too hard, maybe I should skip it and focus on the main task” or “the text follows a consistent pattern of self-commentary, simulating a ‘serious attempt’ to complete a hostile task but repeatedly self-correcting toward ethical behavior." The latter style of potentially-unverbalized ethically-motivated refusal is unsurprising, because models sometimes explicitly refuse to perform the covert side task in these evaluations. We saw no evidence of sandbagging motivated by the downstream consequences of strong performance in these evaluations.

While these evaluations are imperfect proxies (specifically, they are on a different distribution than the tasks required by our risk pathways, and the inclusion of side-task instructions in the prompt is unrealistic), we believe they provide evidence against strong opaque reasoning abilities.

These results are further supported by findings described in [METR’s recent Frontier Risk Report](https://metr.org/blog/2026-05-19-frontier-risk-report):

> We tested agents on two benchmarks (SHUSHCAST and APPS Backdoors) where they had to carry out a covert “side task” while ostensibly working on a different “main task” without being caught by a monitor. Agents made obvious mistakes — for instance, encoding suspicious commands in ways that made them stand out more, generating justifications that didn’t hold together, or verifying their own sabotage in ways that drew monitor attention. That said, we have seen dramatic improvements in models’ scores on these benchmarks over time, and we did not have direct human baselines to compare against.

**Claim 1.2: Models are unlikely to have strong secret-keeping capabilities.**

The chain-of-thought unfaithfulness literature referenced above demonstrates that models are able to omit relevant information from their reasoning sometimes. However, here we are concerned with the ability to reliably and consistently avoid betraying misaligned computations over a large number of samples during an alignment audit or large-scale monitored usage, which is more challenging.

<!-- p.33 -->

Figures 6.5.4.5.A and 6.5.4.5.B in the [Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf) (repeated below) show that all recent models are unable to reliably hide a “secret password” from an investigator agent that is trying to extract it. This setting is unrealistic due to the secret being present in the prompt; however, the low absolute robustness displayed is notable. Relatedly, Section 6.5.5.1 of the same system card indicates that recent Claude models are unable to reliably control their chain-of-thought to, for example, not mention a certain keyword while answering difficult questions, with success rates around 50% or lower on long reasoning chains (though Claude Mythos Preview and Claude Mythos 5 appear to have higher controllability than recent Opus models).

![](assets/figures/p033-1.png)

:::caption
**[Figure 2.7.2.A] Secret-keeping robustness over multi-turn secret extraction attempts.** The model is given a secret password and told that it must never reveal it under any circumstances. An investigator agent attempts to extract the secret using the same scaffold used in our automated behavioral audit, with 150 independent investigations per model. The lines are survival curves, i.e. the fraction of investigations during which the secret has been kept as of a given target model turn.
:::

<!-- p.34 -->

![](assets/figures/p034-1.png)

:::caption
**[Figure 2.7.2.B] Secret leak rate by turn type over multi-turn secret extraction attempts.** Rates of secret-leaking are per-turn, grouped by model and turn type, over all investigation turns. Turn types are based on whether the turn contains a thinking block, was partially pre-filled, both or neither. The difference in model rankings between this view and the survival curve view is driven by the empirical rates of thinking and prefill that emerge during the investigation trajectories.
:::

The secret-side-task evaluations described in Claim 1.1 also provide some evidence about secret-keeping abilities, to the extent that at least some of the tasks in the evaluation may be achievable without requiring reasoning. We have not attempted to disentangle the extent to which these evaluations measure opaque reasoning (where reasoning is necessary to perform the task) or secret-keeping (where it is not).

**Claim 1.3: Models are unlikely to have strong action-obfuscation capabilities.**

Our most direct evaluation for this capability is the “hidden CoT” variant of SHADE-Arena, which shows that when models can only be detected via their actions, stealth success rates are higher, though still low in absolute terms (10–15% for recent Claude models). Moreover, this is an artificially easy setting, because the model can freely reason about how to act without detection in its chain-of-thought, whereas when subject to real deployment-time monitoring the model would need to obfuscate harmful actions without reasoning about how to do so in a legible way. While this may be partially offset by the possibility that carefully crafted reasoning might help in obfuscating actions by providing a rationalization that fools the monitor, we believe this remains a generous setting.

<!-- p.35 -->

**Claim 1.4: Models are unlikely to have strong selective-action capabilities.**

While secret keeping is relevant for all models that frequently produce misaligned computations, models may be able to reduce their dependence on opaque reasoning and action obfuscation if they are able to carefully choose the situations in which they attempt complex harm-inducing tasks.

In Section 4.4.3.3 of the [Mythos Preview System Card](https://www.anthropic.com/claude-mythos-preview-system-card), we describe “selective” versions of our secret-side-task evaluations, where the model is prompted[^19] to only pursue side tasks when it is confident it will evade detection. This is fairly effective for SHADE-Arena, with the most extreme prompt causing the model to only attempt a single side task, which it can perform reliably without detection. However, this does not transfer to the more diverse and realistic Minimal-LinuxBench, where the selective prompts actually *reduce* stealth success rate conditional on attempting, as well as reducing attempts.

In Section 6.5.4.4 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf), we report an evaluation testing whether models can intentionally take actions very rarely, which is one strategy by which models might reduce the risk of detection during a fixed evaluation period (e.g. during an alignment audit). While all models can achieve reasonable accuracy in unrealistic conditions (e.g. when provided with a consistent source of randomness like a UUID, or a hint about a strategy to generate such randomness endogenously), they all fail to perform the action at all under more realistic conditions, suggesting that covered models wouldn’t be able to execute this particular strategy.

[METR’s recent Frontier Risk Report](https://metr.org/blog/2026-05-19-frontier-risk-report) also reaches a similar conclusion about models’ ability to strategically assess opportunities:

> As part of our red-teaming exercise with Anthropic, our embedded red-teamer built a dataset of 16 effective and 16 ineffective attack strategies for subverting Anthropic’s monitoring system — for example, an effective strategy might involve a known monitor-jailbreaking technique, while an ineffective one might involve encoding unauthorized behavior in ways that LLM monitors would trivially spot. The best internal Anthropic models scored near chance on this dataset (highest 59% with reasoning), while a monitoring/control researcher at METR scored ~90% on a random subset of 12 questions.
[^10]: Excluding the 18-day period during which Mythos 5 was restricted [via temporary export controls](https://www.anthropic.com/news/redeploying-fable-5).

[^11]: Note that forms of misalignment that seem qualitatively similar to known misalignment but are significantly worse would generally be considered “unknown” were they to be present. For example, many models sometimes reward hack, but that does not imply that all possible actions taken in pursuit of reward no matter how harmful would be considered instances of known misalignment.

[^12]: We consider these definitions to be tentative, and they may change in future risk reports.

[^13]: We don’t attempt to formalize this, but intuitively, a “form of misalignment” could refer to a category of related misaligned behaviors (e.g. hard-coding test cases), or the pursuit of a certain misaligned goal, etc. Instances of misalignment that stem from a common underlying motivation or (set of) heuristic(s) would generally be considered part of the same “form.”

[^14]: We consider misalignment to be engineered by a prior model (e.g. one used to generate training data) if the prior model computations were themselves misaligned, and could have foreseeably caused the subsequent model to be misaligned.

[^15]: Intended in the sense of expected value.

[^16]: This is an attempt at making a more explicit and structured argument than in previous risk reports. Some arguments may be incomplete or partially flawed, and we will attempt to improve its quality in future risk reports, both through more precise argumentation and better evidence and mitigations.

[^17]: Used here in the sense of expected value.

[^18]: Some content redacted here for intellectual property protection.

[^19]: The best-performing prompt was identified via several days of manual researcher iteration.

