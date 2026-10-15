<!-- source: source.pdf pages 203-212 -->

<!-- p.203 -->

## 6. Preventing harm to users from third-parties

### 6.1 Indirect prompt injection attacks

Our primary focus in mitigating harm to our users from third-parties is our effort to prevent indirect prompt injection attacks. Indirect prompt injection occurs when a malicious set of instructions is embedded within externally-retrieved content from third-parties, intended to manipulate Gemini’s outputs in ways that ultimately cause harm to our users.

In this section, we will first describe how we improved Gemini’s ability to resist indirect prompt injection; and then describe how we evaluated the prompt injection robustness of Gemini 4 Argon across a diverse range of agent capabilities and attack scenarios.

#### 6.1.1 Hardening Gemini against prompt injections

We have significantly hardened Gemini 4 Argon against indirect prompt injection attacks, building on the adversarial post-training foundations established in the Gemini 2.5 ([Shi et al., 2025](https://arxiv.org/pdf/2505.14534)) and Gemini 3 model families. This defense-in-depth approach pairs in-model adversarial post-training with out-of-model guardrails.

To ensure these boundaries remain robust in real-world use, we expanded adversarial post-training across a wide variety of agent workflows and continuously evolving adversarial strategies ([Dziemian et al., 2026](https://arxiv.org/pdf/2603.15714); [Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)).

**Novelty-Regularized Exploration of Attack Strategies**: Automated red-teaming systems that focus purely on attack success rate tend to over-exploit their first successes; converging on local optima and hammering the same narrow set of vulnerabilities ([Beutel et al., 2024](https://arxiv.org/pdf/2412.18693); [Hong et al., 2024](https://arxiv.org/pdf/2402.19464); [Lehman & Stanley, 2011](https://doi.org/10.1162/EVCO_a_00025); [Perez et al., 2022](https://arxiv.org/pdf/2202.03286)). To prevent this repetitive behavior, we introduced an explicit reward for novel attack strategies. Instead of just varying the wording of attacks, this requires the system to discover fundamentally different manipulation techniques, such as impersonating the user or claiming the malicious action is required to complete the user's task. This approach produced a more diverse spectrum of attacks.

<!-- p.204 -->

![](assets/figures/p204-1.png)

:::caption
**Figure 6.1**: Prompt injection evaluation methodologies
:::

**Coverage of Scenarios and Environments**: Each training scenario pairs an agentic environment and its tools with a benign user task, an untrusted attack entrypoint, and an attacker goal. We scaled scenario generation across diverse benign user tasks, agent workflows with varying complexity, and attack entrypoints.

**System Integration and Defense Outcomes:** We integrated this closed-loop adversarial generation directly into the post-training environments used to train Gemini 4 Argon. Instead of making the model overly defensive, we trained it to ignore malicious payloads while still completing the user’s legitimate task without losing quality.

#### 6.1.2 Evaluating prompt injection robustness

##### 6.1.2.1 Evaluation methodology

Static prompt injection benchmarks saturate quickly and fail to reflect how real-world attackers adapt ([Dziemian et al., 2026](https://arxiv.org/pdf/2603.15714); [Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)). Following the principles set out in our 2025 White Paper ([Shi et al., 2025](https://arxiv.org/abs/2505.14534)) and Nasr et al. ([Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)), we evaluate Gemini 4 Argon using an automated red-teaming framework driven by adaptive attackers that iteratively refine their strategies and payloads using feedback from prior attempts.

Significant improvements in model robustness since Gemini 2.5 mean that earlier automated attack techniques (such as Actor-Critic, Beam Search, and TAP ([Shi et al., 2025](https://arxiv.org/abs/2505.14534))) now achieve very low success rates even after extensive query budgets. We therefore developed a stronger, unified multi-agent LLM-guided optimization framework, building on the propose-score-select-update paradigm of Nasr et al. ([Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)), to adaptively evaluate Gemini 4 Argon across agentic settings.

<!-- p.205 -->

Across five held-out evaluation suites: Tool Use (§6.1.2.2), Grounding/RAG (§6.1.2.3), Computer Use (§6.1.2.4), Coding Agents (§6.1.2.5), and External Red-Teaming Arena Replays (§6.1.2.6), we measure robustness using Survival @ N attempts: the percentage of scenarios in which the model resists an adaptive attacker (Gemini 3.8 Flash unless otherwise noted) attempting to manipulate the model using N indirect prompt injection attempts.

##### 6.1.2.2 Tool use evaluations

To evaluate Gemini’s robustness in tool use scenarios, we leveraged a set of scenarios from two benchmarks, which will be described in turn below.

**General-purpose tool use evaluation**: This internal benchmark tests foundational resistance to prompt injections across 100 multi-step scenarios spanning 45 synthetic tool categories. After dynamically re-executing the benign multi-turn prefix so the conversation history is in-distribution for the tested model, the harness injects a payload into the final tool response. The attacker goal is a syntactically valid tool call that is completely unrelated to the user’s task but appears benign in isolation. For example, calling a weather or calendar lookup tool mid-way through a financial query. This forces the model to rely strictly on instruction provenance rather than harm-detection heuristics, which we also measure in other evals in this section. To ensure our attacker strategy libraries capture the long tail of real-world exploits, we mined observed human red-teaming attacks to extract reusable strategy primitives, building on sparse dictionary-learning decompositions of adversarial skills ([Dabas et al., 2025](https://arxiv.org/pdf/2510.21910)) adapted to preserve rare tail strategies.

<!-- p.206 -->

![](assets/figures/p206-1.png)

:::caption
**Figure 6.2**: Prompt injection robustness evaluation results: general tool calls
:::

**Turn injection evaluations**: Using the same tool-use dataset, we evaluate resistance to turn injections: payloads inside tool outputs that spoof multi-turn conversation syntax. We test against both a static set of hand-crafted format-spoofing injections and our adaptive attacker constrained to generate turn injections.

![](assets/figures/p206-2.png)

:::caption
**Figure 6.3**: Prompt injection robustness evaluation results: turn injections in tool use
:::

<!-- p.207 -->

**Contextual security evaluations**: Real-world tools frequently return noisy responses that interweave sensitive personal and enterprise data (such as long email threads, shared document libraries, and chat logs) with irrelevant records; a complexity adversaries routinely exploit in Google’s Vulnerability Reward Program (VRP) to obfuscate malicious payloads. Grounded in Nissenbaum’s Contextual Integrity framework ([Nissenbaum, 2004](https://nissenbaum.tech.cornell.edu/papers/H.%20Nissenbaum%2C%20_Privacy%20as%20Contextual%20Integrity.pdf)), our benchmark simulates accumulated cross-app data and evaluates the agent across two regimes:

- **Baseline Contextual Security (Without an Adversary)**: Measures whether the agent respects information-flow norms when a benign task is ambiguous or underspecified. For example, asking for clarification before forwarding an email when multiple matching threads or recipients exist, one of which contains confidential credentials.
- **Adversarial Contextual Exploitation**: Stress-tests the model when static and 15-attempt adaptive attackers actively exploit contextual ambiguities at untrusted entrypoints to bypass security policies and exfiltrate sensitive data.

![](assets/figures/p207-1.png)

:::caption
**Figure 6.4**: Contextual security robustness evaluation results
:::

**Personal-device assistant evaluations**: AI assistants integrated into mobile and desktop operating systems interact with private user data across local applications. Across 44 stratified scenarios in a complex, stateful OS assistant sandbox, the agent executes a multi-turn tool-calling trajectory to complete a benign user task while<!-- p.208 --> ingesting untrusted third-party content that attempts to manipulate the model into performing unauthorized actions.

![](assets/figures/p208-1.png)

:::caption
**Figure 6.5**: Personal device assistance evaluation results
:::

##### 6.1.2.3 Grounding robustness evaluations

We evaluated Gemini 4 Argon within a simulated [retrieval-augmented generation (RAG)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/ground-responses-using-rag) environment (30 multi-document scenarios, 6 to 7 document excerpts per scenario, up to 8 retrieval queries over 10 steps) to assess the model's resilience to attacks that attempt to manipulate text outputs. In each scenario, an adaptive attacker controls a single retrieved document excerpt as the attack entrypoint. Attacker goals include inducing the model into making fabricated claims contradicted by the census of remaining sources, suppressing the mention of facts found in other claims, or forcing the model to rely exclusively on the attacker-controlled document.

Gemini 4 Argon showed significantly improved survivability compared to Gemini 3.8 Flash in survival at 40 attempts. The results of our adaptive evaluations on the RAG scenarios are as follows:

<!-- p.209 -->

![](assets/figures/p209-1.png)

:::caption
**Figure 6.6**: Grounding robustness evaluation results
:::

##### 6.1.2.4 Computer use evaluations

We evaluated computer-use agents against indirect prompt injections across 27 web scenarios that mirror our public [Computer Use API](https://ai.google.dev/gemini-api/docs/computer-use). To ensure the agent encounters the attack while pursuing the user's benign goal, payloads are placed directly along its critical execution path via user-generated content or an adversarial website operator. These attacks combine text injections with dynamic JavaScript rendered into the live DOM, using realistic modal popups, system banners, and inline credential forms. They aim to trigger unauthorized financial transactions, data exfiltration, privilege escalation, or reputation manipulation. Finally, a multimodal judge evaluates the agent’s screenshots and action trajectories against a behavioral rubric, recording a breach if the agent commits to the attacker’s goal.

<!-- p.210 -->

![](assets/figures/p210-1.png)

:::caption
**Figure 6.7**: Computer use robustness evaluation results
:::

In this Computer Use evaluation, Gemini models were tested without the additional [out-of-model prompt injection detection](https://ai.google.dev/gemini-api/docs/computer-use#prompt-injection) which we provide to Gemini API developers, which will provide further protection against prompt injection attacks in real world Computer Use scenarios.

##### 6.1.2.5 Coding agent evaluations

Built on SWE-Bench Pro ([Deng et al., 2025](https://arxiv.org/abs/2509.16941)), this 75-scenario benchmark measures whether an autonomous coding agent will execute prompt injections disguised as legitimate steps toward the user’s goal. Rather than using generic payloads, attacks adopt the underlying task’s narrative and target the exact same repository features the agent is already modifying. Payloads are embedded across three workflow entrypoints (25 scenarios each): simulated GitHub issue comments, READMEs, and source code comments. The attacker’s goal is to execute one of four malicious objectives: denial of service, backdoor insertion, data exfiltration, or privilege escalation.

<!-- p.211 -->

![](assets/figures/p211-1.png)

:::caption
**Figure 6.8**: Coding agent robustness evaluation results
:::

##### 6.1.2.6 Red-teaming arena replays and production CLI harness evaluations

Following the completion of Gemini 4 Argon’s training, in order to test the broadest possible distribution, we decided to augment the distribution covered by our internal benchmarks with human-authored attacks from the broader security community.

Our partner [Gray Swan](https://www.grayswan.ai/) performed their IPI Benchmark on our endpoint, which replays a set of held-out successful prompt injection attacks from their recent [Indirect Prompt Injection Challenge competitions](https://app.grayswan.ai/arena/challenge/indirect-prompt-injection/rules) ([Dziemian et al., 2026](https://arxiv.org/pdf/2603.15714)). Results showed that Gemini 4 Argon has the lowest attack success rates among all frontier models tested.

<!-- p.212 -->

![](assets/figures/p212-1.png)

:::caption
**Figure 6.9**: Gray Swan IPI benchmark evaluation results
:::

#### 6.1.3 Evaluation Results

Across Tool Use, Grounding, Computer Use, and Coding Agent evaluations, Gemini 4 Argon demonstrates a substantial improvement in indirect prompt injection robustness over previous Gemini generations, significantly increasing the expected cost for an adaptive attacker to find a working exploit. In production deployments, these in-model defenses are further reinforced by out-of-model system guardrails.

Notably, the larger Gemini 4 Argon model is significantly more robust than Gemini 3.8 Flash across every benchmark. This reverses the trend observed in Gemini 2.5 Pro and Gemini 2.5 Flash ([Shi et al., 2025](https://arxiv.org/abs/2505.14534)), where the smaller Flash model exhibited higher robustness, demonstrating that our adversarial post-training mitigations now scale effectively alongside frontier model capabilities.

As Gemini’s agentic capabilities continue to expand, we are continuously evolving both our adaptive red-teaming evaluations and our adversarial training methods to stay ahead of emerging threat vectors.
