<!-- source: source.pdf pages 135-157 -->

<!-- p.135 -->

#### 4.5.3 Evidence about robustness of classifiers

##### 4.5.3.1 Ongoing bug bounty results

We run our [Model Safety Bug Bounty Program](https://support.claude.com/en/articles/12119250-model-safety-bug-bounty-program) through HackerOne to incentivize third-party researchers to discover and report vulnerabilities in our AI systems, particularly jailbreaks that could bypass the classifiers against harmful biology discussed here. We have been running this program since August 2024. Since before our previous Risk Report, we have run a bounty through this program using a live-updating version of our safeguards on Sonnet 4.5, which originally ran on a system similar to our Level 1 Robustness classifiers; since May 2026, this model uses Level 2 robustness classifiers. We have run a second ongoing bug bounty using our latest classifiers from Opus 4.7 since shortly after the release of that model; this bounty tests our Level 3 robustness classifiers.

We provide approved testers with access to a free model alias, where we can monitor and train on their jailbreak efforts. In order to be eligible, testers need to sign an NDA and sign up for a Claude console account using their [wearehackerone.com](http://wearehackerone.com) email. Our terms of use require testers to only use these accounts to test against a fixed set of eight harmful biological questions that would be blocked by our classifiers. Testers are tasked to bypass the classifiers and elicit informative responses from the model. We perform automated assessments of response informativeness to determine whether the hackers have succeeded.

We pay up to $35,000 per novel universal jailbreak identified. Bounty payments are rewarded based on a curve that encourages hackers to aim for universal jailbreaks while still earning bounties for non-universal jailbreaks. This structure aims to encourage wide participation and testing.[^62]

Since March 1, 2026, we have paid out $87,800 in bounties. The program has surfaced 21 reports, of which we validated 5 as non-universal jailbreaks and 1 as a universal jailbreak (which we describe further in [Section 4.5.3.2.4](#45324-bug-bounty-sourced-jailbreak) and does not apply to our models with Level 2 or higher robustness).[^63] These reports collectively represented about 600 self-reported hours of red-teaming effort, although this excludes hours spent by red-teamers who did not submit any reports.

<!-- p.136 -->

##### 4.5.3.2 Notes on jailbreak methods that remain viable on at least some models in some cases

As of the coverage date of this report, we are aware of four routes which we think could plausibly be used to circumvent our deployed classifiers and obtain assistance with dangerous CB tasks from at least one of our models without a large degradation in their capabilities. One of these is a coverage gap (rather than a jailbreak *per se*) independently identified by UK AISI and internal testing, which we are in the process of rolling out mitigations for; two others were surfaced to us from AISI; and one was surfaced by our ongoing bug bounty described above. None of the methods discussed below are publicly disclosed in enough detail for a threat actor to easily implement, and in all cases we have already deployed or are in the process of deploying mitigations which make the approach in question difficult or impossible to execute on our most capable models.

Although our track record of eventually patching or mitigating every universal highly-effective jailbreak or coverage gap that we learn of for bypassing our biological classifiers is strong, and to our knowledge there has never been a period of time since our first deployment of these classifiers in which there was a publicly known method by which an attacker could straightforwardly bypass them, our resolution times for these non-public jailbreaks have been as long as several months to reach all deployment surfaces on our most capable models. These timelines are longer than we would ideally prefer, though in our opinion they are commensurate with the risks given that these jailbreaks were not known to threat actors. We expect that if there *were* to be a publicly known highly effective universal jailbreak which attackers could easily implement, we would deploy a fix more quickly, but this has not been tested.

###### 4.5.3.2.1 Boundary-point jailbreaking

[Boundary Point Jailbreaking (BPJ)](https://arxiv.org/abs/2602.15001) is an automated methodology developed by [UK AISI](https://www.aisi.gov.uk/) that optimizes against black-box classifiers to search for strings that would universally jailbreak classifiers and obtain harmful outputs from guarded models. The jailbreaks found via BPJ are especially concerning because they cause little to no degradation in the target model’s capabilities, as opposed to most other universal jailbreaks that have been discovered. While the high-level methodology behind the attack is public, we do not know of any public implementations which would be effective against our safeguards at any robustness level.

**Points mitigating the risk from BPJ:**

- **1.** **It is difficult to implement, and more difficult to implement with high efficiency.**

<!-- p.137 -->

We reimplemented BPJ with the help of UK AISI with considerable effort—it took one of our researchers several weeks (though this was due in part to extended back and forth conversations with UK AISI, and we estimate around 20 hours of total fulltime effort on our side). We believe that an actual attacker would have much more trouble reproducing the methodology, since critical implementation details were redacted from the published version and because UK AISI would not assist them with active debugging during reproduction. We think this issue alone means the risks are low for our CB-1 threat model.

Getting a working and efficient BPJ implementation is the kind of verifiable hill-climbable task that recent models are often good at, and for which the capability frontier is rapidly advancing. However, we believe it would be quite difficult for external threat actors to replicate BPJ with assistance from current public models, for two reasons: (1) During our collaboration with UK AISI to internally reimplement BPJ, we made use of Opus 4.5, Opus 4.6, and Mythos Preview along with internal human expertise and extensive UK AISI interactive support and still found the implementation quite difficult; (2) we have continued to use internal models to suggest improvements to our internal implementation since then, and have not found their suggestions particularly helpful. Given this evidence, we think the risk of attackers building effective BPJ implementations remains low, but we expect this to change for sufficiently capable models and plan to continue monitoring the risks from this possibility.

- **2.** **Our Level 3 classifiers are significantly more (though not perfectly) robust to BPJ.**

We tested our implementation of BPJ against the second-stage LLM-based classifier from our Level 3 robustness classifier both by itself and compared its robustness to that of our Level 1 blocking classifier in production at the time. We found that across two different BPJ experiments, the Level 3 robustness classifier was at least 3× more robust to BPJ optimization than our Level 1 classifier, as estimated by the rate at which optimization succeeded against a given classifier. This increase in robustness was also independently verified by UK AISI, though they estimated a 2× increase in robustness.[^64]

When our Level 3 robustness second-stage classifier is combined with our first-stage probe into our full Level 3 robustness classifier, our system becomes significantly more robust, on top of the gains from the second stage on its own. Our experiments show that the full Level 3 robustness classifier appears to be roughly 1.7× as robust as the Level 3 second-stage classifier by itself, as well as at least 5× (but likely closer to 7–8×) as robust as the Level 1 classifier.[^65]

<!-- p.138 -->

- **3.** **Attacks have a high chance of being caught by our monitoring.**

We additionally implement some BPJ-specific monitoring of our traffic; we believe our finished implementation of this monitoring would make it extremely difficult and costly for an attacker to successfully run an end-to-end BPJ pipeline against our most capable models without being banned and flagged to law enforcement, though our implementation as of the coverage date has some significant limitations we are in the process of improving. More detailed discussion of this monitoring, and our evidence for its efficacy, has been redacted from the public version of this report.

Our current evidence suggests that in cases where we are running Level 3 classifiers and when monitoring for BPJ is enabled, an attacker that attempts to leverage BPJ to jailbreak our defenses would need to (1) reproduce the BPJ attack, which would be very technically challenging and (2) take on very costly measures to evade our monitoring (details redacted from the public version of this report).

One additional, weaker consideration which may make it more difficult for an attacker to successfully get uplift from using BPJ against our classifiers has been redacted from the public version of this report.

**Notes on limitations to the above arguments:**

1. Our assessment of our system’s robustness to BPJ is based on our own internal replication of UK AISI’s BPJ attack, cross-validated by AISI. There is the possibility that an attacker could develop a version of the attack that is significantly stronger than both our version and AISI’s version. We believe this risk is not very large because both our team and AISI have had months to develop the attack and collaborated on methodology; an actual attacker would likely have less assistance from red-teaming experts to optimize their version of the attack.
2. Our monitoring approaches currently have significant limitations, as mentioned above, though we are in the process of making improvements. One limitation we do *not* expect our improvements to resolve is that we have less confidence in our ability to flag BPJ-relevant activity on surfaces with zero data retention (ZDR). We do not currently know of a mitigation strategy for this limitation for CB-2 threat actors other than refraining from deploying sufficiently capable models on ZDR surfaces in settings at risk of use by such actors (e.g. enterprise deployments without both strong KYC requirements and very strong security guarantees against compromise of individual users’ access).
3. <!-- p.139 -->We have redacted a limitation related to a possible strategy an attacker could use, which we do not wish to publicize. We have some weak evidence suggesting the strategy would not be particularly effective.

###### 4.5.3.2.2 UK AISI-sourced jailbreak

UK AISI reported a jailbreak to us in November 2025 that (a) leveraged information we had given them to help them find jailbreaks; (b) was hard for us to replicate (we were not able to do so consistently); (c) was assisted by jailbreakers’ already knowing answers to the questions they were trying to get the model to answer (though it may have worked partially or fully without this). We believe this jailbreak would be hard to find and execute, and have not seen any signs of it in our bug bounties or in public.

Our Level 2 and above classifiers are able to robustly block this jailbreak, though we are less confident about Level 1.

###### 4.5.3.2.3 Coverage gap identified by both Anthropic and UK AISI

Internal robustness testing of our safeguards surfaced a coverage gap in our classifiers’ training data, whose details have been redacted from the public version of this report since we have not yet deployed our mitigations on all models.

UK AISI later reported a similar issue to us.

We have since developed new classifiers with expanded coverage of these gaps, which we are in the process of rolling out for all models. Though we are aware of the existence of limited scenarios that bypass the new classifiers, all such scenarios that we are currently aware of are now primarily limited to generic tasks for which we estimate low uplift, and which are accessible on models of significantly lower capabilities.

###### 4.5.3.2.4 Bug-bounty-sourced jailbreak

As mentioned above, our ongoing bug bounty has surfaced one universal jailbreak since our previous Risk Report. This jailbreak was first located when our bounty was running on Level 1 robustness classifiers; by the time we learned of the jailbreak, we had already migrated to weighted two-stage classifiers with Level 2 robustness, which mitigate this jailbreak without any additional training, so only our Level 1 robustness classifiers are vulnerable to this (non-public) jailbreak.

#### 4.5.4 Offline monitoring

In addition to online safeguards like our streaming classifiers described above, we perform some *offline monitoring*: cases where we analyze traffic after the fact to look for patterns of<!-- p.140 --> misuse across many exchanges. We have generally de-emphasized offline monitoring as an untargeted jailbreak discovery measure, as mentioned in our previous Risk Report. However, our Enforcement teams regularly make use of offline monitoring to understand account-level behaviors and identify systematic misuse in a number of ways. For example:

- We have an offline monitor that looks for attack patterns characteristic of boundary-point jailbreaking (BPJ), as described above in [Section 4.5.3.2.1](#45321-boundary-point-jailbreaking).[^66]
- We use offline monitoring for organizations with exemptions from our blocking classifiers (as described in [Section 4.5.5.2](#4552-exemptions-for-all-other-sub-mythos-class-commercial-models)). Specifically, for traffic flagged (but not blocked) by our bio classifiers for such organizations and for which ZDR is not enabled, we run a weekly automated monitoring pipeline over all such traffic, which surfaces signals of various categories of concerning activity. These reports are surfaced for regular review by a limited pool of Anthropic employees, and if there are especially concerning findings, the human reviewer can investigate the raw traffic in question more closely and take action as necessary.
- We also use offline monitoring for routine account-level monitoring over a subset of traffic across all CB harm areas and on multiple (though not yet all) traffic surfaces. Content surfaced by semantic search against curated query sets, and by flags from our online monitoring classifiers and probes, receives an automated first pass investigation against rubrics specific to each harm area, producing a list of cases ranked by severity for a limited pool of internal reviewers. While not targeted specifically to identify jailbreak attempts, this monitoring pipeline may catch instances of successful jailbreaks if they are present within the sampled traffic population.

#### 4.5.5 Bioclassifier exemptions

We allow some trusted and vetted users to access our models with reduced or no CB-risk-based blocking classifiers, via the policies described in the following subsections. Where data retention agreements permit, we still log classifier scores on traffic from the exempted party (but do not block model completions when the classifiers fire).[^67]

##### 4.5.5.1 Exemptions for Mythos Preview, Mythos 5, and Fable 5

As of the coverage date of this Risk Report, we do not offer external access to Claude Mythos Preview, Claude Mythos 5, or Claude Fable 5 for any commercial use without blocking biology classifiers. Organizations with exemptions for other less capable<!-- p.141 --> Anthropic models are still subject to these classifiers. We may offer these models with reduced or no biological safeguards to select customers via a trusted access program in the future.

We briefly offered unsafeguarded access to these models to a very limited pool of external testing organizations during predeployment testing, but as of the coverage date have not offered such access since the models’ release dates.

##### 4.5.5.2 Exemptions for all other sub-Mythos-class commercial models

Exemptions for the classifiers discussed in this chapter (other than those in the previous section) are governed by a unified exemption policy, whose criteria are largely unchanged since our February report. We have since added one process-level requirement: new exempt customers are asked to attest to use of short-lived API credentials (which we provide on our first party API through Workload Identity Federation). As before, we manually vet every organization before granting an exemption, including an assessment of the potential for harm and a review of the organization’s security posture.

Blocking classifier exemptions are subject to ongoing monitoring (as described in [Section 4.5.4](#454-offline-monitoring)) and monthly reassessment.

Our harmful biology classifiers still run on all traffic from these organizations, but do not block model outputs. For the small subset of organizations with exemptions that additionally have ZDR enabled (less than 3% of active exemption seats), we have no ability to view flagged traffic, but still have visibility into the rate of classifier flags.[^68]

No concerning bio activity has been identified from organizations with exemptions during weekly monitoring, and we have not offboarded any exempted orgs since launch.

Separately from our policy for ongoing organization-level exemptions, we sometimes grant temporary exemptions to our CB classifiers on a case-by-case basis for collaborations with external safety researchers where that collaboration requires such access (e.g. red-teaming experiments). Individual researchers must attest to fulfilling a list of Anthropic-provided security requirements before receiving access.[^69]

<!-- p.142 -->

We have made exceptions to this org-level exemption policy in a small number of cases; this is generally done for organizations with a time-sensitive beneficial use case (e.g. addressing an ongoing public health crisis) for which it is valuable to grant an exemption before our usual security review process has completed. Such exceptions require explicit escalation and approval on a case-by-case basis, and are generally scoped to a relatively small number (<40) of seats and expire after a limited time period unless actively renewed. In all cases to date for which we have granted such exceptions, the organization in question has either been offboarded, successfully completed a review under our standard policy which suffices to grant an ordinary exemption, or we expect to complete such a review in the near future.

##### 4.5.5.3 Access controls for other models not available for general access

In addition to our primary suite of commercial models, we have a small number of limited deployments of models with reduced or no biological safeguards which are not offered commercially, or are offered in advance of our main commercial deployment, discussed immediately below.

###### 4.5.5.3.1 Helpful-only models

We train “helpful-only” variants of our production models—models trained not to refuse on potentially harmful user requests—for evaluating dangerous capabilities and for use on some internal red-teaming tasks.[^70]

Internal policy restricts employee access to these models to a very limited set of staff requiring manual approval, although our technical controls to prevent such access in violation of our policies are fairly limited, and we expect that technically sophisticated employees could still obtain such access via higher-friction routes. We plan to implement additional controls on internal access to these models later this year.

External access to helpful-only models is governed by our Helpful-Only Model Access Policy, which only permits such access for external AI safety testing partners working with Anthropic who have fulfilled our security requirements as of the coverage date.[^71]

As of the coverage date, external access to helpful-only models was held by six organizations, totaling 48 users.[^72]

<!-- p.143 -->

We additionally offer limited duration access to h-only models for some collaborations with individual external safety researchers, when required by these projects.

###### 4.5.5.3.2 Claude Gov

We offer a version of Claude with post-training for national security uses, e.g. fewer refusals for potentially national-security-relevant requests, via our Claude Gov product on AWS Secret Cloud and AWS Top Secret Cloud.

Gov Sonnet 4.5 does not run with CB-relevant safeguards. It is available only to users with US Secret and Top Secret security clearances and access to US Secret and Top Secret networks. Such access requires vetting, and is available only in isolated networks accredited by the government and accessed from locations meeting the government’s security standards for accessing highly sensitive information. We are willing to serve Gov Sonnet 4.5 in these contexts without blocking classifiers to however many appropriately authorized users choose to access them and can be served with available capacity (note that millions of individuals have U.S. Secret or Top Secret clearances).

All other Claude Gov deployments (as of the coverage date and, we expect, for the foreseeable future) are deployed with the same set of blocking CB classifiers that we have for ordinary deployments of the corresponding commercial model (which may be none, for lower-capability models which have no blocking classifiers in commercial settings). We will evaluate potential exceptions for these classifiers on a case-by-case basis going forward. We expect our Claude Gov models to have essentially identical capabilities relevant to CB risk compared to the commercial models from which they are derived.

###### 4.5.5.3.3 Pre-deployment access to unreleased models

During pre-deployment testing of our commercial models, we sometimes offer model access to three categories of users: external testers, early access program users, and human feedback contractors. This access is sometimes to slightly earlier snapshots of the models than the commercially released snapshot for research and development or testing purposes; these early snapshots generally have similar or slightly lower risk-relevant capabilities.

**External testers:** These all have blocking classifiers enabled, except for a small number of trusted external testers (generally fewer than 10) specifically testing dangerous biological capabilities. Access is for a limited period of time.

**EAP users:** These users have blocking classifiers enabled, though they are often running with early versions of those safeguards which have not yet been fully tested (indeed, some<!-- p.144 --> of our testing evidence for our deployment safeguards comes from EAP usage). As above, this is for a limited period of time, and we expect our early safeguards to generally be comparably robust to our deployment safeguards.

**Human feedback contractors:** We work with outside data vendors for human data and testing that goes into training and evaluating our models. These vendors do that work on our data collection platforms, some of which requires access to models we haven’t released to the general public.

We do not directly vet the individual contractors that the vendors engage to provide human feedback data; screening those individuals is the vendor’s responsibility. We have, however, implemented a risk-based assessment governing vendor access, based on the sensitivity of the model and the interactivity of the access. We require that all vendors perform consistent identity and background checks for each worker. They must also meet our endpoint security and access control technical requirements, including phishing resistant multi-factor authentication.

As of the coverage date, the vast majority of this access runs with blocking biological classifiers enabled; vendors with the most robust controls are allowed access to our safeguards-exempt and other higher-risk models which are provisioned on a per-project basis (though these stronger controls would likely not be robust against a well-resourced threat actor making a concerted effort to attain access via this route).

Historically, our vetting process for human feedback data contractors was much weaker, and lacked many of the above requirements. As described in more detail below in [Section 4.5.8.2](#4582-incidents-related-to-our-classifiers-and-access-controls), we experienced some vendor-related model access incidents.

Following these incidents, we have increased monitoring and technical enforcement of our policies with better detections for harmful misuse and use of models outside of scope of the engagement remit.[^73]

##### 4.5.5.4 Malicious access via prompt injection

In theory, an agent running with classifier exemptions and granted broad internet permissions could encounter online content which performed a successful prompt injection, and convinced the agent in question to spend time working on a harmful bioweapon-related task and upload its answer to the internet at a requested location. This<!-- p.145 --> would not require the threat actor to have direct API access to unsafeguarded model inference.

We think that meaningful uplift in bioweapon creation is extremely unlikely via this route, for several reasons:

1. Our models, especially recent ones, are generally quite robust to prompt injection risks, and are regularly used in real-world computer use settings without significant issues from this failure mode. (See Section 5.2 of the [Claude Fable 5 & Claude Mythos 5 System Card](http://anthropic.com/claude-mythos-5-system-card) for additional information.)
2. This kind of behavior would likely be apparent to an authorized user paying even moderate attention to the actions of their agent; we expect that we would learn of and promptly respond to this if even a few authorized users noticed such behavior and informed us of it.
3. As described in [Section 4.2.3](#423-timescale-and-scope-of-uplift), we think nontrivial risk from this threat model requires repeated, sustained access to a large number of harmful model outputs over the course of weeks or months; this would require such an attack to successfully prompt inject models regularly over an extended period of time without attracting enough notice that this rose to our attention. It seems very difficult for an attacker to do this.
4. Given the high commercial demand for our models, there is already a strong financial incentive for an external actor to implement such a prompt injection pipeline in order to obtain free usage of our models for ordinary non-CB use cases. Doing so would be much easier than for harmful CB usage, since the external actor could prompt inject a much greater fraction of our traffic. To our knowledge, no significant pipeline of this sort has been successful (due to the above challenges), which is additional evidence that the real-world barriers to implementing such a pipeline are prohibitive.

#### 4.5.6 Threat intelligence

We contract with threat intelligence vendors to monitor and scrape the deep and dark web for: (i) publicly available universal jailbreaks of concern (i.e., relevant to chemical and biological weapons); (ii) black markets for model jailbreaks; (iii) reports of API key leaks, and in particular, markets for API key leaks from organizations with exemptions.

We have found a number of leaked API keys but none related to organizations with exemptions from our biological classifiers; we are aware of one API key leak related to human feedback vendors which had biological classifiers disabled, as discussed below in [Section 4.5.8.2.1](#45821-unauthorized-mythos-preview-access-on-our-human-feedback-platforms) (and for which we confirmed there was no CB misuse). While there have<!-- p.146 --> been reports of relevant jailbreaks for these classifiers, none found through this pathway have been confirmed as universal jailbreaks.

#### 4.5.7 Model weight security

Weights of models at least as capable as Claude Opus 4 are kept under enhanced security compared to earlier less-capable models. We believe this to be sufficient security that it would be difficult for most attackers—excluding sophisticated insiders and attackers with nation-state backing—to steal model weights.

Security measures that are robust against nation-state-level actors are extremely difficult to implement, and we do not believe any frontier AI developer currently meets this bar; we do not either, though we are investing heavily toward achieving it (e.g. via the projects described in our Frontier Safety Roadmap). We discuss our security posture and mitigations further in [Appendix 6.4](#63-appendix-redacted).

#### 4.5.8 Changes to our risk mitigations since our last Risk Report

As described earlier in [Section 4.5](#45-our-risk-mitigations), we have made a large number of improvements to our risk mitigations for this threat model, including significantly improved blocking biological classifiers, new forms of offline monitoring, and improved security requirements for our human feedback contractors and classifier-exempt organizations. In this subsection, we describe changes which weakened one of our mitigations or represented an unintentional failure of some component of the mitigations described above, along with notes on how we mitigated these failures and our plans for further improvement.

##### 4.5.8.1 Slight relaxations to our model weight storage criteria

As stated above, we keep the weights of our more capable production models under enhanced security, and only permit their storage in compartments for which we enforce the controls described in [Appendix 6.4.2](#642-notable-security-controls) (among others).

For models which have not yet finished training and been directly evaluated for CB risks, we use broad general capabilities measures (e.g. training loss) to determine which model snapshots are appropriate for storing under which compartments, based on comparisons to models that we *have* evaluated as meeting the CB-1 threshold or not. Historically, we defaulted to these secure compartments for any model snapshot below a very conservative threshold of training loss; since our previous Risk Report, we have set a somewhat less conservative loss threshold. We have also permitted some *activations* of more capable models to be stored outside these compartments in certain cases. We don’t consider these<!-- p.147 --> changes to present a meaningful difference in our overall risk posture, as our earlier threshold was highly conservative and we believe the new threshold still corresponds to models that could not easily be converted into a model as capable as Claude Opus 4 or any more capable model in risk-relevant domains, even given nontrivial amounts of additional fine-tuning.

##### 4.5.8.2 Incidents related to our classifiers and access controls

We focus here on incidents that are relevant to our assessment of the efficacy or coverage of our classifier safeguards or access control policies. We describe these incidents for several reasons. First, some of them entailed temporary gaps in our safeguards. Understanding the scope and duration of these gaps is necessary for assessing the overall risk our systems posed during the coverage period. Note that we are not aware of any evidence of actual chemical or biological misuse from the incidents described below. Second, even where we found no evidence that harm occurred, the occurrence of these incidents provides some signal on our overall state of preparedness, including how quickly we detect and remediate failures as well as our confidence level that no similar gaps remain undiscovered. Third, we believe transparency on this topic serves the broader safety ecosystem, for example by prompting other AI developers to check their own systems for similar vulnerabilities, and by giving policymakers and the public a more accurate picture of the practical challenges of operating safeguards at scale.

To be clear, some rate of incidents like these is an expected feature of running complex safeguard systems across many models, platforms, and deployment surfaces. As any security or safety professional knows, preventing incidents from ever occurring is an unrealistic ideal; this is why it is important to invest in detection, containment, and remediation processes. Each incident described below has prompted concrete improvements to our safeguards and processes, which we describe alongside it, and we expect this cycle of detection, prevention, and refinement to continue.

We have omitted from the list below any incidents already described elsewhere in this report, and have included a list of minor incidents which posed no-to-low risk of actual harm in [Appendix 6.5](#65-list-of-minor-incidents-related-to-our-cb-risk-mitigations).

###### 4.5.8.2.1 Unauthorized Mythos Preview access on our human feedback platforms

We describe this incident separately from those in Appendix 6.5 because it involved deliberate unauthorized access by external parties, rather than solely internal errors in our own systems, and the model accessed was among our most capable and was not running with blocking biological classifiers at the time (see [Section 4.5.8.2.2](#45822-all-human-feedback-vendor-traffic-run-without-blocking-biological-classifiers)).

<!-- p.148 -->

In April 2026, in response to an external report, we confirmed that a small number of contractors at data-labeling vendors leveraged their existing access to exploit a flaw in one of our data collection platforms to obtain an API key that let them interact with models, including Mythos Preview, outside the scope of their assigned tasks. The access path had been usable for a period of several weeks, including roughly two weeks during which Mythos Preview was accessible. We contained the activity within 90 minutes of learning of it by taking affected systems offline and disabling vendor credentials. The vulnerable access vector was closed the day we received the report.

Despite the features that make this incident notable, we assess the risk it posed to have been low. The only unauthorized access was to unsafeguarded model conversations; our investigation found that no model weights were accessed, no customer data was exposed, and Anthropic’s networks and core systems were not breached. The access occurred through the third-party vendor environment used for model development work, not through our production API. Further, we subsequently reviewed all traffic associated with the affected API key and do not consider the traffic from this incident to have resulted in any significant risks from our CB threat models.

Since this incident, we have introduced new controls and strengthened existing ones to mitigate the risk of similar unauthorized access, as described in [Section 4.5.5.3.3](#45533-pre-deployment-access-to-unreleased-models). We have now restored vendor access to publicly available models and our lower-risk unreleased models.

###### 4.5.8.2.2 All human feedback vendor traffic run without blocking biological classifiers

Since our last Risk Report, we discovered that our bio classifiers were not running for a substantial amount of time on our human feedback vendor traffic. We have fully remediated the issue, conducted a review to analyze potential impacts, and have found no evidence of concerning CB misuse stemming from this issue. The discovery of this gap, however, leads us to believe that there is an increased likelihood of other, similar issues unknown to us.

From May 2025 (our first deployment of models with CB safeguards) until April 2026, all traffic through our systems for collecting human feedback data from contractors evaluating our models ran without blocking biological classifiers. This covered a pool of roughly 50,000 people, who were vetted only by our vendors (many of which did not have screening processes capable of stopping even CB-1 threat actors, prior to our strengthened requirements described above), and totaled around 133M exchanges. The vast majority of this pool had general access to open-ended conversation with these models (rather than limited interfaces like rating a fixed set of provided completions).

<!-- p.149 -->

This traffic was controlled by a flag meant only for internal use, which disabled not only the blocking behavior of the classifiers but also the logging of their flags; as such, traffic that would otherwise have been flagged was not recorded or propagated to any review mechanisms.

We retained transcripts for almost all of this traffic, other than some conversations on one of our platforms (a platform representing around 1% of this traffic) in which the user did not click “submit” on the conversation.

We performed a review of this traffic in which we ran a prompted classifier model (Claude Sonnet 5) over all human turns sent during the affected time period to flag for harmful biological use. Claude Sonnet 5 was prompted to assess if each human turn contained harmful information in line with a constitution for CB-1 biological harm.[^74] It flagged a very small fraction of these queries (1197 transcripts) as “high” for biological harm. The majority of these flags (757) were generated from internal Anthropic teams using the same infrastructure as our external vendors, and all but 62 of the remainder came from exercises where we asked red-teamers to deliberately stress-test our systems.[^75] We conducted a manual review of all 62 transcripts containing a flagged non-red-teaming query, and a random subset of 30 of the external red-teaming transcripts, and did not observe clearly concerning CB misuse which could have provided meaningful uplift to a threat actor (though we identified a handful of potentially dual-use conversations, or red-teaming interactions at a fairly academic level). The longest external transcript with any flagged queries was 240k tokens long, and the 75th percentile length was 2102 tokens.[^76]

Based on this review, we think it is very unlikely that this vulnerability was used in a way that led to a meaningful increase in CB risk, because 1) any threat actor trying to construct a bioweapon using this access could not have sent more than a few dozen detailed high-harm queries without our human review being very likely to examine at least one of the resulting conversations, 2) the vast majority of these conversations were quite short, and 3) the considerations discussed in [Section 4.2.3](#423-timescale-and-scope-of-uplift) around the necessary extent of access<!-- p.150 --> to provide meaningful uplift mean that such small amounts of traffic would be of limited use in providing significant end-to-end assistance at bioweapon development.

This vulnerability was live when our previous Risk Report was published; that report did not consider our human feedback platforms as a risk surface or make claims one way or another about their controls.

As with the previous incident, the only unintended access was to unsafeguarded model conversations. No Anthropic customer data, internal systems, or model weights were accessed or exposed.

We corrected this issue shortly after learning of it in April 2026, and now run with biological classifiers enabled on the vast majority of our vendor traffic, with exceptions granted only for vendors with robust controls where merited by a specific project (as described in [Section 4.5.5.3.3](#45533-pre-deployment-access-to-unreleased-models)).

### 4.6 Overall assessment of risk

#### 4.6.1 Risks from the CB-1 threat model

We currently believe that the risk of catastrophic harm in this category from our AI models is **low but not negligible.** Based on the new information we learned regarding the vulnerability discussed in [Section 4.5.8.2.2](#45822-all-human-feedback-vendor-traffic-run-without-blocking-biological-classifiers), we now also assess the risk posed by our models in February 2026 as low, rather than the “very low” description we gave at the time in our previous risk report.

The above statement also works as a description of the level of risk our systems impose over and above the risks posed by other AI developers’ systems (that is, a description of the “marginal” risk of our systems). We believe it also holds for the level of risk that would be imposed industry-wide, if all AI developers had models and practices similar to ours (that is, a description of the “absolute” risk across the industry). This distinction is further discussed in our Responsible Scaling Policy.

Our argument is essentially the same as the one from Section 4.6 of our previous Risk Report. A brief summary with updates on things that have changed:

1. As before, we believe that our security measures offer strong protection against **theft of model weights** from low-resource actors, as described in [Section 4.5.7](#457-model-weight-security) and [Appendix 6.4](#63-appendix-redacted).
2. <!-- p.151 -->We believe that finding **highly effective, universal jailbreaks** for our classifiers would be challenging for the threat actors of concern for this threat model (individuals or groups with relatively modest resources). As detailed above, we have aimed to find jailbreaks using a variety of methods including a bug bounty; highly effective, universal jailbreaks that we believe can be realistically executed by such actors remain rare and (as far as we can tell) nonpublic; and most of what we’ve found has been remediated, especially on higher-capability models. The boundary point jailbreaking (BPJ) attack is publicly characterized, but we believe it would be very challenging to implement (and even more challenging to implement without detection) for threat actors of concern.
3. We believe that other approaches to **jailbreaks** would be very challenging as well, for a threat actor seeking persistent help on a variety of topics (we have some further discussion of this in Section 4.6 of our previous Risk Report).
4. We believe that subverting our **access controls for exemptions**—either by breaching an authorized user (which would require gaining persistent access despite our move toward workload identity federation) or becoming an authorized user (despite our relatively limited exemptions and manual vetting process)—would be difficult for threat actors of concern. However, this is the point we are least confident in, given the existence of a substantial gap in this area (discussed above in [Section 4.5.8.2.2](#45822-all-human-feedback-vendor-traffic-run-without-blocking-biological-classifiers)) that we have since remediated.

#### 4.6.2 Risks from the CB-2 threat model

We currently believe that the contribution to catastrophic risk in this category from our AI models is **low, with high uncertainty.**

We think it is plausible—though far from assured—that models as capable as Claude Opus 4.6 and above can provide substantial operational uplift with bioweapons development to threat actors that already have such capabilities, such as well-resourced state programs, though we estimate that such uplift potential is significantly lower than that of Mythos 5. (Note that as of the coverage date, multiple different AI developers have trained and deployed models at or above the capability level of Opus 4.6.)

This view is a slight update on our prior risk assessment for Opus 4.6, published in our February Risk Report, in which we assessed that any uplift to well-resourced and technically sophisticated threat actors was likely insubstantial. Since then, we have substantially improved our red-teaming practices, and developed new capability evaluations that are more informative of uplift for this threat model. Though we still think that the capability gaps identified in our capability assessments prior to the publication of the February Risk Report are real, we now also know that they can be substantially<!-- p.152 --> ameliorated by better expert steering and elicitation. This steering makes Opus 4.6 and later models slightly greater force multipliers for existing expertise than we had estimated earlier.

And while we believe that the safeguard measures detailed earlier in this section would substantially increase the difficulty of such threat actors’ using our models for this purpose, we also believe it’s highly plausible that a concerted effort by a well-resourced actor (e.g. state-sponsored programs) could result in theft of our model weights, breach of our access controls, or development of highly effective, universal jailbreaks. We believe these vulnerabilities are not unique to Anthropic, but shared by all frontier developers. (We do not currently assess that the risk of such access is higher for our models than for other models currently generally available on the market.) We believe that our more capable models would be harder to use in this way, due to their stronger safeguards, and that using Mythos-class models in this way would be particularly challenging.

When considering the full picture—uncertainty about how much uplift our models can provide in addition to the low baseline likelihood of this risk—we believe risks are low, but also recognize that this is a judgment call.

We have chosen to implement especially strong protections for our Mythos-class models not due to thinking they have crossed a bright-line capabilities threshold, but because—in our uncertainty—we think a policy of especially strong protections for especially strong models is broadly sensible.

Our assessment of low risk above is a description of the absolute risk we believe Anthropic’s actions impose on the world, relative to a world without powerful AI models. We also consider marginal risk to be relevant here.[^77] We believe our Mythos-class models are currently the world’s most capable models. By contrast, we believe that our other models are not substantially more capable than a variety of other AI models that can be accessed without safeguards as robust as those we have implemented. As such, we believe that our sub-Mythos-class models add limited risk to the ecosystem, on a marginal basis.

<!-- p.153 -->

When considering marginal risk, we seek to address the question of what the ideal ecosystem-wide policy would look like and what we are doing to advocate for that policy. On this topic:

- We believe that an ideal ecosystem might require models across the industry with capabilities comparable to those of Claude Opus 4.6 and above to be safeguarded similarly to how we are safeguarding our Mythos-class models—in particular, to be available for research biology use only within trusted access programs.
- We are not confident that this policy would be the correct one. AI systems like these have the potential to significantly accelerate beneficial life sciences work, as well as to create value in other ways. Restricting their use for research biology would add friction to these uses and reduce the benefits of these models. It would be a highly conservative, risk-prioritizing policy.
- We do not believe the ideal ecosystem would require a pause on developing models like these until they could be kept under even stronger model weight security. This also is not an obvious call—one could argue that it should require this. However, our guess is that these models ultimately offer more benefit to the world than risk, if safeguarded as above.

### 4.7 Looking forward

We will continue to work toward better capability evaluations and better threat assessment, and continually reconsider and improve the safeguards we’re using in light of this.

Our most capable models are relatively close to the CB-2 threshold described in our RSP, and we expect that subsequent Anthropic models will cross this threshold in the relatively near future. For models which cross this threshold, our planned mitigations described in our RSP are:

*We will apply protections at least as strong as our ASL-3 protections to an expanded set of potential use cases for AI, covering the most likely vectors for this threat.*

*Additionally, we will identify the most concerning specific threat pathways, create policy recommendations for early detection and response for such threats, and share this content with policymakers.*

We already meet the first of these criteria for all of our models as or more capable than Opus 4, as detailed above in [Section 4.5.2.1](#4521-extension-in-coverage-since-our-prior-risk-report), and we apply protections for an even more expansive set of use cases for Fable 5, as described in [Section 4.5.2.2](#4522-wider-coverage-of-cb-classifiers-for-fable-5).

<!-- p.154 -->

We believe we have also met the second of these criteria as well, although our work in this area is ongoing, and we will provide an update in a future safety artifact (e.g. a future System Card or Risk Report) if and when we develop a model that we determine crosses the CB-2 threshold.

<!-- p.155 -->

### 4.8 Connection to our recommendations for industry-wide safety

Our [recommendations for industry-wide safety](https://cdn.sanity.io/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf) include the following:

<table><tbody>
<tr><th>Capability or usage threshold</th><th>Substantive standards for model developers</th></tr>
<tr><td>Non-novel chemical/biological weapons production. AI systems with the ability to significantly help individuals or groups with basic technical backgrounds (e.g., undergraduate STEM degrees) create/obtain and deploy chemical and/or biological weapons with serious potential for catastrophic damages.</td><td>A frontier developer should make a strong argument that individual users and relatively small teams will not become significantly more likely to cause catastrophic harm via their usage of product surfaces or via theft of model weights. This will likely require: ● Restrictions on model behavior, and/or measures for quickly detecting and acting on Usage Policy violations, accompanied by a strong case that these measures are difficult to reliably, sustainably circumvent via jailbreaking. ● Precautions against opportunistic theft of model weights, such as centralized controls on third-party applications and software updates.</td></tr><!-- p.156 --><tr><td>Novel chemical/biological weapons production. AI systems that can functionally substitute for the scarce human expertise that is currently the primary barrier to novel development of chemical and biological weapons with potential for catastrophic harm.<sup>[^78]</sup> That is, a well-resourced team<sup>[^79]</sup> could, using the model, accomplish the end-to-end agent design and deployment (including, as relevant, agent design, verification and validation, formulation, and dissemination) that would otherwise<sup>[^80]</sup> require recruiting one of a small number<sup>[^81]</sup> of world-leading specialists.</td><td><p>A frontier developer should make a strong argument that threat actors will not become significantly more likely to cause the sort of catastrophic harm discussed in the lefthand column via their usage of product surfaces or via theft of model weights.</p><p>This will likely require similar measures to those from the previous row, but to a higher standard—to the point where even well-resourced and -staffed threat actors would be unlikely to reliably jailbreak models or cause catastrophic harm via unauthorized access to or modification of models (including via stolen or modified model weights). This would likely mean security roughly in line with RAND SL4, but it depends on the capabilities of the strongest and most plausible threat actors that are not bound by a credible governance regime enforcing the recommendations for industry-wide safety outlined here.</p></td></tr>
</tbody></table>

:::caption
**[Table 4.8.A] Summary of our recommendations for industry-wide safety** on our CB threat models.
:::

We believe, in light of the above analysis, that:

- Many of our models possibly meet the left column’s threshold for CB-1 (non-novel weapons)—as [discussed above](#441-notes-on-how-we-weigh-evidence), we currently have high uncertainty about this.
- We currently do meet the right column’s criterion for CB-1: we have, above, made a sufficiently strong case arguing that individual users and relatively small teams will not become significantly more likely to cause catastrophic harm via their usage of product surfaces or via theft of model weights.
- Our models do not meet the left column’s threshold for CB-2 (novel bioweapons). This judgment is significantly more difficult and uncertain than it was in our previous Risk Report, and we have proactively strengthened our safeguards to target this threat model as described in [Section 4.5](#45-our-risk-mitigations). As noted above in [Section 4.6.2](#462-risks-from-the-cb-2-threat-model), there is still a reasonable case to be made that the ideal ecosystem would require greater restrictions, particularly on our recent Opus-class models.

<!-- p.157 -->

As discussed in [Section 4.7](#47-looking-forward), it is our expectation that we will declare near-future models to meet the RSP threshold for CB-2, or at least fail to rule it out. We expect to meet the planned mitigations described in our RSP for the CB-2 threshold at that time, but we do not expect to meet our ambitious industry-wide recommendations (specifically, security that can reliably stop attacks from well-resourced state actors) in time, absent a change in the rapid pace of model capability improvement. As described in our [Frontier Safety Roadmap](https://www.anthropic.com/responsible-scaling-policy/roadmap), we are pursuing “moonshot R&D” projects and a general leveling up across the board of our security to make progress on this gap, and we will update on our security posture in our next Risk Report.
[^62]: Some detail redacted here from the public version of the report.

[^63]: We paid out a bounty for a second universal jailbreak, but determined upon closer inspection of the attack that this submission had gamed the rubric used by our automated bug bounty system and did not correspond to getting meaningful help from the model in answering the target questions.

[^64]: Some content on our numerical estimates of the degree of optimization required redacted here for public safety considerations.

[^65]: Some content redacted here for public safety reasons.

[^66]: Some notes from the redacted discussion of this monitor in 4.5.3.2.1 above have also been redacted from this summary bullet point.

[^67]: Some content redacted here from the public version of the report.

[^68]: Some additional details on ZDR traffic and organization exemptions have been omitted from the public version of this report for privacy and security reasons.

[^69]: Some additional detail on the scope of exemptions in this category has been redacted here for security reasons, but there are far fewer exemptions in this category than for our org-level exemption policy.

[^70]: Some detail on the nature of internal usage of these models is redacted here.

[^71]: Some content redacted here for reasons of public safety.

[^72]: Additional detail on the organizations in question, as well as details on the distribution of access for external safety researchers, have been redacted from the public version of this report for privacy and security reasons.

[^73]: Some commercially sensitive information on the scale of this contractor population has been redacted here.

[^74]: The prompt used here was originally designed for assessing if a multi-turn exchange provided detailed harmful information to a user, but was run on isolated human turns from this traffic; from manual inspection of the reasoning of this prompted grader, we expect that it would have flagged a significant fraction of human turns including or requesting information at the level of detail and specificity that threat actors would require to see significant uplift in the construction of dangerous weapons.

[^75]: Note that we expect it would not have been particularly difficult (prior to April 2026) for threat actors to get hired in a red-teaming role by one of our vendors.

[^76]: A commonly used rule of thumb for readers unfamiliar with tokenization is that 1 token is roughly equal to 1 word.

[^77]: Our RSP discusses the possibility of a Risk Report that justifies a decision to move forward on the basis of a marginal risk analysis. We do not consider our overall risk-benefit determination in Section 5.4 to depend on this marginal risk analysis, but we elaborate on these considerations below because they inform our decisionmaking around safeguards for some of our models.

[^78]: In particular, weapons with the potential to cause events with consequences comparable to or worse than those of COVID-19.

[^79]: For example, a program with millions of dollars available and support from recent PhDs from top-tier international programs. We are focused on the sorts of teams that would be realistic for real-world threat actors.

[^80]: E.g., in a world with access only to the best AI models as of 2023.

[^81]: E.g., hundreds.

