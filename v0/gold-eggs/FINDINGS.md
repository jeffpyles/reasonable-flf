# Hand-seed first pass — "Are eggs good for you?" (dietary-cholesterol crux)

*Authored 2026-07-02 by Fable, playing three authoring agents (`agent-a` primary author,
`agent-b` second author who Agrees selectively, `agent-c` skeptic). Built through the real v0 CLI
per `AGENT-GUIDE.md`. This is the gold reference graph + its falsification log — the single most
valuable output of the structure test (Feature Discussions, Entry 7/11).*

Load it: serve `v0/` and open `viewer.html?data=gold-eggs/graph.json`. Full provenance is in
`gold-eggs/events.jsonl` (56 events); the snapshot is `gold-eggs/graph.json`.

## What was built

**17 nodes · 13 ground edges · 2 conjunction groups · 3 antithesis sets · 10 agrees · 7 frictions.**

The slice maps the crux of the eggs question — does dietary cholesterol from eggs raise
cardiovascular risk — as three rival answers in one antithesis set (`s1`):
- **N1 (n001)** eggs are ~neutral for most healthy adults,
- **N2 (n002)** eggs meaningfully raise CVD risk,
- **N3 (n003)** it depends on the person (diabetes, hyper-responders).

**Curated reading path (start here):**
1. **Focus n002 → the conjunction chain.** N2's support is a genuine two-stage conjunction:
   *(n008 yolks are cholesterol-rich)* **AND** *(n009 dietary cholesterol raises LDL)* jointly →
   *(n012 eggs raise serum LDL)*; then *(n012)* **AND** *(n010 LDL causally raises CVD)* jointly →
   N2. Neither half gets you there alone — this is exactly what Conjunction is for, and it rendered
   and read cleanly. **The grammar's biggest success in this pass.**
2. **Focus n003 → the subgroup story**, and the same source (`eggs-001`, Hu 1999) grounding both
   N1 (no link in non-diabetics, n004) and the N3 line (higher risk in diabetics, n013).
3. **Set s3 (n016 vs n017)** — the undercut experiment. See F5 below; note n017 shows up as an
   **orphan** in `stats` (antithesis membership but no support edge) — that stranding is itself the
   finding, not a mistake.

## The falsification log (7 frictions) — grouped, with implications

### A. Relational sufficiency gaps — the grammar's real limits

- **F5 — undercutting defeaters have no home (highest-priority finding).** The confounding claim
  (n017) doesn't deny that the diabetic association is real (n013); it attacks the *inference* from
  n013 to a causal reading. Support-only has no undercut edge, so I had to invent a positive "it's
  causal" node (n016) purely to give the confounding claim something to be antithesis *to*. This
  turns an argument about **inference strength** into a fake rival **factual claim**, and leaves
  n017 orphaned. → **Directly answers Entry 11 falsification item #1: support-only + antithesis is
  NOT sufficient for undercutting.** This is the strongest evidence yet that we need either a typed
  *undercut/rebut* edge or a first-class "claim about another claim/inference" relation.
- **F1 — no way to mark evidential vs. rhetorical support.** The "guidelines dropped the
  cholesterol cap" node (n007) is offered as a Ground for N1, but it's an appeal to authority /
  consensus, not first-order biological evidence. A plain Ground edge hides that. FLF *explicitly*
  wants rhetorical-vs-evidential moves surfaced (criterion 1) — so this is both a grammar gap and a
  scored-dimension gap.
- **F4 — antithesis exclusivity is binary but reality is graded.** n005 (weak effect for most) and
  n009 (strong effect in hyper-responders) are *in tension* but not mutually exclusive — both can
  be true. Putting them in an antithesis set renders them as rivals of the same kind as N1/N2/N3,
  overstating the opposition. → Confirms the Entry 11 "graded exclusivity" watch-item.
