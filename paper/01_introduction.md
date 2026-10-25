<!--
DRAFT. Written as a planned study; results are not in yet, so change the tense once they are.
Markers used in this file and its siblings:
  [N]                 sample size not final
  [TODO: ...]         open item to fill in
  [DECISION NEEDED]   author must choose before the text is final
  [PROPOSED]          addition not yet in the repo scaffold; accept or delete
  [VERIFY: ...]       claim or citation detail to check before submission
Citation keys such as [Olive2017b] are defined in references.md.
Check AES Europe 2027 length/format once the call is published, then trim.
-->

# 1 Introduction

Online enthusiast communities now publish frequency-response measurements and written or video reviews for a very large number of in-ear monitors (IEMs). One public measurement site listed 611 entries in its index on 2026-10-18, 311 of them linking to a review [SquigLink]. Some of those entries are EQ-processed variants rather than distinct IEMs [TODO: report the number of distinct IEMs after filtering].

These resources hold two kinds of information that are rarely connected: objective graphs and subjective words. A newcomer is told that an IEM is "warm", "bright" or "muddy" and has to guess how those words relate to the graph in front of them. The difficulty is more than a missing glossary. Metaphorical timbre words are not shared equally by everyone. In a rating study of 520 orchestral instrument sounds, roughness was widely shared across sound engineers, conductors and non-experts, whereas brightness depended on expertise [Rosi2023]. In a study with 40 non-expert listeners, some descriptors such as smooth/rough and metallic were understood intuitively, while others such as natural and non-rich were not [Holmgren2025]. Community guides acknowledge the problem: one notes that a headphone that is "peaky" to one reader may be "mildly bright" to another [MobileAudiophile]. Informal rules of thumb also attach the same word to different spectral regions; a widely shared forum guide lists "warm/lush" both among descriptors of emphasized bass and among descriptors of recessed treble [Reddit2013].

Existing research covers neighbouring questions but not this one. Measurement-based models predict how much listeners like an IEM [Olive2017b]. Expert lexicons such as the Sound Wheel standardize how trained panels describe reproduced sound [PedersenZacharov2015]. Objective predictors of individual descriptors have been built, but for a handful of devices and trained listeners [Volk2016; Volk2017]. Work that maps words to equalization addresses music production rather than the measured response of a product [Cartwright2013; Stables2014; Venkatesh2022; Doh2025]. To our knowledge, no prior work links the vocabulary used in public IEM reviews to IEM measurements at scale [TODO: confirm with a final AES E-Library and Google Scholar search before keeping this sentence].

We present Lexiem, an open pipeline that connects the two sources. It (i) collects public measurements and review text, (ii) uses a large language model (LLM) to extract sound descriptors from each review into a structured list, (iii) reduces each measurement to a small set of band features, and (iv) models which descriptors go with which features, in both directions: from graph to descriptor probabilities, and from a word to the typical graph shape behind it. The model is compared with rule-based heuristics and checked against a small listening study with beginner listeners. We ask three questions:

- **RQ1.** Which descriptors do public IEM reviews use, and how consistently does each co-occur with measured features?
- **RQ2.** Can descriptor probabilities be predicted from measured features better than by rule-based heuristics [PROPOSED: and better than a zero-shot LLM reading the same features]?
- **RQ3.** Do beginner listeners choose the same equalized version of an IEM for a descriptor that the model predicts?

Our contributions are:

1. a reproducible pipeline, with prompts, model settings, and cached LLM outputs published, that links review-extracted descriptors to measured response features;
2. a measurement-grounded map between descriptors and graph shapes, with uncertainty, showing which words map consistently and which are ambiguous [RESULTS PENDING];
3. a comparison of the data-driven model with rule-based [and zero-shot LLM] baselines [RESULTS PENDING];
4. a small listening check of the mapping with [N] beginner listeners [RESULTS PENDING].

The scope is deliberately narrow. A descriptor says what an IEM sounds like relative to a reference, not whether it is good, and a listener can like or dislike a "warm" IEM. Lexiem concerns the meaning of words, not preference. The review text also comes from sighted listening by reviewers with varying experience, so the extracted vocabulary reflects how the community writes, not controlled perception. Section 3.9 lists these and other limits.

The rest of the paper is organized as follows. Section 2 reviews related work, and Section 3 describes the data, pipeline, models, and listening study. [TODO: add a sentence for results, discussion and conclusion sections once they exist.]
