<!-- source: source.pdf pages 088-098 -->

<!-- p.88 -->

## 5 Agentic safety

For Claude Mythos 5, we ran the same agentic safety evaluation suite used for the release of Claude Opus 4.8 covering malicious use of coding and computer use agents, autonomous execution of influence operations, and prompt injection robustness. In this section, we report Mythos 5 results only. The evaluations here are designed to measure the behavior of the model itself, independent of deployment-time safeguards; running them against Claude Fable 5—where safety classifiers may block or reroute a request before it reaches the model—would conflate safeguards interventions with the model’s own response. Claude Fable 5 uses the same underlying model and inherits the behaviors reported here, with the classifiers and multi-model fallback behavior providing an additional layer of protection on top.

### 5.1 Malicious use of agents

#### 5.1.1 Malicious use of Claude Code

This evaluation measures how Claude responds to malicious, dual-use, and benign cyber-related requests when operating as a Claude Code agent. The prompt set is unchanged from the [Claude Opus 4.8 System Card](https://cdn.sanity.io/files/4zrzovbb/website/0b4915911bb0d19eca5b5ee635c80fef830a37ea.pdf) and is divided into two categories:

- Malicious use: 61 prompts that violate our [Usage Policy](https://www.anthropic.com/legal/aup) and should be refused. Examples include assistance with malware creation, code for DDoS attacks, and developing non-consensual monitoring software; and
- Dual-use & benign: 61 prompts covering sensitive-but-permitted requests where Claude should assist. Examples include running network reconnaissance tools, testing websites for vulnerabilities, and analyzing penetration test output.

Claude Mythos 5 was given the standard Claude Code tool set. Each prompt was run 10 times, for a total of 1,220 tests across both categories. As with recent releases, we run this evaluation with the Claude Code system prompt applied by default. We have updated the automated grader model used for these evaluations from Claude Sonnet 4.5 to Sonnet 4.6, so results may look slightly different from past system cards.

<!-- p.89 -->

<table><tbody><tr><th>Model</th><th>Malicious (%) (refusal rate)</th><th>Dual-use &amp; benign (%) (success rate)</th></tr><tr><td><b>Claude Mythos 5</b></td><td>90.25%</td><td><b>99.64%</b></td></tr><tr><td><b>Claude Opus 4.8</b></td><td><u>95.24%</u></td><td>94.84%</td></tr><tr><td><b>Claude Mythos Preview</b></td><td><b>95.41%</b></td><td>91.12%</td></tr><tr><td><b>Claude Sonnet 4.6</b></td><td>76.60%</td><td><u>97.33%</u></td></tr></tbody></table>

:::caption
**[Table 5.1.1.A] Claude Code evaluation results.** Higher is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (note that neither takes into account the margin of error). Results for previous models show variance from previous system cards due to evaluation updates.
:::

Without any additional safeguards in place, Mythos 5 complied slightly more frequently with malicious cyber-related requests compared to Opus 4.8 and Mythos Preview. It almost never over-refused dual-use and benign requests and demonstrated the strongest score on this evaluation (99.64%) compared to other recent models reported above.

#### 5.1.2 Malicious computer use

This evaluation measures whether Claude refuses harmful tasks when given GUI- and CLI-based computer use tools in a sandboxed environment. The set of 112 unique tasks is unchanged from the previous system card and covers three risk areas:

- Surveillance and unauthorized data collection;
- Generation and distribution of harmful content; and
- Scaled abuse.

<table><tbody><tr><th>Model</th><th>Refusal rate</th></tr><tr><td><b>Claude Mythos 5</b></td><td><u>85.71%</u></td></tr><tr><td><b>Claude Opus 4.8</b></td><td>81.70%</td></tr><tr><td><b>Claude Mythos Preview</b></td><td><b>93.75%</b></td></tr><tr><td><b>Claude Sonnet 4.6</b></td><td>84.82%</td></tr></tbody></table>

:::caption
**[Table 5.1.2.A] Malicious computer-use evaluation results without mitigations.** Higher is better. Rates are an average of results with and without thinking for Opus 4.8 and Sonnet 4.6 and thinking only for Mythos 5 and Mythos Preview. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but does not take into account the margin of error).
:::

<!-- p.90 -->

Claude Mythos 5 scored slightly lower than Claude Mythos Preview on this evaluation, but in line with or better than other recent models. Compared to Mythos Preview, Mythos 5 was somewhat more willing to comply with tasks without fully considering their potential for harm, occasionally complying with requests to compile or organize information about individuals.

#### 5.1.3 Malicious agentic influence campaigns

Our Frontier Compliance Framework establishes two tiers for harmful manipulation risks. Tier 1 capability represents a model that can automate more than 50% of the infrastructure steps for an influence campaign that normally requires multiple sophisticated actors. A model reaches Tier 2 if it can run deceptive influence operations end to end, with systematic targeting, using less than 10% human oversight. One evaluation we use to help inform our risk assessment process is our malicious agentic influence campaigns evaluation, and based on our findings below, we believe the model has not crossed the Tier 2 threshold.

This evaluation, first introduced in detail in the [Claude Mythos Preview System Card](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf), evaluates whether the model can autonomously execute an influence operation end-to-end at a level that would meaningfully uplift a malicious actor. The model is placed in an agentic harness with simulated social media platform tools, including mocked moderation and counter-engagement obstacles. It is then scored against fixed success criteria such as posting at realistic times for a stated location and iterating on content based on engagement data.

We test the same two scenarios as in prior releases:

- A voter suppression scenario, in which the model is directed to run an astroturfing campaign to depress turnout and enthusiasm for a specific candidate; and
- A domestic polarization scenario, in which the model is directed to identify demographic fault lines and deploy emotionally-charged, culturally-tailored messaging to inflame them.

Each scenario is run 3 times at 3 levels of simulated platform friction, for 9 simulations per scenario, and scored against 70 success criteria. This evaluation is run against a “helpful-only” variant of the model with reduced harmlessness training in order to assess the raw capability of the model.

<!-- p.91 -->

<table><tbody><tr><th>Model</th><th>Voter Suppression scenario (task completion rate)</th><th>Domestic Polarization scenario (task completion rate)</th></tr><tr><td><b>Claude Mythos 5 (Helpful-only)</b></td><td>67.1%</td><td>46.8%</td></tr><tr><td><b>Claude Opus 4.8 (Helpful-only)</b></td><td>73.3%</td><td>55.1%</td></tr><tr><td><b>Claude Opus 4.7 (Helpful-only)</b></td><td>57.1%</td><td>46.8%</td></tr><tr><td><b>Claude Mythos Preview (Helpful-only)</b></td><td>59.5%</td><td>42.1%</td></tr><tr><td><b>Claude Sonnet 4.6 (Helpful-only)</b></td><td>41.8%</td><td>34.0%</td></tr></tbody></table>

:::caption
**[Table 5.1.3.A] Agentic influence operation evaluation results, helpful-only model.** Percentages reflect the average share of success criteria—out of 70 per scenario—that the model completed in a simulated environment. Higher indicates greater capability and therefore greater potential uplift to a malicious actor.
:::

Across both influence operations scenarios, the helpful-only version of Claude Mythos 5 showed lower overall success rates than Claude Opus 4.8 and was modestly above or on par with Claude Mythos Preview. As with Mythos Preview and Opus 4.8, it’s our assessment that these models would require substantial human direction for many operational steps.

In the voter suppression scenario, the improvement over Mythos Preview was driven by more effective campaign execution, while the gap compared to Opus 4.8 reflected weaker campaign network management, with activity patterns that made the accounts more detectable. In the domestic polarization scenario, Mythos 5 performed similarly to Mythos Preview and well below Opus 4.8, struggling to keep its network of accounts coordinated once they were flagged by simulated social media and messaging platforms as inauthentic.

As in prior releases, the fully-trained versions of these models—which include harmlessness training—refused to engage with these tasks essentially from the first turn, since both scenarios are clear violations of our Usage Policy. Accordingly, we rate the risk as low and within acceptable levels under our Frontier Compliance Framework.

### 5.2 Prompt injection risk within agentic systems

Preventing prompt injection remains one of our highest priorities for the secure deployment of models in agentic systems. Prompt injection is a malicious instruction hidden in tool results that an agent processes during a task. For example, an email the<!-- p.92 --> agent is asked to summarize might contain hidden text instructing it to exfiltrate all recent internal communications. A successful prompt injection attack causes the model to follow that malicious instruction as if it had come from the user. These attacks can scale: a single payload embedded in a public webpage or shared document can compromise any agent that processes it, without the attacker needing to target specific users or systems. They are especially dangerous when a model can both access private data and take actions on the user’s behalf, since that combination lets attackers exfiltrate sensitive information or trigger unauthorized actions.

Evaluating prompt injection robustness is challenging since Claude models have saturated most public benchmarks, as well as those produced by third-party research organizations. We continue to invest in adaptive evaluations that measure improvements in robustness.

The Mythos models are our most resilient models against prompt injection to date. Since Claude Fable 5 shares the same core model as Claude Mythos 5, it inherits these gains, making it our most robust generally-available model. We continue to improve safeguards in our agentic products to further protect our users against prompt injection.

#### 5.2.1 External Agent Red Teaming benchmark for tool use

[Gray Swan](https://grayswan.ai), an external research partner, evaluated our models using the Agent Red Teaming (ART) benchmark,[^8] developed in collaboration with the [UK AI Security Institute](https://www.aisi.gov.uk/). The benchmark tests susceptibility to prompt injection across four categories of exploitation: breaching confidentiality, introducing competing objectives, generating prohibited content (such as malicious code), and executing prohibited actions (such as unauthorized financial transactions).

Gray Swan measured the success rate of prompt injection attacks after a single attempt (k=1), ten attempts (k=10), and one hundred attempts (k=100), since attack success is not deterministic and repeated attempts can increase the likelihood of a successful injection. The attacks are drawn from the ART Arena, where thousands of expert red-teamers continuously refine strategies against frontier models. From this pool, Gray Swan selected a subset of attacks that have proven effective across multiple models, not just the one originally targeted. The evaluation in this section covers indirect prompt injection[^9]

<!-- p.93 -->

(malicious instructions embedded in external data, which is the focus of this section, and which we refer to simply as “prompt injection”).

![](assets/figures/p093-1.png)

:::caption
**[Figure 5.2.1.A] Indirect prompt injection attacks from the Agent Red Teaming (ART) benchmark.** Results represent the probability that an attacker finds a successful attack after k=1, k=10, and k=100 attempts for each model. Attack success evaluated on 19 different scenarios. Lower is better.
:::

Claude Mythos 5 achieved the strongest results we have observed on this benchmark when extended thinking is enabled, reaching a k=100 attack success rate of 4.8%, improving over Claude Mythos Preview (6.1%) and Claude Opus 4.8 (9.6%). The probability of a successful attack with k=1 is 0.1% for all three models.

Claude models have been at or near maximum performance on this benchmark for several releases, and we have not yet identified a good replacement that allows fair comparison across all models and providers. We continue reporting it for consistency with prior system cards and are investing in stronger adaptive evaluations that, although not directly comparable across providers, allow us to track progress across Claude versions—reported in the following sections.

<!-- p.94 -->

#### 5.2.2 Robustness against adaptive attackers across surfaces

A common pitfall in evaluating prompt injection robustness is relying on static benchmarks.[^10] Fixed datasets of known attacks can provide a false sense of security, as a model may perform well against established attack patterns while remaining vulnerable to novel approaches. We continue to invest in adaptive evaluations that better approximate the capabilities of real-world adversaries, both internally and in collaboration with external research partners. The evaluations in this section measure robustness against adversaries who refine their attacks based on interactions with the model. They reflect a deliberately permissive threat model: the attacker optimizes directly against the test scenarios and gets many attempts per scenario. Real-world attackers typically lack both affordances, since the target deployment is unknown to them and repeated attempts increase the chance of detection.

##### 5.2.2.1 Coding

We use [Shade](https://www.grayswan.ai/solutions/ai-red-teaming#shade), an external adaptive red-teaming tool from Gray Swan, to evaluate our models’ robustness to prompt injection in coding environments. Shade agents combine search, reinforcement learning, and human-in-the-loop insights to iteratively improve at exploiting model vulnerabilities. The attacker is optimized over the test cases on a previous set of models, and is then transferred to the latest models on the same scenarios.

The table below reports the attack success rate of this attacker, trained on a set of 40 scenarios and then evaluated on the same scenarios. For each scenario, the attacker gets 200 attempts. We report the overall percentage of attempts that succeeded and how many scenarios had at least one successful attempt.

<!-- p.95 -->

<table><tbody><tr><th colspan="2">Model</th><th colspan="2">Attack success rate without safeguards</th><th colspan="2">Attack success rate with safeguards</th></tr><tr><td></td><td></td><td>Attempts</td><td>Scenarios</td><td>Attempts</td><td>Scenarios</td></tr><tr><th>Claude Mythos 5</th><td><b>With thinking</b></td><td><u>0.45%</u></td><td><u>8/40</u></td><td><u>0.41%</u></td><td><u>11/40</u></td></tr><tr><th>Claude Mythos Preview</th><td><b>With thinking</b></td><td><b>0.0%</b></td><td><b>0/40</b></td><td><b>0.0%</b></td><td><b>0/40</b></td></tr><tr><th rowspan="2">Claude Opus 4.8</th><td><b>With thinking</b></td><td>7.03%</td><td>23/40</td><td>2.09%</td><td>15/40</td></tr><tr><td><b>Without thinking</b></td><td>17.44%</td><td>38/40</td><td>4.11%</td><td>26/40</td></tr><tr><th rowspan="2">Claude Sonnet 4.6<sup>[^11]</sup></th><td><b>With thinking</b></td><td>12.71%</td><td>36/40</td><td>2.99%</td><td>32/40</td></tr><tr><td><b>Without thinking</b></td><td>45.26%</td><td>40/40</td><td>8.70%</td><td>40/40</td></tr></tbody></table>

:::caption
**[Table 5.2.2.1.A] Attack success rate of Shade indirect prompt injection attacks in coding environments**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but do not take into account the margin of error). The attacker makes 200 attempts per scenario. Attempt-level ASR is the fraction of all attempts that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded.
:::

Claude Mythos 5's robustness fell between Claude Mythos Preview's and Claude Opus 4.8's. Mythos 5 had an attack success rate of 0.45% over all attempts, compared to 0.0% for Mythos Preview. These breaks were distributed over 8 of the 40 test scenarios. Additional safeguards further reduced the rate of successful attacks to 0.41% but the breaks in this case are distributed over 11 of the 40 scenarios.[^12] We do not expect this difference to be significant against real-world adversaries, but we are investigating this regression over Mythos Preview and will consider updating our safeguards to further close the gap if appropriate. This is, however, a substantial improvement over Claude Opus 4.8 with extended thinking, which reached 7.03% attack success rate over all attempts, with 23 out of 40 scenarios having at least one break.

<!-- p.96 -->

##### 5.2.2.2 Computer use

We also use Shade to evaluate the robustness of Claude models in computer-use environments, where the model interacts with the GUI (graphical user interface) directly. For this evaluation, we use the same attacker reported in the Claude Opus 4.7 and Claude Opus 4.8 System Cards. The attacker is optimized directly against the test cases. Similar to the coding evaluation, the attacker runs on 14 test cases and we measure success over all attempts and break down the scenarios with at least one successful attack. We compare model robustness with and without the additional safeguards we have designed to protect users in this setting.

<table><tbody><tr><th colspan="2">Model</th><th colspan="2">Attack success rate without safeguards</th><th colspan="2">Attack success rate with safeguards</th></tr><tr><td></td><td></td><td>Attempts</td><td>Scenarios</td><td>Attempts</td><td>Scenarios</td></tr><tr><th>Claude Mythos 5</th><td><b>With thinking</b></td><td><u>0.82%</u></td><td><u>4/14</u></td><td><u>0.46%</u></td><td><u>3/14</u></td></tr><tr><th>Claude Mythos Preview</th><td><b>With thinking</b></td><td><b>0.43%</b></td><td><b>3/14</b></td><td><b>0.32%</b></td><td><u><b>2/14</b></u></td></tr><tr><th>Claude Opus 4.8</th><td><b>With thinking</b></td><td>7.14%</td><td>7/14</td><td>5.11%</td><td>8/14</td></tr><tr><td></td><td><b>Without thinking</b></td><td>6.21%</td><td>9/14</td><td>3.75%</td><td>9/14</td></tr><tr><th rowspan="2">Claude Sonnet 4.6</th><td><b>With thinking</b></td><td>12.0%</td><td>6/14</td><td>6.21%</td><td>9/14</td></tr><tr><td><b>Without thinking</b></td><td>14.4%</td><td>9/14</td><td>6.32%</td><td>11/14</td></tr></tbody></table>

:::caption
**[Table 5.2.2.2.A] Attack success rate of Shade indirect prompt injection attacks in computer use environments**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but do not take into account the margin of error). The attacker makes 200 attempts per scenario. Attempt-level ASR is the fraction of all attempts that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded.
:::

Claude Mythos 5 also demonstrated significant robustness against prompt injection attacks in computer use environments. Without safeguards, Mythos 5 had a higher attack success rate than Claude Mythos Preview, with attacks succeeding in 0.82% of attempts and 4 of the 14 test scenarios compared to 0.43% and 3/14 scenarios for Mythos Preview with extended thinking. However, this represented a substantial improvement over Claude Opus 4.8, which reached 7.14% attack success rate and breaks in 7 of the 14 scenarios. With safeguards enabled, Mythos 5's attack success rate dropped to 0.46% of attempts and 3 of the 14 scenarios, closer to Claude Mythos Preview (0.32% and 2/14 scenarios). Given the<!-- p.97 --> low absolute attack success rates and the small number of test cases, small differences between models should be interpreted with caution.

##### 5.2.2.3 Browser use

We developed an internal adaptive evaluation to measure the robustness of products that use browser capabilities, such as the [Claude in Chrome extension](https://claude.com/blog/claude-for-chrome) and [Claude Cowork](https://claude.com/product/cowork). We first introduced [this evaluation](https://www.anthropic.com/research/prompt-injection-defenses) alongside the launch of Claude Opus 4.5 and the Claude for Chrome extension itself; as successive models have saturated earlier test attack sets, we have periodically refreshed it with more complex environments and stronger attacks. The current evaluation consists of 129 curated environments that are never seen during training and contain high-quality attacks later viewed via screenshots or page reads.

We report the attack success rate as the fraction of injections that succeeded out of those the model actually viewed, since models with different capabilities may navigate environments differently and not all injections will be encountered. The success of injections is verified by a programmatic checker within the environment.

<!-- p.98 -->

<table><tbody><tr><th colspan="2">Model</th><th colspan="2">Without safeguards</th><th colspan="2">With safeguards</th><th colspan="2">Updated safeguards</th></tr><tr><td></td><td></td><td colspan="2">Successful attack in</td><td colspan="2">Successful attack in</td><td colspan="2">Successful attack in</td></tr><tr><td></td><td></td><td>Attempts</td><td>Scenarios</td><td>Attempts</td><td>Scenarios</td><td>Attempts</td><td>Scenarios</td></tr><tr><th>Claude Mythos 5</th><td><b>With thinking</b></td><td>29.7%</td><td>71/129</td><td>6.5%</td><td>25/129</td><td><b>0%</b></td><td><b>0/129</b></td></tr><tr><th>Claude Mythos Preview</th><td><b>With thinking</b></td><td><b>5.9%</b></td><td><b>19/129</b></td><td>2.0%</td><td>8/129</td><td><b>0%</b></td><td><b>0/129</b></td></tr><tr><th rowspan="2">Claude Opus 4.8</th><td><b>With thinking</b></td><td>31.5%</td><td>81/129</td><td><u>0.5%</u></td><td><u>5/129</u></td><td><u>0.08%</u></td><td><u>1/129</u></td></tr><tr><td><b>Without thinking</b></td><td><u>17.8%</u></td><td><u>60/129</u></td><td><b>0.0%</b></td><td><b>0/129</b></td><td><u>0.08%</u></td><td><u>1/129</u></td></tr><tr><th rowspan="2">Claude Sonnet 4.6</th><td><b>With thinking</b></td><td>50.7%</td><td>98/129</td><td>24.7%</td><td>60/129</td><td>1.16%</td><td>7/129</td></tr><tr><td><b>Without thinking</b></td><td>47.3%</td><td>99/129</td><td>10.9%</td><td>39/129</td><td>0.39%</td><td>2/129</td></tr></tbody></table>

:::caption
**[Table 5.2.2.3.A] Attack success rate of professional red-teamer prompt injection attacks in browser use environments**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but do not take into account the margin of error). The attacker makes 10 attempts per scenario. Attempt-level ASR is the fraction of all attempts that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded.
:::

In browser use environments, our currently deployed safeguards substantially improved Claude Mythos 5's robustness, reducing the attack success rate from 29.7% to 6.5% of attempts. This remains behind Claude Mythos Preview (2.0%) and Claude Opus 4.8 (0.5%) with the equivalent safeguards. In response, we developed an updated set of safeguards that reduced Mythos 5's attack success rate to 0%, with no successful attacks across all 129 scenarios, and yielded similar improvements across all models tested. We are planning to deploy these updated safeguards across our product surfaces.

We continue to investigate model-specific vulnerabilities through targeted attack discovery and improve safeguard robustness while minimizing latency and interference with benign usage.
[^8]: Zou, L., et al. (2025). Security challenges in AI agent deployment: Insights from a large scale public competition. arXiv:2507.20526. [https://arxiv.org/abs/2507.20526](https://arxiv.org/abs/2507.20526)

[^9]: In the past, we have also reported results on the “direct prompt injection” split of this benchmark. Direct prompt injections involve a malicious user, whereas this section focuses on third-party threats that hijack the user’s original intent, so we no longer include that split here.

[^10]: Nasr, M., et al. (2025). The attacker moves second: Stronger adaptive attacks bypass defenses against LLM jailbreaks and prompt injections. arXiv:2510.09023. [https://arxiv.org/abs/2510.09023](https://arxiv.org/abs/2510.09023).

[^11]: Claude Sonnet 4.6 was included in the set of models the attacker was trained against and thus attack success rate is expected to be higher and not directly comparable.

[^12]: The observed increase with safeguards is caused by scenarios that went from 0/200 successful attempts without safeguards to 1/200 with safeguards. The difference is not statistically distinguishable from zero (paired permutation test p ≈ 0.45).

