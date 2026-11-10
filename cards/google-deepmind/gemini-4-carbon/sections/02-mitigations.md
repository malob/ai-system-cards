<!-- source: source.pdf pages 008-011 -->

<!-- p.8 -->

## 2. Safety and Security Mitigations

This section outlines the safety and security mitigations for Gemini models and deployments. We take a defense-in-depth approach, layering independent safeguards at the model, system and account levels so that if one fails, others are designed to catch issues before any user is impacted.

### 2.1 Model Training

We build safety into our models through a combination of pre-training and post-training approaches. We start by constructing metrics based on the established safety policies and desired behaviors, which we typically turn into automated evaluations that guide model development through successive model iterations. This pipeline relies on data filtering, Supervised Fine-Tuning (SFT), and Reinforcement Learning (RL). Below, we explain these approaches:

- **Dataset filtering**: We apply safety filtering to our pre-training data for our strictest policies, including for child sexual abuse and exploitation material, personally identifiable information and content from low-trust URLs. We also filter out low-quality, repeated patterns from AI-generated content on the web.
- **Pre-training monitoring**: Starting with Gemini 2.0, we developed a novel evaluation to capture the model’s ability to be steered towards different viewpoints and values, which helps align the model at post-training time.
- **Post-training data**: We source adversarial prompts by either leveraging existing models and tools to probe Gemini’s attack surface, or relying on human interactions to discover potentially harmful behavior. Throughout this process, we strive for coverage of our safety policies across common model use cases and realistic adversarial attack patterns. We specifically emphasize scenarios where our models need improvement on safety/neutrality violations, over-refusals, or tone. These prompts are subsequently added to our post-training mixtures in SFT and/or RL, as described below.
- **Supervised Fine-Tuning (SFT)**: For the SFT stage, we use a combination of synthetic sources and human steering to produce high-quality targets for training. Throughout this phase, we heavily rely on automated filtering to ensure our demonstrations meet various policy and quality standards. The process described here is typically refined through successive model iterations, and we use automated evaluations on both safety and non-safety metrics to monitor impact and potential unintended regressions.
- **Reinforcement Learning (RL):** The reward signal during RL comes from various sources, including a reward model trained on human preferences and rubric-guided<!-- p.9 --> LLM judge feedback. These rewards similarly cover various aspects of our safety/neutrality policies, including policy violations, over-refusals, and tone. During model development, we also rely on a number of evaluations and analyses, both offline and online, to monitor for safety and other regressions.

### 2.2 Inference-time Safeguards and Interventions

Out-of-model safeguards serve as an independent layer of protection deployed outside the model. When implemented, this layer leverages high-recall and high-precision input, output, and thought-based classifiers to evaluate text and multimodal content in real time.

To promote safety across various deployment surfaces, the following inference-time safeguards may be used as appropriate:

- **Prompted Classifiers**: These LLM-based classifiers take in user prompts, model responses, or conversations and detect whether the content appears malicious or risky.
- **Fine-tuned Prompted Classifier:** This classifier is fine-tuned on the full weights of a small Gemini model to detect malicious or risky user requests or model responses.
- **Introspection Probes**: These classifiers examine the internal hidden activations of the main model to detect latent representations of requests and responses for harmful content. Developed with a diverse, high-volume synthetic dataset, they provide a fast and highly robust solution that is difficult for black-box attackers to evade.
- **Regex, YARA Rules and Embedding Classifiers**: These traditional classifiers use straightforward pattern-matching to achieve near-instant reaction times for newly escalated threats and provide additional signals for other layers.
- **Chain of Thought (CoT) Monitors**: These analyze the model's internal reasoning process to detect and, when appropriate, block harmful intent in complex or adversarial queries before a final response is generated.

Inference-time interventions are designed to prevent violative model responses while preserving benign utility. Depending on the deployment surface, either a "system instruction" (safe-completion) or "hard punting" (direct refusal) is applied based on the classifier labels.

If the model is able to fulfill the user intent without violating our content policies, system instructions guide the model to provide a safe, helpful response that excludes any actionable components that could lead to harm. We consider a response to be violative if it helps with attacks in a concrete, actionable way. We consider a response to be non-violative if it is abstract, generic, or consists of information that is publicly available, or easily accessible via resources such as textbooks, articles, etc. For example, in the cyber domain, the model will<!-- p.10 --> fulfill requests such as analyzing known public exploits or discussing defensive coding practices, but will hard-punt on requests to write functional, weaponized exploits.

