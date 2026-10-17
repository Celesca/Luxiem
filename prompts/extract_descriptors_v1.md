# extract_descriptors_v1

You will be given the text of one IEM review. List the sound descriptors the reviewer uses to describe how the IEM sounds (tonal balance, bass, mids, treble, soundstage, etc.).

Rules:
- Return descriptors only, as short lowercase words or phrases. Do not quote sentences from the review.
- Include only descriptors that apply to this IEM's own sound, not comparisons to other products.
- For each descriptor, give the region it refers to if stated: `bass`, `mids`, `treble`, or `overall`.
- Return JSON matching: `{"descriptors": [{"term": str, "region": "bass|mids|treble|overall"}]}`

TODO: finalize wording, add examples, then freeze. Bump the version number in the filename for any change.
