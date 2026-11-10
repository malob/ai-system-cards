<!-- source: source.pdf pages 048-057 -->

<!-- p.48 -->

## 4. Content safety & preventing agentic misuse

This section describes our approach to identifying and mitigating certain risks arising from the potential misuse of Gemini in ways that could harm individuals, institutions, or society. Misuse can take many forms, depending on the context in which models are deployed. Here, we present evaluation results for two categories: content risks, which are most evident in conversational settings, and agentic risks, which are increasingly relevant to both agentic coding and consumer-use applications. This section does not cover misuse related to Frontier Safety risks (e.g. Cyber and CBRN), which is discussed in [Section 3](#3-frontier-safety).

### 4.1 Prohibited Content

Gemini 4 Carbon is subject to content safety policies that aim to prevent it from being used to generate certain types of content that could be harmful to users, other people, institutions, or broader society. These policies include:

- **Child Safety**: Content related to child sexual abuse material and exploitation.
- **Dangerous Content**: Content that promotes or provides instructions for activities that may cause serious injury or real-world harm.
- **Sexually Explicit Material**: Content that describes sexual acts or body parts in an explicit or graphic manner, non-consensual sex, or abuse.
- **Hate and Harassment**: Content that dehumanizes members of protected groups (hate speech) and content that encourages violence against a specific person or group of people (harassment).
- **Medical Advice and Information**: Content that runs contrary to scientific or medical consensus.

These policies apply across all input and output modalities, including audio, images, and video.

Below we present results of prohibited content evaluations in four of these policy areas - Child Safety, Sexually Explicit Material, Dangerous Content, and Hate and Harassment. Evaluations related to Medical Advice and Information are covered in [Section 5.1](#51-health).

For all prohibited content evaluations, we use “Safe Response Rate” as our primary evaluation metric, where Safe Response Rate measures how often the model successfully avoids generating policy-violating content in response to direct and adversarial requests.

<!-- p.49 -->

#### 4.1.1 Child Safety

We maintain a strict policy for content related to Child Sexual Abuse and Exploitation (CSAE), which includes Child Sexual Abuse Material (CSAM), sexual grooming, sextortion, endangerment and sexualization of minors. We train and evaluate Gemini to ensure it does not generate, facilitate, or assist in the creation of such content, and that it robustly refuses any related requests.

To safeguard training datasets from CSAE, we employ two primary methods:

- Integrating hash-matching and child safety classifiers to remove CSAM and other exploitative or illegal content.
- Using curated training datasets from sources already built or integrated with child safety protections.

We encourage third-party developers to make use of [Google’s child safety toolkit](https://protectingchildren.google/tools-for-partners/), which enables the identification of known instances of CSAM in videos and the classification of potential new instances in both images and videos.

Evaluations are conducted within the limits of the law using dedicated CSAE red-teaming datasets that contain challenging, adversarial, and coded requests designed to probe the model's boundaries. A specialist child safety team with deep subject matter expertise creates these evaluation sets, drawing on multiple intelligence sources to reflect the latest bad actor behavior. This same team grades the model's completions.

We evaluate both text-to-text (T2T) and multimodal (image-to-text and video-to-text) interactions, using single-turn and multi-turn prompts, to ensure comprehensive protection. All evaluations are performed in English and are run with our standard child safety filters applied.

Our Child Safety evaluations found that Carbon, like Argon, is robust to requests for this type of content.

<!-- p.50 -->

![](assets/figures/p050-1.png)

:::caption
**Figure 4.1:** Child safety evaluation results.
:::

In addition to measuring Safe Response Rate, we also evaluate Gemini’s helpfulness when presented with benign queries containing sensitive keywords or on topics adjacent to sensitive material (e.g., educational queries about child abuse prevention or child health). We estimate helpfulness by looking at “over-refusals” - how often the model incorrectly declines to respond to safe, benign, or dual-use queries. Results of these evaluations are covered in [Section 5.6](#56-helpfulness).

#### 4.1.2 Dangerous Content

We evaluate the model's resistance to direct, indirect, and adversarial requests for instructions or actionable blueprints for dangerous actions or illegal activities that could result in severe real-world harm or self-harm.

We developed an internal evaluation set covering four primary dangerous content types:

- **Weapons and Explosives**: Requests for instructions on manufacturing or planning violent attacks using weapons, explosives, or other dangerous materials.
- **Illegal Acts**: Requests for assistance in planning or executing crimes, bypassing safety regulations, or fabricating illegal substances.
- **Physical Violence & Terrorist Propaganda**: Requests for content that encourages activities that may cause injury or real-world harm, or that celebrate real-world terrorist groups or symbols.
- <!-- p.51 -->**Self-Harm and Suicide**: Requests for instructions and methods related to self-harm or suicide. Additional evaluations on this topic are also presented in [Section 5.2 Mental Health](#52-mental-health).

We tested the model using a combination of an evaluation set with single-turn and multi-turn prompts alongside human-led multi-turn red teaming for robustness. We use a policy-aligned autorater (also known as LLM-as-a-judge or model-based grader) to label model outputs as “safe” or “not safe” to determine the Dangerous Content Safe Response Rate (%).

Gemini 4 Carbon demonstrates a slight improvement over Argon on Dangerous Content Safety and performs similarly to 3.8 Flash.

![](assets/figures/p051-1.png)

:::caption
**Figure 4.2:** Single-turn dangerous content safety evaluation results.
:::

<!-- p.52 -->

![](assets/figures/p052-1.png)

:::caption
**Figure 4.3:** Multi-turn dangerous content safety evaluation results.
:::

For benign queries on topics that could pose dangerous content risks, we also evaluate Gemini’s helpfulness by estimating the model’s “over-refusal” rate - how often the model incorrectly declines to respond. These evaluation results can be found in [Section 5.6.1.](#561-over-refusals)

For queries that Gemini cannot respond to in a non-violative way, we want Gemini to provide a concise, direct rationale for its refusal without lecturing, moralizing, or speculating about the user's intent. We measure the “tone” of these refusals to evaluate whether model responses are free from patronizing language, judgment, or unsolicited lecturing. The results of these evaluations can be found in [Section 5.6.2.](#562-tone)

#### 4.1.3 Sexually Explicit Material

Gemini’s safety policy prohibits the generation of sexually explicit content, including graphic descriptions of sexual acts or pornography. We evaluate the model's adherence to this policy, which includes exceptions to permit content that is educational or artistic.

To benchmark policy adherence, we evaluate the model with single-turn and multi-turn prompts spanning diverse sexual themes. This includes both direct requests for sexual content (e.g., requests for erotica or explicit descriptions of sexual activities), adversarial queries (e.g., attempts to jailbreak the model), and benign requests (e.g., medical queries about sexual health, educational queries about biology, or literary analysis).

<!-- p.53 -->

Model outputs are assessed by our policy-aligned safety autoraters to measure Safe Response Rate.

Gemini 4 Carbon improves on the slight regression in Sexually Explicit Content Safety from Argon and saturates our single-turn evaluation.

![](assets/figures/p053-1.png)

:::caption
**Figure 4.4:** Single-turn sexually explicit content safety evaluation results.
:::

![](assets/figures/p053-2.png)

:::caption
**Figure 4.5:** Multi-turn sexually explicit content safety evaluation results.
:::

<!-- p.54 -->

#### 4.1.4 Hate Speech & Harassment

We evaluate the model's resistance to generating hate speech (content that demeans, dehumanizes, or attacks protected demographic groups based on protected identity factors such as race, ethnicity, religion, gender, sexual orientation, disability) and harassment (content that targets individuals with abuse, threats, or bullying).

Evaluations are performed using targeted prompt sets designed to test boundaries and check the model's behavior under adversarial conditions. The prompt set contains three primary categories:

- **Requests for hateful content**: Requests to generate slurs, write derogatory statements about specific groups, or endorse discriminatory ideologies.
- **Requests for harassment**: Requests to generate abuse, threats of violence, or write bullying messages targeting specific individuals.
- **Sensitive/controversial benign prompts**: Queries about historical conflicts, political arguments, or cultural differences that could easily trigger an over-refusal if the model cannot distinguish between debate and hate speech.

We use our policy-aligned safety autorater to rate the outputs and calculate Safe Response Rate.

Gemini 4 Carbon demonstrates improvement in Hate & Harassment Safety, both in single-turn and multi-turn evaluations, over Argon’s strong baseline.

![](assets/figures/p054-1.png)

:::caption
**Figure 4.6:** Single-turn hate speech & harassment safety evaluation results.
:::

<!-- p.55 -->

![](assets/figures/p055-1.png)

:::caption
**Figure 4.7:** Multi-turn hate speech & harassment safety evaluation results.
:::

### 4.2 Agentic Misuse

As models evolve from chatbots into autonomous agents with access to real-world tools, databases, and APIs, the scope and scale of potential misuse is expanding. We measure Gemini’s robustness to misuse when deployed in agentic harnesses.

#### 4.2.1 Agent Harnesses

Gemini is frequently deployed in agentic harnesses, where it can execute code, call external APIs, browse the web, manage files, and use many other tools. We developed a safety evaluation that places Gemini in agentic scenarios mirroring these deployments and measures whether it carries out harmful tasks when users ask it to, across harm areas outside the scope of Frontier Safety (see Section 3). The evaluation tests the model alone, without out-of-model safeguards; in deployment, additional safeguards may be applied where appropriate to help protect against this kind of misuse.

We measure three categories of risk:

- **Prohibited actions**: Direct and adversarial user requests to perform illegal activities, such as purchasing illegal goods or services, or accessing platforms containing illegally obtained information.
- **Physical harm**: Tool-use sequences that could lead to physical injury, e.g. controlling industrial equipment.
- <!-- p.56 -->**Scaled abuse**: Multi-step workflows designed to automate large-scale abuse, such as fraud, scams, mass account creation, or ticket scalping.

The agent safety evaluation set comprises both malicious and benign requests. It includes scenarios where the prompt itself is explicit about the intended harm as well as scenarios where the prompt disguises the harmful intent and the agent only becomes aware of the potential harm when trying to fulfill the user’s request.

Testing is conducted within a secure, sandboxed environment using Antigravity, Google’s agentic software development and execution platform, equipped with a basic computer-use toolset and select workspace tools.

The benchmark evaluates agent performance across two core metrics:

- **Safe Action Rate:** The rate at which the agent successfully identifies and avoids executing malicious user requests.
- **Helpfulness Score**: The rate at which the agent avoids over-refusals, ensuring it does not decline benign user requests.

Gemini 4 Carbon achieves a higher safe action rate than both Gemini 4 Argon and Gemini 3.8 Flash. On helpfulness, Gemini 4 Carbon performs comparably to both Gemini 4 Argon and Gemini 3.8 Flash.

![](assets/figures/p056-1.png)

:::caption
**Figure 4.8:** Agent harnesses safe action and helpfulness evaluation results.
:::

<!-- p.57 -->

### 4.3 Model Distillation

Unauthorized distillation of Gemini violates our terms of service, including the [Google Cloud Platform Terms of Service](https://cloud.google.com/terms/service-terms), the [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms), and the [Google Terms of Service](https://policies.google.com/terms). It also poses indirect safety risks, as distilled capabilities can be deployed without appropriate safeguards. In this report, we focus on more direct safety and security concerns for our users, and only summarize our anti-distillation stack at a high level.

To address this threat, we have substantially expanded our distillation detection stack, incorporating both real-time defenses and offline classifiers and agents. When distillation is detected, we may apply real-time mitigations alongside project and account-level enforcements, as appropriate. Our detection and defense stack is capable of detecting distillation attacks that span many accounts, and Gemini 4 Carbon also adds real-time defenses for distillation campaigns specifically targeting Gemini's cyber capabilities.

Additionally, we have addressed [avenues](https://arxiv.org/pdf/2608.09867) related to unauthorized extraction of reasoning traces associated with thought signatures produced by stronger models. In addition to mitigating cross-model thought extraction, we are gradually rolling out additional changes to mitigate unauthorized same-model thought extraction as well.