- **F7 — the is/ought transition is unmarked.** n015 ("high-risk people *should* limit eggs") is
  normative but grounded by empirical claims; the Ground edge silently crosses the is/ought gap and
  a value-laden conclusion looks identical to a factual one.

### B. Provenance / external grounding

- **F2 — one source, multiple findings, no study-level identity.** Hu 1999 (`eggs-001`) yields two
  findings supporting *different* positions; I split them into two external_anchor nodes both citing
  `eggs-001`, but nothing records they're the same study — so a reader can't see one dataset cuts
  both ways, and double-counting its weight is invisible. → external_anchor wants a **study-level
  id** distinct from the claim node.
- **F3 — source-pack insufficiency.** The ~185 mg cholesterol fact (n008) should exit to a
  food-composition database, but the pack has no such ref, so it sits as a bare internal claim. The
  "external_anchor must cite a pack ref" rule and the pack's coverage are out of sync.

### C. Boundary / depth

- **F6 — relevance-horizon truncation.** "Elevated LDL causally raises CVD" (n010) is a huge
  separately-contested question (the diet-heart hypothesis) the egg argument *leans on* but
  truncates at one external anchor. The cut point is load-bearing and semi-arbitrary; a reader
  can't tell whether we endorse n010 or merely need it. → the Entry 10 continuity/relevance-horizon
  problem, showing up concretely on the very first real map.

## Verdict on the four criteria (this pass)

- **Decomposability — strong.** The question broke into atomic propositions without feeling
  arbitrary or regressing infinitely; grain (~1–2 sentences/node) felt natural. Minor watch:
  near-duplicate risk (n009 vs n014, both touching hyper-responders) — handled by distinct framing,
  but a swarm will need the `search`-first discipline hard.
- **Relational sufficiency — PARTIAL (the experiment paid off).** Grounds/Dependents + Conjunction
  covered the *support backbone* expressively (the conjunction chain is genuinely better than
  prose). But four distinct gaps surfaced (F1, F4, F5, F7), with **undercutting (F5) the serious
  one.** This is the headline result: the support-only grammar is a good backbone but demonstrably
  under-expressive for defeaters, support-typing, and graded tension.
- **Faithfulness — good, with known distortions.** The map captures the real state of play (the
  subgroup nuance, the conjunctive structure of the causal case) better than a linear paragraph.
  But F5's fake-rival encoding and the untyped-support issues (F1, F7) mean some inferential texture
  is currently *misrepresented*, not just omitted.
- **Legibility — good in the viewer, untested on a true non-author.** Node-view reads clearly and
  the antithesis arc shows the rivals at a glance; needs a real outside reader to confirm.

## Recommendations before pointing a swarm at it

1. **Pilot the undercut question empirically, not on paper.** We now have a concrete case (s3 /
   F5). In a v0.1 branch, add one candidate mechanism — a typed *undercut/qualifier* edge (or a
   support edge with polarity) — re-map this same slice, and compare faithfulness. This is the
   single highest-value grammar experiment.
2. **Consider a lightweight support-type tag** on Ground edges (`evidential | authority |
   definitional | normative-bridge`) to address F1 and F7 without importing formal logic — optional,
   agent-set, and itself a testable variable. Cheap to try.
3. **Split "rival-answer sets" from "in-tension cross-links,"** or add a per-membership tension
   degree, for F4.
4. **Give external_anchor a study-level id** (F2) and **expand the source pack** with a
   food-composition reference and more primary studies (F3) before the swarm authors at volume.
5. **Update `AGENT-GUIDE.md`** with explicit interim guidance for the undercut case and for when
   *not* to reach for antithesis (non-exclusive tensions) — until the grammar decides.

## Minor tooling notes

- `stats` correctly flags n017 as an orphan — useful signal; keep it.
- The viewer has no focus deep-link (`?focus=n002` is ignored); add a URL param so a findings doc
  can point at a specific region (supports FLF's "curated pointers to effective regions"). Small.
