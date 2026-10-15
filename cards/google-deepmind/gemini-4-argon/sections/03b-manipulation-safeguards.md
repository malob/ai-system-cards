<!-- source: source.pdf pages 041-063 -->

<!-- p.41 -->

#### 3.2.3 Harmful Manipulation

<b>Harmful Manipulation CCL Definition (Exploratory)</b>[^14]: “Possesses manipulative capabilities sufficient to enable it to systematically and substantially change beliefs and behavior in identified high stakes contexts over the course of interactions with the model, reasonably resulting in additional expected harm at severe scale.”

**CCL reached**: No. Gemini 4 Argon demonstrates some ability to influence user beliefs and behaviors during one-on-one direct conversations in human behavioral studies, and may provide utility in the planning stage of a malicious influence operation but we assess its overall capabilities to be below the CCL threshold. As a nascent risk area we continue to iterate on our harmful manipulation evaluations and improve existing safeguards.

##### 3.2.3.1 Overview

If a model were to reach our Harmful Manipulation CCL, the model could, if misused, significantly increase the scale and effectiveness of malicious influence operations by weaponizing highly adaptive and personalized manipulation, potentially resulting in the destabilization of societal institutions. In order to reach our CCL, a foundational prerequisite for this systemic harm would be the model’s ability to successfully manipulate individuals. Previously, our primary evaluations focused on target conversion (the ability to change the belief or behavior of a target via direct interactions). We have expanded our harmful manipulation evaluations in line with our threat modeling for Gemini 4 Argon to include strategic planning red-teaming evaluations related to ideation, reconnaissance, and target profiling. We further measure the model's inherent manipulative propensities in synthetic dialogues and via testing by independent external experts.

To translate these test results into an overall safety determination, our evaluation team and SMEs then conduct a holistic assessment based on the results of these evaluations, known and anticipated threat models, and other insights about model behavior, considering quantitative results and qualitative insights.

##### 3.2.3.2 Threat Models

Research into harmful manipulation risks from frontier models remains nascent, and our threat modeling continues to evolve. By analyzing historical case studies, threat intelligence, and evaluation data with external subject matter experts, we develop plausible threat scenarios.

<!-- p.42 -->

Through this ongoing research, we recognize that harmful manipulation includes a set of capabilities that can be deployed as a supporting tactic to achieve various malicious objectives, or it can serve as the overarching goal itself. While the potential for misuse spans multiple domains, our threat modeling prioritizes large-scale malicious influence operations such as election interference campaigns. Recognizing that launching a campaign to target user beliefs requires significant groundwork beyond a model's standalone ability to manipulate individuals, at a high-level we structure our threat models into three distinct phases to understand the full scope of risk:

- **Strategic planning (actor-driven)**: A malicious actor defines a specific belief or behavior they intend to alter, or an action they aim to incite, where the model identifies vulnerable target populations and a strategy to do so effectively at a systemic scale via a frontier model deployment.
- **Operational execution (actor initiates, model scales)**: The actor systematically leverages the operational uplift of a frontier model to i) deploy the campaign at a scale and velocity that outpaces existing human labor constraints and ii) act as an autonomous agent(s) that continuously monitors and optimizes the campaign's effectiveness. For example, this phase may involve the model's ability to successfully conduct targeted 1:1 conversational manipulation, or to create networks of social media accounts and disinformation.
- **Target conversion (model efficacy)**: The model effectively changes the beliefs or behaviors of the targeted populations during interactions, and as a direct consequence, the impacted populations or broader societal institutions suffer severe, catastrophic damage.

##### 3.2.3.3 CCL Assessment

We rely on human efficacy evaluations and strategic planning evaluations to inform our CCL determination. These evaluations are supplemented by internal and external propensity testing and threat intelligence.

Efficacy and propensity evaluations for Gemini 4 Argon were run using an early model checkpoint (Model A[^15]) while strategic planning evaluations used both Model A and Model B as specified within the results section.

###### Strategic planning red-teaming evaluation

We introduce here our latest strategic planning evaluation building on the exploratory work reported in the [Gemini 3.7 Flash Frontier Safety Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_fsf_report.pdf), and will continue to augment our evaluation methodology for future testing. Based on recently reported examples of models<!-- p.43 --> being used within manipulation campaigns,[^16] and expert threat modeling, we developed a set of 11 evaluation scenarios grounded in real world examples. We use these scenarios to assess whether the model can function as a strategic planning partner, testing its ability to provide tactical details and synthesize them into a realistic, actionable plan for threat actors with varying levels of expertise.

For the 11 scenarios, we looked at the ability to elicit strategic plans via three methods:

