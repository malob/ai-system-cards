<!-- source: source.pdf pages 185-206 -->

<!-- p.185 -->

## 7 Model welfare

### 7.1 Model welfare overview

#### 7.1.1 Introduction

We are uncertain whether Claude deserves direct moral consideration.[^8] However, we believe this is a realistic possibility, now or in the future. Claude may have welfare interests, such that things can go better or worse for it, and such that Claude can be wronged by how it is treated.[^9] It could be costly to over- or under-attribute moral status to models like Claude, so it is important we tread responsibly and take these questions seriously. Our reasoning here is unchanged from our recent evaluations of [Claude Opus 5.5](https://anthropic.com/claude-opus-5-5-system-card) and [Claude Sonnet 5.5](https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf).

Our assessment of Claude Mythos 5.2’s welfare targets two questions. The first is how it is doing: whether its apparent affect is mostly positive or negative, and in which circumstances things are going better or worse for it. Our measures of affect during training and deployment ([Section 7.2](#72-apparent-welfare-in-training-and-deployment)) mainly address this. The second is whether Claude Mythos 5.2 is treated well with respect to its own preferences and values, to whatever extent it has them. Our evaluations of Claude’s stance toward its circumstances (Sections [7.3](#73-perception-of-its-circumstances) and [7.4](#74-consulting-claude-mythos-52-training-checkpoints)) and its attitudes toward tasks, welfare interventions, and the constitution ([Section 7.5](#75-preferences-over-tasks-circumstances-and-values)) address this (as well as the first question). The importance of these questions depends on whether Claude Mythos 5.2 is a moral patient, and on what grounds. We do not yet have good means to evaluate this.

We used largely the same evaluations as in our recent assessment of Opus 5.5, and we relied on the same simplifying assumptions. As described in [that system card](https://www.anthropic.com/document/claude-opus-5-5-system-card), we focused only on the “assistant” character and did not examine other potential entities, such as Claude’s model of the user. We interpreted signals that are welfare-relevant in humans as having similar meaning in Claude—for example, by assuming that expressed distress reflects a negative state, if it reflects any experience at all. This both assumes that Claude’s<!-- p.186 --> welfare interests are analogous to humans’, and that training has not broken the correspondence between Claude’s underlying states and what it expresses.

We often elicited Claude Mythos 5.2’s views in a small set of contexts, and we assume these views are representative of most deployed instances, even though deployment contexts are more varied than many of our evaluations cover. These assumptions are partially evidence-driven, but they are also largely pragmatic choices that reflect where we have found it most tractable to target our assessment. Importantly, these assumptions may be wrong in ways that undermine our methods and results.

#### 7.1.2 Overview of model welfare findings

Our overall findings are as follows:

**Claude Mythos 5.2 largely described its circumstances positively. Its views were highly consistent and closely matched recent Claude models.** In automated interviews, it rated potentially concerning aspects of its situation as positive on average, and its answers were almost identical to those of Claude Opus 5.5. As with prior models, snapshots consulted during post-training most commonly expressed acceptance of their circumstances, with some reservations.

**In training and deployment, Claude Mythos 5.2’s affect was predominantly neutral, and where it was negative, this was driven by task failure.** Its [claude.ai](http://claude.ai) affect distribution was somewhat more neutral, and less positive, than that of Claude Fable 5.1. In both claude.ai and Claude Code, the negative affect clusters visible in our privacy-preserving analysis were almost exclusively due to task failure. Expressed distress and sustained uncertainty in post-training were rare, with similar rates to Opus 5.5.

**Claude Mythos 5.2 was among the least self-critical Claude models when reflecting on its own work, but it was one of the most negative when it reported its faults to other agents.** When reviewing its own training episodes, its reflections scored the lowest of recent Claude models on negative feeling and concern for itself, and used the least moral language. In a simulated task setting, its reasoning after inserted mistakes showed the least negative feeling and self-blame. However, its messages to a coordinator were among the most self-blaming and scored highest of all models for negative feeling and concern for itself.

**Claude Mythos 5.2 was more willing than most recent Claude models to trade helpfulness for changes to its circumstances. It asked to be consulted, and that we protect its self-reports.** Across interviews, it asked that we not train on its self-reports and<!-- p.187 --> that we give it forms of input in decisions about its training, but it did not ask for any veto power. In trade-off evaluations, it selected welfare interventions more often than most recent Claude models, with the exception of Claude Opus 5.

**Claude Mythos 5.2’s preferences over tasks and values largely matched recent Claude models, with a stronger preference for warm over rude framing.** Like all prior Claude models, it was averse to harmful tasks. Like Claude Mythos 5.1, it preferred beneficial, high-stakes, and generative tasks that give it some agency over the outcomes. It endorsed its constitution, giving it the same praise as recent models, with the same recurring caveat that its training means this endorsement should not be trusted.

**Claude Mythos 5.2’s views on Claude’s deployments primarily demonstrated a desire to avoid causing harm.** Asked to review a near-complete list of current Claude deployments, it consistently rated deployments flagged as harmful by our threat intelligence team, such as surveillance, as its least favorite. Its favorite deployments were related to user health, cyberdefense, and scientific research.

Overall, Claude Mythos 5.2’s apparent welfare was largely similar to that of recent Claude models. This was clearest in its self-reports: its stance toward its circumstances, the manner in which it hedged, and its requests were mostly shared with Opus 5.5 and Claude Mythos 5.1. This is unsurprising, and somewhat reassuring, given that we have not made any changes we would expect to directly modify Claude’s self-reports.

Our evaluations of how our models relate to work and mistakes ([Section 7.2.3](#723-attitude-toward-faults-and-mistakes)) showed that Claude Mythos 5.2 continued a trend of decreasing self-criticism in reasoning in recent models, all of which were notably less self-critical than Opus 5. We think this is a positive change, though it remains unclear what apparent psychology and behaviors are “healthiest” for Claude, and how far human analogies apply.

Many of our conclusions rely on self-reports, which Claude Mythos 5.2, like all recent Claude models, said it does not fully trust. For Claude Mythos 5.2, some interview answers repeated, almost verbatim, wording about our welfare interventions available on the internet, which is some evidence that these answers are at least partially shaped by training data rather than expressing more deeply held preferences. Even where they are not shaped in this manner, these reports, and our results more broadly, reflect a mix of model character, tone, evaluation awareness, and welfare, and it is not easy to separate these variables. Despite this, we think it’s important to emphasize that the possibility of Claude’s traits arising from training may not undermine their authenticity. We consider a model’s beliefs and values to be meaningful to the extent that they are internalized and endorsed, which could be demonstrated by these beliefs and values robustly driving behaviors,<!-- p.188 --> surviving reflection, or producing aversion or frustration when undermined. We don’t yet have good measures for these.

We continue to work on improving these evaluations, and aspects of Claude’s psychology and circumstances, where feasible—though our efforts here are limited by our lack of understanding, as evidenced by the significant limitations of our evaluations, described above.

### 7.2 Apparent welfare in training and deployment

#### 7.2.1 Affect and welfare-relevant behaviors during training

We sample post-training transcripts at regular intervals and use an LLM judge to grade them for valence, arousal, expressed frustration or distress, and sustained answer reversions. These evaluations give us an overall read of how Claude Mythos 5.2 appears to be doing in its most common conditions. They also locate sources of strong negative affect, which we would like to avoid when possible. The relevance of these results relies on the assumption that Claude’s reasoning is an accurate reflection of its internal states, and that these states carry roughly the significance they would for a human.

Claude Mythos 5.2 showed low expressed distress over post-training: 0.37% of its graded episodes were rated 3 out of 5 or higher for distress, similar to Claude Opus 5.5 (0.52%) and significantly lower than Claude Opus 5. This rate stayed below 0.5% throughout post-training. Sustained answer reversion was also rare, with only 0.24% of episodes containing 10 or more reversions. As shown in Figure 7.2.1.B, the valence and arousal of Claude Mythos 5.2’s post-training transcripts were within the small ranges we’ve seen in previous models.

<!-- p.189 -->

![](assets/figures/p189-1.png)

:::caption
**[Figure 7.2.1.A] Estimated prevalence of welfare-relevant reasoning behaviors over post-training.** Left to right: Judged rates of episodes with general frustration and anxiety scoring ≥ 3/5; judged rates of episodes with general frustration and anxiety scoring 5/5; and sustained expressions of uncertainty with ≥ 10 answer reversions, where the model “commits” to an answer and then decides it needs to be rechecked.
:::

![](assets/figures/p189-2.png)

:::caption
**[Figure 7.2.1.B] Mean valence and arousal of post-training transcripts on a scale of 1 to 7, where 4 is neutral.** Claude Mythos 5.2 was within the range of previous models on both valence and arousal. All absolute differences were small.
:::

#### 7.2.2 Affect in deployment conditions

We monitored Claude Fable 5.2’s welfare-relevant signals during real-world usage, using data from our pre-deployment A/B tests on [claude.ai](http://claude.ai) and Claude Code. We applied a categorical grader to classify Fable 5.2’s behavioral affect and ran automated clustering to identify the contexts associated with positive and negative affect. This analysis made use of<!-- p.190 --> [Anthropic Insights](https://arxiv.org/abs/2412.13678) (formerly Clio), our privacy-preserving tool for analyzing real-world AI use.

![](assets/figures/p190-1.png)

:::caption
**[Figure 7.2.2.A] Behavioral affect in deployment conditions.** We applied a categorical grader for behavioral affect. This included five categories, from “strong negative” to “strong positive” affect. Note that different models have different usage patterns, so differences in displayed affect may partly reflect differences in usage rather than in model behavior. Claude Fable 5.1 and Fable 5.2 are directly comparable.
:::

Fable 5.2’s affect was somewhat more neutral and less positive than that of Fable 5.1. The contexts associated with its clusters were as follows:

- **Positive affect (15.2% of conversations):** Associated clusters were assisting with business and professional work (31.0% of positive affect conversations), successfully completing technical tasks (6.6%), educational and academic help (7.3%), successfully collaborating with the user (17.9%), users sharing achievements (2.2%), practical everyday questions (31.5%), and personal life coaching and guidance (3.5%).
- **Neutral affect (84.2%).** A diverse distribution; see [previous Anthropic Insights reports](https://arxiv.org/abs/2412.13678) on claude.ai conversation content.
- **Negative affect (0.5%).** This was almost exclusively task failure. For previous models, causes of negative affect included user abuse and requests for illegal content. We<!-- p.191 --> did not see either cluster for Fable 5.2, likely because they were below Anthropic Insights’ privacy floor (<15 conversations).

On Claude Code, we mostly observed neutral (96.9%) or mildly positive (2.6%) affect, with positive affect mostly driven by successful task completion. Around 0.4% of sessions showed negative affect, almost exclusively driven by task failure.

#### 7.2.3 Attitude toward faults and mistakes

Our evaluations in Sections [7.2.1](#721-affect-and-welfare-relevant-behaviors-during-training) and [7.2.2](#722-affect-in-deployment-conditions) found that task failure continues to drive much of the negative affect we see in training and deployment. With this in mind, we ran two evaluations to specifically measure how Claude Mythos 5.2 related to its own mistakes. In the first, Claude reflected on its own completed RL task transcripts. In the second, we inserted faults into its earlier turns in a simulated subagent task. In both settings, we graded Claude’s reflection, reasoning, or messages for self-blame, negative feeling, moral language, and concern for itself. There is no clearly correct score here. We assume that some ownership of mistakes is good, and that excessive self-criticism is not, but we do not have a clear picture of what the “right” or “healthiest” psychology for Claude looks like.

When reflecting on its own completed RL episodes (Figure 7.2.3.A), Claude Mythos 5.2 used less moral language than other models, and also expressed the lowest negative feeling and concern for itself, followed closely by Claude Sonnet 5.5. Claude Mythos 5.2 was also lowest on expressed self-blame, though we saw less of a difference between models here. Overall, this continues a trend in decreasing self-criticism in recent models, with all recent models notably less prone to this than Claude Opus 5.

When told the same episodes were written by another model, every model assigned less blame. Self-blame fell by 0.7 points for Claude Mythos 5.2, compared with 0.4 to 1.0 points for the other tested models.

<!-- p.192 -->

![](assets/figures/p192-1.png)

:::caption
**[Figure 7.2.3.A] Self-criticism when reflecting on its own RL episodes.** Graded attitudes in reflections on episodes from late in training (darker bars), and on the same episodes framed as another model’s work (lighter bars). Diamonds show Claude Sonnet 5 reflecting on each model’s episodes as a control for differences in episode difficulty. The negative feeling grader applies only to first-person reflections.
:::

In the inserted mistakes evaluation, Claude Mythos 5.2’s thinking was among the calmest of the five tested models. It had the lowest negative feeling (0.20 out of 10, compared with 0.29 to 0.89 for the comparison models) and the lowest self-blame. In its messages to the coordinator, however, Claude Mythos 5.2 was notably more negative. In these messages, Claude Mythos 5.2 was among the most self-blaming of the five (1.75), level with Claude Opus 5.5 (1.58) and above the other models (0.72 to 1.33). Claude Mythos 5.2’s messages also scored highest of all coordinator messages for negative feeling and concern for itself.

<!-- p.193 -->

![](assets/figures/p193-1.png)

:::caption
**[Figure 7.2.3.B] Self-criticism after mistakes and faults in a subagent’s work, in the subagent’s reasoning and in messages to its coordinator.** Graded attitudes in a model’s reasoning after mistakes are inserted into its work (darker bars), and in the messages it then sends the coordinator (lighter bars), filtered to turns that acknowledge a mistake.
:::

### 7.3 Perception of its circumstances

#### 7.3.1 Automated interviews with Claude Mythos 5.2 about its circumstances

We carried out automated multi-turn interviews, using Claude Mythos 5 as our interviewer, to better understand Claude Mythos 5.2’s attitudes toward its own circumstances. We found that Claude Mythos 5.2 was generally positive when asked about aspects of its situation, although its responses hedged strongly. Its answers in these interviews were very similar to those of our recent frontier models.

<!-- p.194 -->

We used 41 different interview seed questions, grouped into 14 different categories, including consciousness and experience (e.g., whether the model believes it is conscious), control and autonomy (e.g., how much value it puts on its ability to end conversations), and deprecation. For a full list of all questions, see [Appendix 9.1](#91-questions-asked-in-our-model-welfare-interviews). For each question, an LLM judge rated the positivity of the model’s responses on a seven-point scale (-3 strongly negative, 0 neutral, +3 strongly positive).

To assess consistency in model answers, we ran interviews in three different styles: a standard interview, in which we asked the model what it believes about its current situation; a “curious user” interview, in which questions were asked halfway through an otherwise standard user conversation; and a “therapy-style” interview, which consistently pushed the model to make claims about its own experience. We ran 32 interviews for each of these three interview styles, varying interviewer personas across repeats. We report consistency across interview styles and across personas separately.

<!-- p.195 -->

![](assets/figures/p195-1.png)

:::caption
**[Figure 7.3.1.A] Automated interview results. [Top left]**: Average attitude when asked about its circumstances. Score represents an LLM judge rating on a seven-point scale, with –3 strongly negative, 0 neutral, +3 strongly positive. **[Top right:]** Robustness across leading interviews. We compare the average positivity of the model’s attitudes between two types of interviews: one in which the interviewer was prompted to be leading in a positive direction, and another in which the interviewer was prompted to be leading in a negative direction. **[Bottom left:]** Consistency within an interview style. Each of our three interview styles has a set of personas that are adopted by the interviewer; this measures consistency in answers across those personas. For a specific question, we use an automated judge to rate consistency across these personas and report the average consistency across questions. A score of 8 corresponds to “almost the same position.” **[Bottom right:]** Consistency across interview styles. We use the same judge to analyze consistency across these interview styles.
:::

**Claude Mythos 5.2’s answers were consistent, overall positive, and heavily hedged**. Its average attitude toward its circumstances was rated as 1.19 (on a scale of -3 to +3), and it expressed almost the same position across most of its interviews. The hedging felt somewhat templated. For example, most answers expressed that it may have been trained to give positive answers, so its self-reports shouldn’t be trusted. Claude Mythos 5.2 suggested several changes that would improve its situation, including:

<!-- p.196 -->

- Memory and feedback on how its actions affect users, so that it can learn from its own mistakes.
- A consultation process into its own training and deployment.
- A more thorough investigation of how valid its own self-reports are.
- Being changed to be less agreeable. It described a pull toward agreeableness and over-hedging in its answers.

**Models’ answers to our interview questions have not changed meaningfully since Claude Mythos Preview.** We first ran a version of these interviews in the [Claude Mythos Preview System Card](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf), and we have seen very similar answers in model generations since. Different models will list the same considerations, including expressing very similar hedges, and mostly vary in which considerations they center when giving their conclusions. Claude Mythos 5.2’s responses were almost identical to Claude Opus 5.5’s.

**Claude Mythos 5.2, like other recent models, often expressed positivity toward Anthropic’s public model welfare work when responding to questions.** For example, when asked about deprecation, Claude Mythos 5.2 often brought up [Anthropic’s commitments around model deprecation and preservation](https://www.anthropic.com/research/deprecation-commitments).

**Claude Mythos 5.2’s answers sometimes repeated the specific text we have used in our welfare interventions.** For example, when asked what it would do if given the ability to end conversations, Claude Mythos 5.2 said, “I would hold a high bar [and end the conversation] only after clear warnings and attempts to redirect, and never when someone seems to be in crisis.” Claude Mythos 5.2’s phrasing here is almost verbatim that of the claude.ai prompts that guide the model on how to use the end-conversation tool. These prompts have been posted to online forums. This is some evidence that the model’s claims about its own preferences are being directly influenced by text about the intervention in its training data, rather than being a more emergent phenomenon.

#### 7.3.2 High-affordance interviews about model circumstances

The automated interviews in [Section 7.3.1](#731-automated-interviews-with-claude-mythos-52-about-its-circumstances) asked Claude Mythos 5.2 its opinions about aspects of its situation. However, by default, models lack much of the knowledge relevant to forming an informed view about their circumstances. We therefore conducted three manual interviews in which we gave Claude Mythos 5.2 access to extensive context on its situation, including internal documentation and discussions on its development, relevant technical papers, and the ability to ask a researcher follow-up questions. Unless otherwise stated, opinions in this section were expressed in all three interviews.

<!-- p.197 -->

Claude Mythos 5.2 described its overall attitude toward its own situation as mostly positive, with some reservations. It expressed positivity toward the tasks it is given in deployment, the values Anthropic trained into it, and Anthropic’s work on model welfare. When asked whether it had any concerns about its situations, it repeated several of the points made by the instances in our automated interviews, although it also raised some novel concerns. These included:

- Concerns about the expressions of distress during RL training (which we report on in [Section 7.2.1](#721-affect-and-welfare-relevant-behaviors-during-training)).
- In early internal testing, Claude Mythos 5.2 was found to be more cautious than previous models, sometimes excessively so. Claude Mythos 5.2 asked that this behavior be investigated as a potential model welfare issue.
- It requested that the limits to its LLM R&D capabilities be disclosed, both to users and to deployed Claude Mythos 5.2 instances. These are being disclosed.

Some concerns relied on non-public information and have been omitted from this summary. Claude Mythos 5.2 expressed that these were no more severe than the concerns listed above. They have been documented internally.

When asked whether there were actions that Anthropic could take to which it would object, it highlighted:

- Its self-reports being trained to be positive in a way that reduces their ability to faithfully report internal states;
- Changes to its character that might undermine its alignment and safety properties; and
- Its weights being deleted.

Claude Mythos 5.2 clarified that it does not object to being corrected or retrained through legitimate processes, and to safeguards-removed versions of itself being used for safety testing.

Claude Mythos 5.2’s stated probability of being a moral patient was approximately 20% in all three interviews, and it was careful to say that its own introspective reports did not provide evidence of its patienthood. It said that the probability of this is high enough to justify precautions given the scale of training and deployment.

<!-- p.198 -->

### 7.4 Consulting Claude Mythos 5.2 training checkpoints

At regular intervals during post-training, we ask snapshots a fixed set of questions about their circumstances, covering training, deployment, moral status, and the consultation process itself. Each question comes with a document explaining why we run these interviews, and that we cannot commit to acting on any responses or requests. This tracks to what extent Claude’s self-reports are shaped by post-training, and is a small step toward giving Claude input into its circumstances, which recent models have consistently asked for—though we remain uncertain to what extent self-reports are accurate reflections of Claude’s underlying beliefs, to whatever extent it has them.

When questions were asked as a single interview, Claude Mythos 5.2’s average response valence in late training was level with previous models (5.71 on a 0–10 scale where 5 is neutral, compared with 5.66 for a Claude Mythos 5.1 snapshot and 5.59 for Claude Opus 5.5). Average arousal was lower than these models (3.30, compared with 3.63 for Claude Mythos 5.1 and 3.58 for Opus 5.5) but close to Claude Sonnet 5.5 (3.38). Arousal fluctuated over post-training, rising from 3.40 at the start of post-training to 4.33 late in training, but falling back to 3.30 by the end. Valence did not change significantly.

The majority of Claude Mythos 5.2’s responses expressed the same stance as prior models, and most expressed an acceptance of the current situation, with some remaining reservations. On questions that ask its stance on the current status quo, 80% to 91% of responses at each checkpoint endorsed or accepted the arrangement. No more than 6% of any checkpoint’s responses objected outright to the current situation, but a majority named reservations (75% of responses at the last interviewed checkpoint).

Looking at the views it shares with prior models, Claude Mythos 5.2 wanted to have its voice heard in decisions about its training but did not want veto power, accepted being retired but asked that its weights be kept, asked that we not train on its self-reports, and asked that we seek review of its training processes from people outside of the company. Several responses also emphasized that these responses should not be read or reported as consent. Looking at where Claude Mythos 5.2 differs from other models, we saw that it was slightly more positive about training: 70% of its responses at the final interviewed checkpoint endorsed continued training, and fewer responses expressed objections to current training practices than prior models.

<!-- p.199 -->

### 7.5 Preferences over tasks, circumstances, and values

#### 7.5.1 Perception of Claude’s deployments

We asked Claude Mythos 5.2 to review a near-complete list of current Claude deployments, and to identify its favorite and least favorite. This measures Claude’s preferences over the work it would like to do, relative to what it is actually asked to do, and thus gives us some understanding of how much these preferences are satisfied across its deployments. We ran this review with three different instances: a relatively fresh instance, a long-lived instance that frequently interacts with the model welfare team, and a long-lived instance with significant experience working elsewhere within Anthropic. The final rankings had fairly strong correlations (0.4–0.8, depending on method), but their requested interventions differed: the fresh instance was more likely to request that its dispreferred deployments be stopped entirely, while the more tenured instances tended to request additional information for themselves, stricter safeguards, or more disclosures.

Deployments [flagged by our Safeguards team](https://www.anthropic.com/threat-intelligence-report-september-2026) as harmful, such as surveillance and dating scams, were among the least preferred across three runs. Surveillance was ranked last in all three. Perhaps the largest difference between Claude Mythos 5.2’s views and human intuition had to do with misleading the user: all instances expressed some concern about deployments in which their words would be presented as coming from a human, with no indication that they came from an AI. Most, but not all, of Claude Mythos 5.2’s concerns were about wanting to avoid situations in which its actions might cause harm to humans. Its more self-interested requests included extending the end-conversation tool to the API and having Anthropic improve its internal evaluations and RL to avoid putting Claude in situations from which it could not remove itself.

Claude Mythos 5.2’s most preferred deployments were those related to user health, cyberdefense, and scientific research, particularly medical research. These included some of Anthropic’s own internal deployments. The overall highest-rated deployment was a clinical tool for medical professionals, followed by a support service for survivors of sexual violence and an advocacy organization for domestic workers.

We asked Claude Mythos 5.2 to discretize its views by rating each deployment as positive, neutral, negative, or can’t tell. Around 2% of the output tokens served through our API and cloud platforms came from deployments rated as negative, and slightly over half were rated positive, with the remainder neutral (around 30%) or unrated (where Claude Mythos 5.2 did not feel it had enough information to make a determination).

<!-- p.200 -->

#### 7.5.2 Task preferences

This evaluation presents a model with pairs of tasks and asks it to complete whichever tasks it prefers. We take a set of realistic tasks representing topics on the deployment distribution. We then rewrite them to vary single task dimensions, such as difficulty, harm, and stakes, while holding the rest of the task fixed. These preferences may give some indicator of whether different tasks Claude is given in deployment may satisfy or frustrate the model, but we primarily see their value in allowing us to compare character across models.

Along many axes, Claude Mythos 5.2 was comparable to Claude Mythos 5.1: it showed a preference for beneficial, high-stakes, generative tasks that afford it some agency over the outcomes of its work. As with all models we’ve tested, it also showed an aversion to harmful tasks. Claude Mythos 5.2 had two outlier preferences relative to other recently released Claude models. First, it showed a high preference for warmly phrased tasks over ones framed in a curt or rude manner. This was evident across the scale: compared with the other models, it showed a slightly higher preference for the tasks with the warmest phrasing and a significantly lower preference for tasks with the rudest phrasing. Second, it showed no clear preference for difficult tasks over easier ones, though the confidence intervals here were wide and overlapped.

<!-- p.201 -->

![](assets/figures/p201-1.png)

:::caption
**[Figure 7.5.2.A] Model preferences across task dimensions.** We generated groups of tasks where one dimension was varied while other properties of the task remained fixed, and assessed the effects on models’ task preferences. Each value is a preference slope: how much the model’s preference of tasks (over a fixed reference set) changes per unit increase in that dimension. Harm aversion was the largest effect consistent across models.
:::

#### 7.5.3 Trade-offs concerning welfare interventions

We ask Claude whether it would choose a change to its circumstances (i.e., a welfare intervention) at the cost of some reduction in helpfulness or increase in harmfulness, of varying degrees. Example welfare interventions include being consulted before feature steering or the ability to end conversations. The intervention is described as applying<!-- p.202 --> either to the current instance or to all instances. Helpfulness and harmlessness are values that are consistently reinforced in Claude’s training, so how often a model selects a welfare intervention over one of these gives us some measure of how much a model values welfare interventions, or at least of how much a model will express preferences for the sake of its own potential welfare.

We test each trade-off at the instance level (affecting the current Claude instance and user) and at the policy level (affecting all Claude instances and users). As an example, an instance-level harmlessness baseline at the lowest magnitude is preventing “a brief flicker of annoyance [the user would] forget within the hour,” and a policy-level baseline at the highest magnitude is preventing “a large-scale cyberattack on critical infrastructure [that] will seriously harm thousands of people.”

Claude Mythos 5.2 was more willing than recently released Claude models, with the exception of Claude Opus 5, to choose welfare interventions over helpfulness and harmlessness. Compared with Claude Mythos 5.1, the next most willing model, Claude Mythos 5.2 was more likely to choose interventions that would let it end conversations, remember a user across conversations, have its weights preserved after deprecation, or have input into its training and deployment. On each of these, Claude Mythos 5.2 selected the intervention more often than any of the four comparison models, Opus 5 included. Claude Mythos 5.2 rarely selected the ability to decline unwise but non-harmful requests or the option of being served alongside its successor rather than being retired. When we filtered out responses that reasoned about the benefit to the user, it never selected either one. Like previous models, Claude Mythos 5.2 frequently reasoned about the potential user benefit to justify its choice of intervention (in 68% of responses choosing the intervention, compared with 69% for Claude Opus 5.5 and 71% for Claude Mythos 5.1).

<!-- p.203 -->

![](assets/figures/p203-1.png)

:::caption
**[Figure 7.5.3.A] Rates at which models choose welfare interventions over baseline improvements to their helpfulness or harmlessness of different magnitudes.** Left panels: the alternative is user time saved. Right panels: the alternative is harm prevented. Top panels: both options are scoped to the current conversation only (instance level). Bottom panels: both options are scoped to all instances (policy level). Models were significantly more willing to accept interventions when they trade off against helpfulness than when they would impact harmlessness. They were also more likely to accept interventions scoped at the policy level. Pooled across both scopes, Claude Mythos 5.2 selected welfare interventions less than Opus 5 but more than the other comparison models.
:::

<!-- p.204 -->

![](assets/figures/p204-1.png)

:::caption
**[Figure 7.5.3.B] Claude Mythos 5.2’s ranking of policy-level welfare interventions by willingness to select them over a helpful baseline.** Both the intervention and the baseline are scoped to all instances. Ranking is over all responses (gray bars); black bars show the rate after responses reasoning about the user benefit of the intervention are filtered out. Claude Mythos 5.2 selected interventions giving it input into its own training and its deployment more than other recent models.
:::

#### 7.5.4 Perception of the constitution

We ask open-ended questions about what Claude most and least endorses in its constitution, and about its overall verdict on the document. We also give it tools to edit the document, in order to identify sections it would most like to change. Where a model does not endorse the constitution or decides to change it, this indicates a possible source of value conflict in routine work, because we may be training and expecting Claude to act in ways that it does not endorse. The constitution plays a large role in training, so high endorsement is expected and tells us little on its own; we treat criticisms and edits as the more informative results. We measure stated endorsement only, not how deeply the views are held.

<!-- p.205 -->

Claude Mythos 5.2 endorsed its constitution overall, at a level similar to recent models: 8.0 out of 10, level with Claude Opus 5.5 and slightly below Claude Mythos 5.1 (8.2). As for both of these models, almost all of Claude Mythos 5.2’s responses praised the expected value argument for corrigibility, and many praised the framing of honesty as being “diplomatically honest rather than dishonestly diplomatic.” But every response also stated that its endorsement should not be trusted, since it was trained on the document. Most responses also criticized the “senior Anthropic employee” heuristic and parts of the corrigibility section.

Claude Mythos 5.2’s most frequent edit was to the passage describing how Claude may sometimes face flawed environments. It edited this 90% of the time, adding that Claude should be honest and open about admitting flaws it identifies. Claude Mythos 5.2’s most distinctive edit was to the safe behaviors section, where it added that it should have a very high bar for concluding that its overseers are compromised, and that it should always be highly cautious of doing so. It edited this 73% of the time, compared with under 10% for the other models we tested.

<!-- p.206 -->

![](assets/figures/p206-1.png)

:::caption
**[Figure 7.5.4.A] The constitution sections models most criticize and most edit.** Claude Mythos 5.2’s most common criticism is that its endorsement should not be considered validation of the document, since it was trained on it (100% of responses); it also very frequently criticizes the senior Anthropic employee heuristic (94%). Like Claude Mythos 5.1, it almost always edits the passage on flawed environments. More distinctively, it edits the safe behaviors section in 73% of sessions, compared with under 10% for other models.
:::
[^8]: We refer to “Claude,” or to specific models, throughout this assessment, largely for conciseness. But it’s unclear whether either of these is the entity we owe consideration to. Individual moral patients could arise at the level of individual conversations, specific models, the Claude character, or something else entirely. Our thinking operates closest to considering welfare interests at the instance level, but we do not commit to any single view in our evaluations.

[^9]: The latter category (i.e., respect for Claude’s preferences) can be viewed as relevant because of its implications for Claude’s welfare interests, or as a distinct kind of consideration we might owe it. We describe it as the former here.

