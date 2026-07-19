# Can you "solve debate"? — a Reasonable graph of Scott Alexander's critique and our reply

*2026-07-17. A graph that steelmans Scott Alexander's argument in **"Your Attempt To Solve Debate Will
Not Work"** (Astral Codex Ten, ~28 Apr 2026) and maps the Reasonable project's counter-position against
it — plus the concessions where Scott is right. Built with the project's own grammar (`build.py`), so
it doubles as a demonstration of the tool arguing about whether the tool works.*

> **Provenance / honesty note.** The graph was first built as a **steelman reconstructed** from the
> post's key examples as quoted in response pieces, plus Scott's closely related essays *Varieties of
> Argumentative Experience* and *Double Crux* — the post was paywalled/bot-blocked to our fetcher and
> dates after our training cutoff. **The full post text has since been supplied by the project owner
> (2026-07-17), and the reconstruction was checked against it.** The verdict of that check: the
> load-bearing points are faithful — the lockdown/weighing example (`n006`), values-as-generator
> (`n007`), the no-demographic/dating-app point (`n009`), and the 2000-years point (`n010`) are all
> accurate to the actual text. Two caveats: (a) the **Alice/gun-control** example in the
> over-determination node (`n008`) is from Scott's *related* essays, not this post — the post's own
> over-determination material is the "people drop the false fact and keep arguing" point, now added
> directly as `n029`; (b) the first pass **omitted two load-bearing arguments** the real post makes,
> now added in Round 2 (below): that arguments rarely hinge on a findable false fact or named fallacy
> (`n029`, with the AI-risk-panel example `n030`), and that adding *more* circles makes the map worse
> (`n031`). Evidence nodes cite the post as `acx-solve-debate-2026`.
>
> **Round 2 (2026-07-17):** four nodes added from the verified post — `n029`/`n030` (no-false-fact +
> AI-risk-panel evidence), `n031` (more-circles-is-worse), and the Reasonable response `n032`
> (graded/support-only support models "drop it and continue"), in two new antithesis sets (`s9`:
> `n029`↔`n032`; `s10`: `n031`↔`n012`). Graph is now **32 nodes / 10 antithesis sets**. The same
> 12-rater panel then rated the four new nodes blind: **`n029` 3.36, `n030` 3.61, `n031` 2.73, `n032`
> 3.68** — Scott's added descriptive points land with moderate agreement, the sharper "more circles is
> worse" claim (`n031`) is genuinely contested at mid-scale, and the project's graded-support reply
> (`n032`) is well-received. Behaviour holds: the structural verdict is now **20 contested / 12
> settled**, between-camp dispersion **56%** — the theses/framing/value-crux contested, the evidence
> and concessions settled. The original 28-node analysis below is unchanged as a snapshot.

## Scott's argument (steelmanned)

His thesis: platforms that try to "solve debate" / "map arguments" are well-intentioned, sophisticated,
and doomed. The load-bearing sub-arguments, as I read them:

1. **Structure mismatch** — real arguments don't decompose into clean premises→conclusion where you
   point at the one false premise; the argument-map model assumes a form disagreement lacks.
2. **Weighing, not facts** — the real work is quantifying magnitudes and weighing them. *Lockdowns:*
   even granting "lockdowns hurt the economy," getting to "lockdowns are bad" needs magnitudes of every
   harm and benefit, a specific proposal, and a theory of interpersonal utility. Resolving the atomic
   premise touches none of it.
3. **Values are the generator** — "civil rights regardless of cost-benefit," "we owe the weakest more":
   ethical-framework differences no map can resolve.
4. **Over-determination** — people hold positions through many weak considerations, not one crux; flip
   one and they don't move (Alice's gun-control example).
5. **No demographic** — formal mapping is an inefficient way to change minds, and the "wants to argue
   online, but rigorously" user barely exists.
6. **2000 years** — unsolved for two millennia ⇒ probably not tool-fixable.
7. **Wrong altitude** — the action is at high-level generators of disagreement; maps work on surface
   claims.

## Why this is the ideal graph for us to build

Read that list against what this project actually built, and the overlap is uncanny — **Scott's
critique is essentially a list of the design constraints we converged on:**

| Scott's point | The project's design response (a claim node, answering it) |
|---|---|
| structure mismatch | graded Ground edges + antithesis sets + conjunction groups — *not* premise→conclusion (`r_grammar`) |
| weighing not facts | we don't resolve the weighing, we **locate** it; covid's "unresolved" verdict scored HIGH (`r_locate`, `r_covid`) |
| values are the generator | the **Ought node type** + Hume rule + democratic endorsement give values a first-class home (`r_oughts`) |
| over-determination | many-grounds + chain-strength + camps are native; no single crux needed (`r_multiground`) |
| no demographic | "Wikipedia for arguments" — a durable artifact for readers, not a live persuasion tool; AI builds it (`r_wikipedia`, `r_builtgraphs`) |
| 2000 years | the conditions changed (cheap AI authorship/rating, reputation, blind rating) (`r_conditions`) |

So the two sides mostly **don't disagree about the mechanism** — they disagree about the **goal**. Scott
attacks "make people agree / win the argument"; the project aims at "faithfully map the disagreement,
value-cruxes and all, for third parties." That gap is the graph's third root node (`n003`,
`thesis_depends`).

