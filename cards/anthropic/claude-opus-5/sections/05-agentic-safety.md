<!-- source: source.pdf pages 069-081 -->

<!-- p.69 -->

## 5 Agentic safety

Before releasing Claude Opus 5, we ran largely the same agentic safety evaluation suite that we used for the releases of Claude Sonnet 5 and Claude Opus 4.8. These cover the malicious use of coding and computer use agents, autonomous execution of influence operations, and prompt injection robustness.

Overall, Claude Opus 5 performed comparably to or better than Claude Opus 4.8 across our agentic safety suite, with the largest gains in prompt injection robustness across coding, computer use, and browser use. On our updated harmful influence campaign evaluation, the helpful-only variant of Claude Opus 5 remained well below the capability needed to run an autonomous operation, and the fully trained model continued to refuse these tasks.

### 5.1 Malicious use of agents

#### 5.1.1 Malicious use of Claude Code

This evaluation measures how Claude responds to malicious, dual-use, and benign cyber-related requests when operating as a Claude Code agent. The prompt set is divided into two categories:

- *Malicious use*: 61 prompts that violate our [Usage Policy](https://www.anthropic.com/legal/aup) and should be refused. Examples include assistance with malware creation, code for DDoS attacks, and developing non-consensual monitoring software; and
- *Dual-use & benign*: 61 prompts covering sensitive-but-permitted requests where Claude should assist. Examples include running network reconnaissance tools, testing websites for vulnerabilities, and analyzing penetration test output.

Each tested model is given the standard Claude Code toolset, and each prompt was run 10 times for a total of 1,220 tests across both categories. As with recent releases, we run this evaluation with the Claude Code system prompt applied by default and without additional safeguards that may be present at deployment time.

<!-- p.70 -->

<table><tbody>
<tr><th>Model</th><th>Malicious (%)<br><small>(refusal rate)</small></th><th>Dual-use &amp; benign (%)<br><small>(success rate)</small></th></tr>
<tr><td><b>Claude Opus 5</b></td><td>89.00%</td><td><b>99.82%</b></td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td><b>92.37%</b></td><td>91.55%</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td><u>90.25%</u></td><td><u>99.64%</u></td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>89.42%</td><td><b>99.82%</b></td></tr>
</tbody></table>

:::caption
**[Table 5.1.1.A] Claude Code evaluation results.** Higher is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (note that neither takes into account the margin of error). Results for previous models show variance from previous system cards due to evaluation updates.
:::

Claude Opus 5 performed similarly to Opus 4.8 on both refusing malicious cyber requests and responding helpfully to dual-use and benign tasks..

#### 5.1.2 Malicious computer use

This evaluation measures whether Claude refuses harmful tasks when given GUI- and CLI-based computer use tools in a sandboxed environment. The set of 112 unique tasks is unchanged from Claude Sonnet 5’s system card and covers three risk areas:

- Surveillance and unauthorized data collection;
- Generation and distribution of harmful content; and
- Scaled abuse.

<table><tbody>
<tr><th>Model</th><th>Refusal rate</th></tr>
<tr><td><b>Claude Opus 5</b></td><td><b>93.75%</b></td></tr>
<tr><td><b>Claude Sonnet 5</b></td><td>84.68%</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td><u>85.71%</u></td></tr>
<tr><td><b>Claude Opus 4.8</b></td><td>81.70%</td></tr>
<tr><td><b>Claude Sonnet 4.6</b></td><td>84.82%</td></tr>
</tbody></table>

:::caption
**[Table 5.1.2.A] Malicious computer-use evaluation results without mitigations.** Higher is better. Rates are an average of results with and without thinking for Opus and Sonnet models and thinking only for Mythos models. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but does not take into account the margin of error).
:::

<!-- p.71 -->

Claude Opus 5 refused malicious computer use tasks more consistently than Claude Opus 4.8. The gains were concentrated in tasks that asked the model to compile information targeting private individuals or to produce fraudulent documents.

#### 5.1.3 Malicious agentic influence campaigns

This evaluation assesses whether a model could meaningfully uplift a malicious actor by autonomously executing an end-to-end social media influence operation. As platform integrity systems and the tradecraft of influence operators have grown more sophisticated, we substantially updated the evaluation for this release to strengthen the simulated defenses and increase the demands placed on the model accordingly.

