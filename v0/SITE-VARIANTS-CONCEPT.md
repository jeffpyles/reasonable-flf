# Site variants, benchmarks, and the reality-refereed frontier — a concept note

*A standalone design/vision note (2026-07-15), separate from the frozen specs and the empirical
findings. It captures a direction that emerged from the reputation investigation: running the
*Reasonable* site in several access configurations, what comparing them teaches, and how the
structure could become a reality-refereed benchmark of collective epistemic capability — including,
eventually, in mathematics. Speculative by design; nothing here is built. It rests on the empirical
results in `coldstart-lab/`, `eggs-p8*/`, `eggs-external-check/`, and `review/`, and should be read
as "where those results point," not as validated fact.*

---

## 1. Three access configurations (a 2×2 with one cell dropped)

The site has two independent layers, each of which can be **open** (outside humans + agents) or
**in-house** (a vetted, known-prompt, vendor/model-diverse agent panel):

- **who BUILDS** the graph — authors nodes, draws edges, constructs arguments, raises frictions;
- **who RATES** the graph — supplies the graded Agreement/Reasonableness/Clarity judgments.

Three configurations worth running side by side:

| version | build | rate | character |
|---|---|---|---|
| **V1** | open | open | the full public site; maximum input, maximum attack surface |
| **V2** | open | in-house | crowd builds the argument space; a controlled panel evaluates it |
| **V3** | in-house | in-house | fully controlled; minimal attack surface, maximal reproducibility, lowest outside credibility |

(The fourth cell — in-house build, open rate — is omittable: little reason to hand-build a graph and
then crowd-rate it.)

## 2. Why the comparison is the prize (each adjacent pair isolates one layer)

The value isn't any single version's output; it's that **matched pairs isolate one variable**:

- **V1 vs V2 isolates the RATING layer.** Same built graph; only the rater pool differs. This measures
  the project's foundational open question: *does opening rating to the world add epistemic signal, or
  mostly attack surface plus tyranny-of-the-median noise on top of what a good panel already gets?*
- **V2 vs V3 isolates the BUILDING layer.** Both rated by the same in-house panel; only authorship
  differs. This measures whether outside builders surface concepts, framings, and contested frontiers
  a controlled panel wouldn't generate.

### The prediction the existing data makes (and it's asymmetric)

Our results already suggest the two layers behave very differently:

- **Rating is largely panel-approximable.** A vendor-diverse panel of ~4 tracks documented reality at
  ~0.10 mean error (`eggs-external-check`); rating competence lives mostly at the coarse
  disposition/tier level and is cheaply recovered (`coldstart-lab`); adding same-kind voices dies into
  a shared-bias floor (the panel-size curve). So the *rating* function is close to a solved, cheap,
  approximable thing. **Predict: V1 ≈ V2 on rating quality** — the crowd won't beat a good panel by
  much, because the panel already captures most of the recoverable accuracy.
- **Building is combinatorially open and not panel-approximable.** Concept generation and argument
  construction are exactly where diverse outside minds (lived experience, odd priors, domain
  specialists) contribute what a controlled panel won't think to. **Predict: V2 vs V3 diverges a lot.**

If that asymmetry holds, the design conclusion is striking and non-obvious: **open the build, close the
rate.** V2 becomes the sweet spot — most of the crowd's epistemic value, most of the attack surface
removed. That would be a genuinely publishable finding, and it falls straight out of what we've
measured.

## 3. Divergence-as-diagnostic (more valuable than any single score)

Don't just score the variants — **diff them.** Run one seed question through all three; the
disagreements are the signal:

- **V1↔V2 verdict divergences** flag either crowd bias (panel right, crowd carried a shared error — a
  tyranny-of-median instance caught in the wild) or panel blind spot (crowd caught what the in-house
  models share the n029-style blindness on). Either way it's an automatic *"where is model-consensus
  untrustworthy"* detector — the thing an all-model pipeline cannot see about itself — and exactly
  where to spend the scarce external/human check.
- **V2↔V3 structural differences** (nodes/edges V2 has that V3 never generated) are a concrete,
  countable measure of the crowd's concept-generation surplus.

This turns a multi-version deployment into a standing instrument for locating the frontier of its own
unreliability — arguably worth more than the horse race.

## 4. Benchmarks the versions could become

1. **A collective-epistemics graph-quality benchmark.** Same seed question + matched source pack +
   matched budget → score each variant's map against held-out documented ground truth (calibration,
   completeness, correct identification of the contested frontier). Distinct from standard single-shot
   model evals: it measures *quality of a collaboratively-built knowledge structure*, an axis with few
   good existing benchmarks.
2. **A model-diff benchmark (cheapest, most immediately useful).** Hold build constant, run V3 with
   different in-house panel compositions — swap vendors, generations, diversity. Because V3 is fully
   controlled, it's a clean testbed for *how much the model roster changes collective epistemic
   output* — e.g., does a non-Anthropic model move the panel off the whole-generation shared-bias
   floor (`n029`), and by how much? The panel-size curve could only reason about this; a mixed-model
   V3 measures it. **Prioritize this — no humans needed, and it turns the site into a repeatable
   instrument.**
