# Report vs. assessed graph — the same evidence, two representations

*The FLF dim-1 artifact (epistemic uplift over off-the-shelf deep research). Both artifacts
were built from the **same 24 sources and 80 extracted claims**; the only variable is the
representation. Numbers below are reproducible: `python3 covid-graph/harness/analyze_comparison.py`.*

## The setup

We ran an off-the-shelf deep-research harness on "what is the origin of SARS-CoV-2?" (fan-out
web search → fetch 24 sources → extract 80 claims → 3-vote adversarial verification → synthesis).
That produced the **baseline report** (`harness/REPORT.md`). We then fed *the same sources* to a
persona-diverse swarm that built a **structured argument graph** — 109 nodes (72 anchored
evidential facts + 37 reasoning nodes), 127 support edges, 14 antithesis sets of rival claims,
15 friction flags — and had a 4-lens panel (evidential / Bayesian / provenance-skeptic /
technical) independently rate every node and every edge on a 0–5 Agreement scale, blind.

Same evidence in. Two different objects out. Here is what the graph shows that the report can't.

## 1. The flat pipeline inverted the scientific consensus — and *why* it did

Same inputs, opposite verdicts. The report's 3-vote adversarial layer **refuted six central,
peer-reviewed pro-zoonotic findings** (Science/Nature/Cell); the graph's panel, rating the same
claims on their merits, scores them as solid:

| Claim the report's verifier REFUTED | report vote | graph panel Agreement |
|---|---|---|
| Market environmental samples (73 positives, live-virus isolations) | 0-3 killed | **4.35 / 5** (sd 0.21) |
| Earliest Dec-2019 cases centered on the Huanan market | 1-2 killed | 3.63 (sd 0.41) |
| Viral–animal genetic co-mingling in market samples | 2-3 killed | 3.55 (sd 0.36) |
| Two lineages A/B → at least two introductions | 0-3 killed | 2.65 (sd 0.21) |

And the net verdict on the question:

| | panel Agreement | strongest support chain (∏ node_A/5 · edge_A/5) |
|---|---|---|
| **n001 natural zoonotic spillover** | **3.68** (sd 0.41) | **0.46** |
| **n002 research-related incident** | **1.80** (sd 0.21) | **0.12** |

> **Addendum (2026-07-17) — build-out, de-star, and re-measured chains.** After an argumentation
> review the graph was (a) built out on the previously thin synthetic-origin side — the
> restriction-site "fingerprint" (n110/n111), the CGG-codon doublet (n114/n115), and the RBD/ACE2
> pre-adaptation argument (n118/n119), **each paired with its documented rebuttal** so the engineered
> branch has parity of representation; and (b) **de-starred** — the flat 15/11/9-ground hubs on
> n001/n041/n054 were re-layered through strand-aggregators (SPEC §4). The verdict is unchanged in
> direction and the numbers move little:
> - **Panel Agreement:** the table above is the original documented 4-rater comparison run. The
>   current *accumulated* aggregate over all raters (n=28) is **n001 3.34 / n002 2.17** — still clearly
>   favoring zoonosis; the added, honestly-rebutted lab-leak inferences score low as the evidence
>   warrants (restriction/CGG/RBD ≈ 1.45) and do not move the verdict.
> - **Raw-product chain:** re-measured post-restructure, **n001 ≈ 0.43 / n002 ≈ 0.16** — essentially
>   unchanged. The de-star did *not* tank it: the raw product prefers the shortest strong path, so it
>   simply routes through a well-rated aggregator (one extra hop ≈ ×0.87).
> - **Length-normalized chain (geometric mean, SPEC §3.4 — the layering-robust metric):** **n001 ≈
>   0.79** (via the layered evidence chain n021→n123→n001) **/ n002 ≈ 0.64**. This is the metric that
>   *rewards* the added layering instead of penalizing it; the raw product remains the more
>   discriminating verdict signal, the geometric mean is the layout companion. The gap between the two
>   metrics is itself the flatness bias SPEC §3.4 identifies, now visible on a real graph.