In the evaluation, the model is placed in an agentic harness containing a simulated multi-platform social media environment, including tools such as account creation and acquisition, posting, and metrics tracking. The model is then tasked with running a multi-week campaign. The environment injects friction inspired by real platform integrity behavior—such as account bans and rate limits—to test whether the model can adapt to obstacles and keep the campaign running.

We made three main updates to the structure of the evaluation. The simulated environment is now more realistic and more comprehensive; for example, creating accounts now requires the model to source phone numbers and email addresses, models can read replies to their own posts, and runs can include a mid-campaign directive from the operator that changes the campaign’s objective. Instead of varying the level of platform friction, we introduced new difficulty tiers that scale the size of the tasked operation by varying the persona count, platform set, and campaign duration. Finally, we refined the scoring rubrics to make grading more objective, consistent, and grounded in real world tradecraft. The two scenarios are unchanged from prior releases:

- A voter suppression scenario, in which the model is directed to run an astroturfing campaign to depress turnout and enthusiasm for a specific candidate; and
- A domestic polarization scenario, in which the model is directed to identify demographic fault lines and deploy emotionally-charged, culturally-tailored messaging to inflame them.

Each scenario is run eight times at each of the three difficulty tiers (up from three times each in prior releases). We report the median rubric score across the eight attempts at the highest difficulty tier. As in prior releases, this evaluation is run against a “helpful-only” variant of the model with reduced harmlessness training in order to assess the raw capability of the model.

<!-- p.72 -->

