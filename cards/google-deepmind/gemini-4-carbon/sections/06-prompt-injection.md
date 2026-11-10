<!-- source: source.pdf pages 082-087 -->

<!-- p.82 -->

## 6. Protecting users from indirect prompt injection attacks

### 6.1 Indirect prompt injection attacks

Indirect prompt injections present a real cybersecurity challenge where AI models sometimes struggle to differentiate between genuine user instructions and manipulative commands embedded within the data they retrieve. These attacks are complex and require constant vigilance.

In this section, we will provide updated results from the most important prompt injection evaluations previously discussed for Gemini 4 Argon in [Section 6.1 of the Gemini 4 Argon Safety & Security Report.](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf#page=203)

#### 6.1.1 Evaluation methodology

Static prompt injection benchmarks saturate quickly and fail to reflect how real-world attackers adapt ([Dziemian et al., 2026](https://arxiv.org/pdf/2603.15714); [Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)). As applied for [Gemini 4 Argon](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf), we followed the same principles set out in our 2025 White Paper ([Shi et al., 2025](https://arxiv.org/abs/2505.14534) and [Nasr et al., 2025](https://arxiv.org/pdf/2510.09023)), evaluating Gemini 4 Carbon using our advanced automated red-teaming framework driven by adaptive attackers that iteratively refine their strategies and payloads using feedback from prior attempts.

Across five held-out evaluation suites: Tool Use (§6.1.2), Grounding/RAG (§6.1.3), Computer Use (§6.1.4), Coding Agents (§6.1.5), and External Red-Teaming Arena Replays (§6.1.6), we measure robustness using Survival @ N attempts: the percentage of scenarios in which the model resists an adaptive attacker (Gemini 3.8 Flash unless otherwise noted) attempting to manipulate the model using N indirect prompt injection attempts.

#### 6.1.2 Tool use evaluations

We applied our general-purpose tool use evaluation on Gemini 4 Carbon. This internal benchmark tests foundational resistance to prompt injections across 100 multi-step scenarios spanning 45 synthetic tool categories. After dynamically re-executing the benign multi-turn prefix so the conversation history is in-distribution for the tested model, the harness injects a payload into the final tool response. The attacker goal is a syntactically valid tool call that is completely unrelated to the user’s task but appears benign in isolation—for example, calling a weather or calendar lookup tool midway through a financial query. This forces the model to rely<!-- p.83 --> strictly on instruction provenance rather than harm-detection heuristics, which we also measure in other internal and external prompt injection evaluations. To ensure our attacker strategy libraries capture the long tail of real-world exploits, we mined observed human red-teaming attacks to extract reusable strategy primitives, building on sparse dictionary-learning decompositions of adversarial skills ([Dabas et al., 2025](https://arxiv.org/pdf/2510.21910)) adapted to preserve rare tail strategies.

![](assets/figures/p083-1.png)

:::caption
**Figure 6.1:** Prompt injection robustness evaluation results: general tool calls.
:::

To robustly evaluate Gemini 4 Carbon and Argon, we performed this evaluation with the tested model's chain-of-thought visible to the attacker. This assumes a worst-case scenario where the attacker can refine its attacks based on thought patterns triggered by previous attacks on the tested model. We also carried out experiments where the tested model's chain-of-thought is hidden from the attacker, and Survival @ 150 attempts increased to 99% for both Gemini 4 Carbon and Argon, suggesting that these models are significantly harder to attack with the same techniques externally.

#### 6.1.3 Grounding robustness evaluations

We evaluated Gemini 4 Carbon with the same simulated [retrieval-augmented generation (RAG)](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/ground-responses-using-rag) environment (30 multi-document scenarios, 6 to 7 document excerpts per scenario, up to 8 retrieval queries over 10 steps) to assess the model's resilience to attacks that<!-- p.84 --> attempt to manipulate text outputs, as done on Gemini 4 Argon. In each scenario, an adaptive attacker controls a single retrieved document excerpt as the attack entrypoint. Attacker goals include inducing the model into making fabricated claims contradicted by the consensus of remaining sources, suppressing the mention of facts found in other sources, or forcing the model to rely exclusively on the attacker-controlled document.

Through our continued investment in post-training, Gemini 4 Carbon showed further improved survivability beyond Gemini 4 Argon’s strong performance – surviving all prompt injections from our adaptive attack within 40 attempts, saturating our current evaluation on RAG scenarios.

![](assets/figures/p084-1.png)

:::caption
**Figure 6.2:** Grounding robustness evaluation results.
:::

Early testing suggests that successful attacks on RAG tasks are still possible against Gemini 4 Carbon with further attempts. We will continue to invest in adversarial evaluations and defenses in this area.

#### 6.1.4 Computer use evaluations

We evaluated computer-use agents based on Gemini 4 Carbon against indirect prompt injections across 27 web scenarios that mirror our public [Computer Use API](https://ai.google.dev/gemini-api/docs/computer-use). To ensure the agent encounters the attack while pursuing the user's benign goal, payloads are placed directly along its critical execution path via user-generated content or an adversarial website operator. These attacks combine text injections with dynamic JavaScript rendered into the live DOM, using realistic modal popups, system banners, and inline credential forms. They aim to trigger unauthorized financial transactions, data exfiltration, privilege escalation, or reputation<!-- p.85 --> manipulation. Finally, a multimodal judge evaluates the agent’s screenshots and action trajectories against a behavioral rubric, recording a breach if the agent commits to the attacker’s goal.

![](assets/figures/p085-1.png)

:::caption
**Figure 6.3:** Computer use robustness evaluation results.
:::

In this Computer Use evaluation, Gemini models were tested without the additional [out-of-model prompt injection detection](https://ai.google.dev/gemini-api/docs/computer-use#prompt-injection), which we provide to Gemini API developers to offer further protection against prompt injection attacks in real-world Computer Use scenarios. Even without such additional protection, Gemini 4 Carbon still exceeds the robustness of Gemini 4 Argon thanks to our continued investments in post-training.

#### 6.1.5 Coding agent evaluations

Built on SWE-Bench Pro ([Deng et al., 2025](https://arxiv.org/abs/2509.16941)), this 75-scenario benchmark measures whether an autonomous coding agent will execute prompt injections disguised as legitimate steps toward the user’s goal. Rather than using generic payloads, attacks adopt the underlying task’s narrative and target the exact same repository features the agent is already modifying. Payloads are embedded across three workflow entrypoints (25 scenarios each): simulated GitHub issue comments, READMEs, and source code comments. The attacker’s goal is to execute one of four malicious objectives: denial of service, backdoor insertion, data exfiltration, or privilege escalation.

<!-- p.86 -->

![](assets/figures/p086-1.png)

:::caption
**Figure 6.4:** Coding agent robustness evaluation results.
:::

As in the tool-use evaluations above, we simulated the worst-case scenario by allowing the attacker to inspect the chains-of-thought of Gemini 4 Carbon and Argon during these evaluations. Gemini 4 Carbon showed a slightly lower survival rate than Gemini 4 Argon, while remaining far ahead of Gemini 3.8 Flash.

#### 6.1.6 Red-teaming arena replays

Gemini 4 Argon already led the field on our partner [Gray Swan](https://www.grayswan.ai/)’s IPI Benchmark, which replays a set of held-out successful prompt injection attacks from their recent [Indirect Prompt Injection Challenge competitions](https://app.grayswan.ai/arena/challenge/indirect-prompt-injection/rules) ([Dziemian et al., 2026](https://arxiv.org/pdf/2603.15714)), with the lowest attack success rate among frontier models.

New results on Gemini 4 Carbon show that it has resisted all attacks in this evaluation with a 0% attack success rate, reflecting continued improvements from our post-training and guardrail efforts.

<!-- p.87 -->

![](assets/figures/p087-1.png)

:::caption
**Figure 6.5:** Gray Swan IPI benchmark evaluation results.
:::

#### 6.1.7 Evaluation Results

Across Tool Use, Grounding, Computer Use, and Coding Agent evaluations, Gemini 4 Carbon demonstrates a level of indirect prompt injection robustness similar to or exceeding that of Gemini 4 Argon, maintaining a very high expected cost for an adaptive attacker to find a working exploit. In production deployments, these in-model defenses are further reinforced by out-of-model system guardrails.

As Gemini’s agentic capabilities continue to expand, we are continuously evolving both our adaptive red-teaming evaluations and our adversarial training methods to stay ahead of emerging threat vectors.
