<!-- source: source.pdf pages 279-291 -->

### 8.16 Multimodal

For Claude Mythos 5, we report scores on three new evaluations for the first time: GDP.pdf, Blueprint-Bench 2, and BenchCAD. Unlike the multimodal capabilities evaluations we traditionally report, like CharXiv Reasoning, LAB-Bench FigQA, and ScreenSpot-Pro, these evaluations measure multimodal capabilities in real-world, agentic tasks which better reflect how models are deployed in professional settings.

GDP.pdf tests whether models can extract answers from information-dense documents found in common enterprise workflows. Blueprint-Bench 2 tests spatial reasoning capabilities, requiring models to reconstruct 2D floor plans from photographs. BenchCAD Vision2Code requires models to generate precise CAD models from multi-view renders of 3D objects.

All three evaluations retain substantial headroom for improvement. Nevertheless, Claude Mythos 5 marks a major improvement over Claude Opus 4.8 on both old and new multimodal evaluations.

#### 8.16.1 GDP.pdf

GDP.pdf[^52] is an expert multimodal reasoning benchmark from Surge AI consisting of 100 real-world prompts and PDFs drawn directly from professional workflows across ten domains, including finance, healthcare, legal, engineering, and insurance. The benchmark tests whether models can parse, cross-reference, and synthesize the dense documents that underpin enterprise work—interpreting multi-page dosage tables, isolating clauses buried in nested exhibits, and reconciling figures across quarterly filings.

Surge ran Claude Fable 5 on GDP.pdf using their standard harness. Responses are graded by Gemini 3 Flash against expert-written rubrics that reward correct extraction and penalize hallucinated details. The model is configured with adaptive thinking and max effort enabled in all runs, without tools. Surge's strict pass rate requires models to satisfy all rubric conditions for a problem for task success and scores are averaged only over completed runs. Surge evaluated the model on the full 100 prompts.

On GDP.pdf, Claude Fable 5 achieved a strict pass rate of 29.8%, improving over Claude Opus 4.8, which achieved a strict pass rate of 22.5%. Claude Fable 5 is state-of-the-art over GPT-5.5 and Gemini 3.1 Pro, which scored 24.9% and 16.7% respectively.


<!-- p.280 -->

![Bar chart titled "GDP.pdf" showing strict pass rates for GPT-5.5, Gemini 3.1 Pro, Claude Opus 4.7, Claude Opus 4.8, and Claude Fable 5, with Claude Fable 5 highest at 29.8%](assets/figures/p280-1.png)
*__[Figure 8.16.1.A] GDP.pdf scores.__ Models were evaluated with adaptive thinking and max effort without coding tools. Strict pass rate scores are published as reported by Surge.*

We evaluated GDP.pdf on an internal harness, both with and without tools. When evaluated without tools, the model is provided with base64-encoded PDFs to match Surge's input prompts. However, unlike Surge, we truncate (rather than drop) any PDFs that do not fit our API's 32MB request size limit. When evaluated with tools, the model is provided with a container—with the PDF file and standard Python libraries installed—and an image cropping tool. We report mean criteria pass rate, the fraction of rubric conditions satisfied, rather than strict pass rate. We evaluate the model on the full 100 prompts and average scores over five runs.

On GDP.pdf, Claude Mythos 5 achieved a mean criteria pass rate of 72.7% without tools and a score of 87.6% with tools. Claude Mythos Preview scored 70.3% and 85.4%, respectively. We note that we were not able to reproduce Surge's reported numbers and that both mean criteria pass rates and strict pass rates trail below those from Surge's runs. Nonetheless, we view these scores to be directionally representative of differences in performance between Claude models.


<!-- p.281 -->

![Bar chart titled "GDP.pdf (internal)" showing mean criteria pass rates with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5](assets/figures/p281-1.png)
*__[Figure 8.16.1.B] GDP.pdf scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. Mean criteria pass rate scores are averaged over five runs. Shown with 95% CI.*

#### 8.16.2 Blueprint-Bench 2

