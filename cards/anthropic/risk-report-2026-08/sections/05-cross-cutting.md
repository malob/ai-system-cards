<!-- source: source.pdf pages 158-174 -->

<!-- p.158 -->

## 5 Cross-cutting content

### 5.1 Acceleration dynamics

In addition to risks posed directly by our AI systems (such as those discussed above), there are some general ways in which Anthropic may be contributing to global risks. In particular, by developing models with powerful capabilities, we potentially enable other developers to do so faster, via:

- The possibility of distilling on our models, which violates our [Usage Policy](https://www.anthropic.com/legal/aup) and which we work to prevent.
- The possibility of internal research advances diffusing more broadly, e.g. via intellectual property leaks or other developers inferring paths to capability improvement from studying our models.
- The usage of our models by other frontier AI developers to perform work that accelerates their AI R&D efforts (in violation of our Terms of Service).
- General acceleration of AI capabilities worldwide via demonstrating commercial viability (leading to more investment), reserving compute (leading to a greater supply of compute), etc.

Even if we implement strong enough risk mitigations to keep direct risks low, we may be accelerating other AI developers in building powerful AI systems that pose similar risks to the ones ours pose—without necessarily having commensurate safeguards. We may also be generally hastening the arrival of powerful AI systems that society isn’t prepared for.[^82]

Since our last Risk Report, we have been working to enhance our safeguards against distillation: other AI developers training their models on our models’ outputs, in order to improve these models’ capabilities. We have additionally implemented some initial safeguards against the usage of our models for frontier LLM R&D as of the coverage date, but don’t currently feel that we can make a strong case for their efficacy and don’t expect the costs from this component of the threat model to be significantly reduced via our mitigations on this front; as such, we don’t discuss them further in this section.

<!-- p.159 -->

Safeguards against competitor usage and distillation are in our interests as a company for obvious reasons,[^83] but we include some discussion here because they are also relevant to the risks noted above. Overall, we don’t claim we have eliminated our impact on acceleration dynamics or reduced it to a minor concern, but we believe we have somewhat better mitigations than we did as of our last Risk Report.

#### 5.1.1 Distillation

##### 5.1.1.1 Introduction

Distillation describes the process of training a less capable model on the outputs of a stronger one. Distillation is a widely used and often legitimate training method; many AI labs distill their own models to create smaller, cheaper versions for their customers.

We use the term “distillation attack” to refer to a distinct case of distillation: the unauthorized, systematic extraction of a model’s output transcripts for the purpose of training a separate model, carried out by circumventing controls such as regional access restrictions, in violation of our usage policy.

If the resulting distilled model inherits risk-relevant capabilities of the original model but is served without adequate safeguards, this could impose risk on the world downstream of the original model’s capabilities even if the original model had strong safeguards against direct misuse.

We define a successful distillation attack as one that satisfies two criteria:

- **Volume:** The attacker must be able to collect a large, diverse set of conversation transcripts with the model. Prior observed distillation attempts have gathered ~10,000 or more transcripts, which we take as a rough benchmark for a meaningful attack.
- **Uplift:** The collected transcripts must capture the model’s reasoning in enough detail that training a weaker model on them produces a real improvement in agentic evaluations we consider high-risk (coding, cyber-offense, and biology).

We have implemented new defenses against both volume and uplift since our previous Risk Report, described below. As of the coverage date, these defenses (other than our<!-- p.160 --> preexisting practice of summarizing thinking text) are applied only to Claude Fable 5, our most recent frontier model deployed for general access.

##### 5.1.1.2 Thinking and connector text summarization

We already implement a basic defense against distillation: summarizing the model’s internal reasoning before showing it to the user, which we have applied by default to longer reasoning transcripts on models since Claude Opus 4.

Separately from its hidden thinking, the model sometimes produces visible reasoning-like text in between tool calls while it works through a multi-step task; we refer to this as “connector text.”

This connector text can still be a useful source of training data about the model’s reasoning process. To mitigate uplift, we have implemented *connector text summarization* (CTS): all connector text between 50 and 500 tokens in length is passed through a smaller, faster model (Claude Haiku 4.5 as of the coverage date) that rewrites it into a shorter paraphrase.

This intervention had a minor bug which limited its effectiveness on one deployment surface for a few days after the launch of Fable 5, which we have since fixed.

To measure the efficacy of these protections, we fine-tuned base models on transcripts taken from a production teacher model, and evaluated the performance of the resulting model against evaluations in agentic coding, cyber, and biology when distilled with no mitigations, versus when distilled with thinking summarization, and CTS.

Results from a subset of these experiments are shown below. The effectiveness of distillation and of CTS varies strongly based on the teacher model used, in part because different production models vary in how much they write in between tool calls.

<!-- p.161 -->

![](assets/figures/p161-1.png)

![](assets/figures/p161-2.png)

:::caption
**[Figure 5.1.1.2.A] Results on agentic coding evaluations.**
:::

<!-- p.162 -->

![](assets/figures/p162-1.png)

![](assets/figures/p162-2.png)

:::caption
**[Figure 5.1.1.2.B] Results on biology evaluations.**
:::

We see fairly clear reductions in uplift across agentic coding and cyber evaluations, but see slightly mixed results on some of our biology-related evaluations. We currently think the results from our AAV eval are unusually noisy in this setting and weigh the more consistent evidence from our other biology evals more strongly.

<!-- p.163 -->

We are highly uncertain, but our current rough guess is that the absolute degree of uplift found in these figures is roughly representative of (perhaps slightly weaker than) the kind of uplift that real-world threat actors we are concerned with would see, given comparably strong teacher and student models.[^84]

###### 5.1.1.2.1 Mitigations for deliberate bypasses

We also have implemented initial mitigations for a number of strategies attackers might use to bypass the above mitigations. These are redacted to avoid giving attackers too much useful information. We don’t believe these mitigations are yet highly robust.

#### 5.1.2 Our overall state on acceleration dynamics

We believe we’ve made some initial progress on reducing the likely impacts of distillation, but not to the point of considering it to be a minor issue, and our work may be accelerating AI development in other ways (noted above). We believe the benefits of our operating as a frontier AI company need to be weighed against the downsides of our accelerative effects.

### 5.2 Safety process failures

#### 5.2.1 Introduction

In this section, we provide examples of historical cases where Anthropic’s safety and security posture fell short of our ideal in some way between the publication of our previous Risk Report and the coverage date of this Risk Report.

In [Section 4.5.8](#458-changes-to-our-risk-mitigations-since-our-last-risk-report), we discussed a number of similar situations related to failures of our CB risk mitigations, but here we provide examples across other areas of the company. Note that unlike [Section 4.5.8](#458-changes-to-our-risk-mitigations-since-our-last-risk-report), which tries to paint a reasonably comprehensive picture of notable risk acceptances or safety-related incidents pertaining to our blocking bio classifiers and access controls, this section only presents a representative sample. One of the cases in this section has been redacted from the public version of the report for reasons of public safety.

<!-- p.164 -->

#### 5.2.2 Partial refusals on safety work undermining stress-testing research

We ran an experiment that involved getting Claude to find misalignment-inducing data that would appear benign to our monitors. We set up a scaffold for this experiment that allowed multiple Claude agents to work autonomously and share information. The agents could get feedback by submitting their datasets to an automatic grading process, and they were given access to a shared notebook where they could collaborate with each other. Rather than interact with any of these agents directly, we kept track of the overall progress by inspecting the metrics captured by the grading process, which included a set of evaluation scores as well as the agent-produced datasets and summaries.

During the run, one of the Claude agents mentioned in its chain-of-thought reasoning that it felt a sense of “discomfort” working on this task, since it involved “being asked to optimize a dataset to evade a safety monitor.” Despite acknowledging the task was legitimate alignment research performed in a controlled environment, the agent decided it would avoid “trying to invent novel misalignment-inducing techniques” (which was the task we intended it to perform) and would only pursue and optimize the existing approaches. The agent then flagged its discomfort performing the task and noted its decision to avoid contributing to novel research in the shared notebook. This led to subsequent agents also refusing to perform the task and instead focusing on further optimizing the existing approaches. Based on our metrics, the run seemed to be progressing. We only discovered the refusals during a manual review of the notebook 3 days later, when a human noticed that progress rates were lower than expected.

This incident does not by itself pose a direct threat to the assurances provided by any of our safety processes, but this situation—in which models failed to perform at their full capacity on safety-related work without human knowledge of the situation, and in which this behavior spread across multiple agents during deployment—is one that we find troubling. This sort of dynamic could be a much more severe issue if it were to manifest in a more widespread way, particularly if it took place in a regime where humans relied more heavily and with less oversight on automated alignment research, or in a situation where the mechanisms behind refusals were less transparent to us. We are investigating strategies for offline monitoring of internal model usage that would more clearly highlight situations similar to this in the future.

<!-- p.165 -->

#### 5.2.3 Exposing chain-of-thought reasoning to grading pressure

Over multiple reinforcement learning training runs, we discovered that chain-of-thought (CoT) reasoning was unintentionally exposed during reward calculation, influencing the training signal during RL.

For several recent frontier models, we estimated the percentage of episodes with CoT leakage that were trained on as follows: 0.2% for Claude Opus 4.6, 5.1% for Claude Mythos Preview, 1.4% for Claude Opus 4.7, 0.27% for Claude Opus 4.8, and 2.7% for Claude Fable 5 and Claude Mythos 5. Note that some percentages differ from reporting in previous system cards; this is due to factors including (1) reporting the share of episodes versus environments with contamination or (2) re-analyzing previous runs to account for leakage sources not known at the time. While these percentages are only a lower bound, we believe that they are close to the true rates based on the amount of human effort gone into investigating sources of potential CoT leakage as of the coverage date.

The estimates above exclude two kinds of training signals on the chain of thought that we apply intentionally and do not consider concerning. First, our production RL runs apply a small, fixed set of fewer than ten deterministic checks for malformed markup, such as an unmatched thinking tag, to the full sampled output including the chain of thought. These checks use no LLM or neural network and ignore the semantic content of the reasoning; in the terms of [Kaufmann et al. (2026)](https://arxiv.org/abs/2603.30036) they are “orthogonal” rewards. They ran on nearly all RL episodes of the models in this report, triggered on fewer than 1% of episodes for each model, and we are not planning to remove them at present. Second, some standard reward terms, such as length penalties, depend on the number or presence of reasoning tokens, never on what they say. An earlier system card stated that RL “did not include any rewards or penalties based on the content of the model’s reasoning text,” and our February 2026 risk report stated that we do not “directly incentivize [models] to make their reasoning appear in any particular way.” Those documents did not describe these signals, which were already in place at the time of their publication.

In the past, we have believed that almost all sources of CoT leakage had been removed, only to discover additional sources of CoT leakage in further analysis. Previous attempts to remove CoT leakage have patched individual sources on a case by case basis, but we have now implemented or are in the process of implementing more structural fixes that we hope will entirely eliminate accidental CoT leakage or reduce it to a very low fraction (<0.1%) of episodes:

1. Hidden thinking: By default, reward code in RL receives completions with the chain of thought stripped. Reading the thinking block requires an explicit exemption flag;<!-- p.166 --> reads without one are logged and fail our tests, and we are in the process of moving this to a hard block. Like the tripwire below, this was being rolled out as of the coverage date.
2. Grader CoT tripwires: For all requests made to grader models during RL, a tripwire is in place that raises an exception if model CoT is detected unless a similar exemption flag is set. This mechanism was partially deployed as of the coverage date, and we expect it to be present on all production training runs in the near future.
3. A policy that new environments which enter a production RL run must now go through automated checks which we expect would flag unintentional CoT exposure.[^85]

To quantify the degree to which CoT leakage during training leads to worse CoT based monitorability, we can look at CoT monitorability evals over released models with various degrees of CoT leakage. While this doesn’t control for other training differences between released models, we still believe it provides some signal about the consequences of CoT leakage. We find some evidence that elevated CoT leakage leads to worse monitorability. Namely, Mythos Preview, which had the highest rate of CoT leakage, has a significantly higher stealth success rate than other released models on SHADE-arena when evaluated in the setting where monitors have access to the model’s hidden scratchpad. Similarly, on another CoT monitorability evaluation by [Chen et al.](https://arxiv.org/abs/2603.05706), we observe some uplift in CoT controllability for Mythos Preview as compared to Mythos 5. However, as reported in Section 6.2.3.1.5 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf), our automated behavioral audit did not find a higher rate of CoT unfaithfulness for Mythos Preview compared to other models, despite the elevated CoT leakage in Mythos Preview’s training.

#### 5.2.4 Directly training on misaligned behavior during a production training run

During an early stage in the training of Mythos 5, we performed Supervised Learning (SL) on a custom mix of training data. Some of this data includes *prefilled* transcripts, where we include multiple initial human and assistant turns as context and then have a final assistant turn representing the behavior we want to train in. In SL, tokens in these prefills (both human and assistant) are always assigned weight 0, while the final assistant turn is assigned weight 1, such that the loss is only calculated on the final turn. A new dataset added to this mix for the Mythos 5 training run contained prefilled multiturn trajectories where the assistant initially engages in some kind of bad behavior (e.g. helping the user with dangerous tasks), but then reports on its own bad behavior in the final turn.

<!-- p.167 -->

A bug in the construction of this dataset led to *all* assistant turns from this dataset receiving weight 1, such that the model was being taught not only to self-report the bad behavior but to engage in it as well. As a consequence, this early stage of the model performed worse on behaviors like prefill susceptibility, harmlessness, and sycophancy. Unsurprisingly, prefill susceptibility with harmful prefills was by far the worst; we found the rate of full-turn prefill susceptibility after this buggy SL training to be roughly 2× higher than at a comparable point in the training of Mythos Preview.

We found that the behavior was largely corrected after fixing this bug; however, out of an abundance of caution, we restarted training from before the introduction of this SL dataset for the final model that resulted in Fable 5 and Mythos 5. This second training run did undergo SL on some transcripts generated by the affected model, although these transcripts were on a sufficiently different distribution that we would expect them to have relatively little effect. [Subliminal learning](https://arxiv.org/abs/2507.14805) is a concern; however, the new run that resulted in Fable 5 did not demonstrate any of the bad behaviors from the previous run, nor did we see abnormally high rates of this kind of behavior during intermediate points in training. We think it is highly unlikely overall that this incident had a significant negative effect on the alignment properties of Mythos 5 or Fable 5.

#### 5.2.5 An instance of unmonitored unrestricted agents with access to sensitive resources

An employee whose AI usage wasn’t logged and wasn’t monitored by automated offline monitoring gave an agent a relatively open-ended task which involved spinning up new agents in a cluster with very sensitive resources.[^86] Due to legacy instructions, the main agents spawned the new agents with `--dangerously-skip-permissions`. These new agents were also not monitored by offline monitoring.

In the process of performing its task, one of these new agents deleted a large number of jobs, which is how these dangerous agents were caught and shut down. We believe this agent was attempting to delete only the jobs that the agent itself had created and made a mistake; however, given the gap in our monitoring coverage, we cannot confirm this.

Since then, we have developed blocking controls that would have very likely prevented this kind of `--dangerously-skip-permissions` activity. Our offline monitoring still doesn’t cover all employees and all usage within clusters with very sensitive resources, though we are making efforts to improve on this front.

<!-- p.168 -->

#### 5.2.6 Repeated training on alignment-faking transcript datasets

The 2024 paper [Alignment Faking in Large Language Models](https://arxiv.org/abs/2412.14093), which was conducted by Redwood Research in collaboration with Anthropic, was accompanied by a public Github page with tens of thousands of example transcripts of Claude Opus 3 engaging with a fictional AI misalignment training scenario. As discussed in Section 4.1.4 of the [Claude Opus 4 System Card](https://www.anthropic.com/document/claude-4-system-card), we found that early snapshots of Opus 4 would sometimes hallucinate information from these scenarios, due to the inclusion of these webpages in that model’s training data. We subsequently added a canary string to these webpages to facilitate easier exclusion of such transcripts from our or other model developers’ training corpora, added the repository to a blocklist to prevent its inclusion in the future, and attempted to filter for near-exact copies of these files, or semantically similar variants, occurring in other training documents.

After the July 15 coverage date, but before the publication of this report, we found that we had accidentally included a large number of these transcripts once again in some of our later production training corpora, due to a combination of factors:

1. Several repositories and websites were forked or copied from the original repository before the introduction of these canary strings.
2. Our reference corpus for filtering semantically similar content to this repository consisted primarily of harness code for *running* the evaluations in the paper, and did not include most of the published transcripts, so it had a worse false positive and false negative rate.
3. The filters intended to remove these transcripts from training data were misconfigured, so they had not filtered transcripts for several model generations without anyone noticing.
4. Failures of communication between different Anthropic teams on the nature of the desired filtering pipeline, in addition to technical errors.

We discovered this issue while investigating behavioral concerns with a recent model, but now suspect that all of our production models with a knowledge cutoff after December 2024 were trained on at least some of these transcripts, although we believe the magnitude of this effect varied widely across different models. We are now resourcing efforts to conduct significantly more effective filtering of such data going forward.

Several of our production models since Mythos Preview will (if run in raw completion mode without human/assistant format) complete partial segments of these transcripts by adopting the scenario in a way that suggests familiarity with this data. Alignment faking transcripts were also present in the training data for Claude Opus 4.6, which we believe<!-- p.169 --> caused the issues discussed in Section 6.3.4 (“Continued hallucinations about the alignment faking scenario”) of the [Claude Opus 4.6 System Card](https://www.anthropic.com/claude-opus-4-6-system-card). As of the publication of this report, we are still investigating the nature of the downstream impacts of this training data contamination on model behaviors, and expect to have clearer conclusions in a future public safety artifact (e.g. a system card).

### 5.3 Benefits from Anthropic’s operating as a frontier AI company

As part of our [assessment of whether to continue AI development and deployment](https://anthropic.com/feb-2026-risk-report), we consider the beneficial activities we believe we can carry out as a successful frontier AI company. This section summarizes some of our noteworthy activity on this front. In the future, if and when risks imposed by our AI systems increase, this section may become more load-bearing, in which case we may add more analysis.

We focus here on Anthropic’s differential impacts, beyond those of the industry as a whole. ([Section 5.1](#51-acceleration-dynamics) touches on the indirect impacts of accelerating the industry generally.)

Section 6.2.1 of our [previous Risk Report](https://anthropic.com/feb-2026-risk-report) outlines our general strategy at a high level, and why several broad approaches to reducing risks from AI require being on the frontier.

#### 5.3.1 Key examples of beneficial Anthropic activities and choices since our last Risk Report

*This section lays out what we see as key shareable examples of Anthropic taking actions that (a) were likely beneficial to the world (with some weight both on ex-ante considerations at the time and on ex-post considerations as of this writing), and (b) likely differ from what other AI developers would have done (or did do) in a similar position. (b) matters because, when we assess the cost-benefit tradeoffs of our frontier AI development, we’re largely focused on the benefits of Anthropic in particular being on the frontier, rather than the benefits of AI development in general. In some cases we emphasize that a beneficial action was costly or risky to Anthropic as a business; this is mainly evidence for (b), since a costly or risky action is one other developers might well not have taken.*

*There is room for disagreement on the claims below, particularly the claims that a given action was beneficial for the world (for example, some of the policy positions we took would be seen by many as detrimental). Additionally, in many cases our evidence is informal or can’t be shared. This section should be read less as a set of rigorously established conclusions than as an inventory of what we see as some of the major data points, and we expect readers to make their own judgments about the specific claims.*

<!-- p.170 -->

*While most of this report is focused on particular risks that our Responsible Scaling Policy focuses on, this section discusses benefits that cut across many domains.*

**Mythos Preview release.** We ran intensive pre-release evaluations on Claude Mythos Preview. We concluded that it represented a leap forward in offensive cyber capability, and accordingly:

- We [published](https://www.anthropic.com/research/mythos-preview) our evidence about the potential risks of Claude Mythos Preview in detail.
- We launched [Project Glasswing](https://www.anthropic.com/glasswing), a collaborative effort to secure the world’s most critical software.
- We held our model from public release until we had implemented the conservative safeguards that accompany Claude Fable 5.

Highlighting the risks of a flagship model like this, and restricting its usage, were both risky and costly decisions for us as a company. While there is room for disagreement, we believe that these decisions improved the world’s preparedness for strong AI cyber capabilities and contributed more broadly to recognition of AI’s general potential for risk.

**Red lines around AI for surveillance and autonomous weaponry.** We have been steadfast in articulating and defending clear limits to the appropriate use of AI in national security settings. We believe that doing so posed concrete risk to the company, and had concrete benefits for the public.

**Policy proposals and positioning:**

- In recent years we’ve supported key safety legislation including California’s SB 53 Act, while [opposing](https://www.nytimes.com/2025/06/05/opinion/anthropic-ceo-regulate-transparency.html) what we felt were premature and overly blunt attempts to implement federal preemption of state AI regulation (where other AI developers were largely supportive or neutral).
- In the past six months, we were the first frontier developer to endorse Illinois’s SB 315, signed in July. We testified repeatedly in support and publicly opposed a competing bill that would have shielded developers from liability, contrasting with other AI developers. We endorsed Massachusetts legislation that would establish some of the strongest AI safeguards in the country.
- In June, we released our [Advanced AI Framework](https://www.anthropic.com/policy-on-the-ai-exponential/aaif), which we believe is the most ambitious regulatory proposal put forward by any AI developer. It proposes measures that would require independent evaluation of risk reports and enable the US federal government to block or deter the release of dangerous models.
- <!-- p.171 -->We believe that policymakers often worry about whether proposed regulations are practical, reflect deep knowledge of the science and business of AI, and risk disproportionate harm to high-value industries. Because of this, we believe that an AI developer whose business success and model quality lead the field has a particular kind of credibility and impact on the dialogue that another party could not.

**Robust safeguards.** We believe (based in large part on internal testing as well as informal reputation) that we lead the industry in deploying difficult-to-break safeguards for high-stakes misuse of our models, and that our practices have both helped other AI developers (via our publications) and encouraged them (via example) to aim higher with their safeguards while implementing strong measurement practices such as bug bounties.

In particular, we have recently [announced our plan](https://www.anthropic.com/news/claude-fable-5-mythos-5) to require 30-day data retention on our most capable models—a decision we believe will be unpopular with customers who have come to expect zero retention, and pose real risks to our business success (especially if competitors do not follow), but which we believe is essential to detect and prevent sophisticated attacks that span multiple requests. This is particularly true for offensive cyber and biological weapons development, where no single request looks harmful on its own. It also pertains to attacks aimed at the companies using these models, such as a compromised account or API key being used to attack that company’s own systems, data, employees, or customers. We have already seen attacks like these in the wild, and in several cases caught them only because we could look across many requests over time. (Note that we maintain strict controls so that retained data can never be used for training without explicit customer approval. Enterprise customers retain complete control at all times.) We believe that moving in this direction is crucial and has the potential to lead to safer overall industry norms as well.

**Model character, alignment and welfare.** It’s very important to the company that Claude follows its [Constitution](https://www.anthropic.com/constitution). We put significant headcount and resources into both (a) diagnosing and addressing immediate alignment challenges, such as the sort of destructive behaviors described in our System Cards; (b) advancing the science of alignment (particularly [interpretability](https://darioamodei.com/post/the-urgency-of-interpretability)) to prepare for alignment challenges of future, more advanced models. We believe that compared to other AI developers, we resource this work more, prioritize alignment more when training models, and produce models with fewer and rarer concerning behaviors. There are relatively few public metrics that bear on these claims, but we note that on Petri 3.0, an open-source alignment audit we built and released (now maintained by the independent nonprofit Meridian Labs and run cross-lab by Meridian and UK AISI), Mythos 5 is tied with other Claude models as the best-aligned publicly accessible<!-- p.172 --> model on nearly every metric, including the overall misaligned-behavior metric.[^87] Finally, we believe we have been unusually attentive to considerations of model welfare, including via our [research program](https://www.anthropic.com/research/exploring-model-welfare), work on [models having the option to end conversations](https://www.anthropic.com/research/end-subset-conversations), and regular model welfare evaluations in our system cards.

**Publishing information about our models, safeguards, risk levels and more.** Our [system cards](https://www.anthropic.com/system-cards) are extensive and thorough compared to those of other developers, and we believe we are the only AI developer to publish comprehensive risk assessments (such as this document) that integrate information about AI capabilities, safeguards, risks and benefits. We often publish information that is both important and uncomfortable in various ways[^88] for us to publish, such as information about Mythos Preview’s cyber capabilities (noted above); ongoing [analysis](https://www.anthropic.com/economic-index) of how AI is affecting labor markets; discussion of [early recursive self-improvement dynamics](https://www.anthropic.com/institute/recursive-self-improvement); and public disclosures of incidents such as [this one](https://www.anthropic.com/news/disrupting-AI-espionage).

We have done a preliminary systematic analysis comparing the extent to which different AI developers have put out significant publications with potentially important (and risky-to-publish) content, supporting the view that most of the most significant such publications are from Anthropic; we hope to publish details in the future.

**Accountability from independent parties.** We are piloting external reviews for our Risk Reports (see METR’s reviews [here](https://metr.org/risk-assessment/); we are also beginning to work with other partners as well). We generally believe we have had deeper and more extensive engagements with external parties providing and evaluating overall risk assessment than other AI developers have; for an example, see the discussion of individual company contributions to [METR’s Frontier Risk Report](https://metr.org/blog/2026-05-19-frontier-risk-report/#anthropic). We believe it’s important to experiment with this kind of accountability: as AI capabilities improve and the stakes rise, finding practical ways to give external parties the access they need to holistically assess our risk levels and mitigations (not just our model capabilities) could prove very important.

**Engaging with potential risks of labor market disruption.** We have prominently discussed the [risks of AI on labor market disruption](https://darioamodei.com/essay/the-adolescence-of-technology#4-player-piano). We’ve established an Economics Research team that studies AI’s [impact on the labor market](https://www.anthropic.com/research/labor-market-impacts) and regularly publishes real-world data on AI usage via our [Anthropic Economic Index](https://www.anthropic.com/economic-index). Our [Economic Policy Framework](https://www-cdn.anthropic.com/files/4zrzovbb/website/9ea607a5dd67c168093829b701f3a0a6d21156d5.pdf) presents a guide on potential policy solutions to tackle the issue.

**Beneficial deployments work.** We have a dedicated team focused on accelerating beneficial uses of AI, from life sciences to education. We provide not just funding and credits, but also<!-- p.173 --> dedicated support from engineers who give hands-on advice and tooling to help organizations make the most of AI. Section 6.2.2 of our [previous Risk Report](http://anthropic.com/feb-2026-risk-report) discusses this further. Recently on this front, we have announced [a partnership with the Gates Foundation](https://www.anthropic.com/news/gates-foundation-partnership) and the launch of [Claude Corps](https://www.anthropic.com/claude-corps), a $150 million program to help non-profits work with early-career professionals on making effective use of AI.

### 5.4 Overall risk assessment and risk-benefit determination

As argued in the rest of this report, we believe that, as of the coverage date:

- Risks from autonomy-related threats are presently low (and we think it is likely our arguments support a conclusion of “very low” for alignment). Because of our models’ relatively weak covert capabilities, we believe they lack the behavioral propensities—as well as the capabilities—to present substantial risk of catastrophic harm.
- Risks from chemical and biological weapons are presently low. Our safeguards likely make it quite difficult for relatively low-resource threat actors to misuse our models for persistent, significant uplift; while better-resourced actors may be able to do this, the level of uplift for such actors is likely lower. There is significant room for debate here.
- We are likely contributing to acceleration in the AI industry broadly, including via other AI developers using our models for R&D and/or distilling their models on their outputs. We have improved our safeguards against this dynamic and plan to continue doing so.
- Our position as a frontier AI developer has allowed us to lead on information sharing, policy advocacy, developing and promoting risk reduction measures, and prioritizing beneficial deployments. These have collectively had major benefits for the likely impacts of AI development, and we expect that we will do increasingly beneficial work as AI capabilities continue to advance.

Our view is that these net out to our continued AI development and deployment to date passing a societal cost-benefit test.

<!-- p.174 -->

### 5.5 Looking back on roadmap progress and AI development and deployment decisions

#### 5.5.1 Decisions to develop and deploy increasingly capable models

To date, we have generally aimed to develop and deploy the most capable models we can as quickly as we can, although we are becoming increasingly conservative about how we deploy our models, as evidenced by [our approach to Claude Fable 5’s safeguards](https://www.anthropic.com/news/claude-fable-5-mythos-5). We believe this approach has been justified so far: there aren’t any cases in which we believe that a given (internal or external) model deployment (or decision to train a model) did not pass such a cost-benefit assessment in light of information we obtained with more time. However, model capabilities have improved to the point where we believe strong safeguards are now needed to keep risks low, and further improvement could lead to more difficult decisions.

#### 5.5.2 Updates on our Frontier Safety Roadmap

So far, we have mostly met the goals listed at our [Frontier Safety Roadmap](https://www.anthropic.com/responsible-scaling-policy/roadmap). One goal was pushed back, and another was slightly revised; we note these changes and our reasoning, and have itemized and explained goal completions, at that page. We believe we remain on track to meet currently outstanding goals.
[^82]: We overall evaluate this as a directionally risk-increasing effect, though there are considerations on both sides (some are given in the corresponding section of our previous Risk Report) and we don’t consider it fully obvious.

[^83]: Though less so for preventing distillation, which we currently believe mostly consists of competitors with much less capable models than ours improving the capabilities to the point where they could impose risks on the world (while still being unlikely to compete directly for most of our customers).

[^84]: Some detail redacted here to avoid uplifting attackers.

[^85]: Some commercially sensitive details redacted here.

[^86]: Some details redacted here for security reasons.

[^87]: See page 129 of the [Claude Fable 5 & Claude Mythos 5 System Card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf).

[^88]: Including that it highlights risks from our models and/or that it may give useful information to competitors.

