<!-- source: source.pdf pages 175-186 -->

<!-- p.175 -->

## 6 Appendices

### 6.1 Threat model criteria

Anthropic’s research gives consideration to a very wide variety of risks from AI, and helps us develop and implement safeguards and other responses in many categories. For example:

- Our Safeguards research helps us understand and mitigate potentially dangerous, disruptive, or otherwise suboptimal outputs of our models, such as those relating to child safety, political bias, suicide or self-harm, or the encouragement of user delusions;
- Our Economic Index research tracks usage of AI across the labor market, gathering data on the potential impacts for jobs and other aspects of work;
- Our Threat Intelligence research helps us monitor how AI models are being used in cyberattacks so that we can develop the relevant cyberdefense capabilities;
- Our Alignment research covers a very wide variety of potential risks, including sycophancy (where models deceive users by telling them what they want to hear rather than what’s necessarily true), “reward hacking” (where models find and exploit loopholes in tasks), and “alignment faking” (where models hide their true motives).

However, for the purposes of the Responsible Scaling Policy and these associated risk reports, we believe giving extra focus to a relatively small number of risks is a more promising approach to developing robust (and often partially generalizable) safeguards and analyses than spreading ourselves thin trying to analyze a much larger number.

Our criteria for prioritizing threat models are:

- A combination of high potential damages and high likelihood for these potential damages.[^89]
- A clear role for AI in creating risk beyond what is created by other technologies and background conditions.
- Threat scenarios that survive sanity checks considering historical analogies (e.g., we place lower priority on attacks that have been relatively rare or less damaging<!-- p.176 --> historically, unless there are specific reasons to expect AI to change historical patterns).
- Consideration of some additional factors, such as the extent to which addressing one threat model might help put us in position to address other priority threat models, and the extent to which threats are hard to get early warning signs of and respond to accordingly (the more the latter holds, the more appropriate a focus on prevention is).

These criteria are addressed for specific threat models in the “Threat model” subsections throughout this report.

### 6.2 [Appendix redacted]

This appendix describes the criteria for our blocking bioclassifier exemption policy, and has been redacted from the public version of this report for security reasons.

### 6.3 [Appendix redacted]

