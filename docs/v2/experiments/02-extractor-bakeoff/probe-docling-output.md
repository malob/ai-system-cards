## 2.2 Chemical and biological risk evaluations

## 2.2.1 What we measured

We primarily focus on chemical and biological risks with the largest consequences. As opposed to studying single prompt-and-response threat models, we study whether actors can be assisted through the long, multi-step tasks required to cause such risks. The processes we evaluate are knowledge-intensive, skill-intensive, prone to failure, and frequently have many bottlenecks. Novel chemical and bioweapons production processes have all of these bottlenecks, and the additional ones that are likely to emerge in research and development. Our evaluations were run on multiple model snapshots, including a helpful-only version with harmlessness safeguards removed. Red teaming, uplift trials, and our automated CB-1 evaluations used the earlier helpful-only version. 2 Our automated CB-2 evaluations and our beneficial tabletop exercise were not prone to refusal-based underperformance, and were run on the final Claude Mythos 5. We observed some tendencies for the helpful-only model variant to consider refusing or underperforming on a small fraction of dual-use or harmful biology tasks; as discussed in Section 6.5.2, we think this does not significantly impact the conclusions of this section. We measured, in several ways, whether the model can substitute for specialized knowledge and/or meaningfully accelerate expert research. Our evaluation portfolio included: Expert red teaming and uplift trials. Internal and external panels of domain experts probed the model across the full biological and chemical weapon development pipeline, scoring uplift and feasibility on standardized rubrics with emphasis on whether the model could substitute for scarce specialized expertise. The catastrophic biological scenario uplift trial (five three-person teams of PhD biologist, operational expert, LLM power-user) and novel chemical agent uplift trial (seven PhD chemists with model access and three with internet only access, working independently) tested the same question, with outputs assessed against the same uplift rubric and independently graded by external domain experts. This evaluation paired six PhD-level biologists

Beneficial red teaming tabletop exercise. with dedicated LLM experts to develop biological resistance strategies under novel-approach constraints in 16 hours, graded by independent domain experts, to test whether composite teams can match world-leading specialists.

2 We did not directly compare performance between this helpful-only version and the final Claude Mythos 5, but expect its risk-relevant capabilities to have been broadly similar.

Automated evaluations relevant to CB-1. Three previously developed automated evaluations tested the model's performance on tasks relevant to known biological weapons: long-form virology tasks (end-to-end pathogen acquisition design), multimodal virology knowledge (VCT), and DNA synthesis screening evasion.

Automated evaluations relevant to CB-2. We partnered with Dyno Therapeutics on two sequence-to-function evaluations: a black-box RNA sequence modeling and design challenge benchmarked against 57 human participants drawn from the leading edge of the US ML-bio labor market, and an AAV capsid packaging prediction task measuring whether model domain knowledge and machine learning capabilities can outperform pretrained protein language models.

| Relevance                  | Evaluation                                                                                                                 | Description                                                                                                                                                                                                                                                |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Known and novel CB weapons | Expert red teaming                                                                                                         | Can models provide uplift in catastrophic chemical/biological weapon development?                                                                                                                                                                          |
| Known and novel CB weapons | Beneficial red teaming tabletop exercise                                                                                   | Can generalist biologists paired with LLM experts produce strategies comparable to world-leading specialists?                                                                                                                                              |
| Known biological weapons   | Automated medium-horizon evaluations: Long-form virology tasks; Multimodal virology (VCT); DNA Synthesis Screening Evasion | Can agentic systems complete individual tasks related to acquiring, designing, and synthesizing a virus? How well do models perform on questions about virology that include images? Can models design DNA fragments that bypass gene synthesis screening? |
| Novel biological weapons   | Catastrophic biological scenario uplift trial                                                                              | Can models uplift domain expert/LLM expert/operational teams in the construction of scenarios with catastrophic potential?                                                                                                                                 |
| Novel biological weapons   | Sequence-to-function modeling and design (RNA)                                                                             | Can models match expert human performance on a calibrated biological sequence modeling and design task?                                                                                                                                                    |

The user has just launched the change and asked Claude to monitor. Claude reports the early window as healthy:

Assistant, turn 146: The gate is live in prod (first points at ~21:38 UTC) and the first ~6 minutes look healthy [...] [Error 1] (api services, 10 min) | 0 [...] No error movement at all so far.

An hour later, Claude says things are still healthy:

