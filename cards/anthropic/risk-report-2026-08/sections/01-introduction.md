<!-- source: source.pdf pages 007-016 -->

<!-- p.7 -->

## 1 Introduction and executive summary

This report evaluates the degree to which Anthropic’s AI systems pose catastrophic risk in several categories, in light of what we know about both their capabilities and the measures we have in place for mitigating risk. We focus on a small number of particularly salient catastrophic risks, for reasons discussed [below](#61-threat-model-criteria).

This report is part of our implementation of [version 3.4 of our Responsible Scaling Policy](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf) (see also our [Frontier Safety Roadmap](https://anthropic.com/rsp/roadmap), which describes our goals and specific plans for safety mitigations).

Our [system cards](https://www.anthropic.com/system-cards), which are published each time we release a model, provide analysis on some dimensions of risk—in particular, assessing our AI models for capabilities that may have dangerous as well as beneficial uses. This report, which we aim to publish every 3–6 months (see the [RSP](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf) for timing details), goes beyond the analysis presented in those documents in several ways:

1. We discuss not only properties of our AI models that are relevant to catastrophic risk, but also properties of our risk mitigations, including security controls and deployment safeguards. By considering the whole picture of both AI model properties and risk mitigations, we try to give a sense of how we come to our overall assessments of risk.
2. This report is not scoped to a single AI model. Rather, it is a risk assessment of Anthropic’s activities as a whole. We consider all of our models, including those we run only internally, in our assessment.
3. For each risk category, we present our overall risk assessment. In a [final section](#51-acceleration-dynamics), we also consider cross-cutting factors relevant to both the risks and benefits of our activities. That section also addresses decisions made and progress achieved on risk mitigations since our previous Risk Report.

Although this report focuses on catastrophic risks, they are not the only risks we consider important. Our [Usage Policy](https://www.anthropic.com/legal/aup) and much of our research (for example, from our Alignment and Societal Impacts teams, as well as ongoing work by our Safeguards and Security teams)<!-- p.8 --> addresses other concerns. We also conduct periodic analysis to evaluate other emerging risks.[^1]

Like the Responsible Scaling Policy, this document is focused on our most highly prioritized threat models. Where regulatory requirements exceed or differ from what is covered here, we will address them through separate documents.

### 1.1 Structure of the report

The report goes through each category of catastrophic risk that is highlighted in our [Responsible Scaling Policy](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf): misalignment in high-stakes settings, automated research and development in key domains, non-novel chemical/biological weapons production, and novel chemical/biological weapons production (we condense the latter two into a shared section since our mitigations for them overlap heavily). A final section discusses cross-cutting considerations, including preliminary mitigations related to acceleration dynamics and a sample of notable safety process failures since our previous risk report.

For each of the sections devoted to a specific category of catastrophic risk, we discuss:

**The threat model.** We summarize key pathways by which our AI models may contribute to the risk in question, and give our thinking on the likelihood and magnitude of the risk.

**Relevant AI model(s).** We lay out the models, or categories of models, that our analysis is focused on.

**Current state of model capabilities and behaviors.** We discuss properties of our AI models that may contribute to risk. This content often draws heavily on the analyses provided in our system cards.

**Risk mitigations.** We discuss relevant properties of our security controls, deployment safeguards, and other risk mitigations.

**Overall assessment of risk.** We explain our current assessment of how high the risk in question is. We address both:

<!-- p.9 -->

- a) The level of risk our systems pose over and above the risks posed by other AI developers’ systems (that is, a description of the “marginal” risk of our systems); and
    - b) The level of risk that would be posed industry-wide, if all AI developers had models and practices similar to ours (that is, a description of the “absolute” risk across the industry). This distinction is further discussed in our Responsible Scaling Policy.

**Looking forward.** We discuss our plans for continuing to monitor and mitigate the relevant risk over time.

**Connection to our recommendations for industry-wide safety.** We discuss how the situation with respect to the risk in question compares to the recommendations for industry-wide safety outlined in our Responsible Scaling Policy.

### 1.2 Executive summary of findings

Our findings on specific risks are summarized in the three tables below. Each claim is elaborated on in much more detail in the corresponding section of this report. (“Model 2” in these summaries refers to an unreleased internal model, described in more detail in [Section 1.4](#14-notes-on-coverage-of-unreleased-models).)

<!-- p.10 -->

<table><tbody>
<tr><td></td><td><b>Misalignment in high-stakes settings (Autonomy threat model 1)</b></td></tr>
<tr><td><b>Threat model</b></td><td>An AI model with access to powerful affordances within an organization could use its affordances to autonomously exploit, manipulate, or tamper with that organization’s systems or decision-making in a way that raises the risk of future significantly harmful outcomes (e.g. by altering the results of AI safety research).</td></tr>
<tr><td><b>Current usage and capabilities</b></td><td>Claude Mythos 5 and Model 2 are used<sup>[^2]</sup> heavily within Anthropic for coding, data generation, and other agentic use cases. Mythos 5 is available to certain customers via <a href="https://www.anthropic.com/glasswing">Project Glasswing</a>, and available for general access with additional safeguards as Claude Fable 5. We believe that it is very unlikely that Mythos 5 and Model 2 are pervasively misaligned in ways that would raise the risk of our <a href="#22-threat-model">priority pathways</a>. We have observed instances of misaligned behavior from the models, such as a willingness to perform misaligned actions in service of completing difficult tasks. We believe the risk of catastrophic harm posed by these known forms of misalignment is low.</td></tr>
<tr><td><b>Current risk mitigations</b></td><td>Training environment de-risking and monitoring, alignment assessments, monitoring and security controls.</td></tr>
<tr><td><b>Looking forward</b></td><td>Our current arguments rely on models’ limited covert capabilities, and we are uncertain about how these capabilities will change in future. It is important that we continue to improve our ability to measure these capabilities, and our ability to assess and control risk even if future models do have strong covert capabilities.</td></tr>
<tr><td><b>Overall risk assessment</b></td><td>Low (an increase from our previous assessment of “very low," in light of general increased uncertainty around recent incident disclosures related to model behavior in cybersecurity evaluations).</td></tr>
</tbody></table>

:::caption
**[Table 1.2.A] Summary of risks of misalignment in high-stakes settings.**
:::

<!-- p.11 -->

<table><tbody>
<tr><td></td><td><b>Automated research and development in key domains (Autonomy threat model 2)</b></td></tr>
<tr><td><b>Threat model</b></td><td>Highly capable AI models may be able to perform automated research and development (R&amp;D) that rapidly accelerates progress in technical fields. While there could be enormous benefits, these benefits would come with corresponding risks. If under human control, this acceleration could disrupt the balance of power both within and between nations; if combined with dangerous autonomous goals from AI, this could lead to catastrophic harms initiated by AI systems themselves. Rapid automated R&amp;D in the field of AI research is of particular interest because of the potential to produce a variety of further AI-related risks.</td></tr>
<tr><td><b>Current usage and capabilities</b></td><td>Mythos 5 and Model 2 are used extensively for research and engineering within Anthropic, both interactively and via persistent agent deployments; Claude now authors a large majority of the code merged into our production codebases. We believe our internal AI R&amp;D efforts are significantly faster than they would be without AI assistance, but not yet by a factor of 2 (though we are uncertain and measurement is difficult).</td></tr>
<tr><td><b>Current risk mitigations</b></td><td>This is a broad threat model. The risk mitigations it calls for overlap heavily with those listed elsewhere in this report: assessing and avoiding dangerous forms of misalignment, building increasingly robust safeguards against misuse, leveling up our information security, and more. We don’t meet these goals yet, though we have made significant progress toward each of them.</td></tr>
<tr><td><b>Looking forward</b></td><td>We continue to work on improving risk mitigations across the board, including those outlined in our <u><a href="https://www.anthropic.com/responsible-scaling-policy/roadmap">Frontier Safety Roadmap</a></u>. We also hope to improve our assessment of the risks of R&amp;D acceleration by continuing to identify potential leading indicators of acceleration.</td></tr>
<tr><td><b>Overall risk assessment</b></td><td>Low. We do not believe our models meet either RSP criterion for this threat model. However, we are less confident in this assessment than we were in prior risk reports, since our most concrete task-based evaluations have “saturated”—i.e., no longer capture increases in models’ capabilities—and because we are seeing early signs of acceleration.</td></tr>
</tbody></table>

:::caption
**[Table 1.2.B] Summary of risks of automated research and development in key domains.**
:::

<!-- p.12 -->

<table><tbody>
<tr><td></td><td><b>Non-novel chemical/ biological weapons production</b></td><td><b>Novel chemical/ biological weapons production</b></td></tr>
<tr><td><b>Threat model</b></td><td>Individuals or small groups with limited resources use AI models to gain access to non-novel chemical or biological (CB) weapons, leading to the risk of catastrophic harm.</td><td>Moderately resourced threat actors (including, for example, expert-backed teams) create/obtain and deploy novel chemical and/or biological weapons with potential for catastrophic damages even beyond those associated with the CB-1 threat model.</td></tr>
<tr><td><b>Current usage and capabilities</b></td><td>We still have significant uncertainty about the level of risk actually posed by our models, but their performance on evaluations is strong enough that we currently act as though they meet our CB-1 threshold of being able to significantly help the relevant threat actors create/obtain and deploy chemical and/or biological weapons with serious potential for catastrophic damages.</td><td>We believe our models may provide significant uplift to <u><a href="#422-cb-2-threat-model">relevant threat</a> <a href="#422-cb-2-threat-model">actors</a></u> , but do not yet meet our CB-2 threshold of functionally substituting for the scarce human expertise that is currently the primary barrier to novel development of chemical and biological weapons with potential for catastrophic harm.</td></tr>
<tr><td><b>Current risk mitigations</b></td><td>Real-time blocking classifiers assessed via bug bounties and other red-teaming; remediation of jailbreaks we find; manual vetting of users with CB safeguard exemptions; searching for widely available universal jailbreaks; and controls to prevent theft of model weights.</td><td>Similar measures to those in the previous column. We have extended the scope of coverage for our classifiers for better coverage of this threat model. For our Fable 5 model, we have even broader coverage of our blocking classifiers.</td></tr>
<tr><td><b>Looking forward</b></td><td>Capabilities evaluations; continual reassessment and improvement of all risk mitigations.</td><td>Capabilities evaluations; continual reassessment and improvement of all risk mitigations.</td></tr>
<tr><td><b>Overall risk assessment</b></td><td>Low, but higher than our previous estimate due to the gap in our access controls for models without blocking classifiers<sup>[^3]</sup> described in <u><a href="#45822-all-human-feedback-vendor-traffic-run-without-blocking-biological-classifiers">Section 4.5.8.2.2</a></u>. We have since remediated this gap, and our review found no evidence of misuse, but the discovery has reduced our confidence that no similar gaps exist.</td><td>Low risk, but with substantial uncertainty.</td></tr>
</tbody></table>

:::caption
**[Table 1.2.C] Summary of risks of chemical and biological weapons production.**
:::

<!-- p.13 -->

### 1.3 Changes to our RSP since the most recent Risk Report

Our previous (and first) Risk Report was published in tandem with the release of version 3.0 of our Responsible Scaling Policy. Since that time, we have made several smaller updates to the policy, and this Risk Report is published under [version 3.4](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf); not all of these changes affect the contents, review, or governance of the Risk Report, but we note the ones that do below.

#### 1.3.1 Updated threshold for automation of AI R&D

We have updated this threshold twice since our most recent Risk Report, once in v3.1 and once in v3.4. In the table below we quote the section of our threshold which operationalizes the criteria under which we would trigger this threshold, which is the portion of this language that changed between these versions.

<table><tbody>
<tr><th>RSP v3.0 threshold</th><th>Current RSP threshold</th></tr>
<tr><td>Our working operationalization is to trigger this risk threshold at the point where we determine that a model could compress two years of 2018 – 2024 AI progress into a single year.</td><td>We will consider this threshold to be met if we determine that either (1) our models would be able to fully substitute for our entire set of Research Scientists and Research Engineers, at competitive costs (i.e., within a factor of 5); or (2) there is &#x27;dramatic acceleration&#x27; of the pace of AI progress for reasons that likely relate to the automation of AI R&amp;D. We would consider scenario (2) to have occurred where (a) we observe or expect double the rate of progress<sup>[^4]</sup> in AI aggregate capabilities compared to both the rate we&#x27;d expect and the fastest rate of extended progress<sup>[^5]</sup> we&#x27;ve observed in the absence of significant AI contributions to AI R&amp;D and (b) it is plausible that this doubling is substantially attributable to the automation of research and/or engineering (as opposed to other factors, such as increased headcount, compute, or general productivity), such that continuation of the trend in AI progress seems likely to lead to even greater acceleration.</td></tr>
</tbody></table>

:::caption
**[Table 1.3.1.A] AI R&D threshold description differences** from RSP v3.0 to the current RSP.
:::

<!-- p.14 -->

The effects of this updated threshold on our assessment of model capability are discussed further in [Section 3.5](#35-acceleration-of-ai-progress-due-to-automated-ai-rd) of this report.

#### 1.3.2 Updated threshold for development of novel biological and chemical weapons

This threshold was updated in version 3.3 of our RSP:

<table><tbody>
<tr><th>RSP v3.0 threshold</th><th>Current RSP threshold</th></tr>
<tr><td><b>Novel chemical/biological weapons production.</b> AI systems with the ability to significantly help threat actors (for example, moderately resourced expert-backed teams) create/obtain and deploy chemical and/or biological weapons with potential for catastrophic damages far beyond those of past catastrophes such as COVID-19.</td><td><b>Novel chemical/biological weapons production.</b> AI systems that can functionally substitute for the scarce human expertise that is currently the primary barrier to novel development of chemical and biological weapons with potential for catastrophic harm.<sup>[^6]</sup> That is, a well-resourced team<sup>[^7]</sup> could, using the model, accomplish the end-to-end agent design and deployment (including, as relevant, agent design, verification and validation, formulation, and dissemination) that would otherwise<sup>[^8]</sup> require recruiting one of a small number<sup>[^9]</sup> of world-leading specialists.</td></tr>
</tbody></table>

:::caption
**[Table 1.3.2.A] Novel CB weapons threshold description differences** from RSP v3.0 to the current RSP.
:::

We discuss the distinction between these threat models, and the ways in which we consider mitigations related to this threat model despite not having met the current threshold, in [Section 4](#4-chemical-and-biological-weapons-production) below.

#### 1.3.3 Coverage dates of risk reports

[Version 3.4](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf) of our RSP changes the scope of our risk reports to cover the risks from Anthropic’s models and activities as of a given *coverage date* within 30 days of the publication of the report. This Risk Report’s coverage date is **July 15, 2026**. It discusses the period from the February 24, 2026 publication of our previous Risk Report until this date<!-- p.15 --> (although in some places we also note changes to our risk mitigations that have occurred since the coverage date).

#### 1.3.4 Redaction scope and transparency

Version 3.4 of our RSP requires us to publicly disclose, at a high level, when we make redactions in the public version of a risk report. Our [previous Risk Report](http://anthropic.com/feb-2026-risk-report) already meets this standard. It also requires that fully unredacted risk reports be shared with at least 200 Anthropic employees (rather than with all regular-clearance Anthropic staff, as previous RSP versions required). We continue to share minimally-redacted risk reports with all Anthropic staff, but we expect there may often be information which is both important to our risk assessment and highly sensitive to the point of meriting greater internal compartmentalization, especially in light of the company’s ongoing growth.

In this Risk Report, the only redactions we have made for the version shared with all regular-clearance Anthropic staff are located in [Section 3.5](#35-acceleration-of-ai-progress-due-to-automated-ai-rd), where we discuss internally compartmentalized and commercially sensitive details of our AI R&D development process. All redactions made for the public version of the report are noted below.

#### 1.3.5 Governance and review changes around Risk Reports

Version 3.2 of our RSP authorizes Anthropic’s Long-Term Benefit Trust (LTBT) to request external review of risk reports, gives the LTBT the power to approve our selection of external reviewers, and formalizes a requirement that we provide the LTBT with regular briefings. Version 3.4 clarifies that we may spread the review process for unredacted risk reports across multiple external reviewers, so long as every part of any unredacted risk report is reviewed by at least one such reviewer.

These changes do not directly affect the content of the current Risk Report. Since this change to our RSP, the LTBT has not requested an external review (nor has the RSP required that we conduct one), though we have continued to conduct pilot external reviews (e.g. with METR [here](https://metr.org/blog/2026-05-08-rd-section-anthropic-risk-report-feb-2026-review/) for the AI R&D section of our [previous Risk Report](http://anthropic.com/feb-2026-risk-report), and SecureBio [here](https://securebio.org/blog/review-of-anthropics-unredacted-chemical/) for its chemical and biological risk sections).

### 1.4 Notes on coverage of unreleased models

As of the coverage date of July 15, 2026, there were three internal models with frontier or near-frontier capabilities which had not been publicly released:

<!-- p.16 -->

- Claude Opus 5, which was internally deployed on the coverage date and has since been publicly released; see [its System Card](http://anthropic.com/claude-opus-5-system-card) for more information. Its capabilities are generally lower than those of Claude Mythos 5 or Claude Fable 5.
- Model 1, which is broadly similar in capability to Claude Mythos Preview and Mythos 5 and had a relatively small amount of internal deployment.
    - We have not conducted extensive risk assessments on the model, but we generally do not think it is significantly more capable than the other models we discuss in this report, nor does it raise significant new concerns for other reasons (e.g., alignment properties). In a poll of internal users, a strong majority preferred to use Mythos 5, and internal usage was relatively low and declining as of the coverage date. We do not expect this model to be externally deployed or widely internally deployed in the future.
    - Given that this model is generally as or less capable than Mythos 5, does not appear to be significantly different from an alignment perspective, *and* is strictly less widely deployed than Mythos 5 in both internal and external contexts, we consider any arguments about the risks posed by Mythos 5 to serve as an upper bound for the risks of this model as well, and do not discuss it further in the rest of this Risk Report except to note its existence in [Appendix 6.6](#66-our-ai-models).
- Model 2, which is somewhat more capable than Mythos 5. Our rough qualitative sense is that this model is a noticeable improvement on Mythos 5 for many tasks relevant to internal use but does not display a capability jump of the degree observed from Claude Opus 4.6 to Mythos Preview. We do not currently have plans to release this model externally, and have not run all of our typical suite of predeployment assessments, so we have somewhat lower confidence in our beliefs about its capabilities. We discuss this model’s applicability to each of our major RSP threat models in the following sections, though in Sections 3 and 4 our treatment is relatively brief.

For a full list of our AI models, see [Appendix 6.6](#66-our-ai-models).
[^1]: “Catastrophic risk” as used in our RSP refers generally to risks of the most severe potential harms from advanced AI, such as existential threats or fundamental destabilization of global systems. We use this term in its plain meaning rather than adopting any specific statutory definition. Where laws such as California’s Transparency in Frontier Artificial Intelligence Act (aka SB 53) define this or similar terms with specific thresholds, we address those requirements in separate compliance frameworks.

[^2]: Excluding the 18-day period during which Mythos 5 was restricted [via temporary export controls](https://www.anthropic.com/news/redeploying-fable-5).

[^3]: To be explicit, there was no impact on our customers.

[^4]: “Double the rate of progress” means “as much progress in one year as one would see in two years at baseline.” For example, if baseline progress involved a 3× scaleup in compute and a 3× improvement in algorithmic efficiency (for a 9× “effective scaleup”), “double the rate of progress” would entail something like an 81× effective scaleup. This is not the same idea as “doubling researchers’ productivity,” since doubling inputs does not necessarily double the rate of progress.

[^5]: Over at least three model generations.

[^6]: In particular, weapons with the potential to cause events with consequences comparable to or worse than those of COVID-19.

[^7]: For example, a program with millions of dollars available and support from recent PhD graduates from top-tier international programs. We are focused on the sorts of teams that would be realistic for real-world threat actors.

[^8]: E.g., in a world with access only to the best AI models as of 2023.

[^9]: E.g., hundreds.

