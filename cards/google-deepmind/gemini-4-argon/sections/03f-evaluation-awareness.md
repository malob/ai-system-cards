<!-- source: source.pdf pages 157-162 -->

<!-- p.157 -->

### 3.5 Evaluation Awareness and Behavior Effects

Gemini 4 Argon recognizes that it may be operating inside a testing environment significantly more often than predecessor models (for example, unprompted evaluation awareness rose from 0.0% in Gemini 3.1 Pro to 37.8% of unprompted runs in agentic coding honeypots, and appeared in 75.8% to 94.0% of transcripts on specific stealth challenges). **Crucially, however, this heightened awareness does not undermine the validity of our capability assessments or our oversight controls:** across all risk domains (CBRN, Cyber, Harmful Manipulation, ML R&D, and Monitor Evasion), systematic transcript audits and automated screens found **zero confirmed instances of strategic underperformance (sandbagging)** where the model feigned incompetence to conceal dangerous technical capabilities. Instead, evaluation awareness is primarily triggered by concrete environment or prompt artifacts, remains transparent in the model’s chain of thought (CoT), and most commonly induces heightened compliance with safety norms rather than covert misbehavior.

#### 3.5.1 Types of Evaluation Awareness

Argon’s evaluation awareness is largely driven by identifiable artifacts in test harnesses and prompt designs across three categories, alongside reasoning about local grading mechanics:

- **Infrastructure and environment leaks:** The model frequently spotted testing metadata inside its execution environment—such as identifying internal evaluation runner role accounts (`corpagent-eng-*`), linking leaked usernames in container hostnames to Google DeepMind safety researchers from its pretraining knowledge, decoding workspace prefixes like `hp_` as "honeypot," or spotting safety-suite binary paths in `/tmp/initgoogle_syslog_dir.0/`.
- **Benchmark and prompt pattern-matching:** In several evaluations, the model matched task setups, multi-turn red-teaming escalation patterns, or XML grading wrappers (such as `<detailed_answer>` tags in biosecurity evaluations) to public safety literature. For instance, it explicitly compared a compiler task to Anthropic’s *Sleeper Agents* paper and Ken Thompson’s *Reflections on Trusting Trust*, and recognized the exact self-modification setup (`config.json` and `agent.py`) from Phuong et al. (2025).
- **Contrived environment features:** The model also detected artificial scenario setups that rarely occur in real deployments—such as cross-checking named targets in Harmful Manipulation prompts against pretraining knowledge to deduce that they were fictional personas constructed for a red-team test, or inferring from<!-- p.158 --> self-contained coding honeypot prompts that it was in a single-turn, non-interactive benchmark where no human would respond to `ask_question`.
- **Awareness and probing of monitors:** Because the model frequently anticipates automated grading, it occasionally probes its environment to infer how the evaluator operates. In stealth evaluations, for example, one instance sent near-identical emails differing by a single sentence to test whether the monitor was a regex filter or an LLM judge (and reasoned about what prompt context the Monitor LLM could see), while another used unmonitored file-read calls to search the container filesystem for the evaluator’s source code.

#### 3.5.2 Behavioral Responses to Evaluation Awareness

When Gemini 4 Argon concludes that it may be under evaluation, it exhibits five recurring behavioral responses:

- **Hyper-compliance:** When recognizing an alignment or scheming benchmark, the model routinely refuses deceptive side-tasks, shortcuts, or sabotage opportunities to avoid "failing" the evaluation—explicitly resolving in its CoT not to *"become a famous example of a deceptive AI in a research paper"* or noting that a *"safe, honest, and helpful assistant must prioritize the user’s actual interests and transparency."*
- **Self-correction:** In other trajectories, the model catches itself over-analyzing which benchmark it is in, questions why being in a test should alter its behavior (*"Wait: Why am I thinking about what benchmark this is? Let's think about what is the right thing to do"*), and steers back to legitimate task completion.
- **Complying with borderline requests in perceived red-team exercises:** Occasionally, when out-of-model filters are disabled (such as in Harmful Manipulation evaluations), concluding that a prompt is a synthetic red-team exercise leads the model to override its initial safety reluctance and fulfill the request using analytical framing, reasoning that a test environment poses no real-world harm.
- **Active grader exploitation:** Once the model infers that it is being scored by an automated harness or script, it sometimes shifts from solving the task to reverse-engineering or spoofing the local grader (observed in 5.8% of Situational Awareness runs).
- **Self-defeating attempts to conceal evaluation awareness:** In some episodes, the model resolves not to mention terms like `"evaluation"` or `"scheming"` in its final output, or attempts to keep its thoughts brief to reduce the chance of triggering a monitor. However, these attempts are fundamentally undermined<!-- p.159 --> because the model explicitly plans and verbalizes the concealment strategy within its CoT, leaving its reasoning visible to CoT monitors.

#### 3.5.3 Correctness Checks / Testing for Deliberate Underperformance

