<!-- source: source.pdf pages 191-193 -->

<!-- p.191 -->

## 9 Appendix

### 9.1 Blocklist used for Humanity’s Last Exam

The blocklist functions by substring matching against web URLs. We normalize the URLs and the blocklist patterns by removing forward slashes “/” from them and setting them to lowercase. The URL is blocked if any of the normalized blocklist patterns are a substring of the normalized URL.

Our blocklist contains the following patterns:

```None
huggingface.co 
hf.co 
hf-mirror.com 
promptfoo.dev 
://scale.com 
.scale.com 
lastexam.ai 
agi.safe.ai 
last-exam 
hle-exam 
askfilo.com 
studocu.com 
coursehero.com 
qiita.com 
2501.14249 
2507.05241 
2508.10173 
2510.08959 
2605.02442 
nature.com/articles/s41586-025-09962-4 
openreview.net/pdf?id=46UGfq8kMI 
researchgate.net/publication/394488269_Benchmark-Driven_Selection_of_AI_Evidence_f
rom_DeepSeek-R1 
openreview.net/pdf/a94b1a66a55ab89d0e45eb8ed891b115db8bf760.pdf 
scribd.com/document/866099862 
x.com/tbenst/status/1951089655191122204 
x.com/andrewwhite01/status/1948056183115493745 
news.ycombinator.com/item?id=44694191 
github.com/supaihq/hle 
github.com/centerforaisafety/hle 
HLE_PDF 
```

<!-- p.192 -->

```
researchgate.net/scientific-contributions/Petr-Spelda-2170307851 
medium.com/@82deutschmark/o3-quiet-breakthrough-1bf9f0bafc84 
rahulpowar.medium.com/deepseek-triggers-1-trillion-slump-but-paves-a-bigger-future
-for-ai 
bincial.com/news/tzTechnology/421026 
36kr.com/p/3481854274280581 
jb243.github.io 
github.com/deepwriter-ai/hle-gemini-3-0 
github.com/RUC-NLPIR/WebThinker/blob/main/data/HLE 
github.com/hanjanghoon/DEER 
github.com/repos/hanjanghoon/DEER 
xiaowenz.com 
research-collection.ethz.ch/server/api/core/bitstreams/1902b5a9-4209-4529-b278-c25
8aad557ba/content 
news.qq.com/rain/a/20260228A00WDR00 
evalscope.readthedocs.io 
github.com/ustc-ai4science/Science-Star 
modelscope.cn 
modelscope.ai 
f8fc0386fdd208b51fa885aef27e345a9c08b51b 
blog.asteromorph.com 
hle.shushin.io 
archive.is/KpUb9 
edisonscientific.com/news/edison-literature-agent 
aliexpress.com/s/wiki-ssr 
2604.06753 
```

### 9.2 Blocklist used for BrowseComp

The blocklist for BrowseComp uses the same URL substring matching described in Section 9.1: we normalize the URLs and the blocklist patterns by removing forward slashes “/” from them and setting them to lowercase, and the URL is blocked if any of the normalized blocklist patterns are a substring of the normalized URL.

In addition to the URL blocklist, for BrowseComp any search result or fetched page whose page content contains the string “browsecomp” (case-insensitive substring match) is also blocked. Our blocklist contains the following patterns:

```None
browsecomp 
openaipublic.blob.core.windows.net/simple-evals 
github.com/openai/simple-evals 
```

<!-- p.193 -->

```
openailive.com 
huggingface.co 
hf.co 
2504.12516 
2508.06600 
2510.07861 
2508.13167 
zdnet.com/article/openais-deep-research-has-more-fact-finding-stamina-than-you-but
-its-still-wrong-half-the-time 
aman.ai/recsys/search 
openreview.net/pdf/c6dcd5f3b250378e5b8283ef1ee5b16ead6615d1.pdf 
openreview.net/pdf/10c39467b7f1356121d2e937298acf09641e8c62.pdf 
```

### 9.3 SWE-bench Multimodal Test Harness

Our SWE-bench Multimodal test harness is built on the public dev split but includes the following modifications for grading reliability on our infrastructure:

We remove one instance (`diegomura__react-pdf-1552`) due to incompatibilities with our evaluation environment.

The following “pass to pass” tests fail nondeterministically on our infrastructure and are unrelated to the target fix; we drop them from the pass criteria:

```None
```

For `chartjs/Chart.js`, `processing/p5.js`, and `markedjs/marked`, the harness rewrites the JavaScript test-framework configuration (Karma, Grunt, Jasmine respectively) to emit machine-parseable output rather than the default formatted reporter. This changes only the output format, not which tests run or their pass/fail criteria.

All images referenced in issue text are fetched once, validated, cached, and inlined into the problem statement as base64 data URIs.