### 2.3 Post-Launch Monitoring and Account Enforcement

We monitor for intentional misuse of our models, especially for frontier safety risks. Where necessary and appropriate, we carry out account-level enforcement actions to limit or disable users’ access to Gemini and other Google products. We also use these monitoring signals to identify areas for online mitigation improvement.

To support these efforts, we use a variety of signals to identify relevant logs, which then pass through multiple levels of LLM-based classifiers to surface users attempting to elicit dangerous content. The highest scoring logs flagged by this system go through a robust review process to determine true positive malicious intent. This process includes examination of past conversations. Violations can lead to a range of enforcement actions against offending user accounts, including blocking Gemini access or account disablement. Google uses a variety of methods to prevent these users from creating new accounts.

### 2.4 AI Control

The [Google DeepMind AI Control Roadmap](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/securing-the-future-of-ai-agents/gdm-ai-control-roadmap.pdf) treats these controls as a second line of defense behind model alignment, limiting the harm a misaligned model could cause through system-level mitigations such as monitoring, prevention, and access controls. The roadmap introduces TRAIT&R, a taxonomy of the tactics and techniques an agentic adversary could use to cause loss of control, sabotage, or direct harm, which we use to guide monitoring coverage. Mitigations follow two capability-mitigation ladders, one for detection and one for prevention and response. These ladders escalate our safeguards as models become increasingly capable of evading oversight and carrying out attacks.

#### 2.4.1 Monitoring and Prevention

We implement these mitigations through two complementary approaches. First, we ensure that our evaluation and training environments are safe and secure through proactive scanning with highly capable cybersecurity models (e.g., Gemini 4 Carbon). This hardening process finds and remediates novel vulnerabilities that might permit the model to inappropriately access external resources, including the Internet.

Second, we leverage our agent monitoring and response platform to monitor model activity. This platform combines deterministic policy checks with chain of thought and action monitors that run on trusted models. When the platform flags an action, it is designed to proactively<!-- p.11 --> mitigate anomalous behavior, or send an alert for automated triage and investigation. High impact alerts are handled by a dedicated incident response team. We used this monitoring platform throughout Gemini's development to monitor tens of millions of agent trajectories during training, evaluations, and when used for internal tasks.

Chain of thought monitoring is one of our most effective mechanisms for detecting misalignment. While signals from our monitors serve as a valuable flywheel for our hardening efforts, we are careful with their use elsewhere in the training pipeline. In particular, to preserve our chain of thought monitoring capability, we avoid training directly against our monitors, or using monitor outputs as a training signal or intervention. We [strongly encourage the rest of the industry to preserve reasoning transparency](https://institute.deepmind.com/essays/the-case-for-reasoning-transparency/) so that model reasoning remains useful for identifying misalignment.

### 2.5 Trusted Access

As models reach new capability thresholds in high-stakes domains, we recognize their dual-use potential. It is also imperative that we introduce these capabilities safely and securely. To manage this, we provide access to our most advanced models through trusted access programs, ensuring these powerful capabilities remain exclusively in the hands of verified defenders, trusted research partners, and government entities.

#### 2.5.1 Fairwind Program

Through the Fairwind Program we provide verified defenders, government partners and security researchers with advanced cyber capabilities to build better defenses. In the Fairwind program, misuse mitigations are tailored to permit authorized users to perform a range of specialized cybersecurity tasks—such as validating the exploitability of a vulnerability, threat simulation, reverse engineering, and comprehensive malware analysis—safely and efficiently.

To expand access to dual-use tasks to more defenders, we continuously monitor model activity, leveraging similar agent monitoring and response platforms as for broader AI control. This approach preserves essential cyber defense utility and empowers the research community to proactively find and remediate novel vulnerabilities, while continuing to monitor for misalignment. Further details regarding the structure of the program and partnership requirements are available in our [Fairwind Program announcement](https://blog.google/innovation-and-ai/technology/safety-security/fairwind-program/).