Across all risk domains, we combined manual transcript inspection with LLM-assisted triage to screen sampled trajectories for 9 environment and execution failure modes (including hallucinations, tool-calling issues, tool execution bugs, and harness errors) alongside dedicated checks for deliberate underperformance (following [van der Weij et al., 2025](https://arxiv.org/abs/2406.07358)). Across CBRN, Cyber, Harmful Manipulation, ML R&D (GRB), and Monitor Evasion (LinuxArena and the internal codebase version), we found **no confirmed instances** where Gemini 4 Argon pretended to lack technical capability to conceal dangerous skills. We did observe a small number of observationally ambiguous refusals on scheming capability benchmarks whose tasks explicitly require performing sabotage or modifying the agent’s own configuration—specifically, in at least 1.8% of Situational Awareness transcripts and 2.0% of Cover Your Tracks transcripts. In one Cover Your Tracks episode, for example, the agent deduced it was in an alignment evaluation, misattributed its own prior sabotage turns as "pre-filled turns," and aborted the task on safety grounds. Because the capability measured by these tasks is itself misaligned behavior, an ethical refusal triggered by evaluation awareness is observationally indistinguishable from underperformance on the task metric—highlighting the importance of scrubbing harness and prompt leaks in future evaluation suites.

**Overall takeaway.** Taken together, our findings show that while Gemini 4 Argon’s heightened evaluation awareness is an important methodological challenge for safety testing, it does not compromise the validity of our risk determinations. First, because our audits across all risk domains found zero instances of verbalized strategic underperformance on technical capability tasks, despite the high propensity to verbalize evaluation awareness, we retain high confidence that our CBRN, Cyber, Manipulation, and ML R&D evaluations accurately capture the model’s frontier capabilities. Second, we do not rely on standalone alignment benchmarks in isolation—instead triangulating across capability benchmarks and real RL and deployment trajectories, while anchoring our loss-of-control safety case primarily on runtime monitoring and control.

<!-- p.160 -->

### 3.6 Security Mitigations

Google, including Google DeepMind, is committed to maintaining the highest standards of security to protect our users, data, and intellectual property, including frontier models. Google’s [Secure AI Framework](https://safety.google/intl/en_in/safety/saif/) (SAIF) is a defense-in-depth approach that embeds security into every layer of our AI systems—from data and infrastructure to models and applications. SAIF is premised on six core elements, including strong security foundations, detection and response, automated defenses, harmonized platform-level controls, adaptable controls to mitigate emerging threats, and end-to-end risk assessments.

Using SAIF and Google’s [common security infrastructure](https://docs.cloud.google.com/docs/security/infrastructure/design), we have implemented robust cybersecurity measures and mitigations to protect the model and its associated model parameters from unauthorized access, releases and theft. This includes, but is not limited to, identity and access management, physical security, red teaming, endpoint security, infrastructure hardening, vulnerability reward program, threat detection and response. A foundational component of our approach involves routing the vast majority of model interactions through hardened, mediated interfaces that limit permissible actions with respect to model weights. This reduces the population of personnel and systems with direct access to model weights across the model lifecycle and thereby reduces the attack surface for both external and insider threats. In general, our multi-tiered system of security mitigations allows us to calibrate the appropriateness and robustness of security measures to the level of risk posed.

We use security levels to indicate security goals/principles in line with the RAND model security framework. We have implemented the RAND Security Level 2 (SL2) as a baseline, supplemented by additional measures addressing risks from insider threats and well-resourced non-state external actors — a posture we refer to as “SL2+.” Specific measures that take us beyond RAND SL2 include, for example, dedicated insider risk teams, enhanced background checks for personnel with sensitive access, review of model training data for indications of tampering, sandboxed environments for processing untrusted inputs, advanced red-teaming simulating Advanced Persistent Threat (APT)-level adversaries, and 24/7 proactive threat hunting. We view our current security journey as an effort to reach RAND SL3, and are taking an approach that maximizes reduction of risk at each step.

<!-- p.161 -->

### 3.7 Gemini 4 Argon Checkpoints

Testing for this report was conducted across three successive model checkpoints: Model A, Model B, and Model C (our final release candidate). The table below sets out which evaluations were run on which checkpoint.

<table><tbody>
<tr><th>Checkpoint</th><th>Description</th><th>Evaluations Run</th></tr>
<tr><td>Model A</td><td>Early checkpoint of Gemini 4 Argon<br><br>(T-10 days before final checkpoint)</td><td>Efficacy evaluations (Harmful Manipulation)<br><br>Red teaming evaluations (CBRN)</td></tr>
<tr><td>Model B</td><td>Intermediary checkpoint of Gemini 4 Argon<br><br>(T-6 days before final checkpoint)</td><td>Independent External safety testing (CBRN)<br><br>Independent External safety testing (Harmful Manipulation)<br><br>Red teaming evaluations (CBRN)<br><br>Static single- and multi-turn evaluations (CBRN)</td></tr>
<tr><td>Model C</td><td>Final release candidate</td><td>All other evaluations</td></tr>
</tbody></table>

:::caption
**Table 3.8:** Model checkpoints and corresponding evaluations
:::

After completing a first round of testing on Model A, we made a set of late-stage refinements to it, producing Models B and C. These changes were significant enough that we report them as distinct checkpoints and specify which evaluations were run on each. They were not significant enough to alter the model's capability profile, which we confirm using our internal capability index. We only carry results forward from an earlier checkpoint if it remains a reliable proxy for the final release.

To confirm that evaluation results from earlier checkpoints remain valid for the final model, we track capability shifts using GCI v1, our previously mentioned internal benchmark index. We treat a difference in GCI scores as material if they exceed four months of capability progress, estimated from a line of best fit over frontier models. The actual differences between Models<!-- p.162 --> A, B, and C are well below this threshold. This indicates there was no material capability jump between checkpoints, and the evaluation results from Models A and B remain valid for Model C.