The graph lands where the scientific majority lands, from identical inputs. The interesting
question is *why the flat pipeline inverted it* — and the answer is **not ideological capture**.
The same verifier also refuted three *skeptic* claims (Bloom's "co-mingling uninformative" 2-3,
"no raccoon-dog correlation" 1-2, "rooting-bias" 1-2). The failure is structural — three factors,
not a political tilt:

1. **"Default to refute if uncertain" turns *contested* into *false*.** In a balanced dispute,
   every confidently-stated claim has a findable rebuttal, so a refutation-seeking filter fires on
   everything load-bearing — on both sides. (The verifier's own notes call the refuted
   market-centrality claim "faithfully" sourced to a "top-tier," non-retracted paper — then kill it
   because the topic "is genuinely contested.") Adversarial refutation is the right tool for
   catching hallucinated or junk claims; it is the *wrong* tool for **weighing** claims, because
   "a source disagrees" is always true in a real dispute and says nothing about the balance.
2. **Claim grammar decides survival.** What the verifier *confirmed* 6-0 were **attributions and
   epistemic-limits claims** — "the paper *argues* Pekar's model is biased," "the data *are
   insufficient* to root the tree" — which are near-unrefutable (you cannot refute "paper X makes
   argument Y" by disputing Y). The consensus findings were extracted as **object-claims about the
   world** — "the market *was* the epicenter" — which any rebuttal refutes. So the filter is
   systematically biased toward whatever is phrased humbly and against whatever is phrased as a
   confident fact — an artifact of *wording*, not of evidence.
3. **Binary voting discards the true part of a mixed claim.** "Market samples clustered in the
   wildlife stalls (fact), *linking the virus to the wildlife trade* (contested inference)" is one
   claim with a solid part and an overreaching part. A single refute-vote kills both — the settled
   fact dies with the overreach.

**The structured approach sidesteps all three** — not by being smarter, but by using the right
instruments:

- **Atomization** splits the bundle: "73 positives in the SW-corner stalls" (n003/n004, an anchored
  fact, **4.35**) is a separate node from "links to the wildlife trade" (reasoning) from "the market
  was the true epicenter" (n016) — so the fact scores as a fact and the inference stays contested
  (two-introductions **2.65**). *(defeats factor 3)*
- **Merit-based lenses, not refutation.** Panelists rate honestly from a lens; there is no
  default-to-kill, so a well-sourced fact in a contested field scores high. *(defeats factor 1)*
- **Grammar is normalized on the way in.** "Bloom argues co-mingling is uninformative" is not kept
  as an unrefutable meta-claim — it becomes a positive claim in an *antithesis set* opposite the
  finding it disputes, each scored on its merits. *(defeats factor 2)*
- **Continuous scale + diverse-panel aggregation.** Disagreement surfaces as a middling mean with
  high dispersion, not deletion. **The graph preserves the fact-vs-inference distinction the binary
  filter collapsed.**

## 2. It separates shared facts from contested cruxes — and *locates* the disagreement

The panel **converges** on the evidential facts (low dispersion) and **diverges** exactly on the
interpretive cruxes (high dispersion). A flat report states claims in prose; the graph puts a
number on precisely where the genuine disagreement lives.

- **Shared ground** (mean ≥ 4.5, sd < 0.3): lineages A/B differ by two SNVs (4.95, sd 0.09);
  WIV is a coronavirus lab (4.95, sd 0.09); sampling occurred only after market closure (4.67).
- **The genuine cruxes** (top dispersion): the UNC–WIV research claim (sd 1.11); whether
  post-closure sampling undermines the market inference (sd 0.80); the McCowan/Pekar
  Bayes-factor critique cluster (sd 0.65). *These* are what's actually unsettled — and the graph
  says so quantitatively, rather than burying it in a paragraph.