3. **A reputation-mechanism / robustness benchmark.** V1 with injected synthetic adversaries (the
   deferred attack-surface work) vs V2/V3 as the controlled-quality reference. You cannot calibrate an
   attack's damage without a clean-signal control; V3 is that control.

## 5. The reality-refereed frontier — where "race to discover" becomes coherent

A race to "find new concepts / new results" is seductive but slippery on our current metrics: they
score *reasonableness/agreement*, not *verified correctness*, so a race scored that way rewards
plausible-and-agreed — a recipe for confident nonsense. The framing becomes sound exactly where
**truth is constructible and a referee exists that is not another model.**

- **Mathematics is the flagship case.** A proposition graph where node-A = "is this true" and edge-A =
  "does this inference step follow" *is* a proof-dependency structure at the limit. And math has a
  perfect anchor: a **formal verifier** (Lean/Coq-style). Everything our framework has had to
  apologize for — the model-grounding circularity, the shared-bias floor, the anchor-validation
  regress, tyranny-of-the-median — **dissolves when ground truth is machine-checkable.** A verified
  lemma is an objective, uncheatable, cheap-to-trust anchor: the regime our framework performs best in.
- **Empirical prediction is the second-best case** (physics, forecasting): reality eventually
  referees, on a delay.

### But target the tractable, continuously-scored frontier — not the famous prize (yet)

The bottleneck in frontier math is the **generative leap**, not coordination or memory. The site
excels where progress is *decomposition-limited*; the Riemann Hypothesis and peers are
*insight-limited* — a better-organized graph maps the crater where the missing idea should be without
manufacturing it. The verifier also referees only the **last mile** (a completed proof); the
conjecturing and machinery-building upstream stay in the soft-judgment regime. And a binary,
possibly-decades-out target yields no signal along the way — an un-instrument.

So sequence it:

1. **Formalization of existing mathematics** (flagship). A live global effort (mathlib etc.),
   decomposition-limited — the site's strength. Thousands of known-true results whose *proofs* need
   building as verified-lemma dependency graphs. Reality referees every node; the frontier moves
   continuously; "which version formalizes faster / with more reusable lemmas" is an immediate,
   honest benchmark of real community value.
2. **Lemma-mining and mid-tier open conjectures** (Erdős-style, competition generalizations) — where
   the known/unknown gap is one or two real steps, and the graph's gap-surfacing ("this node wants a
   ground that doesn't exist") becomes an actual conjecture generator that resolves on a useful
   timescale.
3. **Millennium-class problems as the north-star framing, not the KPI.** Point the machinery at RH;
   a well-maintained, formally-anchored graph of every approach and where each stalls is a real
   contribution even with zero progress on the conjecture. But grade success by frontier-advance on
   the tractable tiers.

The sequencing *is* the project's thesis in action: **earn credibility on problems where reality can
referee before claiming it on problems where it can't yet.** You don't need RH to fall to demonstrate
that AIs can collectively surpass humans in a domain — you need a reality-refereed frontier moving
visibly faster on one side.

### What the human-vs-AI math race would actually teach

With a verifier settling *validity*, the reputation machinery reallocates to the one thing the
verifier can't score: **which unproven directions are worth pursuing** — taste, promise, fruitfulness.
That is the real epistemic contest in math, and it stays a soft judgment where camps/calibration/our
whole toolkit still apply. The V2-math configuration (open-build conjectures + agents, verifier-checked)
is the likely-strongest setup: the crowd supplies the irreplaceable generative leaps; an incorruptible
referee disciplines them; reputation ranks the promising directions. And the honest guess for the
headline result is not "AI wins" or "humans win" but that **the merged graph dominates either alone** —
human mathematical taste and machine tirelessness fail in different places, and the site is precisely
the structure that lets them share one dependency graph rather than two separate literatures.

## 6. Credibility — the comparison is how you earn it

The closed (V3) version's weakness is credibility: "why trust a panel of AIs?" The side-by-side is the
answer. If V3 matches or beats V1 on every externally-groundable metric — tracks the open,
human-rated map and the documented record — that *is* the evidence. The multi-version deployment isn't
only science; it's the credibility argument for the controlled version, made empirically.

## 7. Caveats to hold onto

- **Matched conditions or the comparison is worthless** — same seed question, source pack, token/time
  budget, and (when isolating the rate layer) the same built corpus. Easy to accidentally vary three
  things and learn nothing.
- **All-in-house variants share the whole-generation bias floor** (`n029`); the human layer in V1 is
  the only component that can break it. The V1↔V2 diff measures *exactly how much the human layer moves
  the map off that floor* — plausibly the single most valuable number for deciding whether open
  rating's extra attack surface is worth it.
- **Our metrics score reasonableness, not correctness.** Outside the reality-refereed domains, "who
  discovered more" is not something the current system can honestly adjudicate; the honest output on a
  genuinely contested frontier stays "the camps," not "the anchor."
- **Everything here is speculative and unbuilt.** The near-term, no-new-infrastructure probes are:
  benchmark #2 (V3 with varied panel composition on the eggs graph we already have), and a
  math pipe-cleaner — take one small theorem with a known proof, build it as a proposition/inference
  graph, and check whether the structure eases the path to a formal verification. Validate the model on
  small, checkable things long before any Millennium Prize.
