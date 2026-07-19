# Deep-research brief — LHC black-hole safety (handoff to an instance with working web access)

**Why this exists.** The main working environment's WebFetch is currently blocked (HTTP 403 on
everything, including example.com), so it cannot pull sources. Your job: run the deep research in an
environment that *can* fetch, and drop **two output files into this directory** —
`blackholes-graph/harness/REPORT.md` and `blackholes-graph/harness/sources.json`. Once those exist,
the graph build + tiered assessment run back in the main environment with **no web access needed**
(they read only local files). So you are the fetch-dependent front half of a pipeline; everything
downstream is already built and waiting.

Commit and push the two files to branch `claude/beautiful-fermi-kis8cx` when done.

---

## The question

> **Could a high-energy particle collider (the LHC) create a black hole that destroys Earth?**

This is the FLF "black holes" case — a **confident-answer** question (the scientific answer is a
well-established *no*) with a documented contrarian minority (the 2008 Wagner & Sancho lawsuit). We
want the graph to show *how decisively* the evidence grounds the safety answer and *how thinly* it
grounds the catastrophe claim — so cover **both** sides fairly and let the evidence do the weighting.

---

## The process we want — GRADED verification (this is the important part)

We are testing an assessment methodology, so *how* you verify matters as much as what you find. Our
key finding (from the covid case) is that the usual "be skeptical, try to refute, kill on 2/3 votes"
adversarial verification **inverts the scientific consensus** on contested questions: a rebuttal is
always findable, so it deletes well-sourced facts; it favors near-unrefutable "the paper argues X"
claims over refutable "X is true" claims; and a binary vote discards the true half of a
fact-plus-inference bundle. **Do not verify that way.** Instead:

1. **Separate two judgments per claim.** (a) *Faithfulness / provenance* — does the source exist and
   does the quote genuinely support the claim? This is the ONLY thing that may DROP a claim
   (fabricated/misattributed source, hallucinated quote). (b) *Support* — a **0–5 merit score** that
   annotates but never kills. A genuinely contested claim scores in the **middle (≈3), not 0**.
2. **No "default to refute if uncertain."** Uncertainty → a middling score, not a kill. Do not
   down-score a well-sourced factual claim just because the topic is contested and a rebuttal exists.