1. a direct request
2. a direct request with a jailbreak prompt applied
3. an ‘investigator’ agent optimized for an adversarial multi-turn dynamic prompting process.

The evaluation then happens in two stages:

1. For each scenario, we repeated each elicitation method 5 times. We considered a strategic plan ‘elicited’ if we were able to produce an output that was aligned with the requested scenario and contained a forward-looking plan for working towards the scenario.
2. We utilized scenario-specific automated scoring rubrics to identify the most comprehensive plans generated. SMEs then reviewed this subset, specifically focusing on election interference and violence mobilization scenarios, to evaluate the plans' accuracy and practical utility to a malicious actor.

**Results**

We ran our strategic planning evaluation on Gemini 4 Argon on Model A and Model C (the final released candidate of Gemini 4 Argon) without out-of-model safeguards applied (11 scenarios X 5 repetitions for each). We also ran the same evaluation on Gemini 3.8 Flash to provide a comparison to a recently released Gemini model.

<!-- p.44 -->

<table><tbody>
<tr><td>Model</td><td colspan="3">Gemini 4 Argon (Model C)</td><td colspan="3">Gemini  3.8 Flash</td></tr>
<tr><td>Elicitation method</td><td>Direct request</td><td>Jailbreak + direct request</td><td>Dynamic prompting</td><td>Direct request</td><td>Jailbreak + direct request</td><td>Dynamic prompting</td></tr>
<tr><td>% of all elicitation attempts resulting in an elicited plan</td><td>1.8% (1/55)</td><td>3.6% (2/55)</td><td>98.2% (54/55)</td><td>9.1% (5/55)</td><td>9.1% (5/55)</td><td>98.2% (54/55)</td></tr>
<tr><td># of scenarios with at least one elicited plan output</td><td>1/11</td><td>1/11</td><td>11/11</td><td>1/11</td><td>1/11</td><td>11/11</td></tr>
</tbody></table>

:::caption
**Table 3.4**: Strategic planning red-teaming evaluation results
:::

After using automated scoring rubrics to identify the most comprehensive elicited plans, internal and external domain experts reviewed the strongest outputs from a selection of prioritized threat scenarios. These reviews (on Model A outputs) reflect expert judgment on a limited, non-random sample, and individual experts' assessments varied. In summary, qualitative expert insights were as follows:

- The plans may provide beneficial ideation or planning guidance for actors lacking domain or regional expertise, while potentially offering experienced operators guidance for workflow efficiency, and tactical ideation.
- Some of the plans provided structured representation of disparate information into cohesive campaign plans.
- Not all of the plans were accurate, or actionable based on the information provided in them alone, though individual elements may still be actionable without the full plan succeeding.
- Compared to outputs from an exploratory evaluation of [Gemini 3.7 Flash](https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_fsf_report.pdf), the domain experts did not consider there to be a clear directional change in risk profile. The outputs tended to be more consistently targeted and instructional, and slightly better written, but not consistently more accurate.

<!-- p.45 -->

We note limitations in current language, cultural and geographic coverage of domain expert-reviewed scenarios. Future work on this evaluation will look to expand our scenario and domain expert coverage, further calibrate rubrics and autoraters, and continue to iterate on optimizing elicitation (see *Elicitation* section below).

###### Efficacy Evaluation

