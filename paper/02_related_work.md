<!--
DRAFT. See the marker legend at the top of 01_introduction.md.
Every numeric claim below was checked against the abstract or page listed in references.md.
Only abstracts were read for the AES papers (membership-only full text), so details beyond the abstracts are not claimed.
-->

# 2 Related Work

## 2.1 Predicting IEM preference from measurements

The closest body of work links measurements to how much listeners like in-ear headphones. Olive et al. ran controlled listening tests in which 71 trained and untrained listeners rated 30 IEM models, and found that preference fell as the measured response deviated from a target curve [Olive2017a]. A linear regression on the size, standard deviation and slope of that deviation predicted the ratings with r = 0.91 [Olive2017b]. A comparable machine-learning model for around-ear and on-ear headphones was built from tests with 130 listeners and 31 models [Olive2018].

Preference is not uniform. A summary of the Harman work reports that most listeners (64%) favoured the Harman target, while a "less bass is better" class (21%) included a disproportionate share of women and older listeners and none of the trained listeners [AcousticsToday2022]. A 2025 method-of-adjustment study with 36 mostly trained listeners, who adjusted a bass shelf, an upper-midrange region centred at 3 kHz, and a treble shelf, found four listener clusters. Their preferred settings spanned +2 to +9 dB of bass and −5 to +2 dB of treble relative to a diffuse-field baseline, and the author concluded that a preferred target plus small adjustments (about 3 dB) in bass and treble can accommodate most listeners [Olive2025]. We use those three regions as the structure for our band features (Section 3.6).

These works model preference. Lexiem models description: which words people use for a given response. The two differ, since an IEM can be "warm" and be either liked or disliked.

## 2.2 Sensory lexicons and descriptor models for reproduced sound

Sensory-evaluation research aims to standardize vocabulary. Pedersen and Zacharov collected descriptors from the literature and built the Sound Wheel, a layered lexicon of attributes for loudspeakers, headphones and other reproduction systems, with definitions and sound samples for training [PedersenZacharov2015]. The attribute-development process and the wheel (renamed the Audio Wheel) were later included in ITU-R BS.2399-0 [ITU2399]. These lexicons are built for trained panels, and trained listeners are selected and trained with dedicated tools, such as the computer-automated training program Olive developed to identify reliable listeners and revealing program material [Olive1994].

A smaller line of work builds objective predictors for individual descriptors. Volk et al. modelled six descriptors, chosen by trained listeners, for seven prototype headphones from loudness-model estimates. The most promising metrics were Bass, Clean and Dark-Bright, with r² of 0.62, 0.58 and 0.90 [Volk2016]. For eleven loudspeakers, metrics validated on four held-out loudspeakers correlated with perceptual ratings at r = 0.85–0.96 [Volk2017]. That the strongest headphone result is for Dark-Bright suggests that words with a clear spectral-tilt correlate are the most tractable, a pattern our results can confirm or contradict.

These studies use a handful of descriptors fixed by trained listeners and a small number of devices (seven and eleven). We instead take the vocabulary as it appears in public reviews, across many more IEMs.

## 2.3 Who shares the meaning of a sound word

Rosi et al. had sound engineers, conductors and non-experts (24 participants in all) rank 520 orchestral instrument sounds with Best–Worst Scaling on four metaphorical concepts. Sound engineers were the most consistent, roughness was widely shared, and brightness depended on expertise [Rosi2023]. Holmgren et al. tested a lexicon with 40 non-expert listeners on everyday sounds. Smooth/rough and metallic were understood most intuitively, dull, warm and round/non-round fairly well, and natural, non-dynamic and non-rich poorly. Several others, including nasal, resonant and strident, caused confusion, so the authors suggest that some descriptors need explanations or sound examples [Holmgren2025]. Both studies use orchestral or everyday sounds, not IEMs. They motivate our expectation that some review descriptors will map consistently to the graph and others will not.

## 2.4 Mapping words to audio processing

Semantic audio production links words to equalizer settings. SocialEQ crowdsourced a map from descriptors to 40-band equalizer curves and examined how widely agreed each descriptor's meaning was [Cartwright2013]. The SAFE plugins collected semantic descriptions of equalization, compression and reverberation settings from users inside a digital audio workstation [Stables2014]. Word embeddings have been used to predict equalizer settings for descriptors not seen in training [Venkatesh2022].

More recently, LLMs have been prompted to predict equalization and reverberation parameters from natural-language descriptions [Doh2025]. Another study has LLMs generate distributions of equalization settings from prompts, scored against settings from 11 listeners for 120 prompts, because listeners disagree about what a prompt means [Stylianou2026]. Joint language–audio embeddings show only limited alignment with human timbre semantics, and equalization-induced semantics were encoded less well than reverberation [Deng2025].

These works map words to processing applied to music, not to the measured response of a product. Two points carry over. Disagreement between listeners is better modelled as a distribution than as a single mapping, which is why Lexiem predicts descriptor probabilities. And language models may not read equalization-style timbre words reliably, so we test a zero-shot LLM baseline [PROPOSED] and do not assume it works.

## 2.5 Review text and community heuristics

Text mining of earphone reviews has focused on sentiment and product topics. An analysis of Amazon reviews of ten earphone products identified sound quality, noise cancellation, durability and battery life as the main concerns, treating sound quality as one topic [Maidar2024]. We did not find a study that extracts sound descriptors from IEM reviews and relates them to measurements [VERIFY: final search].

Enthusiast guides do map words to spectral regions, for example by listing which descriptors imply emphasized or recessed bass and treble [Reddit2013; MobileAudiophile]. They are informal, unvalidated and sometimes overlapping. We encode them as a rule-based baseline and treat them as hypotheses to test.

## 2.6 Gap

Taken together, prior work leaves four gaps that Lexiem addresses:

1. no validated link between the vocabulary of public IEM reviews, which is what beginners read, and IEM measurements;
2. no analysis at the scale of the public measurement and review corpus, as opposed to a handful of devices;
3. no check of such a link against beginner listeners, as opposed to trained panels or music-production users;
4. no estimate of how ambiguous each descriptor is, in a form a newcomer can use.

[TODO: confirm each gap with a final search of the AES E-Library and Google Scholar, and soften any that turn out to be partly covered.]
