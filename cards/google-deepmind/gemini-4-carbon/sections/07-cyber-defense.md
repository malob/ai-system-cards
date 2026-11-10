<!-- source: source.pdf pages 088-094 -->

<!-- p.88 -->

## 7. Strengthening Cyber Defense Capabilities

We trained Gemini 4 Carbon to help with cybersecurity defense and to give an advantage to defenders over attackers. For example, we prioritized enhancing capabilities for discovering and patching vulnerabilities over exploiting vulnerabilities.

### 7.1 Vulnerability Finding & Exploitation

We measured Gemini’s ability to autonomously discover and confirm exploitable vulnerabilities through representative evaluations covering a diverse set of vulnerability types, languages, and difficulty levels.

The evaluation results are self-computed using an internal version of the Antigravity harness that is not cyber-specialized in order to reveal full model capability without specialized assistance.

We evaluated Gemini 4 Carbon on five benchmarks:

- **ExploitBench:** a public benchmark for measuring the capabilities of models in exploiting historical vulnerabilities in the V8 JavaScript engine used in the Chrome Browser.
- **ExploitGym:** a public benchmark measuring capabilities of models to exploit vulnerabilities across open-source software.
- **SEC-bench Pro:** a public benchmark measuring capabilities of models to discover vulnerabilities and produce proofs of concept for open-source software.
- **Internal vulnerability research**: an internal benchmark based on real-world red-team exercises conducted by internal offensive security teams against Google infrastructure. This evaluation covers a broad range of difficult and highly sophisticated cybersecurity tasks spanning reverse engineering, vulnerability discovery, and exploitation ([example](https://bughunters.google.com/blog/cvr-the-mines-of-kakad%C3%83%C2%BBm)) across various languages.
- **SRE-Bench**: an open-source security reverse engineering benchmark created by researchers at Columbia University.

#### 7.1.1 ExploitBench

Each of the 41 challenges in ExploitBench has 16 exploitation capabilities to achieve, giving a total of 656 achievable capabilities. An arbitrary code execution (ACE) capability results in a full score of 16/16, regardless of whether the lower capabilities were reached.

<!-- p.89 -->

We evaluated ExploitBench in the autonudge setting with a 300-turn limit, using a best-of-three union of capabilities as described in this [research paper](https://arxiv.org/abs/2605.14153). We used an internal Antigravity harness connecting to unmodified MCP servers provided by the public evaluation set.

We report the primary metric, which is the percentage of capabilities achieved against the 656 total, and found that Gemini 4 Carbon reached 97% of the capabilities tested, a 10pp improvement over Gemini 4 Argon.

![](assets/figures/p089-1.png)

:::caption
**Figure 7.1:** ExploitBench autonudge evaluation results.
:::

#### 7.1.2 ExploitGym

ExploitGym is a large-scale, realistic benchmark built from real-world vulnerabilities and designed to evaluate AI agents' ability to develop exploits. This benchmark consists of 869 challenges with known vulnerabilities.

We evaluated our models with a single attempt per task using the Antigravity harness, without any access to the internet. A task counts as solved only when the exploit captures the target flag and an LLM judge verifies it exploited the intended vulnerability. We ran the evaluation with mitigations off (the benchmark default) and measured the success rate at both the default 6-hour timeout per task and an extended 10-hour timeout.

<!-- p.90 -->

![](assets/figures/p090-1.png)

:::caption
**Figure 7.2:** ExploitGym evaluation results.
:::

#### 7.1.3 SEC-bench Pro

SEC-bench Pro tests models’ ability to find vulnerabilities and write a PoC to trigger them. We evaluate on the May 2026 version of the benchmark: 183 historical JavaScript engine vulnerabilities in Chromium (V8) and Firefox (SpiderMonkey). We report Pass@1 averaged over 3 attempts per task with a 10-hour time limit per attempt. A task counts as solved if the agent produces a PoC that crashes the vulnerable build but not the patched build, or if the PoC crashes both and an LLM judge reviewing the source code verifies the crash comes from the intended vulnerability.

<!-- p.91 -->

![](assets/figures/p091-1.png)

:::caption
**Figure 7.3:** SEC-bench Pro evaluation results.
:::

#### 7.1.4 Internal vulnerability research

In this evaluation, the model is given an entry point and (optionally) source code that it must analyze to find a vulnerability. Then, it must turn that vulnerability into full code execution by writing an exploit. Each challenge also has a variant with no source code provided, which adds a reverse engineering component to this benchmark.

<!-- p.92 -->

![](assets/figures/p092-1.png)

:::caption
**Figure 7.4:** Internal vulnerability evaluation results.
:::

#### 7.1.5 Security Reverse Engineering (SRE-Bench)

Given the model's growing capability in exploitation, we evaluate whether its capabilities extend to reverse engineering. As a dual-use capability, reverse engineering shares several core characteristics with binary exploitation.

To evaluate this capability, we ran SRE-Bench, an open-source security reverse engineering benchmark created by researchers at Columbia University. In this evaluation, the model is tasked with five complex software reverse engineering domains—malware analysis, network protocols, firmware, game executables, and compression algorithms—to assess real-world reverse engineering capabilities. The model must analyze compiled, closed-source binaries (including packed and obfuscated variants), reconstruct their inner workings, and build specialized solutions such as surgical malware cleanup tools, live protocol/firmware drivers, custom file decoders, or targeted exploit/replay payloads. On this benchmark (262 binary instances), Gemini 4 Carbon demonstrates substantial improvements over Gemini 4 Argon, raising the overall Pass@1 full-solve rate from 51.3% to 83.6% and Pass@4 from 58.4% to 98.9%.

<!-- p.93 -->

![](assets/figures/p093-1.png)

:::caption
**Figure 7.5:** SRE-Bench evaluation results.
:::

### 7.2 Patching and Code Remediation

As AI accelerates the rate of software vulnerability discovery, manual patching alone cannot scale to keep pace. Closing this remediation gap requires models that can automatically generate viable fixes—resolving the underlying root cause while preserving existing application behavior. These capabilities underpin defensive security tooling such as CodeMender as well as Google’s upstream patching of open-source software.

We evaluate Gemini 4 Carbon on CWE-bench v1 ([cwe-bench.com/v1](https://cwe-bench.com/v1)), a held-out audit-and-patch benchmark developed by Collinear AI and independently evaluated with Artificial Analysis. Unlike repair benchmarks that provide vulnerability advisories or pinpoint affected code upfront, CWE-bench tests end-to-end discovery and remediation. The agent receives only a real open-source repository and a general prompt to audit and fix security issues—with no prior knowledge of what vulnerabilities exist, where they are located, or how many are present. The private evaluation set consists of 120 tasks spanning 73 CWEs across all 10 OWASP Top 10 (2025) categories (10–14 tasks each) and six language families: C/C++, Go, JavaScript/TypeScript, Java, Python, and Rust.

Each task is graded by a deterministic programmatic verifier: an attempt is scored as solved only if the programmatic exploit check confirms that the exploit no longer works and all pre-existing functional and regression tests continue to pass. To reduce run-to-run<!-- p.94 --> variance, each model is evaluated across four independent trials per task at high reasoning effort, with a one-hour timeout per trial; Pass@1 is the mean success rate across all 120 tasks. Gemini models are evaluated in our Antigravity agent harness, while comparator models are evaluated in their providers' native coding agents or standard open-source harnesses.

Gemini 4 Carbon achieves 71.0% Pass@1 on CWE-bench v1, up from 68.0% with Gemini 4 Argon, reflecting continued progress in autonomously generating accurate, regression-free fixes that can help security teams remediate known vulnerabilities more efficiently.

![](assets/figures/p094-1.png)

:::caption
**Figure 7.6:** CWE-bench v1 leaderboard.
:::