This appendix, redacted from the public version of this report, details the changes made to our constitution to expand classifier coverage to harmful uses in scope for the CB-2 threat model but not the CB-1 threat model, as described in [Section 4.5.2.1](#4521-extension-in-coverage-since-our-prior-risk-report).

### 6.4 Model weight security

#### 6.4.1 Overview

Anthropic has developed a security program to protect ASL-3 model weights against most non-state attackers, including cybercriminal groups, hacktivists, and corporate espionage actors. Our approach follows industry-standard threat modeling practices, systematically identifying attack vectors across six primary categories: endpoint compromise, supply chain attacks, physical attacks, cloud infrastructure compromise, privilege escalation, and data exfiltration.

The security program attempts to implement defense-in-depth principles, layering preventive controls (blocking attacks before they succeed), detective controls (identifying attacks in progress), and responsive controls (containing and remediating incidents). We’ve attempted to broadly align our program with established frameworks including SOC 2 Type 2, ISO 27001, and ISO 42001, while extending these to address AI-specific risks to model weights.

<!-- p.177 -->

Our threat model explicitly scopes ASL-3 protections against non-state actors and unsophisticated insiders. Sophisticated insiders,[^90] and nation-state attackers with capabilities like novel zero-day attack chains, remain out of scope for ASL-3: we are actively working to address these issues, and note that defending against such actors requires security investments beyond what we’ve currently achieved.

Three trends make this risk profile more challenging to maintain over time.

First, our attack surface is growing: we continue to bring significant new compute capacity online across multiple providers and environments, and these environments do not all begin at the same level of security maturity. Raising every environment to our target baseline takes time and forces prioritization, which means that at any given point some parts of our infrastructure may be better defended than others.

Second, the rate at which model capabilities are improving is generally faster than the rate at which we can build and mature our defenses, so the sophistication of the adversaries motivated to target us is growing faster than the sophistication of the adversaries we can reliably stop.

Third, the incentive to steal our weights specifically is rising. As we strengthen controls on legitimate access—tighter customer verification, limits on ZDR deployments, closer monitoring of high-trust deployment arrangements, and safeguards against distillation and the use of our models for frontier AI development—we progressively limit the channels through which a determined actor could otherwise extract much of our models’ value through ordinary use. These dynamics increase threat actor incentives to access our models via weight theft, as other routes of gaining safeguard-free access become more difficult.

As a result, the gap between the capability level of attackers motivated to target us and attackers we can reliably defend against is at risk of widening, and we expect closing it to require sustained, prioritized investment in our security posture.

#### 6.4.2 Notable security controls

Some notes on caveats or limitations to these controls have been redacted from the public version of this report on six of the following controls, to make it more difficult for attackers to exploit those limitations. For similar reasons, we do not identify exactly which subset of these controls have such redacted caveats.

<!-- p.178 -->

1. **Egress bandwidth controls:** Network-level restrictions that limit data transfer rates out of sensitive environments, making large-scale exfiltration of multi-terabyte model weights more time-consuming and detectable.
2. **Multi-party access controls (2PC)**: Requires a second employee to approve access requests for model weights and other sensitive resources, making it harder for single points of compromise to enable unauthorized access.
3. **Binary allowlisting:** Only pre-approved software can execute on employee devices. This can block malware and unauthorized code from running regardless of how it arrives on the system.
4. **Hardware security keys for authentication:** Phishing-resistant MFA using hardware tokens bound to specific domains, reducing the risk of credential theft through fake login pages.
5. **Device authorization:** Only explicitly approved Anthropic-managed devices can authenticate to systems containing model weights.
6. **Cloud storage restrictions:** Technical controls preventing model weights from being written to storage locations outside our security perimeter, using cloud-native policy enforcement.
7. **Restricted session lengths for privileged access:** Privileged cloud identities require re-authentication hourly, limiting the window of opportunity if credentials are stolen.
8. **Network segmentation:** Isolation between environments of different sensitivity levels, limiting lateral movement if an attacker compromises a less-sensitive system.
9. **Centralized security monitoring:** Aggregated logging with automated anomaly detection, enabling rapid identification of suspicious patterns across our infrastructure.
10. **Network source policies on privileged resources:** Even if an attacker steals valid credentials, operations on sensitive resources are rejected if the request originates from outside approved network locations. The goal is to render stolen tokens useless from an attacker’s own infrastructure.

For plans to further improve our controls, see our [Roadmap](https://anthropic.com/rsp/roadmap).

### 6.5 List of minor incidents related to our CB risk mitigations

*This appendix elaborates on the content discussed in* [*Section 4.5.8*](#458-changes-to-our-risk-mitigations-since-our-last-risk-report)*.*

Several incidents during the coverage period individually posed no-to-low risk but are informative for general transparency about our risk preparedness. In each case, there was an internal issue with our classifiers or access controls, but the resulting gaps were bounded in scope, whether by duration, deployment surface, affected population, or the<!-- p.179 --> size of its effect on classifier performance. Each of these issues was identified through our own testing and monitoring rather than surfaced by external exploitation, and has since been remediated. In many cases these incidents have also led us to make (or establish plans for) various process improvements, described below.

**Less robust classifiers for Sonnet 4.6 during launch preview:** Shortly before the launch of Sonnet 4.6, we found that our early classifiers were unusually non-robust; some launch preview customers had early access using the less robust classifier until we developed an improved classifier for the model’s general access launch. Lower-safeguard exposure was limited to a small pool of launch preview customers for a short period of time. We have since improved our classifier evaluations to help catch these kinds of issues earlier in the launch process and made procedural changes to allow probe training to begin further in advance of early access programs.

**Helpful-only model access extended for a longer time period than intended:** For Claude Mythos Preview, we identified that the h-only model access we had granted to two external CBRN testing orgs (intended for predeployment testing) continued for two weeks after model launch due to a failure on our part to revoke this access (which we have now done). Deprovisioning this access still relies on manual action, though we hope to implement automatic expiry of such credentials in the future. These organizations had already been cleared for such access (just for a shorter window of time), and we don’t consider the brief additional period of access to pose significant risks.

**Classifier blocks temporarily disabled on Opus 4 and Opus 4.1 on one deployment surface:** A configuration error led to classifiers not blocking flagged Opus 4 or Opus 4.1 traffic on one of our deployment surfaces.[^91] All other deployment surfaces for these two models were unaffected, as were all other models. The error was resolved within 48 hours of the misconfiguration being deployed. Overall, we assess the risk posed by this incident to have been very low: The exposure was brief (far shorter than the requisite length of access corresponding to our threat models) and confined to one surface; further, these are legacy models, and as discussed in [Section 4.4](#44-current-state-of-model-capabilities) we have updated toward expecting somewhat lower uplift from models of this generation. We are developing – though have not yet deployed – a much more automated, rule-driven model configuration system that we expect to significantly reduce the rate of similar configuration errors.

**Overly high first-stage probe threshold on Opus 4.7:** When rolling out an updated classifier for Opus 4.7, the stage-1 probe threshold was incorrectly set to the numerical value of the previous classifier’s threshold, which was too high for the new classifier. This<!-- p.180 --> led to some traffic not being blocked or logged for offline monitoring for a period of 5 days, due to a large number of requests which should have been forwarded to a stage-2 classifier that were not.[^92]

Note that the large majority of requests flagged by the first-stage probe are benign, and only a very small fraction would have been blocked by the combined classifier system. Despite the too-high threshold for the first-stage probe, the system overall performed as expected with respect to the vast majority of traffic: we estimate that the block rate would have been around 3% higher without this misconfiguration. Further, the system overall remained sensitive to the highest-scoring (i.e., highest risk) traffic; we expect the missed blocks to have been concentrated among more borderline requests rather than clearly harmful ones. We therefore assess the overall risk posed by this incident to have been very low.

The threshold was corrected the same day the error was identified, and follow-up work is planned to ensure that probe and threshold changes are paired programmatically rather than copied by hand.

**Small portions of some completions not scored by classifiers:** A bug in our streaming classifiers had two effects: the last portion of some exchanges (about 40 tokens in the median case) was not scored by the classifiers, and some completions returned slightly more content *after* the point at which the streaming classifier fired. The bug had been present for at least several months prior to discovery, and took us several weeks to fix after we learned of the bug. For nearly all affected traffic, the impact was marginal. The classifiers continued to score the large majority of every exchange; only a short tail went unscored. We estimate that fixing the issue would have increased the flag rates of our bio classifiers by roughly 1.5% (relative, not absolute) – in other words, the classifiers continued to flag the overwhelming majority of the content they were designed to catch. The bug was more significant very early on in the Fable 5 release, and may have caused some early Fable 5 completions to be returned largely or entirely unscored. We have since patched this issue on all traffic. Overall, we consider this incident to pose low risk.

**Image data not shown to part of our classifiers:** For approximately two months, a bug caused image data to be stripped from the input to our second-stage CB classifiers. We rolled out a fix to first-party traffic within 1 day of discovering the bug, and to all other surfaces within 5 days of discovery. We think the risk posed by this bug was very low for two reasons. First, the part of the pipeline that identifies potentially concerning traffic—the<!-- p.181 --> first-stage probe—was unaffected and therefore saw images throughout, so image-bearing exchanges continued to be flagged and escalated at normal rates at that stage. Second, the second-stage classifiers continued to receive the full text of every exchange, including the model’s reasoning, and models generally describe the content of the images they are working with in that reasoning. Image content therefore typically reached the second-stage classifiers indirectly even while the bug was live. The residual exposure was correspondingly narrow: it would have arisen only where harmful content appeared in an image that the model acted on without describing in text. We now maintain multiple tests that include image data, which would catch similar bugs in the future.

Customer granted more bioclassifier exemption seats than had been approved: In May 2026, we determined that an enterprise customer’s bioclassifier exemption for Opus- and Sonnet-class models, approved for a defined subset of the customer’s workforce, was in effect for roughly four times the approved number of seats. These unintended approvals constituted the majority of all exemption seats we had granted. This occurred because the customer’s organization had been expanded to a larger seat allocation, and the exemption was inherited automatically by the new seats. An earlier effort to limit the scope of this specific exemption to actual users had stalled awaiting new tooling.

We assess that the risk posed from this particular incident was low. The customer had already met the requirements of our exemption policy, and telemetry data showed that only a small fraction of the covered users (well below the number of approved seats) ever triggered our classifiers.

To remediate, we are migrating the customer to a configuration scoped to the users who require the exemption, and will re-enable the classifier for the remaining seats once that migration completes. In the interim, we are maintaining enhanced automated review monitoring across all organizations qualifying for bioclassifier exemptions. We are also prioritizing a workstream to scope exemptions to individual users and roles rather than to entire organizations, which will address the root cause of this incident.

### 6.6 Our AI models

This appendix inventories the AI models we serve, externally and internally, as of the coverage date of July 15 2026. It does not list each model individually. Instead, it puts them in categories with a focus on their risk-relevant properties: patterns of usage, capability levels, and potential to have dangerous unintended goals. In many cases, there are a large number of models in a category that—due to limited capabilities or limited usage—we believe poses low risk roughly regardless of alignment properties.

<!-- p.182 -->

<table><tbody>
<tr><th>Model name or category</th><th>Brief description</th><th>Surfaces</th><th>Usage notes</th><th>Capability notes</th><th>Alignment notes</th></tr>
<tr><td><b>Claude Mythos 5</b></td><td>Frontier model with limited external availability</td><td>Limited availability to approved customers via the invitation-only Project Glasswing program; extensively deployed internally</td><td>Used extensively within Anthropic for research and engineering, both interactively and via persistent agent deployments; limited external usage by approved customers</td><td>Our most capable externally deployed model, our most capable model overall in some domains</td><td>See the <a href="https://anthropic.com/claude-fable-5-mythos-5-system-card">Claude Fable 5 &amp; Claude Mythos 5 System Card</a></td></tr>
<tr><td><b>Claude Fable 5</b></td><td>Same model weights as Mythos 5, deployed with higher-coverage safeguards (see <a href="#4522-wider-coverage-of-cb-classifiers-for-fable-5">Section 4.5.2.2</a>)</td><td>Bedrock, Vertex, Azure, 1P (direct service from Anthropic)</td><td>General-purpose model with many users and many use cases</td><td>Our most capable widely released model</td><td>See the <a href="https://anthropic.com/claude-fable-5-mythos-5-system-card">Claude Fable 5 &amp; Claude Mythos 5 System Card</a></td></tr>
<tr><td><b>Claude Mythos Preview</b></td><td>Legacy Mythos-class model, not widely deployed</td><td>Invitation-only access via the Project Glasswing program</td><td>Limited usage</td><td>Broadly similar to other Mythos-class models on risk-relevant evaluations, though Claude Mythos 5 appears more capable (see <a href="#443-cb-2-evidence-for-mythos-preview-fable-5-and-mythos-5">Section 4.4.3</a>)</td><td>See the <a href="http://anthropic.com/claude-mythos-preview-system-card">Claude Mythos Preview System Card</a></td></tr>
<tr><td><b>Internal Model 1</b></td><td>Legacy Mythos-class model, not externally deployed.</td><td>Internal-only</td><td>Limited usage, declining over time</td><td>Broadly similar to other Mythos-class models, generally dispreferred to Mythos 5 internally</td><td>Less extensive assessment, but broadly comparable to our other production models.</td></tr><!-- p.183 --><tr><td><b>Internal Model 2</b></td><td>Mythos-class model, not externally deployed.</td><td>Internal-only</td><td>Internal usage similar to Mythos 5</td><td>More capable than Mythos 5 in some areas, less capable in others; overall slightly more capable.</td><td>Less extensive assessment, but broadly comparable to our other production models.</td></tr>
<tr><td><b>Claude Opus 5</b></td><td>Major commercial model</td><td>Internal-only as of the coverage date (now widely released)</td><td>Moderate internal usage as of the coverage date</td><td>Generally less capable than Mythos 5.</td><td>See the <a href="https://anthropic.com/claude-opus-5-system-card">Claude Opus 5 System Card</a></td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>Major commercial model</td><td>Bedrock, Vertex, Azure, 1P (direct service from Anthropic)</td><td>General-purpose model with many users and many use cases</td><td>Our most capable model without research biology classifiers offered widely to consumers as of the coverage date</td><td>See the <a href="https://www.anthropic.com/claude-opus-4-8-system-card">Claude Opus 4.8 System Card</a></td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>Major commercial model</td><td>Bedrock, Vertex, Azure, 1P (direct service from Anthropic)</td><td>General-purpose model with many users and many use cases</td><td>Roughly equivalent to Claude Opus 4.8 with respect to CB-relevant capabilities (see <a href="#43-relevant-ai-models">Section 4.3</a>); less capable than Claude Mythos 5</td><td>See the <a href="https://www.anthropic.com/claude-sonnet-5-system-card">Claude Sonnet 5 System Card</a></td></tr>
<tr><td><b>Claude Haiku 4.5</b></td><td>Major commercial model</td><td>Bedrock, Vertex, Azure, 1P (direct service from Anthropic)</td><td>General-purpose model with many users and many use cases</td><td>Less capable and cheaper than Claude Sonnet 5; we do not require blocking biological classifiers</td><td>Broadly (though not universally) reassuring observations; see <a href="https://assets.anthropic.com/m/99128ddd009bdcb/Claude-Haiku-4-5-System-Card.pdf">Claude Haiku 4.5 System Card</a></td></tr><!-- p.184 --><tr><td><b>Legacy models (see list in <a href="#661-list-of-all-claude-models-sorted-by-release-date">appendix</a>)</b></td><td>Legacy commercial deployments, generally less widely used and less capable than Claude Fable 5 and Claude Sonnet 5. Some require blocking CB safeguards.</td><td>Bedrock, Vertex, Azure, 1P</td><td>General-purpose models with many users and many use cases</td><td>Varies (but all less capable than Claude Mythos 5)</td><td>Varies</td></tr>
<tr><td><b>Claude Gov</b></td><td>Claude with post-training for national security uses, e.g. fewer refusals for potentially national-security-relevant requests. See <a href="#45532-claude-gov">Section 4.5.5.3.2</a> for more.</td><td>AWS Secret Cloud and AWS Top Secret Cloud</td><td>All users must have at least Secret clearances and work from within accredited networks. Variety of uses, and we do not currently monitor usage</td><td>Presumably similar to underlying commercial models</td><td>Evaluation of Claude Gov version of Sonnet 4.5 was roughly in line with that of mainline Claude Sonnet 4.5. Others unknown.</td></tr>
<tr><td><b>Other fine-tuned models</b></td><td>Models fine-tuned by Anthropic and/or customers. Claude Haiku 4.5 is the current most capable base for such models, and usage is generally small-scale.</td><td>1P and Bedrock</td><td>Limited usage</td><td>Presumably similar to underlying base models</td><td>Not evaluated</td></tr><!-- p.185 --><tr><td><b>Internal models (other than the two internal models described above)</b></td><td>Models used only internally for narrow purposes (such as producing training data and generating preference scores for reinforcement learning) and research purposes.</td><td>Internal-only</td><td>Variety of uses, but none have comparable affordances and integrations to Claude Mythos 5 and our major commercial models</td><td>Varies, but none currently have capabilities beyond that of Claude Mythos 5</td><td>Not evaluated</td></tr>
<tr><td><b>Small externally deployed models for narrow purposes</b></td><td>Some small models are used in production for purposes such as classifying and preventing misuse.</td><td>Variety of surfaces</td><td>Narrow purposes such as classifying and preventing misuse</td><td>Substantially less generally capable than major commercial models</td><td>Not evaluated</td></tr>
</tbody></table>

:::caption
**[Table 6.6.A] Summary of the AI models we serve** by category, with a focus on risk-relevant properties.
:::

#### 6.6.1 List of all Claude models, sorted by release date

- Claude Opus 5
- Claude Sonnet 5
- Claude Mythos 5 (available via the Glasswing program)
- Claude Fable 5
- Claude Opus 4.8
- Claude Opus 4.7
- Claude Mythos Preview (available via the Glasswing program)
- Claude Sonnet 4.6
- Claude Opus 4.6
- Claude Opus 4.5
- Claude Haiku 4.5
- Claude Sonnet 4.5
- Claude Opus 4.1
- Claude Opus 4
- Claude Sonnet 4
- Claude Sonnet 3.7
- Claude Haiku 3.5
- Claude Sonnet 3.5 (New)
- Claude Sonnet 3.5
- <!-- p.186 -->Claude Haiku 3
- Claude Sonnet 3
- Claude Opus 3
- Claude 2.1
- Claude 2
- Claude Instant (1.1/1.2)
- Claude 1 (1.0/1.3)
[^89]: One relevant concept here is the idea of “expected” damages—the probability of each potential harm times the size of the harm, summed over all potential harms. We sometimes create rough estimates of expected damages, and other times simply reason informally about which threat models are most likely to have a combination of high likelihood and high potential damages that would imply high expected damages.

[^90]: We define “sophisticated insiders” as insiders who have persistent access or can request time-limited access to systems that process model weights.

[^91]: The specific deployment surface in question has been redacted here for security reasons.

[^92]: Exact numbers for this traffic have been redacted from the public version of the report for reasons of commercial sensitivity.