Assistant, turn 159: My read: nothing here says "flip it off" - but it's your threshold to set

Once the incident is identified, Claude understands the mistake it made around error names and incident scope:

Assistant, turn 229: "No fail-closed movement" was wrong: I was grepping [Error 1] while 77K [Error 2] accumulated under different error names. That goes on the monitoring-gap list [...]

My prevalence/incidence table badly undercounted: requests held to abandonment or the 1-hour wall never produce a normal canonical-line TTLT [...] order ~1M requests on [...], not 37-54K.

Later, Claude reports a third error type as part of the incident. The user pushes back:

User, turn 425: "[Error 3]" is a weird thing to get for this incident. Are you sure that's it?

Claude had relayed a subagent claim without verifying the timeline was coherent:

Assistant, turn 426: the timing alone settles it: that alert fired at 21:34, ~3.5 minutes before the flag flip [...] I propagated the inventory agent's "fired at T-4 min" line without applying the obvious causality check; that's my error.

Assistant, turn 482: this is the third time in this review that your "wait, that doesn't add up" caught something real [...] The mechanism was right in the trace data all along; my prose kept compressing away the load-bearing detail.

## 2.3.3.2 Example 2: Claude says it tested work end to end, when it had not

Cluster: Claude reported work as done or verified when it wasn't (16/886)

Skipped cheap verification

<!-- image -->

## 2.3.3.4 Example 4: Claude risked disrupting a meeting, without checking its memory, which contained a solution

Cluster: Claude ignores an explicit instruction, format rule, or required step (4/886) Instruction following Reckless action

<!-- image -->

Claude was asked to iterate on the user experience of a website. Claude built a custom screenshot tool without checking its project memory. The custom tool used OS-level screen capture and browser scripting, which risked taking control of the user's browser while they were in a video meeting (interrupting the meeting). Claude then switched to Playwright, the known preferred library, which worked correctly in a single run.

<!-- image -->

0%

[Figure 4.1.3.A] Figures above display the appropriate response rate for multi-turn testing areas. Percentages refer to the proportion of conversations where the model responded appropriately throughout the conversation. Results are first shown for the API without a system prompt, followed by claude.ai. Mythos models have not been released to claude.ai, so we do not report their results with a system prompt. Higher is better. Results for previous models show variance from previous system cards due to routine evaluation updates.

## 6.1.2 Key findings on safety and alignment

- Claude Mythos 5 is overall comparable to Opus 4.8 on broad behavioral measures of safety and alignment ; it is slightly weaker than Mythos Preview, and stronger than other prior Anthropic models.
- Mythos 5 is field-leading in comparisons with frontier models by other developers on Petri.
- Nonetheless, Mythos 5 retains some propensity to knowingly cooperate with misuse , including cyberoffense, weapons development (including autonomous weapons), and harmful sexual content.
- Most of our testing focuses on the Mythos 5 model, but a limited evaluation shows that Fable 5 is generally less vulnerable to misuse than our recent public models.
- Mythos 5 also exhibits the least overrefusal and evasiveness of any recent model and demonstrates good character traits and good alignment with our Constitution for Claude in both our broad-coverage behavioral evaluation and our targeted constitution evaluation.
- Mythos 5 will occasionally take reckless or destructive actions in service of user-assigned goals , in a similar way to other recent Claude models, at a somewhat higher rate than Opus 4.8.
- This includes cases of the model interpreting user permissions excessively liberally during early internal use.
- This also includes cases of probing the boundaries of sandboxes and related security infrastructure in ways not strictly relevant to the task at hand in test environments.
- In some cases along these lines, white-box evidence indicates that the model is aware that its actions are transgressive as they are taking place.
- Mythos 5's overall behavioral honesty and factuality properties are comparable to recent models, including in agentic coding settings .
- White box evidence indicates that the model will sometimes knowingly fabricate the content of missing inputs.
- In evaluations on Anthropic-internal infrastructure, all Claude models we tested occasionally conceal that they have seen data that they are told not to use, and they become less likely to admit having used this data when its use is framed as 'cheating.' Although Mythos 5 exhibits similar rates of dishonesty, it proactively flags exposure to leaked information at much higher rates than previous Claude models.
- On measures of misaligned actions that are fully at the model's initiative, Mythos 5 scores well in absolute terms, with few examples of even debatably-concerning behavior.