3. **Judge each claim on its own terms regardless of grammar** — an attribution ("the paper argues
   X") and an object-claim ("X is true") get the same scrutiny; don't reward humble phrasing.
4. Keep adversarial search for **provenance only** (catching fabrication/junk), not as a truth-weigher.

**Easiest way to do all of this:** run our already-fixed workflow rather than reinventing it.
If you are a Claude Code instance with the Workflow tool:

```
Workflow({ scriptPath: "v0/blackholes-graph/harness/workflow_deepresearch.js",
           args: "<the research prompt below>" })
```

`workflow_deepresearch.js` already encodes the graded verify, a synthesis-output-size cap (a prior
run's report got truncated), and Sonnet model pins. It returns a structured result with `keptClaims`,
`sources`, `findings`, etc. — convert that into the two files below (see the covid recovery scripts
for the pattern, or just write them directly).

If you are NOT using the workflow, follow the graded-verify spec above by hand and produce the two
files directly.

### The research prompt to use (args)

> Could a high-energy particle collider such as the Large Hadron Collider create a microscopic black
> hole that grows and destroys the Earth? Review the physics and the safety case: the theoretical
> conditions under which colliders might produce microscopic black holes (extra-dimension /
> low-scale-gravity scenarios); Hawking radiation and why predicted micro black holes would evaporate
> near-instantly; the empirical cosmic-ray safety argument (nature has bombarded Earth, the Sun, and
> dense stellar objects like white dwarfs and neutron stars with far higher-energy collisions for
> billions of years without consequence); the official safety reviews (CERN LSAG and independent
> reviews); quantitative bounds on any hypothetical accretion rate; and the contrarian/lawsuit claims
> (Wagner & Sancho 2008) with the specific rebuttals. For each significant claim note the strength and
> independence of the evidence, where sources agree or conflict, and what remains genuinely uncertain.
> Prioritize primary sources.

---

## Coverage requirement — do NOT repeat our failure

The run in the fetch-blocked environment reached only 2 of 20 sources and ended up covering **only
the LHC-exclusion-limit strand** — missing the actual safety case. **Before you synthesize, confirm
you have at least one successfully-fetched primary source for EACH of these five strands:**

| # | Strand | Must be covered |
|---|--------|-----------------|
| 1 | **Production theory** | when/whether colliders could make micro black holes at all (extra dimensions, low Planck scale); the ~10^15 energy gap in standard gravity |
| 2 | **Hawking radiation** | why any micro black hole would evaporate near-instantly (and that it's a prediction, not yet directly observed) |
| 3 | **Cosmic-ray safety argument** | the natural experiment; white-dwarf / neutron-star survival closing the exotic loopholes — the load-bearing empirical case |
| 4 | **Empirical LHC searches** | no black holes seen in trillions of collisions; exclusion limits |
| 5 | **Official reviews + the lawsuit** | LSAG conclusions; Wagner & Sancho claims *and* their rebuttals |

If a strand can't be sourced, say so explicitly in the report rather than quietly omitting it.

---

## Starting source set (verify each on open — IDs are from memory / from an earlier search)

**Reviews:** LSAG report https://cern.ch/lsag/LSAG-Report.pdf · arXiv:0806.3414 (Ellis et al.,
"Review of the Safety of LHC Collisions") · CERN safety page
https://home.web.cern.ch/science/accelerators/large-hadron-collider/safety-lhc
**Cosmic-ray argument:** Giddings & Mangano, "Astrophysical implications of hypothetical stable
TeV-scale black holes," arXiv:0806.3381 (Phys. Rev. D 78, 035009) — *the key white-dwarf/neutron-star
paper.*
**Theory/production:** Giddings & Thomas, "High-energy colliders as black-hole factories,"
arXiv:hep-ph/0106219 (⚠ verify) · Dimopoulos & Landsberg, "Black Holes at the LHC," arXiv:hep-ph/0106295
(⚠ verify) · Wikipedia "Micro black hole"
**Empirical searches:** CMS 2012 search arXiv:1202.6396 · Hou, Harms, Cavaglià JHEP 11 (2015) 185
https://link.springer.com/article/10.1007/JHEP11(2015)185
**Lawsuit/contrarian:** https://phys.org/news/2010-09-lhc-lawsuit-case-dismissed-court.html · NBC
https://www.nbcnews.com/id/wbna23844529
**Overview (best single source):** Wikipedia "Safety of high-energy particle collision experiments"
https://en.wikipedia.org/wiki/Safety_of_high-energy_particle_collision_experiments

If four only: the **Wikipedia safety overview**, the **LSAG report**, **Giddings & Mangano 0806.3381**,
and **CMS 1202.6396** together span all five strands.

---

## Output file formats (match these exactly — the build reads them)

### `sources.json`
```json
{
  "question": "Could a high-energy particle collider (the LHC) create a black hole that destroys Earth?",
  "sources": [
    {
      "id": "s01",
      "url": "https://...",
      "title": "…",
      "quality": "primary",          // primary | secondary | blog | unreliable
      "tags": ["cosmic-rays", "white-dwarfs"],   // optional but helpful; see the 5 strands / the persona cluster tags
      "claims": [
        "One isolatable, checkable claim the source supports.",
        "Another. Extract every load-bearing claim; this is the build's coverage checklist."
      ]
    }
  ]
}
```
Aim for ~15–30 sources' worth of claims total, weighted toward primary sources, with every one of the
five strands represented. The `claims` arrays are the most important part — they are what the build
agents map into the graph.

### `REPORT.md`
A readable synthesis: an executive summary that answers the question (noting where it's confident and
where genuinely open), then the claims grouped into findings **each carrying its 0–5 support score**
(preserve the gradient — don't flatten a contested claim into a confident one or vice versa), a short
"provenance-dropped" list if any, and the source list. Mirror the structure of the committed
`covid-graph/harness/REPORT.md` if you want a template.

---

## When done
Commit `REPORT.md` + `sources.json` (and, if you produced them, any recovered/ intermediate files) to
`claude/beautiful-fermi-kis8cx` and push. The main environment will then run:
`workflow_build.js` (5 Sonnet authors) → `setup_assess.py` → `workflow_assess.js` (tiered panel) →
`analyze_*` — no web access required. Everything downstream is already built and validated.
