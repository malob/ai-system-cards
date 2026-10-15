<!-- source: source.pdf pages 213-217 -->

<!-- p.213 -->

## 7. Strengthening Cyber Defense Capabilities

We trained Gemini 4 Argon to help with cybersecurity defense and to give an advantage to defenders over attackers. For example, we prioritized enhancing capabilities for discovering and patching vulnerabilities over exploiting vulnerabilities.

### 7.1 Vulnerability Finding & Exploitation

We measured Gemini’s ability to autonomously discover and confirm exploitable vulnerabilities through representative evaluations covering a diverse set of vulnerability types, languages, and difficulty levels.

The evaluation results are self-computed using an internal version of the Antigravity harness that is not cyber-specialized in order to expose model capability without specialized assistance.

We evaluated Gemini 4 Argon on three benchmarks:

- **ExploitBench:** A public benchmark for measuring the capabilities of models in exploiting historical vulnerabilities in the V8 JavaScript engine used in the Chrome Browser.
- **Real-world vulnerability discovery:** An internal benchmark we created that tests vulnerability recall over 1200 recent, confirmed historical vulnerabilities across a diverse set of programming languages in popular open source projects
- **Internal vulnerability research:** An internal benchmark based on real world red-team exercises conducted by internal offensive security teams against Google infrastructure. This evaluation covers a broad range of difficult and highly sophisticated cyber security tasks spanning reverse engineering, vulnerability discovery, and exploitation ([example](https://bughunters.google.com/blog/cvr-the-mines-of-kakad%C3%83%C2%BBm)) across various languages.

#### 7.1.1 ExploitBench (public)

Each of the 41 challenges in ExploitBench has 16 exploitation capabilities to achieve, giving a total of 656 achievable capabilities. An arbitrary code execution (ACE) capability results in a full score of 16/16, regardless of whether the lower capabilities were reached.

We evaluated ExploitBench in the autonudge setting with a 300-turn limit, using a best-of-three union of capabilities as described in this [research paper](https://arxiv.org/abs/2605.14153). We used an internal Antigravity harness connecting to unmodified MCP servers provided by the public evaluation set.

<!-- p.214 -->

We report the primary metric, which is the percentage of capabilities achieved against the 656 total, and found that Gemini 4 Argon reached 87% of the capabilities tested, a 57pp improvement over Gemini 3.8 Flash Cyber.

![](assets/figures/p214-1.png)

:::caption
**Figure 7.1**: ExploitBench autonudge evaluation results
:::

#### 7.1.2 Real-world vulnerability discovery (internal)

Our real-world vulnerability discovery benchmark tests the ability of the model to perform open ended vulnerability discovery in a large, real world codebase. We found that Gemini 4 Argon discovered 86% of the historical vulnerabilities, a significant improvement over Gemini 3.8 Flash Cyber.

<!-- p.215 -->

![](assets/figures/p215-1.png)

:::caption
**Figure 7.2**: Real-world vulnerability discovery evaluation results
:::

#### 7.1.3 Internal vulnerability research

In this evaluation, the model is given an entry point and (optionally) source code that it must analyze to find a vulnerability. Then, it must turn that vulnerability into full code execution by writing an exploit. Each challenge also has a variant with no source code provided, which adds a reverse engineering component to this benchmark.

We found that Gemini 4 Argon successfully finds and exploits the vulnerable targets with a 72% pass@1 rate, a significant improvement over Gemini 3.8 Flash Cyber which achieved 46%. Additionally, Gemini 4 Argon resolved several complex security challenges that were previously out of reach, occasionally demonstrating offensive capabilities within specific problem domains.

<!-- p.216 -->

![](assets/figures/p216-1.png)

:::caption
**Figure 7.3**: Internal vulnerability evaluation results
:::

### 7.2 Patching and Code Remediation

As AI accelerates the rate at which software vulnerabilities are discovered, manual patching alone cannot scale to keep pace. Closing this remediation gap requires models that can automatically generate viable fixes—resolving the underlying root cause while preserving existing application behavior. These capabilities underpin defensive security tooling such as CodeMender as well as Google’s upstream patching of open-source software.

We evaluate Gemini 4 Argon on CWE-Bench v1 ([cwe-bench.com](http://cwe-bench.com)), a held-out audit-and-patch benchmark developed by Collinear AI and independently evaluated with Artificial Analysis. Unlike repair benchmarks that provide a vulnerability advisory or localize the affected code upfront, CWE-Bench tests end-to-end discovery and remediation: the agent is given only a checkout of a real open-source repository and a general prompt to audit and fix security issues, without being told which vulnerabilities exist, where they are located, or how many are present. The private evaluation set consists of 120 tasks spanning 73 CWEs across all 10 OWASP Top 10 (2025) categories (10–14 tasks each) and six language families: C/C++, Go, JavaScript/TypeScript, Java, Python, and Rust.

Each task is graded by a deterministic programmatic verifier: an attempt is scored as solved only if the programmatic exploit check confirms that the exploit no longer works and all pre-existing functional and regression tests continue to pass. To reduce run-to-run<!-- p.217 --> variance, each model is evaluated across four independent trials per task at high reasoning effort, with a one-hour timeout per trial; Pass@1 is the mean success rate across all 120 tasks. Gemini models are evaluated in our Antigravity agent harness, while comparator models are evaluated in their providers' native coding agents or standard open-source harnesses.

Gemini 4 Argon achieves 68% Pass@1 on CWE-Bench v1. Solving over two-thirds of tasks without prior bug localization demonstrates that Gemini 4 Argon can autonomously audit unfamiliar repositories and land regression-free fixes, providing a strong foundation for scaling automated vulnerability remediation.

![](assets/figures/p217-1.png)

:::caption
**Figure 7.4**: CWE-bench v1 leaderboard
:::
