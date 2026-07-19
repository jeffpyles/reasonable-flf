# Information base — "Did SARS-CoV-2 arise by natural zoonotic spillover or by a research-related incident?"

*A neutral starting map of the argument territory for swarm authors. This is background to build
FROM, not text to copy. Every factual claim you place must trace to a source in `index.json` (via
an `external_anchor` node citing its `ref_id`) or stand as a reasoning/inference node in its own
right. Do not invent specific numbers, dates, sequences, or findings beyond what's stated here and
in the pack — where you're unsure, write at the level of generality the sources support, or
`flag-friction` that a more specific source is needed. This topic is contested and politically
charged: your job is to map the argument **fairly on both sides**, not to reach or push a verdict.*

## The implicit question
"Did SARS-CoV-2 originate through natural zoonotic spillover, or through a research-related
incident (a laboratory leak)?" (Remember: the question itself is never a node — its rival *answers*
are. The top question is **genuinely unresolved** at the level of expert institutions [`cov-intel-assessments`];
one curated debate [`cov-debate`] adjudicated it toward zoonosis, but did not settle it.)

## The live rival answers (candidate top-level positions)
- **Natural zoonotic spillover** — SARS-CoV-2 crossed to humans from an animal reservoir (directly
  or via an intermediate host), most plausibly in connection with the Huanan market. The position
  the curated debate's judges and the WHO-China study favored.
- **Research-related incident (lab leak)** — SARS-CoV-2 entered the human population through an
  accident connected to coronavirus research (e.g., at the Wuhan Institute of Virology), whether of
  a collected natural virus or a laboratory-modified one. A serious minority position held by part
  of the US intelligence community and a number of scientists.
- Represent BOTH as real competing positive claims in an antithesis set. Neither is a strawman.

## The structure to find: anchored EVIDENCE vs. contested INFERENCE
This case has a valuable two-layer structure — build it so the two layers are distinct:

1. **Evidential sub-claims that are largely agreed as FACTS** (these are the anchorable nodes —
   cite them to the pack; a competent panel can score how well-supported each is):
   - SARS-CoV-2 has a **furin cleavage site** at S1/S2, absent in its closest known relatives and
     transmissibility-enhancing (`cov-furin`). *Both sides accept this fact.*
   - The **2018 DEFUSE proposal** described inserting furin cleavage sites into bat SARS-related
     coronaviruses with WIV collaborators; it was **not funded** (`cov-defuse`). *Documented.*
   - The **earliest known cases and positive environmental samples cluster at/around the Huanan
     market**, concentrated in the live-mammal section (`cov-market-epicenter`). *Published.*
   - **Raccoon-dog (and other susceptible-wildlife) genetic material co-occurs** with virus in some
     market samples (`cov-raccoon-dna`). *Reported.*
   - **No infected intermediate host or direct animal progenitor had been identified** as of the
     debate, unlike SARS-1 (civets) / MERS (camels) (`cov-no-intermediate`). *Agreed absence.*
   - The **closest-then-known relative (RaTG13) was held at the WIV**, which ran extensive bat-CoV
     research in the outbreak city (`cov-ratg13-wiv`). *Documented, but RaTG13 is evolutionarily
     distant — not a direct progenitor.*
   - **Expert institutions did not converge**: the WHO-China study rated lab-incident "extremely
     unlikely" (`cov-who-joint`) while the US IC split with low-to-moderate confidence
     (`cov-intel-assessments`). *Both are on the record.*

2. **Contested INFERENCE sub-claims — the cruxes** (these should be **reasoning nodes, NOT anchored
   to a single source**; they are where the two camps genuinely diverge in *interpreting* the same
   facts). Build these as rival positive claims in antithesis sets. Examples of the cruxes:
   - "The furin cleavage site is **better explained by laboratory insertion** than by natural
     acquisition" vs. "…**better explained by natural acquisition**, since FCSs arise naturally in
     coronaviruses and the sequence is not a clear engineering signature" (`cov-proximal`, `cov-furin`).
   - "The market case is **explained by ascertainment/surveillance bias**, not by a true market
     origin" vs. "the market clustering **reflects the true early epicenter**" (`cov-market-epicenter`).
   - "The **absence of an intermediate host strongly favors** a lab origin" vs. "the absence is
     **weak evidence under limited/late sampling**, as with SARS-1" (`cov-no-intermediate`).
   - "**DEFUSE + WIV proximity + the FCS together make a research incident the likelier
     explanation**" vs. "these are **circumstantial coincidences** with no direct evidence of an
     incident" (`cov-defuse`, `cov-ratg13-wiv`, `cov-chan-ridley`).
   - "The two early lineages **indicate multiple market spillovers**" vs. "the two-introductions
     inference **rests on disputed modeling assumptions**" (`cov-two-lineages`).

## Why this two-layer structure matters (a design instruction, not to be placed as a node)
Keep the **evidential facts anchored** and the **interpretive cruxes un-anchored**. This mirrors
the real epistemic situation — the two sides mostly agree on the facts and disagree on what they
imply — and it is exactly the structure the assessment layer needs: a competent panel can anchor
the facts, while the un-anchored cruxes are where reasonableness (and, in an adversarial test, a
coordinated bloc) actually shows up.

## Notes for authors
- This is a **curated-debate shape** (`cov-debate`), different from eggs (a genuine scientific
  split on a mundane question) and from black holes (strong consensus with a vocal edge). The
  distinctive feature here: broad agreement on the **evidence**, deep disagreement on the
  **inference to best explanation**, and a top question that **stays open**.
- Steelman the lab-leak position as real competing positive claims (`cov-chan-ridley`), never as a
  strawman — and equally, do not let the zoonosis case rest on authority; trace it to the market /
  wildlife / phylogenetic evidence.
- Treat institutional conclusions (WHO, intelligence community) as **pointers to underlying
  reasoning and its limits**, not terminal grounds (see the guide on authority nodes). Their
  *disagreement* is itself an important node: the question is unresolved.
- Cite `external_anchor` nodes to the pack; reuse one `--source` ref_id for multiple findings from
  one source (`list-studies` to check existing ids). `search` before `create-node`.
- Where the grammar can't cleanly express something (e.g., "this node comments on another node's
  evidentiary status," or "this is a coincidence-of-multiple-facts argument"), `flag-friction` —
  that is a primary deliverable, not a failure.