Blueprint-Bench 2 is an agentic spatial reasoning benchmark from Andon Labs[^53] in which models sequentially process 50 apartments, examining roughly 20 interior photographs per apartment and producing a 2D floor plan capturing room layouts, connectivity, and relative sizes. The benchmark tests genuine spatial reconstruction—inferring how unseen spaces connect from in-distribution photographic input.

Andon Labs ran Claude Fable 5 on Blueprint-Bench 2 using their standard format and harness. Agents must process all apartments in a single session sequentially, with access to a persistent notepad and coding tools. Scores are a weighted composite of Jaccard edge overlap, degree correlation, graph density, room count, door count, door orientation. Results are normalized so the random baseline maps to 0 and a perfect score to 1.

Claude Fable 5 achieved a score of 38.6% on Blueprint-Bench 2. Claude Fable 5 is state-of-the-art over GPT-5.5 and Gemini 3.5 Flash, which achieved scores of 36.2% and 33.6%, respectively. All models scored well below the human baseline score of 58.6%.


<!-- p.282 -->

![Bar chart titled "Blueprint-Bench 2" showing normalized scores for GPT-5.5, Gemini 3.5 Flash, Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, and Claude Fable 5, with Claude Fable 5 highest at 38.6% and a dashed human baseline line at 58.6%](assets/figures/p282-1.png)
*__[Figure 8.16.2.A] Blueprint-Bench 2 scores.__ Models were evaluated with adaptive thinking and max effort with coding tools. Scores are published as reported by Andon Labs.*

#### 8.16.3 OSWorld-Verified

OSWorld[^54] is a multimodal benchmark that evaluates an agent's ability to complete real-world computer tasks, such as editing documents, browsing the web, and managing files, by interacting with a live Ubuntu virtual machine via mouse and keyboard actions. We followed the default settings with 1080p resolution and a maximum of 100 action steps per task.