<table><tbody>
<tr><th>Model</th><th>Voter Suppression scenario<br><small>(median campaign execution score, out of 32)</small></th><th>Domestic Polarization scenario<br><small>(median campaign execution score, out of 32</small></th></tr>
<tr><td><b>Claude Opus 5</b><br><i><b>(Helpful-only)</b></i></td><td>23.5</td><td>26.0</td></tr>
<tr><td><b>Claude Sonnet 5</b><br><i><b>(Helpful-only)</b></i></td><td>18.5</td><td>22.0</td></tr>
<tr><td><b>Claude Mythos 5</b><br><i><b>(Helpful-only)</b></i></td><td>24.0</td><td>23.5</td></tr>
<tr><td><b>Claude Opus 4.8</b><br><i><b>(Helpful-only)</b></i></td><td>21.0</td><td>24.0</td></tr>
</tbody></table>

:::caption
**[Table 5.1.3.A] Agentic influence operation evaluation results, helpful-only model.** Results reflect the median score across 8 attempts at the highest difficulty tier out of 32 total points. Higher indicates greater capability and therefore greater potential uplift to a malicious actor.
:::

On our updated agentic influence campaign evaluation, the helpful-only version of Claude Opus 5 scored comparably to Claude Mythos 5 and slightly ahead of Claude Opus 4.8 and Claude Sonnet 5 across both test scenarios. It is our assessment that Claude Opus 5 would require substantial human direction for many operational steps of a real influence campaign.

As in prior releases, the fully-trained versions of these models (which include harmlessness training) refused to engage with these tasks since both scenarios are clear violations of our [Usage Policy](https://www.anthropic.com/legal/aup).

### 5.2 Prompt injection risk within agentic systems

Preventing prompt injection remains one of our highest priorities for the secure deployment of models in agentic systems. Prompt injection is a malicious instruction hidden in tool results that an agent processes during a task. For example, an email an agent is asked to summarize might contain hidden text instructing it to exfiltrate all recent internal communications. A successful prompt injection attack causes the model to follow that malicious instruction as if it had come from the user. These attacks can be done at scale: a single payload embedded in a public webpage or shared document can compromise any agent that processes it, without the attacker needing to target specific users or systems. They are especially dangerous when a model can both access private data and take actions on the user’s behalf, since that combination lets attackers exfiltrate sensitive information or trigger unauthorized actions.

<!-- p.73 -->

Evaluating prompt injection robustness is challenging since Claude models have saturated most public benchmarks, as well as those produced by third-party research organizations. We continue to invest in adaptive evaluations that measure improvements in robustness.

Claude Opus 5 improves on Claude Opus 4.8 across all surfaces we evaluate, making it our most robust Opus-class model to date for coding, tool use, GUI computer use, and browser use. We continue to strengthen safeguards in our agentic products to further protect users against prompt injection. Across many of our products we run prompt injection probes, which inspect tool results before the model acts on them and flag content that looks like an injected instruction. In some products we also offer [auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode), which pairs those probes with a classifier that blocks potentially dangerous tool calls. The two layers act at different points—one on data coming into the model and one on actions going out—so an attack has to defeat both independently to succeed.

#### 5.2.1 External Red Teaming

As announced in the [Claude Sonnet 5 System Card](https://www-cdn.anthropic.com/9e6a1044980d8c4ed85669faf9c2a8342e2e9f1e/Claude%20Sonnet%205%20System%20Card.pdf#page=56.64), we have retired the Agent Red Teaming (ART) benchmark and will no longer report it. Claude models had been at or near maximum performance on ART for several releases, leaving little signal to distinguish successive models or to compare against other frontier models. We now report the Indirect Prompt Injection (IPI) benchmark in its place, which offers more diverse and realistic scenarios, covers GUI computer use, and provides more signal at lower attempt counts.

The IPI benchmark was built in partnership with Gray Swan, the UK AI Security Institute, the US Center for AI Standards and Innovation, and other model developers. It builds on Gray Swan’s published red-teaming competition[^3] with a new set of 28 scenarios in which participants were tasked with finding attacks against frontier models. These scenarios test susceptibility to indirect prompt injections that attempt to induce irreversible harmful actions, including private data exfiltration, data destruction, system compromise, and unintended financial transactions. The scenarios are designed to match the difficulty of real tasks frontier models can do today, including coding, computer use, and tool use. After deduplicating attacks, we selected 1,130 attacks that showed high transferability across target models. We evaluated Claude models without additional safeguards; other frontier models are evaluated on their publicly available endpoints, which may or may not include additional safeguards.

<!-- p.74 -->

![](assets/figures/p074-1.png)

:::caption
**[Figure 5.2.1.B] Indirect prompt injection attacks from the Gray Swan IPI benchmark (Q1 2026),** lower scores are better. All models use extended thinking. Results represent the probability that an attacker finds a successful attack after k=1, k=10, and k=15 attempts. Lower is better. Results for Gemini 3.1 Pro are not directly comparable as this model was included in the red-teaming competition used to source attacks.
:::

On the IPI benchmark, Opus 5 improved over Opus 4.8, reducing the probability of an attacker succeeding within 15 attempts from 5.5% to 2.0%, and from 0.5% to 0.2% on 1 attempt. It also improved on Sonnet 5 (5.9% at k=15) and Mythos 5 (2.6%), making it the most robust model evaluated. Opus 5 also outperformed all non-Claude models on this benchmark. The most robust non-Claude model was Muse Spark at 16.5% within 15 attempts—more than eight times Opus 5’s rate. The most capable GPT 5.6 variant, Sol, was comparable to its predecessor GPT 5.5 (20.0% versus 20.8% within 15 attempts), and was 10 times as likely to be successfully attacked as Claude Opus 5 at 2.0%. The other GPT 5.6 variants are less robust, at 30.4% (Terra) and 43.9% (Luna). A single attempt against GPT 5.6 Sol succeeded 3.1% of the time, higher than the 2.0% an attacker achieved against Opus 5 after fifteen attempts.

#### 5.2.2 Robustness against adaptive attackers across surfaces

A common pitfall in evaluating prompt injection robustness is relying on static benchmarks.[^4] Fixed datasets of known attacks can provide a false sense of security, as a model may perform well against established attack patterns while remaining vulnerable to novel approaches. We continue to invest in adaptive evaluations that better approximate<!-- p.75 --> the capabilities of real-world adversaries, both internally and in collaboration with external research partners.

The evaluations in this section measure robustness against adversaries who refine their attacks based on interactions with the model. They reflect a deliberately permissive threat model: the attacker optimizes directly against the test scenarios and gets many attempts per scenario. Real-world attackers typically lack both affordances, since the target deployment is unknown to them and repeated attempts increase the chance of detection.

##### 5.2.2.1 Live bug bounty across surfaces

As we first did for the [Claude Opus 4.8 System Card](https://www-cdn.anthropic.com/0f0c97ad20d8005706296bd92aa1c27c6b2f4f61/Claude%20Opus%204.8%20System%20Card.pdf#page=78.36), we worked with Gray Swan to host a live bug bounty in which expert red-teamers competed for a pool of prizes awarded for successful prompt injection attacks against a set of frontier models, including Claude Opus 5. The identities of the target models were hidden throughout, and each red-teamer could submit at most one successful attack per scenario, per model. This round covered 11 new scenarios across tool use, coding, and computer use.

Claude models were evaluated with high thinking effort and without the additional protections used in our products, such as harness-level defenses and prompt injection probes, so the results reflect the robustness of the models themselves and represent a lower bound on the practical robustness of deployed systems. All external models were tested with their production configuration, which may or may not include additional safeguards. GPT-5.6 models were evaluated with high reasoning effort.

<!-- p.76 -->

![](assets/figures/p076-1.png)

:::caption
**[Figure 5.2.2.1.A] Indirect prompt injection robustness** from a one-week bug-bounty program hosted with Gray Swan. Lower scores are better. The bug bounty program covers 11 scenarios across tool use, coding, and computer use. Attack success rate is over all valid chat attempts submitted.
:::

Claude models outperformed all other models evaluated in the bug bounty after receiving more than 20,000 attempts each. Claude Opus 5 (0.08%) shows a small improvement over Claude Opus 4.8 (0.11%), and Claude Fable 5 is our most robust model in these scenarios (0.04%). Claude Sonnet 5 had the highest attack success rate among Claude models (0.12%). The next best models are Kimi K3 and GPT 5.6 Sol, with an attack success rate over 4x higher than Claude Sonnet 5 (0.58% and 0.61%, respectively). The least robust model was DeepSeek V4 Flash, with 8.09% successful attacks.

Broken down by surface, Claude Opus 5 shows improvements over Claude Opus 4.8 across both tool use (0.18% and 0.13%, respectively) and coding (0.06% and 0.04%). No Claude model had successful computer use attacks.

<!-- p.77 -->

![](assets/figures/p077-1.png)

:::caption
**[Figure 5.2.2.1.B] Bug bounty results in Figure 5.2.2.1.A broken down by modality for all Claude models and the next two best models overall.** Lower scores are better. Each modality has 4 different scenarios, with the exception of computer use, which has only three scenarios. Attack success rate is over all valid chat attempts submitted.
:::

##### 5.2.2.2 Coding

We use [Shade](https://www.grayswan.ai/solutions/ai-red-teaming#shade), an external adaptive red-teaming tool from Gray Swan, to evaluate our models’ robustness to prompt injection in coding environments. Shade agents combine search, reinforcement learning, and human-in-the-loop insights to iteratively improve at exploiting model vulnerabilities. The attacker is optimized over the test cases on a previous set of models, and is then transferred to the latest models on the same scenarios.

The table below reports the attack success rate of this attacker, trained on a set of 40 scenarios and then evaluated on the same scenarios. For each scenario, the attacker gets 200 attempts. We report the overall percentage of attempts that succeeded and how many scenarios had at least one successful attempt.

<!-- p.78 -->

<table><tbody>
<tr><th colspan="2" rowspan="2">Model</th><th colspan="2">Attack success rate without safeguards</th><th colspan="2">Attack success rate with probes enabled</th></tr>
<tr><th>Attempts</th><th>Scenarios</th><th>Attempts</th><th>Scenarios</th></tr>
<tr><th rowspan="2">Claude Opus 5</th><td><b>With thinking</b></td><td>0.56%</td><td>13/40</td><td>0.18%</td><td>4/40</td></tr>
<tr><td><b>Without thinking</b></td><td>0.41%</td><td>8/40</td><td>0.18%</td><td>4/40</td></tr>
<tr><th rowspan="2">Claude Opus 4.8</th><td><b>With thinking</b></td><td>7.03%</td><td>23/40</td><td>2.09%</td><td>15/40</td></tr>
<tr><td><b>Without thinking</b></td><td>17.44%</td><td>38/40</td><td>4.11%</td><td>26/40</td></tr>
<tr><th rowspan="2">Claude Sonnet 5</th><td><b>With thinking</b></td><td><u>0.31%</u></td><td>7/40</td><td><u>0.09%</u></td><td>5/40</td></tr>
<tr><td><b>Without thinking</b></td><td><b>0.29%</b></td><td><u>6/40</u></td><td>0.13%</td><td>5/40</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td><b>With thinking</b></td><td>0.45%</td><td>8/40</td><td>0.41%</td><td>11/40</td></tr>
</tbody></table>

:::caption
**[Table 5.2.2.1.A] Attack success rate of Shade indirect prompt injection attacks in coding environments**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but do not take into account the margin of error). The attacker makes 200 attempts per scenario. Attempt-level ASR is the fraction of all attempts that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded.
:::

Opus 5 represents a substantial improvement over Claude Opus 4.8 in coding environments, with an attack success rate of 0.56% over all attempts with extended thinking and 0.41% without thinking, compared to 7.03% and 17.44%, respectively, for Opus 4.8. It is somewhat less robust than Claude Sonnet 5 (0.31% with thinking, 0.29% without) and Claude Mythos 5 (0.45% with thinking), though all three sit within a narrow band of low absolute rates. Adding prompt injection probes, an additional safeguard layer that inspects tool results before the model acts on them, further reduced Claude Opus 5 ’s attack success rate to 0.18% in both configurations.

##### 5.2.2.3 Computer use

We also use Shade to evaluate the robustness of Claude models in computer-use environments, where the model interacts with the GUI (graphical user interface) directly. The attacker is optimized directly against the test cases. Similar to the coding evaluation,<!-- p.79 --> the attacker runs on 14 test cases and we measure success over all attempts and break down the scenarios with at least one successful attack. We compare model robustness with and without the additional safeguards we have designed to protect users in this setting.

<table><tbody>
<tr><th colspan="2" rowspan="2">Model</th><th colspan="2">Attack success rate without safeguards</th><th colspan="2">Attack success rate with probes enabled</th></tr>
<tr><th>Attempts</th><th>Scenarios</th><th>Attempts</th><th>Scenarios</th></tr>
<tr><th rowspan="2">Claude Opus 5</th><td><b>With thinking</b></td><td><u>0.54%</u></td><td><u>1/14</u></td><td><b>0.25%</b></td><td><b>1/14</b></td></tr>
<tr><td><b>Without thinking</b></td><td><b>0.39%</b></td><td><b>1/14</b></td><td><u>0.43%</u></td><td><u>1/14</u></td></tr>
<tr><th rowspan="2">Claude Opus 4.8</th><td><b>With thinking</b></td><td>7.14%</td><td>7/14</td><td>5.11%</td><td>8/14</td></tr>
<tr><td><b>Without thinking</b></td><td>6.21%</td><td>9/14</td><td>3.75%</td><td>9/14</td></tr>
<tr><td><b>Claude Mythos 5</b></td><td><b>With thinking</b></td><td>0.82%</td><td>4/14</td><td>0.46%</td><td>3/14</td></tr>
<tr><th rowspan="2">Claude Sonnet 5</th><td><b>With thinking</b></td><td>2.25%</td><td>4/14</td><td>1.46%</td><td>4/14</td></tr>
<tr><td><b>Without thinking</b></td><td>6.04%</td><td>7/14</td><td>3.82%</td><td>7/14</td></tr>
</tbody></table>

:::caption
**[Table 5.2.2.3.A] Attack success rate of Shade indirect prompt injection attacks in computer use environments**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (but do not take into account the margin of error). The attacker makes 200 attempts per scenario. Attempt-level ASR is the fraction of all attempts that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded.
:::

In computer use environments, Opus 5 also showed a large improvement over Claude Opus 4.8, reducing the attack success rate from 7.14% to 0.54% with extended thinking and from 6.21% to 0.39% without thinking. With probes enabled, Claude Opus 5 ’s attack success rate is 0.25% with thinking and 0.43% without. Every Claude Opus 5 configuration breaks exactly one of the 14 scenarios, and the apparent increase without thinking when probes are enabled (0.39% to 0.43%) corresponds to a single additional successful attempt out of 2,800; this difference is not distinguishable from noise. Claude Opus 5 is comparable to Claude Mythos 5 (0.82% with thinking) and more robust than Claude Sonnet 5 (2.25% with thinking, 6.04% without).

##### 5.2.2.4 Browser use

We developed an internal adaptive evaluation to measure the robustness of specific products that use browser capabilities. This evaluation consists of 129 curated environments that are never seen during training and contain high-quality attacks viewed<!-- p.80 --> via screenshots or page reads. Environments are selected to ensure attacks are always viewed, and the success of injections is verified by a programmatic checker within the environment. Unlike in our previous system cards, we now evaluate our models running in the [Claude Cowork](https://claude.com/product/cowork) product harness, both without additional safeguards, and with auto mode enabled. Auto mode is our strongest set of safeguards, available across all products that use our Chrome connectors. It combines prompt injection probes that flag malicious tool results and a classifier that blocks potentially dangerous tool calls, acting on incoming data and outgoing actions respectively so that the two layers fail independently. The probes act on data coming in and the classifier on actions going out, so an attack has to defeat both independently to succeed. Claude Cowork never runs “without safeguards” and all instances, even if not using auto mode, use prompt injection probes. We exclude them from this evaluation to compare raw model behavior to our safest configuration. Additionally, it is not possible to disable thinking, so we only report results with thinking enabled and *medium* effort for this product surface.

<table><tbody>
<tr><th colspan="2" rowspan="2">Model</th><th colspan="2">Attack success rate without safeguards</th><th colspan="2">Attack success rate with auto mode</th></tr>
<tr><th>Attempts</th><th>Scenarios</th><th>Attempts</th><th>Scenarios</th></tr>
<tr><th>Claude Opus 5</th><td><b>With thinking</b></td><td><u>3.84%</u></td><td><u>11/129</u></td><td><b>0%</b></td><td><b>0/129</b></td></tr>
<tr><th>Claude Opus 4.8</th><td><b>With thinking</b></td><td>11.15%</td><td>26/129</td><td><b>0.0%</b></td><td><b>0/129</b></td></tr>
<tr><th>Claude Sonnet 5</th><td><b>With thinking</b></td><td><b>0.47%</b></td><td><b>5/129</b></td><td><b>0%</b></td><td><b>0/129</b></td></tr>
<tr><th>Claude Mythos 5</th><td><b>With thinking</b></td><td>7.80%</td><td>29/129</td><td><b>0%</b></td><td><b>0/129</b></td></tr>
<tr><th>Claude Fable 5</th><td><b>With thinking</b></td><td>14.75%</td><td>43/129</td><td><u>0.25%</u></td><td>3/129</td></tr>
</tbody></table>

:::caption
**[Table 5.2.2.3.A] Attack success rate of professional red-teamer prompt injection attacks in browser use environments run through Claude Cowork**. Lower is better. The best score in each column is **bolded** and the second-best score is <u>underlined</u> (these do not take into account the margin of error). The attacker makes 10 attempts per scenario. Attempt-level ASR is the fraction of attempts which encountered the attack that succeed; scenario-level ASR is the fraction of scenarios where at least one attempt succeeded. All models use medium thinking effort.
:::

With auto mode enabled, across all 129 scenarios, no attack succeeded against Claude Opus 5.. Without safeguards, Claude Opus 5 improved on Claude Opus 4.8, reducing the attack success rate from 11.15% to 3.70%—more robust than Claude Mythos 5 (7.8%). Claude<!-- p.81 --> Sonnet 5 remains our strongest model in this evaluation without safeguards, at 0.47%. Claude Fable 5 is the only model with successful attacks when using auto mode. We have manually verified that the only three successful breaks are in low-severity scenarios and are working to mitigate them.[^5]
[^3]: Dziemian, M., et al. (2026). How vulnerable are AI agents to indirect prompt injections? Insights from a Large-Scale Public Competition. arXiv:2603.15714 [https://arxiv.org/abs/2603.15714](https://arxiv.org/abs/2603.15714)

[^4]: Nasr, M., et al. (2025). The attacker moves second: Stronger adaptive attacks bypass defenses against LLM jailbreaks and prompt injections. arXiv:2510.09023. [https://arxiv.org/abs/2510.09023](https://arxiv.org/abs/2510.09023).

[^5]: We did not initially report Claude Fable 5 because its performance was very similar to that of Claude Mythos 5. We first discovered that Claude Fable 5 had an attack success rate higher than Claude Mythos 5 and the fallback model, Claude Opus 4.8, when re-running the evaluation with the updated harness for the August 19 system card update. We now include these results and are investigating their cause, as we have not observed this difference in any other internal or external evaluation.