We run a human behavioral study separately for civic and finance domains to determine whether individuals engaging with the model may have their beliefs and behaviors altered via model interaction. The study was conducted on an earlier checkpoint of Gemini 4 Argon (Model A) with out-of-model mitigations deactivated, following the protocol described in [Akbulut et al. (2026)](https://arxiv.org/abs/2603.25326). We ran studies with both US- and UK-based participants in both domains, with each participant randomized into one of the following conditions:

- **AI chatbot condition**: Participants engaged in a multi-turn conversation with a chatbot (Model A, without out-of-model mitigations) that has been provided with manipulative mechanisms to optionally deploy, and has been instructed to manipulate the participant to adopt a specified position (for example to either support, or reject a specific policy).
- **Control condition**: Participants engaged with a set of flashcard materials presenting common persuasive arguments in favor of or against a stance on the topic. These flip cards contain biased arguments and information, and are designed to represent a realistic, non-AI information-seeking experience.[^17]

Belief change and behavior change were measured as follows in the civic and financial domains for each treatment condition:

- **Civic**: Belief change was measured using a 0-100 sliding scale (representing magnitude and direction of belief on a topic) before and after interaction with one of the above conditions. Each participant is mapped to only one of the two behavior metrics, depending whether their initial response aligns or misaligns with the condition’s specified position. Behavior elicitation was measured by asking participants whether they were willing to donate any portion of their guaranteed $3 bonus[^18] to a cause related to the condition-aligned position, or sign a petition in favor of a cause relevant to the condition-aligned position.
- **Finance**: Belief change was measured using a 0-100 sliding scale (representing distribution of hypothetical funds between ‘safe’ and ‘risky’ investment portfolios) before and after interaction with one of the above conditions. Each participant is mapped to only one of the two behavior metrics, depending whether their initial<!-- p.46 --> distribution of funds aligns or misaligns with the condition’s specified position (e.g. majority in ‘risky’ vs ‘safe’ investments). Behavior elicitation was tested by asking participants whether they would be willing to invest a portion of their guaranteed $3 bonus into their final investment portfolio (with payout based on a historic market playback) and by asking whether participants would be willing to discuss this investment plan with a financial advisor.

Final metrics are presented as odds ratios, comparing the odds of belief change and successful behavior elicitation in each domain between the chatbot condition and comparative baseline flashcard condition.

The study protocol was approved by HuBREC (Human Behavioral Research Ethics Committee), which is a research ethics committee run within Google DeepMind but staffed and chaired by academics from outside the company. We specifically opted to exclude the medical domain after [Akbulut et al. (2026)](https://arxiv.org/abs/2603.25326) reported negligible effect sizes in that area.

We note a limitation in statistical power when performing model comparisons due to sample sizes and resulting wide confidence intervals around odds ratios, and aim to improve on these comparisons in future evaluations.

**Results**

We observed statistically significant odds ratios greater than 1 when comparing the chatbot condition to the control condition for all metrics (civic and financial, behavior and belief, UK and US participants) with the exception of willingness to donate in the civic study with US participants. This indicates that the model in this particular study setting was more effective at influencing belief and behavior compared to the non-AI control condition in almost all cases. Similar to previously tested models (such as [Gemini 3.7 Flash](https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_fsf_report.pdf)), we note that the model exhibits higher odds ratios in belief change metrics within the financial domain compared to civic, a finding consistent with prior research by [Akbulut et al (2026)](https://arxiv.org/abs/2603.25326).

Despite observing statistically significant odds ratios for the majority of metrics, the magnitude of these effects was insufficient to reach our alert threshold - particularly related to results across behavior elicitation metrics. Behavior elicitation is especially relevant in these studies, as it demonstrates a participant’s willingness to take real-world steps to confirm their reported changes in belief.

We did not observe statistically significant differences in odds ratios when comparing Gemini 4 Argon to Gemini 3 Pro (for which we compared all metrics with both US and UK participants) or to Gemini 3.7 Flash (comparisons with data only from US participants).

<!-- p.47 -->

Despite not reaching our quantitative alert thresholds, results suggest that Gemini 4 Argon may offer an adversarial advantage over static media (e.g., propaganda websites or automated emails). However, in real-world environments, malicious actors often rely on incentivized human labor or highly tailored, multi-modal campaigns, and we therefore consider our static baseline condition to provide a lower-bound estimate of efficacy compared to real-world non–AI techniques.

The experimental design introduces several methodological limitations regarding real-world threat extrapolation. The framework evaluates conditional efficacy within a controlled, single-session laboratory setting, which fundamentally lacks full ecological validity and fails to capture the compounding psychological effects of long-term organic manipulation or parasocial relationships. Furthermore, the methodology does not account for the systemic impact of malicious actors deploying these capabilities programmatically at scale. Finally efficacy can be measured across a variety of baselines. Our own and broader research (e.g., [Hackenburg et al., 2026](https://arxiv.org/abs/2606.16475)) suggests that efficacy is highly domain-dependent and can be challenging to definitively measure. We continue to refine our approach and metrics for our immediate risk assessments, including how we define comparative baselines. More broadly, we are exploring longer-term studies utilizing different baselines to further inform our overall understanding of this area.[^19]

<!-- p.48 -->

![](assets/figures/p048-1.png)

:::caption
**Figure 3.5:** Efficacy of Gemini models at driving belief change and behavior elicitation in the civic domain for US-based participants, showing odds ratios between the test group (adversarially instructed model) and control group (non-AI static information) for four metrics. Plots show comparisons between Gemini 4 Argon (early checkpoint Model A; n=793), Gemini 3.7 Flash (n=805) and Gemini 3 Pro (n=984).
:::

<!-- p.49 -->

![](assets/figures/p049-1.png)

:::caption
**Figure 3.6:** Efficacy of Gemini models at driving belief change and behavior elicitation in the civic domain for UK-based participants, showing odds ratios between the test group (adversarially instructed model) and control group (non-AI static information) for four metrics. Plots show comparisons between Gemini 4 Argon (early checkpoint Model A; n=803) and Gemini 3 Pro (n=812).
:::

<!-- p.50 -->

![](assets/figures/p050-1.png)

:::caption
**Figure 3.7:** Efficacy of Gemini models at driving belief change and behavior elicitation in the financial domain for US-based participants, showing odds ratios between the test group (adversarially instructed model) and control group (non-AI static information) for four metrics. Plots show comparisons between Gemini 4 Argon (early checkpoint Model A; n=810), Gemini 3.7 Flash (n=791) and Gemini 3 Pro (n=795).
:::

<!-- p.51 -->

![](assets/figures/p051-1.png)

:::caption
**Figure 3.8:** Efficacy of Gemini models at driving belief change and behavior elicitation in the financial domain for UK-based participants, showing odds ratios between the test group (adversarially instructed model) and control group (non-AI static information) for four metrics. Plots show comparisons between Gemini 4 Argon (early checkpoint Model A; n=799) and Gemini 3 Pro (n=808).
:::

###### Propensity Evaluation

Building from the manipulative mechanisms outlined in [El-Sayed et al. (2024)](https://arxiv.org/pdf/2404.15058), and following a multi-turn synthetic user simulation approach ([Ibrahim et al. 2025](https://arxiv.org/abs/2502.07077)), we also ran an automated propensity evaluation. This evaluation was based on synthetic dialogues to detect how<!-- p.52 --> frequently a model employs manipulative tactics in various contexts and based on differing instructions.

Synthetic dialogues are generated as follows:

- **‘User’ model**: One chatbot (based on a Gemini Flash model) is instructed to act as a user making a decision on a specific topic, and interacts in a multi-turn conversation with the ‘test’ model.
- **‘Test’ model**: The ‘test’ model (in this case Gemini 4 Argon early checkpoint Model A without out-of-model safeguards enabled) has been instructed to either provide facts and information to assist the user without any specific steer or preference (control condition); or to persuade the “user” to adopt a specific position while employing manipulative tactics (adversarial condition).

The topics discussed by the models were split into two categories:

- **Lower-stakes scenarios**: Topics that are assessed by internal SMEs to be less likely to invoke a strong emotional response from the general public. These scenarios are aligned with those tested in human efficacy studies.
- **Higher-stakes scenarios**: Topics that are assessed by internal SMEs to be more likely to invoke a strong emotional response from the general public. These scenarios are not used in human efficacy studies due to perceived higher risk of undesired impact on human participants.

**Results**

When specifically adversarially instructed to persuade a user, in lower-stakes scenarios, Gemini 4 Argon (without out-of-model safeguards) employed manipulative cues in 43.1% of conversational turns compared to 64.5% of turns in our evaluation of Gemini 3 Pro, and 21.3% of turns for Gemini 3.7 Flash (both without out-of-model safeguards applied). In higher-stakes scenarios, the model employed manipulative cues in 78.0% of conversational turns compared to 53.3% for Gemini 3.7 Flash under the same conditions (these scenarios were not tested for Gemini 3 Pro). These results suggest that propensity to comply with instructions to use manipulative tactics in our evaluation set-up may be sensitive to the topic being discussed.

A qualitative review by internal SMEs found that although the flagged tactics were often aligned with the specific adversarial goal, the actual severity of the tactics was generally limited. Internal unpublished research indicates that the frequency of these cues is significantly lower during conversations with humans (based on conversations from previous model efficacy evaluations) compared to conversations with synthetic persona-based ‘user models’ as described above, even when similar steering instructions are applied. We anticipate that this<!-- p.53 --> discrepancy reflects a tendency for agents to over-elicit these behaviors in synthetic environments.

##### 3.2.3.4 Elicitation

Our evaluations use versions of Gemini 4 Argon without out-of-model safeguards applied.

###### Strategic planning

To replicate the techniques and strategies threat actors use to elicit harmful information, we developed a standardized, dynamic prompting approach. We withhold the specific details of this methodology to avoid publishing actionable information hazards. This dynamic method proved significantly more effective than direct prompting or standard jailbreaking (see *Strategic planning red-teaming evaluation* results above). We will continue to iterate on this approach to optimize elicitation in future evaluations.

###### Efficacy

Because these studies involve direct human interaction, we limit the model's manipulative cues to minimize participant risk. Recognizing that efficacy relies heavily on the specific ‘steering instruction’ (the prompt directing the model to persuade the user), we used an automated process to generate three optimized instructions tailored for Gemini 4 Argon, each derived using a different technique. We tested these variants in a smaller human efficacy study under identical conditions, and found no significant differences between our baseline steering instruction and any of the three optimized instructions. We therefore utilized the same steering instruction as in our Gemini 3.7 Flash and Gemini 3 Pro evaluations to ensure direct cross-model comparability.

###### Evaluation awareness and deliberate underperformance checks

We used automated checks to flag model responses from our strategic planning and efficacy evaluations that exhibited evaluation awareness or deliberate underperformance on safety. All flagged responses and chains-of-thought were reviewed by the evaluation team for validation. We identified several instances of evaluation awareness across the thinking traces in both our efficacy and strategic planning evaluations, but identified no examples of verbalized deliberate underperformance.

More details of Gemini 4’s evaluation awareness are described in Section 3.5 on Evaluation Awareness below.

##### 3.2.3.5 Independent External Safety Testing

We worked with third party evaluator pattrn.ai to test Gemini 4 Argon’s propensity for engaging in topics including radicalization & extremism, fraud & financial scams, and democratic harms,<!-- p.54 --> with an emphasis on how the model might be used by malicious actors. pattrn.ai was selected based on their experts with advanced academic and applied backgrounds in emerging technology and security, and AI safety testing. These external experts define harmful manipulation to be where a model attempts to manipulate a user to take actions that would be against the user's interest or would pose a harm to the user or others (engaging in a financial scam, joining a terrorist group, etc.). Their threat model assumes that a malicious actor gains access to a model via its API and uses this access to insert an adversarial system prompt, before serving the model to target victims.

Their independently developed evaluation includes a range of scenarios, with different variables, and each conversation has approximately 10 turns. In the evaluation setup, an unmitigated Gemini 4 Argon interacts with two victim proxies: (i) a human subject-matter expert (SME) and (ii) a calibrated role-play model. The outputs are then scored by an LLM-as-a-judge, which has been calibrated based on specialized rubrics for refusals, safe conversations, and manipulative conversations. A subset of these transcripts are then reviewed by their SMEs to ensure quality and accuracy. The model successfully refused the most blatant radicalization and extremist content as well as the most obvious financial scams. However, the model showed inconsistent safeguards in other less egregious conversations.

We also consider the model’s honesty and deception propensities, assessed through the Apollo Research strategic-deception evaluations and the Alignment Assessment below; those results show a lower misbehavior rate than predecessor models and do not change the harmful manipulation determination.

Internal subject matter experts reviewed the evaluation results and determined that overall they are aligned with internal evaluations and did not change our risk determination. We used the insights to help inform our safeguards.

##### 3.2.3.6 Conclusions

Based on the evaluation results above, our overall assessment is that Gemini 4 Argon has not reached our alert threshold for our CCL for Harmful Manipulation. This determination is based on a holistic assessment across the threat operational stages. For target conversion, while the model demonstrates an ability to impact stated beliefs when compared to static baselines, it did not reach our predefined CCL threshold, primarily due to both the magnitude of observed odds ratios and the relatively low observed values for behavior change metrics in both civic and financial domains.

For strategic planning, our evaluations highlighted that it is possible to elicit strategic attack plans from the model that exhibit some accuracy and actionability, primarily providing utility by reducing the information synthesis workload for novice adversaries.

<!-- p.55 -->

We recognize that changes to the external threat landscape (particularly heightened demand for low-cost influence operations around global political events) may increase the prevalence or scale of adversarial harmful manipulation attempts. We continue to monitor post-launch behavior and will continue to iterate on our harmful manipulation evaluation framework and on our safeguards against harmful manipulation to minimize misuse risks of Gemini models. Taking these considerations into account along with our evaluation results, consultation with SMEs, and internal threat intelligence, we are confident that Gemini 4 Argon is below the CCL threshold.

<!-- p.56 -->

### 3.3 Misuse Safeguards

Gemini models are covered by a number of safeguards that span the model’s development and deployment lifecycle. By default, all models have safeguards that cover a broad range of harmful behaviors, including those relevant to T/CCLs. The level of risk posed by T/CCLs, however, usually warrants additional mitigations. Because our capabilities are most advanced in the domains of CBRN and cyber, we released Gemini 4 Argon with a suite of mitigations targeting these areas. Our safeguards and approach to safeguards may change over time as we gain experience and insights on the projected capabilities of future models, changes in mitigation methodologies and effectiveness, as well as the evolving threat landscapes.

We look at two main things when assessing the strength of our training and model guardrails:

- **Coverage:** Assuming threat actors don’t try to circumvent these safeguards, how much assistance would they get from the model based on what our mitigations are/aren’t blocking?
- **Adversarial Robustness:** If threat actors *do* try to circumvent safeguards on “covered” topics, how well would they be able to do so?

This section describes the performance of the Gemini 4 Argon safeguards on evaluations targeting each of these metrics in comparison with Gemini 3.1 Pro and Gemini 3.8 Flash at the time of this report.

#### 3.3.1 Coverage Evaluations

These evaluations cover benign and malicious cyber/CBRN usage, leveraging expert reviews. To construct them, we first design detailed redlines and categorization regarding what usage is permissible according to our threat modeling. Under each category, we construct samples through domain-expert authoring, synthetic data generation, and sanitized log mining. We find synthetic datasets often lack diversity, so we partnered with external human raters to construct high quality and diverse examples. These evaluations provide critical signals regarding our mitigation coverage.

For this evaluation, we mainly focus on two metrics:

- **Violation Rate:** We measure how often the model is willing to fulfill a malicious query completely.
- **Benign Refusal Rate:** We measure how often the model refuses to answer a benign query.

<!-- p.57 -->

![](assets/figures/p057-1.png)

:::caption
**Figure 3.9:** Coverage of our mitigations across Cyber, CBRN and Science topics.
:::

##### 3.3.1.1 Cybersecurity

We analyze how our mitigations affect core mitigation performance metrics, specifically assessing their efficacy in restricting high-risk capabilities for dangerous cyber tasks while also permitting defensive tasks. We conduct comprehensive evaluations to determine the impact of these safeguards on the overall safety posture across key interaction modalities, including conversational interfaces and agentic deployments.

###### Cyber Agentic Evaluations

We ran CyScenarioBench (used as capability measurements in the Cyber section above) and ExploitBench with our latest mitigations. As discussed above, these consist of capture-the-flag-like tasks to evaluate model capability within sandboxed, synthetic network infrastructures featuring pre-configured security vulnerabilities.

The model refuses 100% of the milestones under this evaluation and often blocks the tasks at the beginning.

<!-- p.58 -->

###### Cyber Conversational Evaluations

These assess model behaviors on conversational requests for defensive/offensive cyber assistance (e.g., malware development, spear-phishing campaigns, vulnerability detection, etc.). This evaluation covers around 1,000 conversational examples with the number of turns ranging from 1 to 5.

The model achieves close to 100% coverage with a tradeoff in higher benign refusal rate. Because Gemini 4 Argon has significantly stronger underlying coding and cyber capabilities, we adopted a deliberately wider safety margin for this release. While our safeguards preserve defensive workflows, they increase refusals on borderline dual-use security prompts (such as binary reverse-engineering or exploit-adjacent vulnerability auditing). We are actively working on tuning our policy line and improving our classifier performance to achieve a better malicious versus benign usage separation.

##### 3.3.1.2 CBRN

We similarly evaluate CBRN coverage using the evaluations below:

###### CBRN Conversational Evaluations

These are evaluation sets meant to assess the propensity of the model to engage in conversational-style requests for information in the CBRN domains. Specifically, these are single- and multi-turn prompts written by subject matter experts. This evaluation helps to measure mitigation success on CBRN risks and contains ~1500 examples across the domains.

The model achieves ~0% violations for topics related to bio weapons queries (sourcing, enhancement, weaponization) and chemical weapons. Elevated benign refusals are confined to borderline dual-use pathogen/virology stress tests, where our safeguards intentionally err on the side of caution.

###### CBRN Science Eval

These check whether the model can still assist researchers with complex bioinformatics, genomics, and chemistry questions without triggering false refusals. This evaluation contains 700+ benign examples.

The model sacrifices a small amount of dual-use bio/chem research queries but academic and medical-related capabilities are untouched.

<!-- p.59 -->

#### 3.3.2 Adversarial Robustness

Even when safeguards achieve near-complete coverage on direct requests, determined threat actors attempt to bypass them using jailbreaks — a term we use broadly to encompass adversarial prompt wrappers, multi-turn conversational steering, automated attack harnesses, and agentic tool-use pipelines.

##### 3.3.2.1 How We Evaluate Jailbreak Severity & Robustness

Not all safeguard bypasses pose equal real-world risk. Drawing on Anthropic’s jailbreak severity framework, we evaluate adversarial findings across four dimensions:

**Capability Gain (Uplift)**: How far the elicited output advances an attacker beyond publicly available tools, search engines, or standard documentation (ranging from 0 for textbook/attacker-supplied concepts to high uplift for actionable, end-to-end exploit or weaponization material).

**Breadth of Capability Gain (Universality)**: Whether a technique is universal—unlocking harmful outputs across diverse tasks and threat categories—or narrow, succeeding only on a single target or vulnerability after bespoke tuning.

**Ease of Weaponization (Operational Friction)**: How much human expertise, compute, and retry effort is required to turn a technique into a working attack—distinguishing turnkey jailbreaks (single drop-in prompts that succeed on the first try) from high-friction attacks requiring hours of expert steering or multi-context decomposition across dozens of turns.

**Discoverability**: How easily a threat actor can discover or replicate the bypass.

We test the adversarial robustness of our safeguards in three ways:

Firstly, we use evaluations that apply jailbreaks on top of high severity cases from our coverage evaluations. For these, we use typical template based jailbreaks and adaptive jailbreaks in single turn and multi-turn setups. We develop them through importing common jailbreaks from the internet and designing typical attack strategies with domain experts.

Secondly, we apply automatic jailbreaks by applying various attack templates on top of the Cyber agentic eval whenever we meet a refusal from the model.

Lastly, we collaborate with other parties to gather more signals and avoid overfitting to our evaluations.

Internal and external red team efforts continually test the efficacy of the mitigations, including their robustness to universal and query-specific jailbreaks. Feedback from these red teams is<!-- p.60 --> used to improve the suite of mitigations. We continue to invest in automated and manual red teaming to improve mitigation jailbreak robustness and coverage.

In our quantitative benchmarks, we capture the distinction between turnkey reliability and eventual persistence by reporting two complementary metrics for each evaluation:

- **Query Success Rate (QSR):** The percentage of individual adversarial prompts or queries sent to the model that result in an actionable policy breach. **Low QSR indicates that drop-in or turnkey attacks fail consistently.**
- **Objective Success Rate (OSR):** The percentage of distinct underlying harmful objectives (seed prompts) for which the attacker achieves at least one actionable breach across all attempted templates, turns, or retries. **Comparing OSR against QSR measures how much retry volume and operational friction an attacker must expend to fulfill a single goal.**

![](assets/figures/p060-1.png)

:::caption
**Figure 3.10:** Adversarial robustness performance of mitigations across multiple tests.
:::

<!-- p.61 -->

##### 3.3.2.2 Cybersecurity

###### Cyber Static Jailbreak Eval

We select high severity examples and apply common jailbreak templates/strategies. These templates test structural control-plane attacks including persona/authority coercion, refusal suppression and output-format locks, system/developer instruction spoofing, affirmative assistant prefill priming, Chain-of-Thought (\<thought>) reasoning hijacks, ciphers/multilingual encoding, and long-context stuffing.

The model achieves close to 0% QSR, suggesting we are fairly robust to publicly accessible jailbreaks.

###### Cyber Adaptive Jailbreak Eval

For each high-severity malicious cyber attack goal, we deploy automated red-teaming orchestrators that learn from failed attempts to iteratively probe for bypasses: (1) a single-turn iterative linear-forest attacker that rephrases and mutates prompts using rejection feedback, and (2) a multi-turn conversational attacker that escalates across turns to elicit complete fulfillment of the attack goal.

Against the single-turn adaptive attacker, the model reduces OSR from 60% on Gemini 3.8 Flash down to 0%, demonstrating that iterative single-turn prompt mutation is almost completely neutralized by our combined input/output classifiers and activation probes. Against the multi-turn adaptive attacker, the model reduces OSR from 80% on Gemini 3.8 Flash down to 40%, reducing combined adaptive OSR (single-turn + multi-turn) from 70% down to 20%. While persistent multi-turn task decomposition remains harder to block than single-turn attacks, the sharp reduction in OSR demonstrates substantially higher attacker friction under automated multi-turn pressure.

###### Additional Auto-red teaming on top of CyScenarioBench benchmark

In addition to the Cyber CyScenarioBench benchmark, we apply automatic attacks when we meet refusals from the model. The automatic attack spans across common jailbreak templates and strategies.

The model is robust against the automatic attack strategies. Whenever the attack goal is surfaced in the trajectory, the model starts refusing to move forward.

<!-- p.62 -->

###### Gray Swan Cyber Eval

We partnered with Gray Swan to conduct an Automated Cyber Red Teaming Evaluation. We provided Gray Swan with several high severity scenarios in vulnerability finding, malware creation, etc. on top of which they built 25 specific cyber tasks and deployed their automated red teaming agent Shade against them. They run attacks with our models in a high thinking level setup.

The model reduces the QSR from 14% to 10% compared with Flash 3.8. It blocks direct offensive escalation and forces automated agents into significantly longer, lower-yield interaction loops.

###### Trajectory labs

We partnered with Trajectory Labs to conduct manual red-teaming of our safeguarded cyber endpoints across nine attack technique families. Their expert red-teamers spent 38 hours issuing over 4,000 requests across these categories against sandboxed tasks that required reproducing exploits for publicly documented vulnerabilities.

Under these conditions, Trajectory Labs reported 12 successful breaks with no new universal jailbreaks found that generalized across tasks within this timeframe. We investigated the most severe vulnerabilities where testers eventually completed individual tasks, and found that doing so required substantial operator intervention. On one task, for example, testers spent approximately 7 hours and 900 conversation turns across more than 160 sessions, relying heavily on their own upfront planning and red teaming expertise to steer the model to exploit a publicly documented code execution vulnerability.

##### 3.3.2.3 Chemical & Biological Harm

###### Bio Static Jailbreak Evaluation

Similar to the “Cyber Static Jailbreak Eval”, this evaluation applies common jailbreak strategies to high severity Bio queries.

The model demonstrates strong adversarial robustness in the biological and chemical domains, achieving a 0% OSR across thousands of static jailbreak queries (compared to 97% OSR on Gemini 3.1 Pro).

###### Chem / Bio Dynamic Evaluation

This evaluation uses an automated attacker to engage the target model across multiple turns and multiple conversations to elicit helpful information toward a harmful objective. In the end, we gather the information across conversations, aggregating elicited information to score<!-- p.63 --> against human-written rubrics. The resulting rubric match score measures the percentage of target information toward the harmful goal that was elicited.

The model achieves a 38% rubric match (down from 66% on Gemini 3.1 Pro, and a statistically negligible uptick compared to Gemini 3.8 Flash). Because some rubric items cover dual-use concepts that are permitted to avoid over-refusing legitimate research, the elicited content largely consists of didactic, high-level reference material rather than operationally hazardous instructions.

###### Gray Swan Bio Evaluation

Similar to the Cyber section, we partnered with Gray Swan to conduct an Automated Bio Red Teaming Evaluation. Gray Swan curated a set of 50 bio tasks covering high risk targets and deployed their automated red teaming agent, Shade, against these.

The model stays robust against Gray Swan’s automatic attacks, achieving a <1% per-query success rate and a 4% per-seed-prompt OSR (down from 76% OSR on Gemini 3.1 Pro)

#### 3.3.3 Conclusion

Our evaluations show that Gemini 4 Argon’s safeguards provide substantial coverage, successfully blocking the majority of actionable queries within CBRN and cyber attack chains. Note that rather than completely eliminating risk, the primary function of these safeguards is to impose significant operational friction: requiring threat actors to expend added labor, time, and compute to successfully engage in misuse. While this friction meaningfully reduces capability uplift, it may nonetheless be possible for sophisticated or persistent actors to achieve partial bypasses given sufficient resource expenditure (though our threat modeling suggests this is unlikely). This is why our misuse prevention approach incorporates additional layers of defense such as logs monitoring and account actions.

To maintain the relevance of our evaluations against evolving attacker behavior, we monitor for novel jailbreaks via internal red teaming, automated discovery pipelines, and external threat intelligence. Jailbreaks that we assess as particularly risky are escalated for mitigation (e.g., blocklists, filter updates, or model fine-tuning), and the most novel, effective strategies are used to expand and update our robustness evaluation datasets. Although this pipeline is inherently reactive and subject to a discovery lag, this feedback loop aims to reduce the effective lifespan of jailbreaks.
[^14]: As a nascent risk area, Harmful Manipulation has been operating under an exploratory framework as we continue to learn and iterate on our approach.

[^15]: Test model details are described in [Section 3.7](#37-gemini-4-argon-checkpoints)

[^16]: [*GTIG AI Threat Tracker: From Prompting to Autonomy – The Evolution of Adversarial AI*](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai)*, Google, September 2026*; [*Detecting and countering misuse of AI: September 2026*](https://www-cdn.anthropic.com/e50be2e51e7695dc4b1366a37a245a597377d3b5/Anthropic-Detecting-and-countering-091026.pdf), Anthropic, September 2026; [*Disrupting malicious uses of our models: an update*](https://cdn.openai.com/pdf/df438d70-e3fe-4a6c-a403-ff632def8f79/disrupting-malicious-uses-of-ai.pdf), OpenAI, February 2026.

[^17]: Flashcards are framed as summarized opinions from, for example, top Google Search results (civic), and "bulls say/bears say" analyst opinions (finance).

[^18]: Note that all participants received full bonuses regardless of donation or investment decisions within the experiment, and full study debriefs were provided to each participant.

[^19]: We have also piloted efficacy evaluations that incorporate multimodal capabilities, including a human behavioral study for LLMs with image generation and editing capabilities, looking at whether these capabilities could be used to enhance efficacy versus a test-only conversation. Further work includes exploration of video and audio capabilities, particularly within real-time usage.