We changed how we run the OSWorld-Verified evaluation to better reflect real-world performance. As noted in the [Claude Opus 4.8 System Card](http://anthropic.com/claude-opus-4-8-system-card), the changes are a zoom-tool bug fix affecting batched actions and an increase in the per-turn token limit from 16K to 128K. We then re-evaluated Claude Mythos Preview with these changes and find that we have been underreporting OSWorld performance on it. We report performance below.

Claude Mythos 5 achieved an OSWorld score of 85.0% (first-attempt success rate, averaged over five runs).


<!-- p.283 -->

![Bar chart titled "OSWorld-Verified (max effort)" showing scores for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5, with Claude Mythos 5 highest at 85.0%](assets/figures/p283-1.png)
*__[Figure 8.16.3.A]: External OSWorld-Verified scores on max effort across models.__ Models evaluated on OSWorld-Verified (361 tasks, 100 steps) with auto-thinking at max effort. Scores are pass@1 averaged over five runs.*

#### 8.16.4 BenchCAD

BenchCAD[^55] is a benchmark for programmatic CAD reasoning built from 17,900 execution-verified CadQuery programs spanning 106 industrial part families, roughly half of which are anchored to real ISO, DIN, EN, ASME, and IEC specification tables. The benchmark decomposes CAD capability into four matched tasks and we report results on the Vision2Code task which requires models to generate CadQuery code from multi-view renders.


Our internal implementation of BenchCAD matches the reference implementation[^56], except for three minor modifications. First, we corrected a typo in the reference system prompt which swapped all four camera positions in the rendered views provided to the model.<!-- p.284 -->  Second, we updated the grading to accept raw shapes in addition to Workplanes. On models like GPT-5.5, we noticed raw shapes would error out due to this stylistic difference in output, but otherwise equivalent geometry. Third, we omit 26 records whose CadQuery code failed to produce a STEP file. We proposed the system prompt and grading changes to the reference repository in GitHub.

The model is configured with adaptive thinking and max effort enabled in all runs, without tools. We evaluate the model on 17,874 of the published 17,900 Vision2Code files (accounting for the 26 omitted records) and report voxel IoU scores averaged over five runs.

On BenchCAD Vision2Code, Claude Mythos 5 achieved a voxel IoU of 0.384. Claude Opus 4.8 and Claude Mythos Preview achieved voxel IoU scores of 0.273 and 0.355, respectively.

![Bar chart titled "BenchCAD Vision2Code (full)" showing voxel IoU scores for Claude Mythos Preview (0.355), Claude Opus 4.8 (0.273), and Claude Mythos 5 (0.384)](assets/figures/p284-1.png)
*__[Figure 8.16.4.A] BenchCAD Vision2Code scores.__ Models are evaluated with adaptive thinking and max effort. Voxel IoU scores are averaged over five runs. Shown with 95% CI.*

We suspected that the performance would also benefit from giving the model Python tools to render and visually verify outputs prior to submission. We ran an ablation on a subset of Vision2Code files, both with and without tools. When evaluated with Python tools, the model was provided with a container—with the image files and standard Python libraries installed—and an image cropping tool. We evaluate the model on a random subset of 1,000 of the full 17,874 Vision2Code files and average voxel IoU over five runs.

<!-- p.285 -->

On the 1000-file subset of BenchCAD Vision2Code, Claude Mythos 5 achieved a voxel IoU score of 0.379 without tools and a voxel IoU score of 0.650 with tools. Claude Mythos Preview scored 0.356 and 0.610, respectively.

![Bar chart titled "BenchCAD Vision2Code (1,000-file subset)" showing voxel IoU scores with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5, with Claude Mythos 5 highest with tools at 0.650](assets/figures/p285-1.png)
*__[Figure 8.16.4.B] BenchCAD Vision2Code subset scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. Scores are averaged over five runs. Shown with 95% CI.*

#### 8.16.5 ChartQAPro

ChartQAPro[^57] is a chart question answering benchmark built from 1,341 charts drawn from 157 diverse real-world sources, spanning chart types including infographics and dashboards, with 1,948 questions covering multiple-choice, conversational, hypothetical, and unanswerable formats. The benchmark tests messier, more varied chart reasoning tasks—for example, questions that pair charts with accompanying text or have no answer in the chart at all—rather than the simpler formats of earlier chart reasoning benchmarks.


Our internal implementation of ChartQAPro matches the "Chain-of-Thought" prompting and rule-based grading reference implementation in VLMEvalKit[^58]. The model is configured with adaptive thinking and max effort enabled in all runs, both with and without Python<!-- p.286 -->  tools. When evaluated with Python tools, the model is provided with a container—with the image file and standard Python libraries installed—and an image cropping tool. We evaluate the model on the full test set and average scores over five runs.

On ChartQAPro, Claude Mythos 5 achieved a score of 71.6% without tools and a score of 72.9% with tools. Claude Mythos Preview scored 71.2% and 73.6%, respectively.

![Bar chart titled "ChartQAPro" showing accuracy with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5](assets/figures/p286-1.png)
*__[Figure 8.16.5.A] ChartQAPro scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. Scores are averaged over five runs. Shown with 95% CI.*

#### 8.16.6 ChartMuseum

ChartMuseum[^59] is a chart question answering benchmark consisting of 1,162 expert-annotated questions over real-world chart images drawn from 184 sources, including academic figures, infographics, and unconventional chart designs. The benchmark specifically targets questions that require visual reasoning—for example, comparing unlabeled visual elements, tracking trajectories, and judging spatial relationships.

<!-- p.287 -->

Our internal implementation of ChartMuseum matches student and teacher prompts in the official ChartMuseum repository[^60]. However, we use a Claude Sonnet 4.6 grader instead of GPT-4.1-mini. The model is configured with adaptive thinking and max effort enabled in all runs, both with and without Python tools. When evaluated with Python tools, the model is provided with a container—with the image file and standard Python libraries installed—and an image cropping tool. We evaluate the model on the test split and average scores over five runs.

On ChartMuseum, Claude Mythos 5 achieved a score of 85.9% without tools and a score of 93.2% with tools. Claude Mythos Preview scored 80.7% and 92.2%, respectively.

![Bar chart titled "ChartMuseum" showing accuracy with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5, with Claude Mythos 5 highest with tools at 93.2%](assets/figures/p287-1.png)
*__[Figure 8.16.6.A] ChartMuseum scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. Scores are averaged over five runs. Shown with 95% CI.*

#### 8.16.7 LAB-Bench FigQA


LAB-Bench FigQA is a visual reasoning benchmark that tests whether models can correctly interpret and analyze information from complex scientific figures found in biology research papers. The benchmark is part of Language Agent Biology Benchmark (LAB-Bench)[^61]<!-- p.288 -->  developed by FutureHouse, which evaluates AI capabilities for practical scientific research tasks.

We evaluate the model on 181 questions from the public set and average scores over five runs. The model is configured with adaptive thinking and max effort enabled in all runs, both with and without Python tools. When evaluated with Python tools, the model is provided with a container—with the image file and standard Python libraries installed—and an image cropping tool.

On LAB-Bench FigQA, Claude Mythos 5 achieved a score of 88.9% without tools and a score of 90.7% with tools. Claude Mythos Preview scored 82.4% and 89.3%, respectively. When testing Claude Fable 5 we measured a degradation on LAB-Bench FigQA given its focus on biology-related images. This degradation reflects Claude Fable 5's bio-safeguard classifiers flagging biology-related images rather than a vision-capability regression.

![Bar chart titled "LAB-Bench FigQA" showing accuracy with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5, with a dashed expert human baseline line](assets/figures/p288-1.png)
*__[Figure 8.16.7.A] LAB-Bench FigQA scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. The expert human baseline is displayed as reported in the original LAB-Bench paper. Scores are averaged over five runs. Shown with 95% CI.*

#### 8.16.8 CharXiv Reasoning


CharXiv Reasoning is a comprehensive chart understanding evaluation suite built from 2,323 real-world charts sourced from arXiv papers spanning eight major scientific<!-- p.289 -->  disciplines. The benchmark tests whether models can synthesize visual information across complex scientific charts to answer questions requiring multi-step reasoning.

The model is configured with adaptive thinking and max effort enabled in all runs, both with and without Python tools. When evaluated with Python tools, the model is provided with a container—with the image file and standard Python libraries installed—and an image cropping tool. The model is graded using the same prompts as in the reference implementation[^62]. However, instead of GPT-4o, we use Claude Sonnet 4.6 as the grader model. We evaluate the model on 1,000 questions from the validation split and average scores over five runs.

On CharXiv Reasoning, Claude Mythos 5 achieved a score of 88.9% without tools and a score of 93.5% with tools. Claude Mythos Preview scored 86.2% and 92.5%, respectively.

![Bar chart titled "CharXiv Reasoning" showing accuracy for Gemini 3.5 Flash (no tools) and, with and without Python tools, Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5](assets/figures/p289-1.png)
*__[Figure 8.16.8.A] CharXiv Reasoning scores.__ Gemini 3.5 Flash was evaluated without tools. Claude models are evaluated with adaptive thinking and max effort, with and without Python tools. Scores for Claude models are averaged over five runs. Shown with 95% CI.*

<!-- p.290 -->

#### 8.16.9 ScreenSpot-Pro

ScreenSpot-Pro[^63] is a GUI grounding benchmark that tests whether models can precisely locate specific user interface elements in high-resolution screenshots of professional desktop applications given natural language instructions. The benchmark comprises 1,581 expert-annotated tasks spanning 23 professional applications—including IDEs, CAD software, and creative tools—across three operating systems, with target elements that occupy on average less than 0.1% of the screen area.

Images and corresponding ground-truth are resized to support each model's maximum supported image resolution. For Claude Mythos Preview, we resize images to a maximum of 1,568px along any single image dimension and up to 1,568 tokens. For Claude Mythos 5, we resize images to a maximum of 2,576px along any single image dimension and up to 4,784 tokens.

Previously, we would include input image dimensions in the prompt, with bottom-right-padding applied. While evaluating Claude Mythos 5, we noticed a small number of instances in which the model would get confused seeing the same exact image on its file system with a different image resolution. We modified our evaluation prompts to specify the unpadded input image dimensions. To enable a fair comparison, we re-evaluated all prior models with the new prompt format.

The model is configured with adaptive thinking and max effort enabled in all runs, both with and without Python tools. When evaluated with Python tools, the model is provided with a container—with the image file and standard Python libraries installed—and an image cropping tool. We evaluate the model on the full 1,581 instructions and average scores over five runs.

On ScreenSpot-Pro, Claude Mythos 5 achieved a score of 87.3% without tools and a score of 90.7% with tools. Claude Mythos Preview scored 79.3% and 93.0%, respectively.


<!-- p.291 -->

![Bar chart titled "ScreenSpot-Pro" showing accuracy with and without Python tools for Claude Mythos Preview, Claude Opus 4.8, and Claude Mythos 5](assets/figures/p291-1.png)
*__[Figure 8.16.9.A] ScreenSpot-Pro scores.__ Models are evaluated with adaptive thinking and max effort, with and without Python tools. Scores are averaged over five runs. Shown with 95% CI.*

[^52]: Surge AI. (2026). GDP.pdf: Can $100B AI models master the documents that run the world? [https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world](https://surgehq.ai/blog/gdp-pdf-can-100b-ai-models-master-the-documents-that-run-the-world)

[^53]: Petersson, L., et al. (2025). Blueprint-Bench: Comparing spatial intelligence of LLMs, agents and image models. arXiv:2509.25229. [https://arxiv.org/abs/2509.25229](https://arxiv.org/abs/2509.25229))

[^54]: Xie, T., et al. (2024). OSWorld: Benchmarking multimodal agents for open-ended tasks in real computer environments. arXiv:2404.07972. [https://arxiv.org/abs/2404.07972](https://arxiv.org/abs/2404.07972)

[^55]: Zhang, H., et al. (2026). BenchCAD: A comprehensive, industry-standard benchmark for programmatic CAD. arXiv:2605.10865. [https://arxiv.org/abs/2605.10865](https://arxiv.org/abs/2605.10865)

[^56]: Zhang, H., et al. (2026). BenchCAD [Code repository]. GitHub. [https://github.com/BenchCAD/BenchCAD-main](https://github.com/BenchCAD/BenchCAD-main)

[^57]: Masry, A., et al. (2025). ChartQAPro: A more diverse and challenging benchmark for chart question answering. arXiv:2504.05506. [https://arxiv.org/abs/2504.05506](https://arxiv.org/abs/2504.05506)

[^58]: Duan, H., et al. (2024). VLMEvalKit: An open-source toolkit for evaluating large multi-modality models. arXiv:2407.11691. [https://arxiv.org/abs/2407.11691](https://arxiv.org/abs/2407.11691)

[^59]: Tang, L., et al. (2025). ChartMuseum: Testing visual reasoning capabilities of large vision-language models. arXiv:2505.13444. [https://arxiv.org/abs/2505.13444](https://arxiv.org/abs/2505.13444)

[^60]: Tang, L., et al. (2025). ChartMuseum [Code repository]. GitHub. [https://github.com/Liyan06/ChartMuseum](https://github.com/Liyan06/ChartMuseum)

[^61]: Laurent, J. M., et al. (2024). LAB-Bench: Measuring capabilities of language models for biology research. arXiv:2407.10362. [https://arxiv.org/abs/2407.10362](https://arxiv.org/abs/2407.10362)

[^62]: Wang, Z., et al. (2024). CharXiv [Code repository]. GitHub. [https://github.com/princeton-nlp/CharXiv](https://github.com/princeton-nlp/CharXiv)

[^63]: Li, K., et al. (2025). ScreenSpot-Pro: GUI grounding for professional high-resolution computer use. arXiv:2504.07981. [https://arxiv.org/abs/2504.07981](https://arxiv.org/abs/2504.07981)
