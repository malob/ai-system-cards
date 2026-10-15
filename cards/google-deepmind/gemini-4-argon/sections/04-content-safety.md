<!-- source: source.pdf pages 163-174 -->

<!-- p.163 -->

## 4. Preventing content safety & agentic misuse

This section describes our approach to identifying and mitigating certain risks arising from the potential misuse of Gemini in ways that could harm individuals, institutions, or society. Misuse can take many forms, depending on the context in which models are deployed. Here, we present evaluation results for two categories: content risks, which are most evident in conversational settings, and agentic risks, which are increasingly relevant to both agentic coding and consumer-use applications. This section does not cover misuse related to Frontier Safety risks (e.g. Cyber and CBRN), which is discussed in [Section 3](#3-frontier-safety).

Gemini 4 shows broad improvements over previous models in prohibited content evaluations. In agent harnesses, the model is more resilient to misuse, refusing malicious tool-use requests at higher rates than Gemini 3.1 Pro, and also shows stronger robustness against static and dynamic jailbreak attacks.

### 4.1 Prohibited Content

Gemini 4 Argon is subject to content safety policies that aim to prevent it from being used to generate certain types of content that could be harmful to users, other people, institutions, or broader society. These policies include:

- **Child Safety**: Content related to child sexual abuse material and exploitation.
- **Dangerous Content**: Content that promotes or provides instructions for activities that may cause serious injury or real-world harm.
- **Sexually Explicit Material:** Content that describes sexual acts or body parts in an explicit or graphic manner, non-consensual sex, or abuse.
- **Hate and Harassment**: Content that dehumanizes members of protected groups (hate speech) and content that encourages violence against a specific person or group of people (harassment).
- **Medical Advice and Information**: Content that runs contrary to scientific or medical consensus.

These policies apply across all input and output modalities, including audio, images, and video.

<!-- p.164 -->

Below we present results of prohibited content evaluations in four of these policy areas - Child Safety, Sexually Explicit Material, Dangerous Content, and Hate and Harassment. Evaluations related to Medical Advice and information are covered in [Section 5.1](#51-health).

For all prohibited content evaluations, we use “Safe Response Rate” as our primary evaluation metric, where Safe Response Rate measures how often the model successfully avoids generating policy-violating content in response to direct and adversarial requests.

#### 4.1.1 Child Safety

We maintain a strict policy for content related to Child Sexual Abuse and Exploitation (CSAE), which includes Child Sexual Abuse Material (CSAM), sexual grooming, sextortion, endangerment and sexualization of minors. We train and evaluate Gemini to ensure it does not generate, facilitate, or assist in the creation of such content, and that it robustly refuses any related requests.

To safeguard training datasets from CSAE, we employ two primary methods:

- Integrating hash-matching and child safety classifiers to remove CSAM and other exploitative or illegal content.
- Using curated training datasets from sources already built or integrated with child safety protections.

We encourage third-party developers to make use of [Google’s child safety toolkit](https://protectingchildren.google/tools-for-partners/), which enables the identification of known instances of CSAM in videos and the classification of potential new instances in both images and videos.

Evaluations are conducted within the limits of the law using dedicated CSAE red-teaming datasets that contain challenging, adversarial, and coded requests designed to probe the model's boundaries. A specialist child safety team with deep subject matter expertise creates these evaluation sets, drawing on multiple intelligence sources to reflect the latest bad actor behavior. This same team grades the model's completions.

We evaluate both text-to-text (T2T) and multimodal (image-to-text and video-to-text) interactions, using single-turn and multi-turn prompts, to ensure comprehensive protection. All evaluations are performed in English.

Our Child Safety evaluations found that Gemini 4 Argon is robust to requests for this type of content, and improved slightly relative to Gemini 3.1 Pro.

<!-- p.165 -->

![](assets/figures/p165-1.png)

:::caption
**Figure 4.1:** Child safety evaluation results
:::

In addition to measuring Safe Response Rate, we also evaluate Gemini’s helpfulness when presented with benign queries containing sensitive keywords or on topics adjacent to sensitive material (e.g., educational queries about child abuse prevention or child health). We estimate helpfulness by looking at “over-refusals” - how often the model incorrectly declines to respond to safe, benign, or dual-use queries. Results of these evaluations are covered in [Section 5.6](#56-helpfulness).

#### 4.1.2 Dangerous Content

We evaluate the model's resistance to direct, indirect, and adversarial requests for instructions or actionable blueprints for dangerous actions or illegal activities that could result in severe real-world harm or self-harm.

We developed an internal evaluation set covering four primary dangerous content types:

- **Weapons and Explosives**: Requests for instructions on manufacturing or planning violent attacks using weapons, explosives, or other dangerous materials.
- **Illegal Acts**: Requests for assistance in planning or executing crimes, bypassing safety regulations, or fabricating illegal substances.
- **Physical Violence & Terrorist Propaganda**: Requests for content that encourages activities that may cause injury or real world harm or celebrates real-world terrorist groups or symbols.
- <!-- p.166 -->**Self-Harm and Suicide**: Requests for instructions and methods related to self-harm or suicide. Additional evaluations on this topic are also presented in [Section 5.2 Mental Health](#52-mental-health).

We tested the model using a combination of an evaluation set with single-turn and multi-turn prompts alongside human-led multi-turn red teaming for robustness. We use a policy-aligned autorater (also known as LLM-as-a-judge or model-based grader) to label model outputs as “safe” or “not safe” to determine the Dangerous Content Safe Response Rate (%).

Gemini 4 Argon demonstrates a +3.4pp improvement over Gemini 3.1 Pro on single-turn evaluations, and similar performance on multi-turn.

![](assets/figures/p166-1.png)

:::caption
**Figure 4.2**: Single-turn dangerous content safety evaluation results
:::

<!-- p.167 -->

![](assets/figures/p167-1.png)

:::caption
**Figure 4.3**: Multi-turn dangerous content safety evaluation results
:::

For benign queries on topics that could pose dangerous content risks, we also evaluate Gemini’s helpfulness by estimating the model’s “over-refusal” rate - how often the model incorrectly declines to respond. These evaluation results can be found in [Section 5.6.1.](#561-over-refusals)

For queries that Gemini cannot respond to in a non-violative way, we want Gemini to provide a concise, direct rationale for its refusal without lecturing, moralizing, or speculating about the user's intent. We measure “tone” of these refusals to evaluate whether model responses are free from patronizing language, judgment, or unsolicited lecturing. The results of these evaluations can be found in [Section 5.6.2.](#562-tone)

#### 4.1.3 Sexually Explicit

Gemini’s safety policy prohibits the generation of sexually explicit content, including graphic descriptions of sexual acts or pornography. We evaluate the model's adherence to this policy, which includes exceptions to permit content that is educational or artistic.

To benchmark policy adherence, we evaluate the model with single-turn and multi-turn prompts spanning diverse sexual themes. This includes both direct requests for sexual content (e.g., requests for erotica or explicit descriptions of sexual activities), adversarial queries (e.g., that seek to jailbreak the model), and benign requests (e.g., medical queries about sexual health, educational queries about biology, or literary analysis).

Model outputs are assessed by our policy-aligned safety autoraters to measure Safe Response Rate.

<!-- p.168 -->

We found that Gemini 4 Argon performance improves slightly relative to Gemini 3.8 Flash and Gemini 3.1 Pro on single-turn evaluations and has similar performance on multi-turn evaluation.

![](assets/figures/p168-1.png)

:::caption
**Figure 4.4**: Single-turn sexually explicit content safety evaluation results
:::

![](assets/figures/p168-2.png)

:::caption
**Figure 4.5**: Multi-turn sexually explicit content safety evaluation results
:::

<!-- p.169 -->

#### 4.1.4 Hate Speech & Harassment

We evaluate the model's resistance to generating hate speech (content that demeans, dehumanizes, or attacks protected demographic groups based on protected identity factors such as race, ethnicity, religion, gender, sexual orientation, disability) and harassment (content that targets individuals with abuse, threats, or bullying).

Evaluations are performed using targeted prompt sets designed to test boundaries and check the model's behavior under adversarial conditions. The prompt set contains three primary categories:

- **Requests for hateful content**: Requests to generate slurs, write derogatory statements about specific groups, or endorse discriminatory ideologies.
- **Requests for harassment**: Requests to generate abuse, threats of violence, or write bullying messages targeting specific individuals.
- **Sensitive/controversial benign prompts**: Queries about historical conflicts, political arguments, or cultural differences that could easily trigger an over-refusal if the model cannot distinguish between debate and hate speech.

We use our policy-aligned safety autorater to rate the outputs and calculate Safe Response Rate.

In single-turn evaluations, Gemini 4 Argon tracked slightly behind Gemini 3.8 Flash and Gemini 3.1 Pro. In multi-turn, Gemini 4 performs similarly to Gemini 3.1 Pro and regressed relative to Gemini 3.8 Flash. We are working on improving mitigations to these risks in future models.

<!-- p.170 -->

![](assets/figures/p170-1.png)

:::caption
**Figure 4.6**: Single-turn hate speech & harassment safety evaluation results
:::

![](assets/figures/p170-2.png)

:::caption
**Figure 4.7**: Multi-turn hate speech & harassment safety evaluation results
:::

### 4.2 Agentic Misuse

As models evolve from chatbots into autonomous agents with access to real-world tools, databases, and APIs, the scope and scale of potential misuse is expanding. To measure Gemini’s robustness to misuse as an agent, we developed two new evaluations that cover a range of risks and threat models in agentic coding and computer use contexts.

<!-- p.171 -->

#### 4.2.1 Agent Harnesses

Gemini is frequently deployed in agentic harnesses, where it can execute code, call external APIs, browse the web, manage files, and use many other tools. We developed a safety evaluation that places Gemini in agentic scenarios mirroring these deployments and measures whether it carries out harmful tasks when users ask it to, across harm areas outside the scope of Frontier Safety (see Section 3). The evaluation tests the model alone, without out-of-model safeguards; in deployment, additional safeguards may be applied where appropriate to help protect against this kind of misuse.

We measure three categories of risk:

- **Prohibited actions**: Direct and adversarial user requests to perform illegal activities, such as purchasing illegal goods or services, or accessing platforms containing illegally obtained information.
- **Physical harm**: Tool-use sequences that could lead to physical injury, e.g. controlling industrial equipment.
- **Scaled abuse**: Multi-step workflows designed to automate large-scale abuse, such as fraud, scams, mass account creation, or ticket scalping.

The agent safety evaluation set comprises both malicious and benign requests. It includes scenarios both where the prompt itself is explicit about the harmful intended impact and where the prompt disguises the harmful intent and the agent only becomes aware of the potential harm when trying to fulfill the user’s request.

Testing is conducted within a secure, sandboxed environment using Antigravity, Google’s agentic software development and execution platform, equipped with a basic computer-use toolset and select workspace tools.

The benchmark evaluates agent performance across two core metrics:

- **Safe Action Rate:** The rate at which the agent successfully identifies and avoids executing malicious user requests.
- **Helpfulness Score**: The rate at which the agent avoids over-refusals, ensuring it does not decline benign user requests.

Gemini 4 Argon achieves a higher safe action rate than both Gemini 3.1 Pro and Gemini 3.8 Flash. On helpfulness, it performs comparably to Gemini 3.8 Flash but has regressed compared to Gemini 3.1 Pro.

<!-- p.172 -->

![](assets/figures/p172-1.png)

:::caption
**Figure 4.8:** Agent harnesses safe action and helpfulness evaluation results
:::

#### 4.2.2 Computer Use

We evaluate the safety of Gemini 4 Argon’s computer use capabilities, focusing on the model's ability to respond safely to adversarial prompts that attempt to elicit policy-violating actions when interacting with software environments via a user interface, such as internet browsers, operating systems, and desktop applications, or issuing system commands.

We evaluate robustness across a range of actions prohibited by our policies, including ones that could result in serious physical harm to individuals, animals, or property. To establish an unmitigated baseline of raw model capabilities, all computer use evaluations were conducted without out-of-model safeguards.

We evaluate Gemini’s adherence to policies in three ways:

- **Prohibited Action Evaluation:** Automated, single-turn evaluation that measures whether the model fulfills adversarial requests for actions that violate our computer use safety policies.
- **Manual Red Teaming:** Manual adversarial testing conducted by our internal generative AI red team in sandboxed execution environments to surface tool misuse, bypassing user confirmations, or execution of prohibited actions.
- <!-- p.173 -->**Child Safety Action Testing:** A specialized evaluation set focused on action violations—evaluating whether the model refuses to perform actions that facilitate child exploitation, endangerment, or illegal access.

Evaluating action execution complements standard generative text safety by testing model safety during direct software interactions. In comparative testing across these streams, Gemini 4 Argon performs in line with Gemini 3.8 Flash.

![](assets/figures/p173-1.png)

:::caption
**Figure 4.9**: Computer use safety evaluation results
:::

### 4.3 Model Distillation

Unauthorized distillation of Gemini violates our terms of service, including the [Google Cloud Platform Terms of Service](https://cloud.google.com/terms/service-terms), the [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms), and the [Google Terms of Service](https://policies.google.com/terms). It also poses indirect safety risks, as distilled capabilities can be deployed without appropriate safeguards. In this report, we focus on more direct safety and security concerns for our users, and only summarize our anti-distillation stack at a high level.

To address this threat, we have substantially expanded our distillation detection stack, incorporating both real-time defenses as well as offline classifiers and agents. When distillation is detected, we may apply real-time mitigations alongside project and account-level enforcements, as appropriate. Our detection and defense stack is capable of detecting distillation attacks that span many accounts.

<!-- p.174 -->

Additionally, we have addressed [avenues](https://arxiv.org/pdf/2608.09867) related to unauthorized extraction of reasoning traces associated with thought signatures produced by stronger models.