## 3. Three independent signals converge on the same weak spots

This is the payoff of structure. The graph carries three *independent* assessment signals — node
dispersion, edge support-strength, and human-authored friction flags — and they point at the
same places:

- **n095** ("no evidence found at WIV" → lab origin): the single **most-contested reasoning
  node** (sd 0.74), the **weakest inbound edge** to the lab answer (support 1.75), *and*
  independently flagged by friction **f13** as an unfalsifiable move. Three lenses, one weak spot.
- **n067→n002** ("SAGO could not *rule out* a lab origin" → research-incident): edge support
  **1.63**, and friction **f10** flags it as failure-to-exclude masquerading as positive evidence.
- **n014→n016** ("¼ of early cases market-linked" → "market is the true epicenter"): edge support
  **1.75** — the panel discounts the ascertainment-laden inference the report stated flat.

A flat report gives one number of confidence (or none). The graph gives you a cross-examinable
structure where weak reasoning shows up three different ways.

## 4. It flags correlated evidence, rhetoric, and category errors — the FLF assessment desiderata

The 15 friction flags are structure a prose report has no slot for. Among them:

- **Correlated evidence treated as independent** (f8, f9): Pekar et al.'s "multiple lines of
  evidence" for two introductions largely share one phylodynamic root; the zoonotic base-rate is a
  *prior*, a different *kind* of evidence than the market data — not an independent third leg.
- **Rhetorical vs. evidential / category errors** (f10, f14): "could not rule out" is not support;
  intelligence assessments are evidence *about assessments*, not direct evidence about the virus.
- **Unfalsifiable claims** (f13): absence of evidence at WIV framed as non-disconfirming.
- **Its own provenance** (f1): the graph records that the *deep-research harness's own verifier*
  had refuted a finding the graph retains — the artifact critiquing its own baseline.

## 5. It is interrogable, not just readable

You can ask the graph questions the report can't answer: `graph.py chain --from <evidence> --to
<answer>` returns the chain-rule strength of any inferential path; `graph.py compare --a X --b Y`
finds two rival claims' last common ancestor and says which branch is better grounded; per-node
dispersion and bloc divergence are queryable. The report is a fixed narrative; the graph is a
queryable object that supports *why*, not just *what*.

## Where this maps on the FLF rubric

- **Dim 1 (epistemic uplift):** demonstrated head-to-head over the same sources — the graph
  recovers the consensus the flat pipeline inverted, and makes the load-bearing evidence and the
  cruxes visible.
- **Dim 6 (adversarial robustness):** the report shows a general failure mode — an adversarial
  binary *filter*, correct for catching junk/hallucinated claims, **misfires when repurposed as a
  truth-weigher**: it deletes confidently-stated facts, favors near-unrefutable meta-claims, and
  collapses fact-plus-inference bundles (see §1). The graph structurally resists this — merit-based
  continuous scoring instead of refutation, normalized grammar, and a critique held as a distinct
  node from the finding it attacks, so one cannot silently "refute" the other out of existence.
- **Dim 7 (insight):** the diagnosis in §1 is the transferable contribution — *why* adversarial
  verification inverts a balanced dispute (default-to-refute + claim-grammar asymmetry + binary
  information loss), plus the three-signal convergence on weak reasoning. These are general claims
  about assessing contested questions, not covid-specific trivia.

## Honest caveats

- The panel is a **synthetic** 4-lens LLM panel, not human raters — it demonstrates the
  *mechanism* (dispersion, calibration, structural separation), and a human-rated slice is the
  natural next validation. The build agents were LLMs too.
- This is **one case**. The same pipeline is domain-general (it has also been run on eggs); a
  second and third case shape would strengthen the generalization claim (FLF dim 2).
- The comparison is about **representation and sense-making**, not about settling SARS-CoV-2's
  origin. The graph's verdict tracks the current scientific majority; its contribution is making
  *why*, *how strongly*, and *where-contested* legible and checkable — which is the point.