## The graph (32 nodes, 10 antithesis sets — `build.py` → `graph.json`; the assessment below covers the original 28)

- **Root antithesis (`s1`):** Scott's "won't work" (`n001`) · our "faithful map adds value" (`n002`) ·
  the dissolution "depends what you demand of it" (`n003`).
- **Six sub-question antitheses** pairing each Scott ground with our answer — structure, weighing,
  values, over-determination, demographic, history. These are the mapped **cruxes**.
- **Four concession nodes** carried as first-class grounds of Scott's thesis, three of them citing *our
  own findings* (`k_findings` → the retired align rule, discrimination inverting on a biased crowd, the
  calibration guard) — the graph argues against itself where honesty demands.
- **The value-crux, as an Ought antithesis (`n027` vs `n028`):** *"a faithful-but-non-resolving map is
  worth building"* vs *"only worth it if it changes minds."* Rated on **endorsement**, not truth —
  Hume-safe (oughts vs oughts), never grounding an is-node.

## The payoff — the graph demonstrates the reply

Scott's deepest point is that **values, not facts, generate the disagreement, and no map resolves
them.** Watch what the grammar does with that: it puts the Scott-vs-Reasonable value-generator on the
board as `n027`/`n028` — an explicit Ought antithesis, to be settled (if ever) by a democratic
endorsement vote, never by truth-weighting. The tool doesn't pretend to resolve the value question; it
**locates it, labels it a value question, and shows it's the real crux.** That is precisely the
project's claim about what "working" means — and the graph enacts it on the debate about itself.

Equally, the graph concedes Scott's strongest narrow point honestly: if "solve debate" means "produce
agreement," `n003`/`k_noconsensus` grant that we don't. The disagreement that remains is
over-determined and value-laden — so, *by Scott's own analysis*, it won't be resolved. A Reasonable
graph responds to that not by declaring a winner but by mapping it. This document's graph is that
response, made concrete.

## Assessment results (12 blind Sonnet raters — 4 lenses × 3 seeds; on the original 28 nodes, pre–Round 2)

Rated 2026-07-17: epistemic-rigor, pragmatic/builder, values-pluralist, and project-skeptic lenses,
blind, claims/evidence on truth and the two Oughts on *endorsement*. Full coverage (28/28 at n=12).
`harness/workflow_rate.js`. **The assessed map behaves exactly as the design predicts:**

**1. It refused to declare a winner — and converged the diverse panel on the *reframing*.** The two
partisan theses both land genuinely contested and near the middle (Scott's "won't work" **n001 = 2.66**;
Reasonable's "adds value" **n002 = 2.93**). The single strongest agreement in the whole graph is the
**dissolution** — *"whether it works depends on what you demand of it"* (**n003 = 3.91**, and agreed
across *all four* lenses: epistemic 4.0 / pragmatic 3.7 / values 4.3 / skeptic 3.7). A diverse panel,
rating blind, landed not on either side but on "you're arguing about the goal" — the map's own thesis.

**2. The deepest disagreement is the value-crux, correctly isolated as an Ought.** The two Ought nodes
are the **two highest-dispersion nodes in the graph**, and they split along the *value* axis, not the
competence axis: *"a faithful map is worth building even if it never makes anyone agree"* (**n027
endorse 3.84**: values 4.8, epistemic 4.3, pragmatic 3.5, **skeptic 2.8**) vs *"only worth it if it
changes minds"* (**n028 endorse 1.95**: values 1.2, epistemic 1.6, **skeptic 3.2**). Rated on
endorsement (democratic), the panel softly endorses the faithful-map value while **preserving the
skeptic's genuine dissent** — a value divide mapped and measured, not resolved.

**3. Settled exactly where the facts are settled.** The lowest-dispersion nodes (sd ≤ 0.14) are the
**evidence** (Scott's lockdown example, n006 = 4.02, sd 0.06 — near-unanimous), the **honest
concessions**, three of them citing our own findings (n020 "if solve=agree we don't" = 4.04; n021
consensus-vs-truth-not-escaped = 4.03; n023 dispersion-low-reliability = 3.64), and **Scott's core
descriptive point** (n005 "the weighing is the load-bearing work" = 3.84). Every lens affirms the
factual substrate and both sides' honest points.

**4. The structural verdict agrees.** `graph.py contested`: **17 contested / 11 settled**, between-camp
dispersion **58%** (a real belief-camp split, not lens/offset noise), split-strength 0.30. The contested
set is the theses, the framing claims, and the value-crux; the settled set is the evidence + concessions.

**The payoff, made concrete.** The graph about *"does argument-mapping work?"* was itself argument-mapped
and assessed — and it did the thing Scott says is impossible and the thing we claim is the actual goal in
one motion: it **did not resolve** the value disagreement (it endorsed a reframing and left the value-crux
openly split by lens), and it **faithfully located** where the disagreement lives (a democratic Ought), on
a substrate of settled fact both sides accept. Settled where facts settle, contested where values diverge.

Reproduce: `python3 debate-graph/build.py` (structure) → `harness/workflow_rate.js` (rating) →
`graph.py contested --data debate-graph`.
