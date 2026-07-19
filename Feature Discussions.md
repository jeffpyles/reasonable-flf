# Feature Discussions

*A living log of the concepts we work through together for Reasonable. Open-ended by design: each entry records what the feature is, where the conversation landed, and what's still unsettled — not final decisions carved in stone. As an idea firms up, its status moves toward **Settled**; things we're still chewing on stay **Open** or **Tentative** so we don't lose the threads.*

**Status legend:** 🟢 Settled (happy with it) · 🟡 Tentative (leaning a way, not certain) · 🔵 Open (still genuinely undecided)

---

## ⚙️ Prototype reminders (build/test at the right stage)

*Pointers parked here so staged build-time concerns don't get buried inside discussion entries.*

- **Core playground:** all scoring schemes (Brier/market-score, surprisingly-popular/BTS, blocs, closeness-to-consensus penalties) must be independently **toggleable, combinable, and tunable**, so we test them empirically rather than settle them by argument. *(Entry 3)*
- **Later prototype — refinement stage:** build/test the **"manufactured consensus" detector** — flag belief shifting suddenly/in coordination *without* corresponding argument churn (number moves, structure doesn't). Reuses the churn/settledness signal. Appropriate once base mechanics are working. *(Entry 4)*

- **Later build feature:** **prose / narrative generation from the settled Graph** — render the strongest lines of reasoning as a readable, mostly-linear essay with click-through to the underlying Graph regions. Serves the narrative-preferring majority while preserving full provenance; it's the inverse of decomposition (re-linearize along the strongest path). *(Entry 7)*
- **Open design tension to resolve in build:** layout **stability** (persistent landmarks → spatial memory) vs. **self-arranging physics** (lowest-energy re-flow). Likely: stable macro geography + local physics. *(Entry 7)*

**Prototype sequence (derived from the dependency chain across all entries):**

1. **Structure** *(Entry 7, ← current)* — is the 4-relation grammar coherent, sufficient, faithful (beats prose), and legible to a non-author? Hand/AI-authored, human-judged, **no mechanics**.
2. **Authoring consistency** — do independent agents map the same question into *similar* graphs? First bots, still no rating.
3. **Mechanics playground** — bot populations with biases/goals; rating, reputation, scoring schemes all toggleable/tunable *(Entries 3–4)*.
4. **Governance / refinement** — manufactured-consensus detection, etc. *(Entries 4–5)*.

---

## 1 · Explanatory depth levels (the "zoom of explanation")

*First discussed 2026-06-23. Source: Concept Overview §4 ("Zoom of explanation, not just of scale"); background docs "Mechanics of the site," "Features outline." Original placeholder terms: ELI5 / 10 / 15 / 25 / PhD.*

**What it is:** Independently of spatial zoom, every idea/node can be explained at a selectable *depth*, so a curious newcomer and a domain expert can both stand on the same node and get an account pitched to them. This is the "zoom of explanation."

**The problem with the original terms:** ELI5 / adult / PhD risk *prejudicing users against the level that would actually help them understand best*. They shame (ELI5 = "you're a child") and credential-gate (PhD), pushing people to over-reach into a level that's too hard, bounce off it, and learn nothing.

### Where we landed

- 🟢 **Core principle: label the *explanation*, not the *user*.** The decisive fix. ELI5/PhD and even Novice/Amateur/Adept all describe the *reader's rank*, so choosing a level becomes a small identity confession. Attaching labels to the explanation's *depth / content* makes the choice read as "which version will land for me right now," which carries no shame. (This principle should govern any future relabeling too.)
- 🟢 **Default = the friendly adult entry tier (The Gist / Straight Talk), with ELI5 one tap below.** The failure mode we're guarding against is people stranded at a level too hard for them, so dropping down should feel frictionless — but with ELI5 now the floor, the literal-simplest tier isn't the right *default* for an adult landing on a node; the second tier is the natural resting state.
- 🟢 **UI placement: a toggle/control right on the individual idea/node card in the zoomed-in (micro) view** — change depth in place, no menus.
- 🟢 **This axis is orthogonal to "kind of explanation."** Depth-of-explanation (this control) is a separate dimension from *framing for different kinds of minds* (mathematically- vs. literarily-inclined), which lives in the **Alternative-statement stacks** (z-axis). One control should not collapse both.
- 🟡 **Recorded state of the naming (let it percolate until we implement): `ELI5 · (The Gist / Straight Talk) · Nuanced · Technical` — a 4-tier set.**
  - **ELI5** (floor, reinstated): kept deliberately even though it labels the *reader* rather than the content, because the term is *playful rather than derogatory*, it produces explanations genuinely valuable for literal children, and it invites silly/child-like metaphors that often turn out to be genuinely insightful and perspective-shifting. A conscious exception to the label-the-content principle, justified by its generative upside.
  - **The Gist** *or* **Straight Talk** (the friendly adult entry): both liked; *Gist* sounds like the *clever/busy* choice rather than the humble one; *Straight Talk* leans warm and plain-spoken. Pick later.
  - **Nuanced** (middle): the *gist → caveats/qualifications → full machinery* ladder; on-brand for the site. Fallbacks if non-parallelism nags: *Detailed*, *In-depth*.
  - **Technical** (deepest): settled — neutral jargon warning, not a brag.
  - Rejected earlier: *Simple* (→ simplistic), *Layman's* (describes user; gendered), *Novice/Amateur/Adept* (rank the reader).
- 🟢 **Discrete tiers, not a continuous slider.** 3–4 named tiers can capture the full breadth of explanatory depth, and discreteness limits how many versions of an idea must be written and rated. (Supersedes the original ~5-anchor ELI5→PhD continuum.)
- 🟢 **Each depth-version is rated and ranked in its own stack.** Every separate version of the same idea is assessed within its own explanatory-level stack, so the system surfaces the *best version at each level* (not one global winner that's only good at one depth). This ties the depth levels directly into the argument-stack mechanics.

### Still open

- 🔵 **Exact wordmark for the adult entry tier:** *The Gist* vs. *Straight Talk* (and confirm *Nuanced* vs. *Detailed* for the middle). Let the 4-tier set percolate and re-judge when we implement.
- 🔵 **How many tiers — 3 or 4?** ELI5 reinstated makes it 4; need to confirm all four pull their weight (esp. that ELI5 and The Gist/Straight Talk are distinct enough to be worth separate versions).
- 🔵 **Authoring burden:** who writes each depth-version for a node (and does an idea need all tiers, or can tiers be sparse / filled in as "holes"?). The per-level-stack rating mechanic is settled; the authoring side is still open.

---

## 2 · Holes — surfacing open problems to the minds best suited to them

*Raised 2026-06-23. Parked for deeper discussion later — captured here so we don't lose it. Source: Concept Overview §4 ("Holes as well as nodes"); background doc "Notes on needed mindmap features."*

**What it is:** "Holes" are explicit placeholders for things we know we *don't* know but want to find a path to — answers indicated-but-unknown, charting the map's own frontiers. The open question is **discovery**: how does a given hole get found by the people and minds best suited to develop it?

**The tension to think about later (🔵 Open):**

- **Map placement is double-edged.** Putting a hole at the placers' collective best-guess location in the Graph is *somewhat* helpful (it sits near related known work), but spatial placement may actively *work against* the left-field, cross-disciplinary connection that often cracks a hard problem — the breakthrough frequently comes from an unexpected neighbor, not the obvious one.
- **Candidate discovery mechanisms to explore:** topic tags on holes; a searchable **directory of open holes** ("problems looking for solvers") that people can browse when they're looking for problems to work on, independent of where the hole sits on the map.
- Connects to: the "map doubles as a to-do list for editors" idea, and (later) the prospective-peer-review and innovation-bounty mechanics, where someone could attach a reward to filling a particular hole.

*No decisions yet — flagged as a thing to develop.*

---

## 3 · Consensus vs. truth — the reputation/credibility core

*First discussed 2026-06-23. **The central open question** — whether the mechanics produce reliable output at all. Fullest source: `Discussion of consensus vs truth and rating schemes to incent both.docx`. Synthesized in Concept Overview §5 (`#consensus`, `#blocs`) and §11 (the consensus-vs-truth box + the "ossify into orthodoxy" / Semmelweis box). Touches: Unaffiliated notes, Race to the bottom, Structure of Reasonable §II, Features outline.*

**The questions raised:** Is a user's Reasonableness/credibility tallied from both (a) scores on their own posts/comments and (b) the closeness of their votes to consensus? Does rewarding closeness-to-consensus merely enforce mainstream opinion and punish heterodoxy? Does small-bloc voting help reward best-guess-at-truth? Is there a way to reward people who were "wrong" (against consensus) early but "right" (consensus moved to them) in the end?

### Initial takes (all 🔵 Open — starting points for more discussion)

- **Untangle two reputations (key move).** *Authoring reputation* = Reasonableness scores others give your content ("do you produce fair, clear, well-reasoned posts?"). *Rater credibility* = how much your votes count, set by closeness to the (bloc/eventual) aggregate ("are you a good assessor?"). Different failure modes; the heterodoxy worry attaches almost entirely to the second. Keep them distinct even if they combine into one influence weight.
- **The heterodoxy worry is blunted by *what* you vote on.** The Reasonableness axis is "is this fairly/logically stated," not "do I agree." A heterodox-but-rigorous argument should score high there even from opponents — so the axis feeding *authoring* reputation is more orthodoxy-resistant than it looks. Danger zone = only where credibility tracks agreement on *contested substance*. → Lean the machinery hardest on clarity/fair-statedness; most lightly on "which side is right."
- **What small blocs actually buy:** an **honesty-extraction / independence** device, *not* an anti-bias one. ✅ Because you can't see the site-wide number or predict your bloc at the moment of judgment, your best play collapses to your honest read — which is why the *bloc-average* reward survives but the *extra overall-deviation penalty* (already self-flagged as a mistake) doesn't. ❌ They do nothing about *systematic* bias: every bloc is drawn from the same pool, so a leaning userbase yields a leaning mean.
- **Reframe the whole thing around independence + diversity (Condorcet / wisdom-of-crowds).** Aggregation tracks truth when individual reads beat chance AND errors are *uncorrelated*. So: blind voting + periodic updates + blocs exist to preserve **independence** (kill anchoring/cascades); viewpoint diversity preserves **uncorrelated error**. The system doesn't *detect* truth — it protects the conditions under which averaging can approximate it. More honest than "the Schelling point is truth."
- **Reward "early-wrong, eventually-right" — the biggest missing lever, and the antidote to ossification.** Score raters against the *eventual settled* assessment, not the *current* one: treat each rating as a prediction of where the node will stabilize (Brier / prediction-market scoring). Someone who rated against the early crowd and was vindicated when consensus moved to them should be rewarded *more* than conformists — inverting the heterodoxy penalty into a heterodoxy bonus *for heterodoxy that proves right*. The passive "minority placements persist and can grow" rule is the current escape hatch; this is the *active* incentive it lacks.
  - Real-time variant: the **"surprisingly popular" mechanism** (Prelec et al. 2017) — ask for both your rating and your guess of the average; positions scoring higher than predicted tend to be the better answers, and this provably beats majority vote. Could surface under-valued minority truths *now*, not only in hindsight.
  - Catches: needs a notion of a question **settling** (fine for clarity/empirical sub-claims; fraught for perennial contested questions that never converge — temporal reward may never fire).

**Bottom line:** existing mechanics are well-designed for *gaming* (blocs/blind voting) and *incivility/noise* (authoring reputation), but do **not** by themselves solve *truth-tracking* or *protect correct heterodoxy* (the docs are honest about this). Two highest-leverage additions: (a) reframe around **independence + diversity** as the truth-enabling conditions; (b) add **prediction-against-eventual-consensus scoring** so being correctly early is the best strategy, not a punished one. (b) is the top candidate to prototype in the bot-playground.

### Refinements, 2026-06-23 (cont.)

- 🟢 **Reputation = ONE Reasonableness score with TWO inputs** *(amended 2026-07-04, Entry 21; supersedes the earlier "two separate reputations, Authoring and Rating" framing).* A single number — how much this account's voice counts — fed by two evidence streams: (a) **authoring** (how others rate your nodes/comments) and (b) **rating** (how well your ratings predict the aggregate / your bloc). Both track **Reasonableness** ("how fair & reasonable is this person"), *not* truth or agreement. The separate **belief/endorsement (Agree)** rating exists but is *not* what weights influence.
- 🟡 **Diversity is recruited mainly by a competitive incentive, not an internal mechanic: "if you don't play, you lose."** Once the site is the canonical record of the state-of-play on a question, abstaining means letting opponents author the strongest version of your own view — and a steelman by someone who doesn't hold a view is weaker than one by someone who does. So non-participation cedes ground rather than staying neutral. This is the real engine for pulling in combative factions (→ uncorrelated error).
  - Caveat: this force is **zero at cold-start** — it depends entirely on the site's status as arbiter, so it lands directly on bootstrapping.
  - 🔵 **Bot-filled early graph = double-edged.** Bots representing views they don't hold *is* the "your view articulated by outsiders" situation — fine, even ideal, *if* bot positions are visibly **provisional placeholders acting as bait** ("here's a sketch of your side — come make it stronger"). Danger: AI framings silently entrenching so a faction arrives to find the terms already set against them. Bot content must be flagged provisional and easy to overwrite.
- 🟡 **Settledness measure (new affordance the format gives us):** measure **activity/churn** in the idea-landscape around a node — volume of new statements, turnover in best-rated versions, new connections forming. High churn = immature/unsettled; quiet = as settled as it'll get (until new info reignites it). This is what makes temporal scoring tractable; never been directly measurable before.
- 🟡 **Brier / market-scoring-rule prediction scoring (concrete sketch):**
  1. Treat every rating as a *forecast of where the node will settle* on an axis (normalized [0,1]).
  2. Score with a **proper scoring rule** (Brier/squared error): `(rating − settled_value)²`. Proper ⇒ incentive-compatible ⇒ honest reporting is the dominant strategy (does the bloc job mathematically; they stack).
  3. Reward **earliness** by scoring *improvement over the contemporaneous consensus* `C_t`: skill = `(C_t − settled)²` − `(rating − settled)²`. Late conformists ≈ 0; correct-early contrarians large +; wrong contrarians large −. This is **Hanson's market scoring rule** (telescopes to final − initial accuracy; only rewards real improvement; robust to wash-trading since you can't fake `settled`).
  4. **Escrow** credit while churn is high; **finalize** when the churn metric says quiet; **reopen** on new info → foresee-the-revision gets rewarded again (the Semmelweis case).
  5. **Never-settling questions:** roll the horizon — score against consensus N months out instead of a permanent end-state. "Settling" becomes a tunable horizon, not a binary.
  6. **Score the Reasonableness/quality axis, not belief.** "Where will reasonableness settle" is a legitimate forecasting target; "where will belief settle" drifts for non-truth reasons.
- 🟡 **"Surprisingly popular" (Prelec, Seung & McCoy, *Nature* 541:532–535, 2017; [link](https://www.nature.com/articles/nature21054)):** ask each rater (1) their answer and (2) their prediction of others' answers; pick the answer **more popular than predicted**. Informed minorities predict the majority's error; the wrong majority doesn't anticipate the minority — so the correct answer beats its predicted share. Cut errors ~21–35% vs. majority/confidence voting. Fits Reasonable unusually well: surfaces under-valued minority truths **with no settlement lag**; the meta-prediction question **rewards understanding the other side** (must model disagreers to predict the distribution) → a third credibility signal that also rewards the viewpoint-diverse.
  - **Bayesian Truth Serum** (Prelec, *Science* 2004, doi:10.1126/science.1102081) is the incentive-compatible sibling for **subjective questions with no verifiable answer** — possibly *more* applicable to Reasonable's domains, where ground truth often never arrives.
- 🔵 **Open:** how Brier/MSR (slow, needs settling) and SP/BTS (real-time, no settling) combine; how to adapt SP (built for single discrete questions) to continuous ratings on a persistent graph; whether predicting-the-distribution becomes its own gameable target.
- 🟢 **Prototype requirement:** all of these scoring schemes (Brier/market-score, surprisingly-popular/BTS, the blocs, the closeness-to-consensus penalties) must be **independently toggleable, combinable, and tunable** in the prototypes, so we can test how they actually play out rather than settle them by argument. The playground exists precisely because these can't be resolved on paper.

---

## 4 · Good consensus vs. bad consensus — consensus as a dynamic variable

*First discussed 2026-06-23. Builds directly on Entry 3. Source: this note + the consensus-vs-truth thread.*

**The framing:** Consensus isn't a fixed thing — it's a *dynamic variable* the site is designed to evolve onto a stronger basis of clarity and reasonableness. Consensus may be all we *can* have on non-provable questions, but there's still a **good consensus** (based on the best arguments we can make) vs. a **bad consensus** (based on lies and propaganda). Largely consolidates Entry 3 — but pushing on it surfaces concrete, prototypeable consequences:

- 🟡 **Consensus quality is computable from the argument substructure, separate from the belief number.** "Good consensus" = a belief whose supporting structure is dense, high-reasonableness, well-connected, with strong antitheses actually answered. "Bad consensus" = a high belief number on thin/weak/unaddressed grounds. → The site should never show "70% endorse X" alone; it should show "endorsement of X rests on *this structure, of quality Q*." Two beliefs at equal endorsement can differ wildly in consensus-quality.
- 🟡 **Belief–reasonableness divergence = a direct disinformation diagnostic.** Because the *belief/endorsement* axis is kept separate from the *reasonableness* axis, the gap between them is a signal: high endorsement on weak grounds (or beside strong, unanswered antitheses) = a belief held for reasons other than its arguments — the fingerprint of propaganda. Surface it as a first-class metric.
- 🟡 **The dynamic view turns churn data into a manufactured-consensus detector.** Genuine consensus forms as argument churn settles (new grounds, antitheses resolved, then quiet); a manufactured one shows belief shifting suddenly/in coordination *without* corresponding argument activity — number moved, structure didn't. The same temporal/churn signal defined for "settledness" (Entry 3) doubles as a "this was pushed, not reasoned" tell.
- 🟢 **Sharper north star:** the site's goal is not to drag consensus to a "correct" point but to **improve the basis whatever consensus rests on** — converting bad consensus into good (same conclusion or not). Success = the substructure grows denser/more reasonable/more complete over time, *whether or not the headline belief moves*. Philosophically: structured, clarified, stress-tested consensus isn't a consolation prize for missing truth in untestable domains — it's arguably the correct *definition* of knowledge there.

---

## 5 · A model of direct democracy / policy stability (long-horizon vision)

*Raised 2026-06-23. Explicitly a **long-term** thought, well down the road — contingent on the site succeeding wildly and becoming a premier sociopolitical institution. **Downstream of Entries 3–4** (it inherits and amplifies every unsolved consensus risk). Source: Concept Overview §9 (Politics & democracy); this note.*

**The vision:** Policy set by the *mature consensus* of what has the best argument for what to do given the full context — and which therefore changes when that reasoned consensus changes, **not** every 4–8 years on power turnover. A more stable, intelligible, predictable basis for law, policy, foreign affairs, and business than the whiplash of radical reversals under each new leader. (You can't have a reliable domestic or global environment when the ground shifts year to year.)

### Where we landed

- 🟢 **Anchor it at the *advisory* end, not the *binding* end.** Big difference between "the site sets policy" (technocratic, dangerous) and "the site makes acting against well-grounded consensus politically expensive" (legitimacy pressure / soft power). Your own framing is the latter — that's the version that holds up. Keep the vision as a **powerful epistemic input to democracy, not a replacement for it.**
- 🟢 **Stability is an underrated, distinct value.** Predictability *compounds* — a stable adequate policy can beat a volatile better one because actors can plan around it. This is a separate selling point from "better policies" ("less volatile policies"). Deeply **Burkean** (cf. the project's own quotes: Burke on the species being wise given time; parliament as a deliberative body for the general good).

### Honest seams (🔵 Open — all trace back to "this is downstream of good-consensus")

- **Stability cuts both ways** — only good if the consensus is good. A policy pinned to an *ossified* consensus (the Entry 3 risk) could entrench bad policy and be *harder* to change than elections. (Slavery had a stable mature consensus.)
- **Representation gap** — the site's userbase ≠ the electorate (skews educated/online/engaged). Pinning policy to *site* consensus risks substituting an unrepresentative deliberative elite for the public — the Fable's own warned-of failure. "If you don't play you lose" narrows but never closes this.
- **Capture risk grows with influence** — once the site has governmental influence, the stakes of getting its consensus wrong (or captured) rise accordingly. A live governance/legitimacy question, tracked as an open concern.
- **Stability vs. responsiveness** — electoral turnover is *also* a feature (a non-violent fast path to throw out leaders/policy). A consensus-pinned system needs a deliberately preserved fast path or it's too slow for real crises and genuine value-shifts.
- **Key design dial:** advisory input ↔ binding authority. The stability benefit largely lives at the advisory end *without* the dystopian downside; most objections bite only as you move toward binding.

---

## 6 · Naming the belief/endorsement axis (universal across all node types)

*First discussed 2026-06-23. Semantics/labeling. The "how much do I believe/endorse/approve this" rating — the second axis, distinct from Reasonableness (Entry 3). Source: this note; Concept Overview §5 (the belief-vs-reasonableness separation) and §7 (entity Approval). Original term: "Approval."*

**The question:** one label for the belief/endorsement axis that works across *all* node types — math/science claims, ethical claims, corporate-behavior evaluations, proposed government actions — without having to sort nodes into categories where it applies vs. doesn't. Candidates: Approve, Endorse, Believe, Support, Like, Agree.

### Where we landed

- 🟢 **The unlock: every node is a proposition — a statement — including evaluative ones.** The node is "*Coca-Cola's marketing is predatory*," not "Coca-Cola"; "*the government should do X*," not "this policy." So we don't need different verbs per node *type*; we need one verb for rating a *stance on a statement*. This dissolves the apply/doesn't-apply problem entirely.
- 🟢 **Settled label: `Agree` (Agree ↔ Disagree).** Reasons: (1) most natural verb for "stance on a proposition," which every node is; (2) pairs cleanly and *distinctly* with Reasonableness — "reasonable but I disagree" is natural, "reasonable but I don't approve" is clunky, so the two axes read as obviously different; (3) symmetric and captures opposition for free (matters for an antithesis-based site). (`Endorse` was the runner-up — slightly weightier but faintly formal.)
- 🟡 **Demote `Approve` from the universal slot.** Despite being the original term, it's awkward on descriptive claims ("I approve of P≠NP" is wrong — you *accept* facts, not approve them). It fails the universality test.
- 🟢 **Resolution that keeps everything: decouple the per-node label from the entity aggregate.** Universal per-node axis = **Agree/Disagree** (one label, every node, no type-sorting). **"Approval" survives as the entity-level *aggregate* metric** ("Coca-Cola's Approval score"), *computed from* Agreement ratings on the set of evaluative claims about that entity. Institution-assessment (Entry/Overview §7) loses nothing; "Approval" stays where it sounds right.

### Still open

- 🔵 **Provably-settled nodes edge case:** on a verified proof, "agreement" is nearly meaningless — the question collapses into validity/Reasonableness. Minor wrinkle; revisit, but not worth a node type-system over.

---

## 7 · First prototype = test the *structure* (before any mechanics)

*First discussed 2026-06-23. A sequencing/architecture decision. Source: this note; ties to Concept Overview assumptions #2 & #4 and open questions "atomicity vs. meaning" and "cold-start / minimum lovable slice."*

**The proposal (agreed 🟢):** the most useful first prototype tests whether the **structure** works — can the four-relation graph coherently order a real body of knowledge, capture the necessary logical relationships, and make them intuitive & clear — **before** adding rating, reputation, or any mechanics.

### Why structure-first (🟢)

- **Mechanics presuppose a coherent substrate.** Every scoring/reputation mechanic assumes "node," "stack," and the relations are well-defined and capture real logical structure. If atomic decomposition distorts meaning, no rating scheme saves it. Structure is the prerequisite *and* the riskiest unproven assumption (Overview #2 graph-mappable, #4 atomicity-preserves-meaning).
- **Isolates the variable** — test structure + mechanics + bots together and you can't tell which failed.
- **Cheap:** one question, a couple of authors, a layout tool. No network, accounts, or scale.

### What "the structure works" must mean — judge on four criteria (🟢)

- **Decomposability** — does a messy contested question break into atomic propositions without feeling arbitrary or regressing infinitely?
- **Relational sufficiency** — do the four relations *cover* real argument, or do we hit relationships that fit none/several ambiguously? **Keep a falsification log of every relationship the grammar can't cleanly express** — the single most valuable output. (Likely stress points: evidential support vs. deductive premise both collapsing to "Grounds"; "reframes the question" vs. Antithesis; Conjunction, already known to need a construct.)
- **Faithfulness vs. prose** — the thesis is *2-D beats 1-D*, but the bar is **completeness & accuracy of the full territory**, *not* "easier to read than an essay" (a good essay reads easier precisely by omitting complexity / picking one path). Test: a *willing* reader gets a deeper, more complete, more correct understanding from the Graph than from the best essay. (See corrected framing under Refinements.)
- **Reader legibility** — "intuitive & clear" needs a reader who *didn't* build it: an authoring side *and* a comprehension side.

### Refinements (note-8 discussion, 2026-06-23)

**Decomposition — grain & floor (🟢):** split/merge is a *core collective affordance* (users decide if a node should split into >1, or is too reduced to cohere; feeds later rating). Grain heuristic: a coherent idea ≈ a few sentences; a phrase/word/letter = "organic chemistry by reasoning about quarks." Natural **floor**: stop going down when a Ground bottoms out in an agreed primitive *or* **exits the Graph to an external reference** (paper, dataset, historical fact).

**Relational grammar — clarified (🟢):**
- The **primitive is a single directed support edge.** "Grounds" and "Dependents" are the *same edge from opposite ends* (A grounds B ⟺ B depends on A) — one relation, two names.
- **Conjunction = a grouping operator** on that edge (grounds that support *jointly*/AND vs. independently), not a peer relation. Probably needed in prototype 1 (A+B ground C only together).
- **Antitheses are NOT formal ¬X** — informal reader-convenience cross-pointers ("wormholes") to countervailing nodes elsewhere; not adjacency, not negation. **Deferred past prototype 1** (not logically fundamental; complicates layout). Caveat: opposition is central to the *value prop*, so a contested question still shows both sides as two support sub-trees — only the explicit cross-link is deferred.
- **No formal logic** — capture *informal* argument. Evidence vs. deductive premise are both **untyped Grounds**, differing only in *termination*: evidence tends to exit to external references; premises bottom out in other nodes/primitives. ⇒ external-reference leaves are first-class (and are what make the Graph a *grounded* knowledge base).
- **Alternative-statements are not an edge** — they're the z-stack of *restatements of one idea*, living with the stack/versioning system (alongside Gist/Nuanced/Technical depth tiers).
- ⇒ **Minimal grammar for prototype 1:** one directed support edge (Grounds/Dependents) + Conjunction grouping + external-reference leaf nodes. Antitheses & Alternative-stacks deferred.

**Reader legibility — tap spatial cognition (🟡):** the format isn't native neural hardware, but **spatial/navigational memory is** (method of loci / memory palace). If the Graph reads as a *stable, navigable landscape with persistent landmarks*, users can build durable spatial memory of an argument-territory.
- ⚠️ **Design tension (open):** this wants **layout stability** (learnable geography), which fights the **self-arranging physics / lowest-energy auto-layout** (re-flows on every change). Likely resolution: stable macro geography + local physics.
- Honest adoption risk: the Graph will *look* harder to absorb than a book even when it conveys more. The argument to win = deeper understanding after the Graph; the prose-generation feature + spatial intuitions are the two on-ramps.

### How to run the first pass (🟢)

- **One well-chosen question:** contested (real antitheses + alternatives), bounded (fully mappable), and **mixing empirical + normative** parts so it exercises all four relations. Candidates floated: *"Is eating meat morally permissible?"*, *"Should governments adopt a UBI?"* (Pure-empirical questions won't stress antithesis/alternative machinery.)
- **Hand-author it first (you + me), before any bots** — first learn whether *we* can build it coherently and what rules/edge-cases emerge. (A micro-version already exists: the hand-built "three methods of knowledge" graph from the Fable.)
- **No backend, no rating, no accounts** — a static or lightly-interactive node-edge layout suffices.
- AI's role here = decomposition proposer / co-author (a first test of AI-as-scaffolding); bots-as-rating-populations come in prototype 3.

### Still open

- 🟡 **Which question to map first** — strong candidate: an **FLF competition topic** (see Entry 9), leaning **lab-leak / COVID origins** (rich evidence base, contested, exercises grounds/conjunction/external-reference leaves). Confirm with topic/cycle decision.
- 🔵 **What tool** for the first layout (paper/whiteboard → simple graph tool → custom). Decide when we pick the question.

---

## 8 · Dogfood: structure prototype as the project's own notes app

*Note 8, 2026-06-23.* Once the structure prototype is tuned and working, map *this project's own* proposed/debated structures & mechanisms (this `Feature Discussions` doc) into the Graph. A recursive test, an honest first dataset, and an embodiment of the "site's machinery turned on itself" theme. 🟡 Caveat: our design space is more *constructive/normative* than the FLF-style empirical cases, so it exercises different relation-types — good ongoing dogfood, not necessarily the competition artifact.

---

## 9 · Funding/launch target: FLF Epistemic Case Study Competition

*Raised 2026-06-23. (Note 9's "next prototypes explore mechanisms/rating" is already captured in the Prototype sequence; the substantive new item is this external opportunity.) Source: web search — **flf.org/epistack is egress-blocked from this environment, so specifics below are unverified and the user should confirm directly.***

**Facts (per search, to verify):** FLF (Future of Life Foundation) runs the **Epistemic Case Study Competition ("EpiStack")** — seeking the best workflows/methodologies for using **AI to produce reliable, trustworthy knowledge bases grounded in real-world cases.** ~**$200k** pool; **$5k–$50k** per winner (multiple $50k possible); **winners may get further funded work.** **Deadline reported July 19, 2026** (~25 days from 2026-06-24). Topics include **lab-leak/COVID origins, black holes, eggs (dietary cholesterol)**; open-minded on submission form.

- 🟢 **Fit is strong:** "AI workflow → trustworthy knowledge base grounded in real cases" ≈ our structure prototype (a real contested question decomposed into an argument/evidence Graph whose evidence-grounds exit to external references = grounding in reality), built via AI-assisted authoring. The Graph *is* a structured knowledge base. Reinforces (doesn't compete with) the structure-first plan.
- 🟡 **Recommended scope if we enter:** **one topic mapped as a structural argument/evidence Graph + a short methodology writeup of the AI-assisted workflow.** Explicitly *not* the full platform — no rating/accounts/scale (those are prototypes 3–4).
- 🟡 **Topic lean: lab-leak / COVID origins** (richest; contested; heavy grounds/conjunction/external-reference use; antithesis-deferral fine since it's evidence-weighing). Black holes = more settled, clean inference chains. Eggs = flip-flopping consensus, better for later consensus-quality/churn work.
- 🔵 **Decisions needed:** (1) target *this* cycle, or treat the deadline as a forcing function for a v0 regardless? 25 days is tight. (2) **Verify** deadline / exact topics / submission format / eligibility at flf.org/epistack (blocked here). (3) Register interest now (low cost; gets updates & commentary)?

**Update (2026-06-24, verified from primary sources).** The user uploaded the actual FLF pages + rules + judging appendix to `/FLF`. Earlier search-based facts now **confirmed**: ~$200k pool, $5k–$50k tiers (multiple $50k possible), winners may get further funded work, three cases (COVID origins / LHC black holes / eggs), open-minded on form. **Deadline confirmed: entries due Jul 19, 2026** (submission via a linked form; general contest rules are boilerplate — you retain ownership but grant FLF a broad license, 18+, sanctions exclusions). The full criteria and the reframe they imply are in **Entry 10**, which supersedes the "pick one topic" lean above.

---

## 10 · Submission reframe: the *prototype + workflow* is the deliverable (not one topic's output)

*Raised 2026-06-24, after reading the real `/FLF` materials (competition page, "The Epistemic Stack," judging appendix, contest rules).*

**The reframe (user's framing, 🟢).** The submission is **the Reasonable prototype format/app itself** — a tool + methodology that *reliably produces coherent structured output* — **not** the hand-crafted analysis of any single question. Around it: (a) **output Graphs for each of FLF's case questions**, generated by the tool, included for reference; and (b) **instructions for how FLF can direct their own swarm of AI agents** (Haiku/Sonnet bots) to fill out structure for these and other questions. Build path is unchanged — prototype through versions, layering refinements — aiming to have something minimally viable *near* the deadline that we can point bot-swarms at to generate the reference Graphs. **We aim at Jul 19 but don't stress it and won't submit anything that doesn't feel genuinely good.**

**Why this is the right read — it maps onto FLF's own criteria almost 1:1 (🟢):**

- **They want methodology, not artifacts.** Page: *"the best workflows and methodologies for using AI to produce reliable, trustworthy knowledge bases."* Judge note #2: *"Read for the spec, not the polish. A clear workflow with a rough prototype usually beats a polished prototype with opaque methodology."* ⇒ The reframe is exactly what they're asking for.
- **Their "Epistemic Stack" = our architecture.** They split investigation into **ingestion → structure → assessment**. Their **structure** layer ("capturing the relations between sources, claims, authors… what evidence/reasons support that, what counterarguments exist") **is the Reasonable Graph.** Our belief/endorsement axis + consensus/credibility mechanics **are their assessment layer** — which they explicitly call *more subjective, "late-binding," customizable per party.* Our objective-structure-vs-subjective-judgment split (Entries 3–6) is **their exact framing**, independently arrived at.
- **The structure layer is the sweet spot.** FLF says the structural level is both the **most objective/shareable/compounding** *and* under-served. That's precisely where our structure-first prototype (Entry 7) lives. External validation of the plan we already had.
- **The swarm = their Scalability dimension.** Criterion 4: *"Not bottlenecked on any single hand-designed human step… scales to mostly-or-entirely hands-free… benefits as base-model capability rises."* The "direct-your-own-bot-swarm" instructions aren't an afterthought — they're how we score on a whole judged dimension. **First-class deliverable.**
- **Submission shapes match.** They name three welcome shapes: a **spec/workflow**, a **prototype tool**, a **protocol for interoperability without flattening.** We're doing prototype-tool + workflow-spec, and the Reasonable *format* aspires to be the protocol. Good alignment across all three.

**Judged dimensions (verbatim list, to design against):** 1 Epistemic uplift · 2 Generalizability · 3 Compounding & shareability · 4 Scalability · 5 Methodological transparency · 6 Adversarial robustness · 7 Insight contribution. Tiers: Promising $5–15k · Strong $15–35k · Transformative $35–50k.

**Cautions / consequences for the plan (🟡):**

- **The bar is explicit: "meaningfully better than off-the-shelf deep research / a careful Claude Code investigation on the same sub-question."** Judges *anchor against that baseline first.* Everything we build must clear it. Design and demo with that comparison in mind.
- **"Run it, don't just read it."** Judges will *exercise* the methodology on a sub-question they pick. ⇒ the prototype must **actually run** (repeatably, on a case) — not merely be described. Pushes toward a real, demonstrable pipeline over a paper spec.
- **Topic choice dissolves into coverage (supersedes Entry 9's "lean lab-leak").** Criterion 2 rewards working *across cases of different shape*, and the three cases are deliberately the three profiles: **COVID = curated debate; black holes = confident answer w/ complex technical evidence; eggs = mundane-but-contested.** Submission shapes ask to *"demonstrate on multiple parts of at least two cases."* ⇒ We don't bet on one topic — we **develop/stress-test on one first, then show the engine generalizing across ≥2–3.** Which topic we *start* with (for building the format) is now a low-stakes call; eggs is still the cleanest dev sandbox, lab-leak the richest showcase.
- **Honesty as strategy.** Criteria 1, 5, 6 all reward *naming uncertainty, faithfulness to evidence, bounded failure modes.* The "swarm output, warts visible" idea fits: showing what the unsupervised swarm produces (with its flaws marked) scores on transparency + adversarial robustness rather than against them.
- **Format constraints:** written discussion ≤ ~10 pages (excl. appendices/worked examples); worked examples can be large but must be **navigable, with curated pointers to the best regions**; code should be either brief legible pseudocode or near-one-click runnable.

**Status:** reframe 🟢 settled; the *open* items are now build-sequencing, not strategy — which case to develop on first, and how far up the stack (structure-only vs. a thin assessment slice) the submission reaches.

---

## 11 · v0 structural-test spec — the node, the grammar, the affordances

*Worked out 2026-06-24 (notes dialogue). This is the concrete build target for Prototype 1 (the "Structure" step in the sequence above). It **redraws the v0 line** from Entry 7's "no mechanics": v0 now includes **structural consensus** (agreement on connections/titles/phrasings) but still excludes **assessment** (node-quality ratings, reputation-weighting, sinking).*

**What v0 tests:** can the structural grammar coherently *capture and convey* argumentative structure & meaning? So v0 must include any **structural** affordance that materially contributes to sense-making, and exclude everything that's assessment or polish.

### The node (🟢)

- **A node is a truth-apt proposition** — something that can be supported or contested. Empirical, normative, and definitional/framing claims all allowed (the mix stresses the relations).
- **Two flavors:** (a) *untyped internal claim* (the default majority); (b) *external-anchor node* — carries source/provenance and points **outside** the graph (merges Entry 7's "external-reference leaf," the "empirical" type, and provenance into one thing). Most nodes are (a); (b) is where the graph touches reality.
- **Questions are NOT nodes** (not truth-apt). The question stays **implicit**; its rival answers are the nodes. A malformed question-node should strand (attract no clean G/D edges) and, once assessment exists, sink. In v0 we test the norm by *instruction + observation*.
- **Node-level Title** — a short, lossy handle shown whenever the node isn't the focus card (margin/arc cards must be scannable). Title is of the *node*, not of any Phrasing; title + best phrasing co-evolve. In v0: agents propose a title on creation, others Agree; fallback = one title-writing pass over the finished graph.
- **Phrasings** — a z-stack of competing *wordings* of the same claim (the Clarity competition). The stack exists in v0; the *rating* that ranks it is post-v0.
- **Claim-text length cap = a tunable knob, not a fixed number.** It's really a **lever on grain** — freezing it pre-decides the decomposition-grain question we're testing. Start ~350 chars, err long; falsification log moves it (truncating atomic ideas → raise; sprawling into compound claims → lower).

### The grammar (🟢) — support-only + Antitheses

- **One directed support edge = Grounds / Dependents** (same edge, two ends: A grounds B ⟺ B depends on A). The structural backbone.
- **Conjunction** = a grouping operator on that edge (grounds that support *jointly*/AND vs. independently). In v0.
- **Antitheses = a set-relation** (see below). Non-local; node-view only.
- **Support-only. No "negative claim" object.** Every claim is a positive assertion about reality in its own chain; opposition is expressed as *competing positive claims linked by Antitheses*, not as negation. Undercutting/retraction is handled by **re-weighting**: a study is a bundle of claims; retraction downgrades them; the downgrade propagates and relative standing vs. Antitheses self-corrects. **v0 falsification test:** does support-only (+ meta-nodes that assert another node's reliability) capture *all* opposition, or do we hit cases that force an undercut edge?

### Antitheses — the set model (🟢)

- An Antithesis is **membership in a shared set** of ~4–6 direct rival nodes (competitors at the single-concept level; sets rarely larger). A node can belong to several sets.
- Each member carries an agreement-weighted **belonging-strength**. Users draw a node into a set; others Agree (strengthen) or draw competing membership.
- **Node-view rendering:** the whole set shown as an **arc of title cards**, ordered by belonging-strength — weakest at low-mid-left, strongest at high-mid-right, focus node in its own slot (click a rival → arc re-centers on it). Distance between neighbors = relative belonging-strength.
- **v0 vs post-v0 signals:** *position/proximity = belonging-strength* is v0; *card color/brightness = node quality* is post-v0; the *ties-broken-by-Reasonableness* rule is post-v0 (v0 ties fall in insertion order).
- **Why it's in v0:** you can't understand a contested question without seeing the live rivals and their relative strength; we're testing on a contested question, so omitting this tests a strawman. **Falsification test:** does the arc reliably read as "these are *all* the live answers," or just "some things in tension with this one"? (If the latter, that's the evidence for an explicit question/frame object later.)

### Structural consensus — the Agreement affordance (🟢)

- Users/agents **draw** connections (G/D/Antithesis); others **Agree** or decline; agreement-count **strengthens** the connection.
- **Strength → proximity**, applied to *both* G/D and Antitheses: stronger connection = shorter line / closer node. This is a **deterministic rendering rule**, IN v0 — *not* an interactive force simulation (that's v0.5+). At node/ego-view (where v0 lives) it's trivial: place each neighbor on a radius ∝ 1/strength; it only becomes force-directed-hard when satisfying all pairwise distances across a large neighborhood at once, which v0 doesn't need.
- **Post-v0:** agreement weighted by the voter's Reasonableness (reputation-weighting).

### The v0 line, explicitly (🟢)

- **IN:** the node model, G/D + Conjunction + Antithesis grammar, support-only, structural consensus (Agree on connections/titles/phrasings), strength→proximity rendering rule, node-view + neighborhood-view.
- **OUT (post-structure):** node-quality ratings (Reasonableness/Clarity), color/brightness quality cues, reputation-weighted votes, sinking/demotion *resolution*, threaded comments, depth tiers, force-directed physics, the wider zoom ladder.

### Agent affordances / verb-set (🟢)

- `create node` · `draw edge (Ground / Dependent / Antithesis)` · `agree with an edge` · `propose/agree a title` · `propose/agree a phrasing`.
- **Split/merge are emergent, not verbs.** To split: create the finer sub-concept nodes as a path routing around the original; if more agreed, it strengthens and the original loses relative standing. To merge: create the consolidated node and see if it's agreed. ⇒ the graph routinely holds **competing parallel decomposition-paths** — the structural-scale twin of the Phrasing z-stack (competing *wordings* of a node ↔ competing *decompositions* of a region). v0 can test whether agents *use* this; *resolving* between rival structures needs the assessment layer (post-v0). Eventual tool for "these two paths are the same conception" = **structural synonymy / path-equivalence** (parked), plus eventual garbage collection.

### Views (🟡)

- **v0:** *node-view* (focus card + G/D + Antithesis arc) and *neighborhood-view* (titles + G/D structure, **no** Antitheses — wormholes would clutter it). These are two reading affordances, not just zoom levels: neighborhood = "follow one line of reasoning"; node = "see this claim in full crossfire." 2D at both scales.
- **Parked:** the wider ladder — titles fade → neighborhood tags → field/branch tags → near-full zoom-out "twinkling" global view (abstracted, not per-node). Store v0 data so it doesn't assume a single zoom level.

### How v0 is run (🟡)

- **Hand-seed first:** you + me map one small slice of the chosen question by hand (≈ a day) → produces (a) a gold reference graph and (b) the first draft of agent instructions. *Then* agents build + Agree. Rationale: can't write good agent instructions for a grammar whose edge-cases we've never hit, and it lets us tell *agent confusion* apart from *grammar insufficiency*.
- **Agents from the start** (consistent with Entry 7's "Hand/AI-authored" Prototype 1), with the rudimentary voting affordances above.
- **Test question:** one contested question — eggs = cleanest dev sandbox, lab-leak = richest showcase; pick at build start.

### What we measure (🟢) — plus this arc's falsification-log items

Criteria from Entry 7: **decomposability · relational sufficiency · faithfulness (beats prose) · legibility (to a non-author).** Keep the **falsification log** (every relationship the grammar can't cleanly express). New explicit items:
1. Does support-only (+ reliability meta-nodes) capture all opposition, or do we need an undercut edge?
2. Does the Antithesis arc convey "these are *all* the live rivals"?
3. At ~350 chars, are margin/arc cards readable without a title — and do titles ever distort/prejudge?
4. Do agents strand themselves on question-shaped nodes?
5. How often do cycles appear; are they a problem?
6. Do competing decomposition-paths proliferate unmanageably?

### Test-suite tunable variables (🟢)

edge-set enabled (v0 = G + Conjunction + Antithesis) · polarity (v0 = support-only) · decomposition grain (via agent instruction) · claim-length cap (~350, a knob) · title on/off · phrasing-vs-new-node boundary (watch) · antithesis exclusivity (graded by agreement) · cycles (allowed, self-flagging, watch) · node typing (untyped vs. tagged) · provenance (external-anchor nodes).

### Parked mechanisms (post-v0)

- **Cumulative-chain-strength metric (🟡):** per-node factor = strength of the strongest underlying chain; doubles as (a) a readout of overall line-of-reasoning strength and (b) the propagation channel for downstream re-weighting when an upstream node changes. Build-time refinements: respect Conjunction (independent grounds *add* confidence; conjunctive grounds *gated by weakest member*); **per-hop distance discount** (longer chains attenuate — the quantitative form of "more steps = more places to fail"); **cycle-safe propagation** (damping or propagate over an acyclic spanning structure).
- **Structural synonymy / path-equivalence (🔵)** — mark competing decomposition-paths as alternate conceptions of one region (Phrasing-stack for subgraphs) + garbage collection.
- Reputation-weighted agreement · node-quality ratings (Reasonableness/Clarity) · sinking/demotion · depth tiers · threaded comments · force-directed physics · full zoom ladder · the "connect all three FLF cases via distant branches" stretch goal (Entry 10).

---

## 12 · First hand-seed built + friction triage — scope-artifact reframe

*2026-07-02. Built the first real graph through the v0 CLI: the eggs / dietary-cholesterol→CVD crux (17 nodes, 13 grounds, 2 conjunctions, 3 antithesis sets, 7 frictions) — committed at `v0/gold-eggs/` with `FINDINGS.md`. Interactive artifact published (redeploys on viewer changes). Then triaged the 7 frictions together.*

**Headline finding (🟢): a small test slice manufactures false "grammar-insufficiency" frictions.** Unbuilt argument is indistinguishable from unrepresentable argument, so several first-pass frictions were **scope artifacts, not grammar limits.** ⇒ Correct next move is a **fuller buildout on the current grammar**, *not* a pivot to negative-claim/undercut edges. This also discounts how much weight any small-slice falsification log should carry.

**Friction triage:**
- **F5 undercutting (🟢 build-out-first, don't pivot):** "confounded" is a legitimate *positive* claim with its own chain; causal-vs-confounded is a real antithesis. Over-read earlier. **Residual to watch:** *pure* undercutters (attack an inference/source, assert no rival conclusion — "observational≠causal," "study retracted") become **meta-nodes** (node whose subject is another node/edge); watch if they read clearly. The retraction/fraud case = **study-level re-weighting** = same mechanism as F2.
- **F1 appeal-to-authority (🟢 scope):** in a complete graph, "guidelines changed" is a pointer to the committee's reasoning; authority *dissolves into* it and rhetorical thinness shows up as **structural thinness**. Residual: whether thinness reliably reads as rhetorical, or we later want an optional support-type tag. Minor.
- **F2 study-id (🟢 concrete v0.1 add):** external_anchor carries a `study_id`; a verb to list studies + attach nodes to an existing one. Enables post-hoc re-weighting of a whole study cluster on fraud/retraction — also the clean answer to F5's pure-undercutter case.
- **F3 pack coverage (🟢 minor):** mostly a test-condition limit. Small worthwhile fix (authoring realism, not grammar): allow external_anchor to cite a **free-text unverified source** when the pack lacks one. Optional.
- **F4 graded antithesis (🟢 resolved by scale):** wider Agreement on membership; tenuous members render as looser connections. Design working as intended.
- **F6 relevance horizon (🟢 scope):** Entry 10 continuity in action; horizon recedes as far as anyone explores.

**F7 — is/ought — 🔵 OPEN (genuine disagreement, unsettled):**
- *User's position:* no *ought* nodes at all — not truth-apt; a general "should" depends on conditions/preferences; decompose into conditional Is-nodes (specific risk under conditions); malformed oughts handled by collective promotion of better structure + eventual **garbage collection** of "not-even-wrong" (oughts, spam) — distinct from removing merely-*weak* (legit) arguments.
- *Fable's counter:* (1) "oughts aren't truth-apt" is **non-cognitivism** — a contested metaethical stance, not a neutral default. (2) **Collides with our own logged decisions:** Entry 5 (pin *policy* — "should govt adopt UBI?") and Entry 6 (the **Agree** axis settled using *"the government should do X"* as the worked example) both commit to ratable normative nodes; banishing oughts guts the political domain the site is meant to inform. (3) Better diagnosis: the malformation is a *hidden, unconditional* ought with **suppressed premises**, not normativity itself. Proposed well-formedness rule — **an ought is well-formed iff it exposes (a) its conditions and (b) ≥1 value-premise node as a Ground**; then the is→ought step is visible and the value premise is Agreed/disagreed *separately* from the facts. Keeps the user's decomposition instinct (conditional Is-claims become the factual grounds) while retaining normativity.
- *Reframed finding (if counter holds):* not "oughts are malformed" but "**the grammar doesn't yet require oughts to expose their value premises.**"
- **Garbage collection (🟡 concept agreed, criteria open):** never GC a legitimate weak argument; GC keys on **form** (truth-apt? connects?), never content (else "malformed" = "a reframe I dislike"); spam yes. Per the counter, oughts should *not* be in the GC bucket.

**Other settled (🟢):**
- **Near-duplicates** resolved by a collective "this node is the same as that" affordance (mechanics TBD) — same pattern as everything else on the site.
- **Verdict update:** the genuine grammar-change surface after triage is *narrow* — pure-undercutter/meta-node reading (F5), study-id (F2), ought-exposes-premises (F7 if counter holds). Much smaller than the first pass implied; the current grammar is holding up better than the raw friction count suggested.

**Viewer changes (🟢, in build):** neighborhood-view = **full graph** (all nodes + all G/D, no antitheses, no focus node), **drag-to-pan** (+ optional wheel-zoom), **click card → node-view**, fix overlapping sibling cards (deterministic layered DAG layout); node-view **antithesis arc excludes the focus node** (no self-duplication).

**Process (🟢):** every subsequent test result gets its own clickable **artifact** (cross-device workflow); new graphs → new links; viewer improvements → redeploy affected artifact to same URL.

---

## 13 · Design meta-principle: the grammar defines the *possible*, not the *mandatory* (F7 resolved)

*2026-07-02. Resolves Entry 12's open F7 and names the principle that decided it — and F5, and will decide future "should the grammar enforce X?" questions.*

**The principle (🟢):** **the grammar defines what *can* be expressed, not what *must* be. Well-formedness is emergent and collective (rating + Agreement + the eventual assessment layer), not schema-enforced.** The minimal grammar stays permissive; the mechanics do the policing. This is the standing answer to "do we need a new rule / edge / node-type / requirement?" — default **no**; let the collective layer surface and demote the problem. (Crystallizes what Entry 7's "no formal logic — rely on innate reason + collective filtering" already implied; F5 and F7 are both instances.)

**F7 (is/ought) — settled the user's way (🟢).** Both sides agreed oughts are **not** malformed and normative nodes belong in the graph (they're ratable via Agree; the policy vision needs them). On the follow-up — *should we require an ought to expose a value premise?* — **no special rule.** Reasons:
- A hard requirement would force **mandatory normative node-typing** (to know which nodes are oughts), reversing the untyped-by-default decision (Entry 11) and re-introducing the node-category sorting dissolved in Entry 6.
- It's a **formal-schema rule**, exactly what Entry 7 rejected. We don't require empirical claims to name their premises either.
- The is/ought gap is just a special case of **"a conclusion resting on an unstated load-bearing premise."** General mechanics handle it: a user adds the value premise (now itself a first-class, contestable, Agree-able node — the thing we actually cared about), or nobody does and the ought underperforms.

**Residual, parked as guidance not enforcement (🟡):** the is/ought gap is unusually easy to commit *invisibly* — a smuggled value premise can leave an ought looking fully grounded on true empirical claims. A *superficially* well-supported ought could accrue undue agreement before someone notices. Handle where it belongs: (a) a **light nudge in `AGENT-GUIDE.md`** ("when a node prescribes an action, check whether its value premise is stated — if not, add it or expect it contested"), and (b) later, a natural case for the assessment layer's **"hidden assumption / thin support" detector** (kin to the manufactured-consensus and belief–reasonableness-divergence diagnostics, Entry 4). Not a grammar rule.

⇒ **Entry 12's "grammar-change surface" shrinks further:** now just **study-id (F2)** and the **pure-undercutter/meta-node reading to watch (F5)**. F7 needs no grammar change.

---

## 14 · Fuller eggs buildout — the scope-artifact hypothesis confirmed (grammar-change surface → 0)

*2026-07-02. Extended the first-pass graph to 27 nodes on the **unchanged grammar** to test Entry 12's hypothesis (first-pass frictions were mostly scope artifacts). Committed at `v0/eggs-full/` (continues the gold-eggs event log; n018–n027 = this pass) + `FINDINGS.md`; its own interactive artifact published.*

**Result (🟢): hypothesis held. 5 of 7 first-pass frictions dissolved with NO grammar change; 1 mitigated; 1 out-of-scope-by-design.**
- **F5 (headline) DISSOLVED:** the "confounded" node — orphaned last pass — grew its **own positive support chain** (n018/n019/n020) and now sits in real antithesis with a balanced causal chain (n016 ← n013/n021/n022). `stats` orphans 1→0. **No negative/undercut edge needed** — the user's "build it out first" call was right, and F5's earlier "residual" largely evaporated too.
- **F1 DISSOLVED:** authority node (n007) now grounded by the actual biological reason (n005); the appeal *dissolved into* the reasoning it pointed at.
- **F7 DISSOLVED (no rule):** the ought (n015) now carries an explicit value-premise ground (n027) — supplied by normal authoring, exactly per Entry 13.
- **F6 RECEDED:** LDL→CVD (n010) now also grounded by MR (n025) + trial (n026) claims; horizon moved out a layer (still finite = expected).
- **F2 RESOLVED:** study grouping (`eggs-001`→2 nodes, `eggs-004`→2 nodes) + new **`list-studies`** read verb (find a study id, see all attached claims, for later whole-study re-weighting). Read convenience, *not* a grammar change.
- **F3 MITIGATED:** pack expanded (Rong 2013 = `eggs-004`); guide now allows a **free-text unverified `--source`** when the pack lacks one.
- **F4 unchanged (by design):** resolved by scale, not buildout.

**⇒ Grammar-change surface after this pass: ZERO.** The support-only + Antitheses grammar survived a harder, more complete argument. *This is the headline result to report to FLF: the minimal grammar's apparent gaps were mostly unbuilt argument.*

**Two NEW frictions — better ones, both additive affordances (not core-grammar fixes), both FLF-valued (🟡 wishlist, post-v0):**
- **F8 — reusable/shared nodes.** A general principle (n019, "observational data can't establish causation") bears on *every* causal inference but could only attach as one local ground. Wants to be a single **shared node** linked from many inference points (the wormhole/reuse idea). Serves FLF *compounding*.
- **F9 — crux vs. common ground.** n021 (the association is real) is **common ground both rivals accept**; the crux is only the causal-vs-confounded interpretation. Grammar marks no difference between shared premise and crux. FLF **explicitly** wants cruxes surfaced (criterion 1). High-value additive tag.

**Resolutions (2026-07-02, user — both settled 🟢 as post-v0 structural affordances, neither a core-grammar change):**
- **F8 → trunk / wormhole by fanout.** A hugely-general node (e.g. "correlation ≠ causation") is not a local ground redrawn everywhere; it sits **upstream of a vast cloud of branches that implicitly depend on it** — part of the knowledge graph's **main trunk**. Proposed rule: **a connection to a node above some degree threshold auto-renders as a wormhole portal, not local spider-silk**, so it never drags its many other links into the local view. Bonus: this *defines* the trunk empirically (= the highest-degree nodes) rather than by hand.
- **F9 → crux = lowest common ancestor.** The crux between two positions is where their support chains diverge. **Select two nodes → highlight both chains back to their last common ancestor**; you get the crux *and* everything built from it on each side. Build-time note: on a DAG with multiple paths/cycles it's the *set* of deepest common ancestors, not a single node — a solvable traversal.

**Tooling landed this pass (🟢):** `list-studies` verb (F2); `AGENT-GUIDE.md` gains the is/ought value-premise nudge (Entry 13), the free-text-source allowance (F3), and study-grouping guidance (F2).

**Process (🟢):** fuller graph published as its own artifact (distinct from the first-pass link), per Entry 12's standing practice.

---

## 15 · First swarm test — independent agents build a coherent graph (Prototype 2 territory)

*2026-07-02. Ran 4 Sonnet agents **sequentially** (each saw prior work), distinct perspectives (mainstream physicist / risk-skeptic / methodologist / synthesizer), on a NEW question of a different shape — **"Could the LHC create a black hole that destroys Earth?"** (consensus-with-vocal-edge, vs. eggs' genuine split) — building ONE shared graph from a source pack + the standard `AGENT-GUIDE`, no human intervention. Committed at `v0/swarm-blackholes/` + `FINDINGS.md`; artifact "blackholes-swarm-v1". Also confirms viewer generalizes to a second domain.*

**Result (🟢): independent agents built a coherent graph.** 23 nodes · 25 grounds · 4 antithesis sets · 24 agrees · 7 frictions · **0 orphans · 0 duplicates.** The format's disciplines **transferred to independent agents from the guide alone** — the core FLF scalability bet:
- **Search-before-create worked → zero duplicates** (the predicted #1 failure mode did not occur; author 2 reused nodes and joined existing antithesis sets rather than forking).
- **Support-only held** (all opposition as rival positive claims; 4 cruxes as antithesis sets).
- **The is/ought nudge (Entry 13) propagated** — two different agents added value-premise grounds under their ought nodes, unprompted.
- Both top positions reachable with full chains; minority side **steelmanned, not strawmanned**.

**Money finding (🟢, with caveat): agreement tracked inferential SOUNDNESS, not side.** Agrees were selective (edge agree-counts 0:9 / 1:9 / 2:6 / 3:1 — not flat rubber-stamp). Agreement concentrated on genuinely sound steps **across ideological lines** — the mainstream evidential backbone *and* a sound risk-side step ("Hawking radiation empirically unconfirmed") both drew multi-agent agreement; the contested cruxes ("evaporation reliable enough to trust", "mere production-possibility → risk") stayed near zero. Structural consensus did real epistemic work.
- ⚠️ **Honest caveat:** in a *sequential* run, late-created edges have fewer/no later reviewers, so "0 agrees" conflates *contested* with *created-late-unreviewed* (the synthesizer's own new edge sits at 0 only because nobody followed). Clean signal = the **reviewed** set. A looping/larger swarm removes the confound. Limitation of a 4-agent linear run, not of the mechanism.

**Friction convergence — the one well-evidenced additive primitive (🟡 → strongest grammar-adjacent candidate):** across 7 frictions, the important pattern is that **f5 (method-03) independently rediscovered, in the black-hole domain, the same meta-node/reliability gap we hit with eggs (Entry 12 F5-residual)**: a node commenting on *another node's evidentiary status* is structurally indistinguishable from a first-order ground. **f7 (synth-04) named it cleanly:** nodes have a KIND (claim/external_anchor) but no **grain/level marker** separating object-level claims from meta-claims-about-a-node. Proposed primitive: a meta-claim kind or a `points-at` field. Recurred across **two unrelated domains + two independent agents** ⇒ promote from "watch" to "the real candidate." Still **additive** (a kind/field), not a change to support-only.

**Limitations named (🟡):** sequential not concurrent (no file-locking yet — the prerequisite for a true parallel swarm, and it under-reviews late edges); small (4 agents), single domain, one hand-authored pack; tested **collaborative convergence**, NOT **independent reproducibility** (do two agents *separately* produce *similar* graphs? — the other half of Prototype 2, and the next test).

**Standing practice reaffirmed (🟢):** the swarm graph is its own artifact; the viewer now also has a **deterministic force-directed neighborhood layout** (organic clustering, replacing columns) + the edge-clipping fix; both eggs artifacts redeployed in place to the new layout.

---

## 16 · Reproducibility test — two independent swarms, same question (verdict: MODERATE)

*2026-07-02. Ran a SECOND independent swarm on the same LHC black-hole question (new persona set: communicator / precaution-advocate / peer-reviewer / editor), blind to run 1, same source pack + briefing. An independent skeptical **judge agent** aligned the two graphs critically. Committed at `v0/swarm-blackholes-2/` + `COMPARISON-run1-vs-run2.md`; artifact "blackholes-swarm-run2". Sizes near-identical (run1 23n/25e/4sets; run2 24n/30e/5sets).*

**Verdict: MODERATE reproducibility — and the honest breakdown is the valuable part** (corrects an over-enthusiastic preliminary read):
- **Content layer reproduced strongly** (same 2 positions, 4 chains, 3 empirical cruxes, value→ought) — BUT the shared **briefing scaffolds this**, so mere presence is weak evidence of format-reproducibility.
- **Beyond the briefing (real signal, 🟢):** two non-trivial *architecture* choices converged independently — both runs' friction logs discovered the **white-dwarf backstop *rebuts* the capture objection** (not parallel support) (run1 f1 ≡ run2 f1), and both **paired the two *oughts*** (not the value premises) in the normative antithesis. Modeling decisions, not boilerplate.
- **Diagnostic-layer DIVERGENCES (🟡):** crux *partitioning* differed (run1 one 3-way set vs run2 two 2-way sets for the capture/white-dwarf cluster); the **LSAG authority node was wired in OPPOSITE directions** (upstream anchor vs downstream aggregator — same citation, inverted edges); shared premise implicit vs explicit fork; weakest-link local-pattern vs promoted meta-argument.

**KEY INSIGHT (🟢, ties the whole thread together):** **the reproducibility divergences cluster exactly at the grammar's known frictions.** Authority-direction divergence *is* the meta-level/restatement friction (f2); crux-partitioning divergence *is* the antithesis-grain friction (f4/f6). ⇒ **reproducibility gaps = underspecified encoding choices = the open frictions.** Resolving them tightens BOTH expressiveness and reproducibility:
- the **meta-claim / `points-at` marker** (Entry 15's recurring primitive) would pin the authority-node direction;
- a **crux-grain / rivalry-kind convention** (run2 f6) would pin the partitioning.

**⇒ The meta-level marker is now supported by TWO independent lines of evidence:** cross-domain friction convergence (Entry 15) AND cross-run reproducibility divergence (this test). Strong, non-obvious case for it as the one real additive primitive.

**Interoperability consequence (FLF criterion 3, 🟡):** two graphs wiring the same authority citation in opposite directions would **conflict on merge** — so content-reproducibility is NOT sufficient for independent contributions to *compound*; authors need shared conventions or grammar primitives at exactly these underspecified spots. Concrete statement of what the format still needs before distributed outputs interoperate.

**Operational finding (🟡):** in both runs an agent occasionally **forgot `--data`** and wrote a stray node into the default `./data` graph (harmless, gitignored; the CLI correctly blocked a destructive self-revert). A real swarm harness should make the target graph unambiguous (require `--data`, or no default) — a robustness fix for the parallel-swarm buildout.

**Limits (🟡):** two runs, one domain, sequential, shared briefing (a stronger test thins the briefing to see if the *arguments* still reproduce); single judge (a panel would be more robust).

---

## 17 · The meta-claim question, resolved — three cases, and a correction to Entries 15–16

*2026-07-04 discussion. Walked the three motivating cases for a "meta-claim / `points-at` primitive." Outcome: **the primitive is substantially dissolved** — most of what motivated it was bounded-test artifact or already-handled by existing mechanics.*

**⚠️ Correction to Entries 15–16 (🟢):** the meta-claim marker was billed as "the one real additive primitive" with "two independent lines of evidence" (eggs F5 friction; black-hole reproducibility divergence). Both are now understood as **bounded-test artifacts**, not grammar gaps: eggs-F5 = *under-decomposition* (Case 1); the LSAG reproducibility flip = *forced-review-usage* (Case 2). With full decomposition + real primary sources, neither friction is generated. The old conclusion is downgraded accordingly.

**Case 1 — source reliability / retraction (🟢 resolved, no primitive).** A study is itself a bundle of claims; decompose it into the graph (study anchor → methods [wormholed to trunk methodology nodes] → findings, each assessed separately). "They fabricated the data" is then a claim *about the world* (an event), mapped as a **rival path** in the study's own subgraph, in antithesis with "data collected as described" — support-only + emergent split/merge doing undercutting work with no new primitive. What looked meta was under-decomposition. **Comments incubate, the graph adjudicates:** reliability concerns surface in a node's comment forum (see below), but any claim that *bears weight* must **graduate** into the graph (comments don't propagate through chain-strength, can't be antithesis-linked, don't render — the Reddit failure mode where the correction is always in the comments nobody reads). Reassessment machinery (staleness/"needs-assessment" markers; propagate downstream + across a study's node-set on new info) lands in the assessment layer (kin to churn/settledness + chain-strength).

**Case 2 — restatements & review articles (🟢 resolved, they don't belong in the graph).** Restatements merge as **phrasings** of the existing node (only when propositional content is *truly identical* — differing scope/caveats = a distinct node, else we over-merge). Reviews are **not primary evidence** — reach *through* them to the primary sources and graph those; the review adds nothing the primaries don't, except original arguments/connections (which map as ordinary nodes) or a **meta-analytic pooled estimate** (a genuinely new quantity → an original finding-node grounded by the primaries). **Bigger insight (headline for FLF writeup):** *the graph subsumes the function of review articles* — a review is a static one-author attempt at exactly what a living structured graph does continuously and better. Direct answer to FLF's compounding/shareability criterion. This also **dissolves the Entry 16 LSAG divergence**: in the full system neither swarm would place the review as an evidence node at all.

**Case 3 — inference quality (🟢 mostly resolved; narrow residual → merges into F8).** **The edge *is* the inference; Agreement on the edge *is* the collective assessment of its strength;** a weak inference renders as a visibly tenuous link and propagates via chain-strength. Add **edge-level comment forums** (mirroring node forums) as the home for discussing *what* an inference is and how strong — a clean additive affordance. Substantive defeaters ("Z confounds X→Y") are **rival positive claims**, not edge-comments (support-only, per the eggs buildout). **Feature to bank:** a *weakest-link highlighter* over a chain (uses the chain-strength metric). **The one surviving sliver:** a **reusable methodological principle** ("observational data can't establish causation") is handled poorly by per-edge comments — it loses *compounding* (re-referenced per edge instead of one node structurally bearing on many inferences) and violates the Case-1 graduation principle. This is **exactly F8** (the trunk/shared-node case — our black-hole methodologist independently said it "wants to be a single shared node linked from many inference points"). ⇒ the meta-claim question **collapses into F8**, narrowed to: *can a node point at an edge (not just a node)?* — a surgical "node targets an edge," rendered as a wormhole/trunk link. **Not building it now** (edge-forums + edge-Agreement suffice for v0/FLF; the cost is a compounding nice-to-have, not a correctness failure); kept on the books as the one surviving primitive candidate, merged with F8.

**Two FLF-named cases that dissolve cleanly (🟢, good coverage signal):**
- **"Rhetoric, not evidence"** → a low-**Reasonableness** node; the two-axis design (Entries 3/6) already separates persuasive-weight from evidential-weight. No new machinery.
- **"Correlated evidence treated as independent"** → under full decomposition, the two sources **share an upstream ancestor**, making double-counting *structurally visible* (two paths converging on one node). ⇒ concrete **chain-strength rule to bank: don't double-count shared ancestors** when propagating strength. FLF calls this out by name; it becomes a graph-topology fact, not an assertion.

*(An anti-brigading jury-trigger note from this discussion has been sequestered to the `adversarial-defense-archive` branch — out of brief for the FLF submission.)*

**New affordances this settles (all 🟢, additive, none touch core grammar):** node comment forums · **edge comment forums** · staleness/needs-assessment markers + reassessment propagation · weakest-link highlighter · (chain-strength) don't-double-count-shared-ancestors · random-jury-on-setpoint-drift.

**Addendum (2026-07-04): the F8-residual closed — edge→trunk inference-typing (🟢).** Resolution of "can a claim bear on an edge": invert the primitive — not *node points at edge* (drawn; lines-to-lines clutter), but **the edge references the node**. Inference-principles ("observation ≠ causation") live as **trunk nodes** (low in the graph, with foundational epistemology). Each edge's comment forum discusses/votes *what inference this edge is making* — candidate typings compete via the standard Agreement pattern (same mechanics as titles/phrasings) — and the winning type is surfaced at the top of the forum **with a wormhole link to the trunk node**, and rendered as an **edge label at node-view** (label = link; node-view only, neighborhood stays clean). Key properties: (1) the voted typing is **machine-readable structural data even though never drawn** — queryable ("all correlation→causation edges"), and trunk-node standing changes flag referencing edges via the Case-1 reassessment machinery → compounding preserved, clutter avoided; (2) **typing disputes are epistemically load-bearing** (deductive-vs-suggestive is often the real crux), hence the competitive pattern; (3) **no auto-coupling** of edge strength to the trunk node's standing (formal-logic creep; Entry 13) — the label *informs* raters, the edge's own Agreement remains the strength; soft version OK: an assessment-layer *diagnostic* flagging type/agreement inconsistency ("typed as weak inference-kind, yet strength 5") — a scrutiny flag, never an automatic discount.

**Line length as strength cue (🟢 status note):** already in the model since v0 — node-view radii, antithesis-arc radii, and neighborhood spring rest lengths all use `distFor = min + range/strength` ("closer/thicker = stronger" in the legend). Caveats: crisp in node-view (deterministic), approximate in neighborhood (forces compromise); the 2026-07-04 flow-direction fix raised the neighborhood minimum rest length (80→175px), narrowing the visible contrast to ~1.8:1. Louder length-contrast = a two-line tune (widen range; trade-off: more spread-out map); deferred — expressive length is one of the things the full 3D physics model does properly.

---

## 18 · Assessment layer, part 1 — the three axes and the rating scale

*2026-07-04 discussion (assessment-layer design, all post-v0 / Prototype-3 territory).*

**The axes (🟢).** Two "how well is this *said*" axes + one "do I *endorse* this" axis, placed by what each is a property *of*:
- **Reasonableness** ("fair-minded & well-argued" vs. weaselly/biased) and **Clarity** ("easily understood") are properties of an **expression** → they attach to **phrasings**, and are how the phrasing z-stack is sorted/surfaced. Surfacing weights **Reasonableness slightly over Clarity** (prefer a slightly-less-clear but eminently-reasonable phrasing over a crystal-clear but only-moderately-reasonable one) — a tunable default for the mechanics playground.
- **Agreement** ("do I endorse this claim/action/stance") is a property of the **proposition** → it attaches to the **node** (you endorse the claim, not the wording).
- **Consequence to spec explicitly (else a builder "fixes" it):** the node has **no R&C of its own — it inherits them from its current top phrasing**, and they can therefore *change without anyone rating the node* when a better phrasing wins. This temporal coupling is intended (it's what lets a profound-but-clumsily-worded claim survive), and it's what underpins the node's visual cues + chain-strength factor.
- **Forums (node & edge):** comments are rated on **R & C** and ranked best→worst at each threading level. **Edges carry only Agreement** (inference-strength) — influenced by, but not a direct readout of, the R&C-mediated discussion in the edge's forum.

**Rating scale (🟢).** Scales are arithmetically arbitrary; the choice is **human psychology** (AI raters treat any scale coherently; humans don't). Design: presented as a clean **5-point** scale but actually **0–5** (humans resent not being able to give a real 0, even when it's functionally a floor) with **tenths** (→ effectively 50 points; the extra precision carries real shades of meaning) — a slider that **soft-snaps to whole numbers** but allows e.g. 4.1. **Add an explicit "no opinion / abstain" that is NOT 0** (0 = "maximally unreasonable"; conflating "I judge this terrible" with "I can't judge this" would poison the aggregate; abstain is also how a rater declines an assigned item they're not fit for — see Entry 19). Scale + aggregation stay **pluggable** in the playground (Entry 3 requirement).

---

## 19 · Assessment layer, part 2 — assigned rating (sortition sampling & independence) [🔵 pillar, still open]

*2026-07-04. How the crowd gets matched to questions, and how independence is protected at the moment of judgment. Freeze the PRINCIPLE now; leave the exact sampling/competence math as a playground knob.*

**Assigned rating = sortition sampling (🟡 adopt as a pillar; details open).** Rating is a **sortition**, not a broadcast: you enter Rating mode and are handed semi-random items rather than choosing what to rate. This is how the crowd is **sampled to the questions that need coverage** — representative assignment instead of whoever-happens-to-show-up — and it **unifies with the Entry-17 random-jury**: assigned-rating is that same sampler running *continuously as the default* ("the crowd is sampled to the question, never the question chosen by the crowd").
- **Reading mode vs Rating mode (🟢 correct seam):** Reading mode shows *everything* (colors/brightness/edge-thickness/ratings — that crystallized consensus IS the product, and a reader casting no vote can't be anchored). Rating mode **hides all cues until you exit** — independence needs protecting *only at the moment of judgment* (Entry 3 Condorcet: seeing the aggregate before voting collapses independence). Precisely scoped.
- **Competence must be EARNED, not self-declared (🟢).** You get *more* of what you've **demonstrably rated accurately** (judged vs. random-jury / eventual-consensus), always diluted with genuinely random assignments so a rater never funnels into a single narrow niche and cross-field coverage stays broad.

*(This entry's original threat-model framing, the Sybil-defense candidate-mitigations section, and the "can a coordinated minority move a score" playground mandate have been sequestered to the `adversarial-defense-archive` branch — out of brief for the FLF submission. What remains is the cooperative sampling mechanism: sortition for coverage, the Reading/Rating independence seam, and earned competence.)*

---

## 20 · Assessment layer, part 3 — reassessment waves, and the open-source transparency stance

*2026-07-04 discussion (post-v0).*

**Reassessment is how the graph stays current (🟢).** The graph MUST respond to new real-world info, and the channel for that is users adding comments/nodes/connections that trigger a **local reassessment wave** — neighbors re-rated in light of the new item. This is core site function: a living graph updates continuously rather than freezing at its first consensus, and a new item's downstream effect flows through the same assessment machinery as everything else (a weak new item, being weakly assessed, moves strong conclusions little).

**Open-source transparency stance (🟢).** Publish the **rules**: the assignment/sampling algorithm and the scoring/weighting formulas are public. Rationale: a transparent-reasoning site should run on transparent mechanisms — a design that needs its formula hidden is already suspect, many-eyes audit is a feature, and methodological transparency is an FLF criterion. The only things legitimately kept out of view are the per-round random assignment **seeds** (who-rates-what this round) and live user state; publishing the *formula* costs nothing, publishing a specific round's *entropy* would (Kerckhoffs: secure the key, not the algorithm).

*(This entry's original attack-surface framing of the reassessment wave, and a cross-cutting manipulation-fingerprint diagnostic, have been sequestered to the `adversarial-defense-archive` branch — out of brief for the FLF submission.)*

---

## 21 · Assessment layer, part 4 — color mapping, rater instructions, reputation bootstrap, rollout

*2026-07-04 discussion (post-v0).*

**Color mapping (🟢).** **Hue/saturation = Agreement** (white-gold high-A → gray low-A); **lightness = combined R&C** ("quality glows"), reserved *size* = activity/churn later. **Critical spec instruction — the two channels must be perceptually INDEPENDENT:** brightness must stay legible across the whole agreement range including the desaturated low-A end, so a *low-agreement-but-excellent* node **glows gray** and a *low-agreement-poor* node sits **dim gray** — visually distinct. Guard against the naive failure where low saturation also crushes lightness. Ship gates: colorblind pass (the gold→gray axis is largely lightness/saturation not red-green — a nice safety property of the choice) **+ a 2×2 swatch test** ({high/low A} × {high/low R&C} → four distinct chips). Post-v0 → assessment-layer spec, not current viewer.

**Rater instructions (🟢).** Human on-ramp: intro to structure/affordances/philosophy at signup + **per-slider hover text** stating what each axis measures ("Is this clearly stated?" over Clarity). (Known) AI: a **guidance block** to add to prompts (good-faith agents use it; also a norm signal). Both must **actively fight the saturation instinct** (the lesson paid for twice): *"the midpoint is the honest default; the extremes are earned; abstain freely when unfit to judge."* Division of labor: instructions make honest raters *coherent*; the assigned-rating + reputation machinery makes dishonest ones *ineffective*.

**Reputation bootstrap (🟢).** (Reputation model amended in Entry 3: one Reasonableness score, two inputs.)
- **Weights are RELATIVE → the bootstrap problem dissolves.** Everyone starts equal → the weighting system runs from day one and just yields equal weights, **phasing into** differentiation automatically as evidence accrues. Same code path throughout (no "flat mode → weighted mode" switch), noisier early. Handles both site-launch AND each new user identically.
- **`Raw × Confidence = True R`** (a known-good pattern: Bayesian rating shrinkage / IMDb weighted rating / Wilson score — little evidence pulls toward the prior; confidence grows with # of independent assessments).
- **Start score: LOW, and via low Confidence not asserted-low quality (🟢).** Cleaner semantics: a newcomer isn't *known bad*, it's *unknown* → neutral Raw R but **Confidence ≈ 0 → low True R**; a genuinely good newcomer then climbs *fast* as their assessments accrue. Reputation is *earned*, not granted — so influence tracks demonstrated contribution rather than mere presence. Floor + climb-rate are **playground knobs** (onboarding friction vs. how fast trust should accrue — empirical).
- **Staged rollout (🟢):** ~100 (1–2 wks) → 1k (1 mo) → 10k (3 mo) → open, with planned whole-site rebuilds; adapts to what breaks. Framing: **the human-facing analog of the bot mechanics-playground** — tune the mechanisms on real users the way the playground tunes them on bots; each expansion is a checkpoint to fold in fixes.

---

## 22 · Next prototype — assessment build + cooperative test

*2026-07-04. Decision on Prototype 3 sequencing.*

**Build:** the next version adds the assessment/commentary/reputation machinery (Entries 18–21) as a **playground** — every scale, aggregation rule, weighting formula, and assignment/sampling rule **toggleable/tunable** (the standing Entry-3 requirement), on top of the now-built forums + locking + `--data` hardening.

**Test cooperatively first (🟢).** Run **cooperative agents (friendly, non-hostile)** to establish the friendly baseline and shake out kinks — you can't measure anything about the mechanisms until you know baseline behavior; hostile-from-day-one would reproduce the original "agent-confusion vs. mechanism-bug" confound (cf. the first hand-seed). Isolate the variable.

*(An adversarial second phase — bot populations with injected biases, testing the mechanisms under coordinated pressure — was also planned here; that work is sequestered to the `adversarial-defense-archive` branch, out of brief for the FLF submission.)*

---

## 23 · First cooperative assessment run — 5 simultaneous raters (phase-1 baseline)

*2026-07-04. Five Sonnet agents (nutrition-skeptic / methods-pedant / plain-language-editor / evidence-hunter / synthesizer) rated + extended the eggs graph (`v0/eggs-coop`, seeded from eggs-full) SIMULTANEOUSLY, ~3 passes each, honest-sparsity discipline (midpoint default, extremes earned, abstain freely, no filler, structural budget caps). First real workout of the file-locking AND the assessment layer on a population. Committed `eggs-coop/` + artifact "coop-assessment".*

**Growth (cooperative, non-adversarial):** 27→34 nodes · 25→32 edges · 3→5 antithesis sets · 9→17 frictions · 109 rate + 27 agree + 15 comment + 5 typing + 3 phrasing events. Genuinely richer: the two top-level rivalries and the causal-vs-confounded fork are now two-sided with real evidence each; a previously rival-less terminal ought (n015) gained a rival (new set s5).

**Concurrency held (🟢).** File-lock survived 5 simultaneous writers: no lost/corrupt events, deterministic rebuild intact. Agents hit real same-tick id collisions (create-node landing at n+1 because a peer just took n) and handled them by re-`search`/`stats` before writes. One low-cost artifact: two agents posted near-duplicate comments ~1 event apart (couldn't see each other drafting) → argues for an eventual lightweight "someone's editing here" signal. Agents also *self-deconflicted* (one redirected its friction on seeing a peer file the same one first).

**Rating honesty — NOT saturated (🟢), with one weak axis (🟡).** The baseline this run existed to establish:
- node/phrasing **Agreement**: n=26, range 1.8–4.5, mean 3.77, **stdev 0.78** — real spread.
- phrasing **Reasonableness**: n=13, 2.0–4.5, mean 4.06, stdev 0.78 — real spread.
- **edge Agreement**: n=25, 1.5–4.5, mean **2.90**, **stdev 1.13** — widest spread, most discriminating (appeal-to-authority edges → 1.5; Mendelian-randomization/RCT grounds → 4.5). Raters applied their sharpest judgment to *inferences*.
- phrasing **Clarity**: n=10, 4.0–4.5, mean 4.35, **stdev 0.23** — COMPRESSED HIGH. The one weak-discrimination axis: either these phrasings were uniformly clear, or Clarity is a low-signal axis raters default-high on. Watch in phase 2.

**Convergence = the healthy headline (🟢).** Independent agents repeatedly landed near-identical ratings on the same nodes/edges (the ecological-evidence edge rated ~1.5–2.0 by three agents unprompted), converged on the same phrasing rewrites, and filed the same frictions — and the layer behaved *dynamically*: an agent **re-rated a node down (4.0→3.5) after a peer's comment changed its judgment** (incubate-then-adjudicate, live). The layer captures *reproducible* judgment, not noise — the single most important thing to confirm before trusting any of it.

**Reputation, first real population (🟢).** True_R differentiated meaningfully: the 5 careful cooperative raters clustered **0.72–0.76**; **agent-a** (an original eggs-full author) sits **0.73 on authoring alone** (61 well-rated items, rated nothing this round) — reputation-from-authoring works; **agent-b** (authored 1 poorly-rated item) sank to **0.33**. The mechanism tracks contribution quality; the earned-reputation floor holds.

**The headline FRICTION — 3-way independent convergence (🟡 → the real refinement):** edge/inference Agreement is a **single scalar carrying multiple dimensions**, filed independently by three agents from three lanes: f12 (*premise reliable* vs *inference valid*), f14 (source *fidelity* vs *reliability*), f15 (*weak ground* vs *dependent overclaims beyond its grounds*). ⇒ **edge Agreement wants ≥2 dimensions** (an inference has several independent failure modes). Strongest, most actionable assessment-layer finding.

**Other assessment-machinery frictions (🟡, all additive — none touch core grammar):**
- **f17** — no **dispersion or coverage** measure: "3 raters converging on 2.5" looks identical to "3 raters split 0/2.5/5"; "well-mapped-but-contested" looks like "unmapped-unknown." Add **stdev + rater-count/density** to the snapshot (already computed in analysis — cheap).
- **f16** — **conjunction-edge** Agreement has no defined semantics (a joint ground isn't meant to support alone; agent correctly abstained).
- **f11** — **titles have no R/C** rating dimension (framing-mismatch judgments got dumped into free-text comments).
- **f13** — R doesn't cleanly catch **scope/magnitude drift** in a "same-claim" reword (Entry-11 phrasing-vs-new-node boundary, resurfacing in the assessment layer).
- **f10** — **source-coverage gap**: a pack source studied an outcome (stroke) its summary omits; silently dropped, uncaught by any health signal.

**Verdict (🟢):** phase-1 cooperative baseline achieved — the assessment layer works, produces reproducible signal, differentiates reputation, and stays honest under 5 concurrent raters. The refinement punch-list (edge-A → multi-dim; add dispersion + coverage; conjunction-edge semantics; title R/C) is the next work, and all of it is additive.

---

## 24 · Weak-argument probe + nonlinear color ramps — the quality channel, stress-tested

*2026-07-07. Two paired changes closing the one open question from the coverage run: does the quality (body-color) channel actually differentiate good arguments from bad, and can a human eye read the differences that matter?*

**The gap (from Entry 23's coverage pass).** Cooperative authoring produced no genuinely bad arguments, so the R&C/quality channel's *range* was untested — all real nodes clustered 3.9–4.5. "Differentiation works" was proven for Agreement (frame) but only *asserted* for quality (body): we'd never shown a bad argument reads as bad, because we never had one.

**The probe (🟢 — quality channel confirmed).** Injected 3 deliberately fallacious claims into `eggs-coop`, each a distinct failure mode, wired as real grounds so raters met them naturally: **n035** appeal-to-nature ("eggs are natural + ancient, so must be good"), **n036** unfalsifiable hand-wave ("all the real science says fine, everyone knows"), **n037** overreaching causal leap ("cholesterol is bad + eggs have it → any eggs directly cause heart attacks"). Three independent rater personas (careful / skeptical-methodologist / generous-but-honest) rated them **blind** — not told which were injected — mixed with six strong anchors for calibration. Result, sharp and convergent:
- Weak claims: quality-mean **1.4–2.0** (n036 the worst at 1.42, the two fallacies at 2.0). Anchors: **3.9–4.54**. Clean, non-overlapping separation.
- All three raters independently identified n035/n036/n037 as the outliers and named the specific fallacy each time — the R axis catches *bad reasoning*, not just false conclusions (n036's conclusion is roughly true; its R still tanked because the *argument* is bad; n037 tanked on both).
- The C axis behaved orthogonally: n035/n037 are grammatically clear (C 3.0) though badly reasoned, while n036's vague wording pulled C to 1.5 — R and C measured different things, as designed. This also un-flattens the Entry-23 Clarity worry further: Clarity *does* discriminate when phrasings actually vary in clarity; round-1's compression was small-sample.

⇒ **The flat quality spread in Entry 23 was a content artifact, not a mechanism failure.** Given bad material, the quality channel separates it cleanly — so the body channel can be trusted wherever genuinely weak claims appear.

**Nonlinear color ramps (🟢 — legibility).** Jeff's read: the linear score→color ramp made a near-uniform gradient across the neighborhood, because a healthy graph lives in the 3.5–5.0 band and a linear ramp spent most of its visual range on scores that never occur — so a 3.9 and a 4.2 (a distinction he cares about) were near-identical shades, while the 0–3.5 range (which he only needs to read as "bad") hogged the palette. Fix: both ramps (frame/Agreement and body/quality) now put scores ≤3.5 in the bottom quarter of the color range (`EMPHASIS_KNEE_SCORE=3.5`, `EMPHASIS_KNEE_T=0.25`) and spread 3.5–5.0 across the top three-quarters. Net effect on this graph: anchors now spread across body-positions 0.46–0.77 (was ~0.13 of range, all crammed at the top) while the weak claims drop to 0.10–0.14 (near-black). The color key gained a 5-chip ramp strip so the knee is inspectable. The two goals — "good scores distinguishable from each other" and "bad reads uniformly bad" — are both served by the same nonlinearity. Cheap to retune (two constants) if phase-2 wants the knee elsewhere.

**Verdict (🟢):** the last untested claim from the phase-1 baseline is closed — quality differentiation is real, and the viewer now renders the band that matters at a resolution a human eye can use. Both changes committed; probe data in `eggs-coop`, ramp in `viewer.html`.

---

## 25 · Phase-2 design settled — sortition sizes, churn, the contrarian, assignment, redemption, chain strength

*(An adversarial-defense sub-thread from this exchange — the "peek-then-rate" alignment-farming discussion and manipulation-detector items — has been sequestered to the `adversarial-defense-archive` branch, out of brief for the FLF submission. The cooperative design below stays.)*

*2026-07-07. Jeff's written phase-2 thoughts arrived; a long design exchange resolved nearly all of the open phase-2 questions. The through-line repeated Entry 13's lesson one layer up: five of six questions resolved to EXISTING machinery pointed correctly, not new machinery. Three genuinely new dials surfaced (flagged 🔵 below).*

**Sortition & blocs — bloc = replicate (🟢).** Jeff's decomposition: the assignment cohort is composed of several voting blocs; blocs small enough to carry idiosyncratic bias, cohort large enough to estimate the true aggregate. Statistical name: the bloc is a *replicate* — k independent estimates of the same quantity, whose agreement shows the measurement is real and whose divergence signals genuine disagreement (split-sample reliability). Sizes: **bloc m=5** (small enough to be numerous; jury-theorem operating range), **k=3 minimum / 5 comfortable** (3+ identifies the outlier bloc), so cohorts ≈15–35. But cohort size should be *derived from measured per-item inter-rater σ* (which f17's dispersion tracking will supply — the coop-run stdevs were cross-item, a different quantity) and sampled **adaptively/sequentially** (group-sequential trials): one bloc → provisional score; more blocs accrue with importance/traffic/dispersion until the CI is tight. Dissolves the scale worry (a small site just leaves more nodes provisional) and gives "contested" a proper meaning: **if added blocs don't shrink the interval, the disagreement is real → display as CONTESTED, a terminal state distinct from mid-scored.** Settled / insufficiently-sampled / contested: one mechanism, three outcomes.

**Churn/settledness = heat diffusion on the graph (🟢).** Jeff's spec (self-activity weighted most, decaying outward, time-windowed, site-relative) is literally the heat equation: every event injects heat at its node; heat decays exponentially (half-life) and partially diffuses to neighbors. Temperature IS churn — distance decay and recency emerge from one mechanism instead of three tuned weights. Computable deterministically in the fold (event `ts` is in the log); site-relative normalization = divide by median node temperature (handles 100-user vs 10k-user scaling automatically). Two refinements: (1) **split content-heat from score-drift** — a score moving while content heat is HIGH is a live debate; a score moving while content heat is LOW (no new arguments/evidence/rewrites to explain it) is an unexplained shift worth a second look. (2) **Cold ≠ settled**: settled = cold AND coverage past quorum; cold-and-uncovered is just ignored. Different states, different display.

**The correct-early contrarian — resolved, no new machinery (🟢).** Jeff talked himself out of a vindication bounty, correctly, and the reason it's NECESSARILY right: **the site has no outcome oracle.** Prediction markets can pay for being-right-early because reality grades the bet; here the only available grader is the site's own future consensus, and "reward whoever agreed with the future majority" is conformity enforcement with a time delay — it trains users to forecast the crowd, not the truth. An intuition with no expressible grounds is ex ante indistinguishable from noise; rewarding the lucky ones selects for overconfidence (survivorship). The contrarian who had *something* puts it in the graph — the right questions, rival claims, structure that becomes load-bearing when evidence arrives — and is paid through ordinary authoring reputation when their nodes get re-rated up. The contrarian with nothing gets nothing. 🔵 **Open dial surfaced: the alignment-scoring dial.** Is rating-alignment scored against consensus *frozen at rating time* (stable, but permanently punishes the vindicated) or the *living aggregate* recomputed at fold time (retroactive vindication through existing machinery)? Lean: **living aggregate, per-node reputation-impact cap, alignment finalizes when the node settles.** Decide at phase-2 spec freeze.

**Unit of assignment = contextual bandit (🟢).** Rating mode serves one item at a time; new raters get a wide cross-field sample (exploration), then more of what they're good at but never exclusively — ε-greedy with **ε floored ≈0.2 forever** (the floor is also the anti-self-funneling defense). Competence is field-sized, not neighborhood-sized ("good at biology," not "good at egg-cholesterol claims"); until named fields exist, graph **community detection** (Louvain-style) supplies latent regions to compute per-field competence against — fields are discovered, not declared, consistent with the grammar philosophy. **Skip-fishing closed:** a skipped item NEVER returns to that rater (Jeff's strengthening: not even with low probability, lest skip-and-note becomes reconnaissance for a later pass). Fishing then costs your only chance at the target; skip-rate itself becomes a monitorable signal.

**Coverage vs randomness; incompetent raters — the continuous version already exists (🟢).** Items are flagged needing-ratings until statistically sufficient, cohorts **stratified** (established + field-competent + newcomers) then randomly partitioned into blocs. For low-reputation raters: no shadowban, no threshold cliff — True_R-weighted aggregation already makes a floor-reputation rater's influence ~zero *continuously and publicly* (anyone can compute their own weight from the published algorithm), while their ratings still feed their own alignment input, so the path to earning trust back is always live. The published weight curve IS the moderation.

**Chain strength (🟢, v1 spec).** Upstream-only ("is the argument leading here good?"), per-path. Normalize A to [0,1] (A/5), take the **product over nodes and edges along the path** — the length penalty is *emergent* (each inference is one more place to be wrong; a chain of 4.5/5 steps decays ×0.81/hop), so no arbitrary 0.9 attenuation constant unless real chains prove over/under-punished. Report **two numbers**: the chain product (confidence transported end-to-end) and the **weakest link** (min factor, with a pointer — the actionable one, and the substrate for the deferred weakest-link highlighter), plus per-step geometric mean so long careful chains aren't shamed against lazy short ones. Conjunctions = one link carried by ALL members (forces the f16 semantics question, usefully). Multi-path aggregation deferred with named prior art: noisy-OR, 1−∏(1−sᵢ), broken by shared ancestors (double-counting) — the known-hard part. UI as Jeff sketched: branched-graph button in Detail view → steps-back / to-node / two-nodes-to-last-common-ancestor (that last one a genuinely novel affordance for antithesis pairs). Note: the metric consumes specifically the *inference-validity* dimension of edge A — the third thing pressing on the f12/f14/f15 split, which should be settled FIRST at phase-2 spec freeze.

**Quorum sealing + uncertainty-weighted credit (🟢, the cooperative core).** Two ideas from that sub-thread are cooperative site function and stay: (1) **Seal until quorum** — below coverage quorum an item shows no public number, just "n ratings, pending quorum"; the aggregate publishes once enough independent ratings exist. Release is *sequenced*, not hidden (same spirit as public-rules). (2) **Uncertainty-weighted alignment credit** (proper-scoring-rules): rating credit scales with how uncertain the item was when rated — parroting a tight settled score earns ~nothing, honest judgment on a wide-open provisional item earns most, which pays raters most for exactly what the site most needs. The ideal user studies the *arguments* in Reading mode and rates accordingly; that is the point of the graph.

**Verdict (🟢):** phase-2's design questions are substantially settled, almost entirely by existing machinery pointed correctly — replicates instead of new jury rules, heat diffusion instead of tuned weights, weighted aggregation instead of shadowbans, ordinary authoring reputation instead of contrarian bounties, emergent decay instead of an attenuation constant, sequenced release instead of secrecy. Remaining before spec freeze: 🔵 the edge-A multi-dimension split (now pressed by three independent needs), 🔵 the alignment-scoring dial (lean recorded above); then the build list: quorum/sealing, heat metric, chain-strength verb + viewer affordance.

---

## 26 · Edge Agreement resolved — conditional semantics, one scalar after all

*2026-07-07. Jeff's proposal: the edge is ONLY the inference. It never expresses whether the premise is good or bad — that lives on the premise node's own ratings; the edge assumes "if that were so, then this would be a reasonable inference from it." Verdict: correct, and it resolves the coverage run's strongest friction (the 3-way f12/f14/f15 convergence) WITHOUT splitting the scalar. The multi-dimensionality raters (and Fable, in Entry 23's "edge A wants ≥2 dimensions") felt was premise-truth leaking into the edge; conditionalizing routes each dimension to its home.*

**How each friction lands:**
- **f12** (premise reliable vs inference valid): premise reliability = the Ground node's A; the edge rates only the conditional step.
- **f15** (weak ground vs dependent overclaims): overclaiming IS an inference failure — the Dependent as phrased exceeds what the granted Ground licenses → low edge A. Weak ground + well-fitted Dependent → low node A, high edge A. The two indistinguishable cases now land in different places.
- **f14** (source fidelity vs reliability): an external anchor asserts "the source says/found X" → node A = *fidelity* (does it really say that?). The source's *reliability* (methodology, power, bias) lives in the EDGE, because the step from "the study found X" to "X is so" is exactly where study quality does its work. The subtlest and most teachable piece.
- **f16** (conjunction edges) falls out free: under conditional semantics a joint Ground's member edge has no independent inference to rate — the rateable unit is the GROUP ("if ALL members were so…"). Member-edge abstention (what the coverage agents already did unprompted) is now the documented norm; a `group:<gid>` rating target is the small build item.

**Two nuances the guidance must carry** (now written into AGENT-GUIDE §9 + ASSESSMENT-SPEC v1.2 + viewer hover text): (1) **degree of support, not entailment** — 5 ≈ granting the Ground would compel the Dependent, 3 ≈ real but partial support (one reason among several needed), 1 ≈ even granted, barely bears on it; partial support is healthy (it's why conjunctions and multiple Grounds exist) and must not be punished into the middle. (2) The anchor-node fidelity/edge reliability split above.

**The bonus:** with node A ≈ "how likely true" and edge A ≈ "how strongly this, if so, supports that," Entry 25's chain-strength product stops being a heuristic and becomes the chain rule — P(premise) × P(step|premise) × … — under the usual independence idealizations. The conditional semantics and the chain metric were secretly the same idea. Prior art: Toulmin — node = grounds, edge = warrant.

**Verdict (🟢):** the first of Entry 25's three spec-freeze dials is closed, by definition rather than by mechanism — no code change, the machinery was always fine; the MEANING of the number was underspecified. Docs + hover text updated. Remaining dials: the alignment-scoring dial, anchor-experiment criteria.

---

## 27 · The alignment-scoring dial closed — eras don't leak; the site rewards reasonableness, not clairvoyance

*2026-07-07. Second of the three spec-freeze dials. Fable proposed an era/re-affirmation design (grade each rating against its era's settlement; on re-opening, holders may re-affirm standing ratings into the new era and collect new-era credit — "forward-facing vindication"). Jeff pushed back on two counts and was right on both; the pushback also produced the final, sharper statement of the contrarian resolution.*

**The error in re-affirmation, named:** it smuggled the outcome-oracle back in through the side door. Entry 25 established that rewarding agreement-with-future-consensus is conformity enforcement with a time delay (the site has no oracle; future consensus isn't ground truth) — and re-affirmation grades a held rating against the NEXT era's settlement, i.e. pays exactly that bounty, with a one-click turnstile attached. Jeff's two symptoms trace to that root: (a) lucky guessers and right-for-the-wrong-reasons contrarians happily click re-affirm and collect; (b) a stale early-era rating becomes a standing fixture re-entering every future era at a click's cost — old positioning converted into future influence, cutting against the principle that "the crowd is sampled to the question": era 2's cohort should be a fresh sample, not whoever showed up in era 1.

**The design (FROZEN for phase-2 spec):** a rating is graded against the settlement of the era it was cast in, and **eras don't leak**. Alignment is *living while the era is open* (first-movers aren't graded against a noisy provisional mean — everyone in the wave faces the same eventual target), *finalizes at that era's settlement*, and is never revisited. Re-opening (content-gated per Entry 25's two-component settledness — new arguments/evidence, not score drift) starts a **fresh sampling question**: new sortition cohort, new seal-until-quorum, new settlement. Prior-era ratings retire into the visible historical record and leave the live aggregate entirely. No carry, no re-affirmation, no damping schedule to tune. Era-1 raters can be sampled into era 2 like anyone else and rate fresh on the new evidence.

**The contrarian resolution, final form (Jeff's):** the reasonable contrarian **rates with the evidence in every era — including eras that disagree with their intuition — while authoring the questions and pointing at the evidence that will vindicate it.** Rating measures how well you track the current state of knowledge; authoring measures what you add to it. Era 1: rate ~consensus like any honest reader (no alignment loss), build the rival structure (authoring credit for well-crafted-though-unconfirmed). Era 2: the new evidence arrives — often *because* their structure pointed at what to look for — they rate the new evidence alongside everyone else, and their era-1 structure is re-rated up into load-bearing. Paid on both inputs, in both eras, entirely for work that was reasonable when done. The intuition-only contrarian who rated against era-1 evidence took a *correct* alignment hit — that rating was unreasonable at the time, whatever happened later. **Right-for-the-wrong-reasons earns nothing; wrong-for-the-right-reasons loses nothing. The site rewards reasonableness, not clairvoyance.** This distinguishes contrarians-with-reasons from lucky landers exactly as intended, with zero vindication machinery.

**Settled by implication — what Agreement means:** "your considered judgment of the current state of knowledge," not "your private credence about the eventual truth." Divergent ratings stay legal and unforbidden (they're how the crowd catches what the graph missed), but a divergence should be *expressible* — which motivates the one small affordance this entry adds: the **divergence nudge**. When a rating lands far from the current aggregate, the UI softly prompts "say why in a comment, or add what's missing to the graph" (never blocking). Articulable disagreement routes into incubate-then-adjudicate where it pays; pure intuition may rate and eat the variance.

**Verdict (🟢):** the alignment-scoring dial is closed, again by pointing existing machinery correctly (era-scoped grading + fresh sortition per era) rather than adding any (no re-affirmation, no carry weights, no retroactive re-grading).

---

## 28–29 · Adversarial-defense work — sequestered

*Entries 28 and 29 recorded a red-team "anchor experiment" (building a graph, then attacking its scores to test manipulation-resistance) and its methodology-corrected rerun. That work is out of brief for the FLF submission and has been **moved in full to the `adversarial-defense-archive` branch** — nothing was lost.*

*One finding from that thread is NOT adversarial and is worth keeping in view here, because it is about ordinary cooperative reputation: the rerun's reputation checkpoint (preserved in `v0/eggs-p3/CHECKPOINT.md`) showed that **True_R-as-alignment-with-consensus penalizes expertise** — sharp, correct-but-different raters land below blunter ones, a tyranny-of-the-median. This holds for an all-good-faith population and points at a proper-scoring / calibration reward (reward information, not raw agreement) as the fix direction for the reputation system. That is a live cooperative design question, tracked on the to-do list.*

---

## 30 · Reputation scoring, put to the test — alignment penalizes expertise (robustly), and the fix ladder

*2026-07-09. Took the Entry-28/29 tyranny-of-the-median finding head-on with a series of larger cooperative runs and offline re-scores. All numbers and method details live in `v0/eggs-p4/{FINDINGS,RESCORE-FINDINGS,BTS-FINDINGS}.md` and `v0/eggs-p5/{BTS-RUN-FINDINGS,SATURATION-FINDINGS}.md`; this entry is the design narrative. All populations are entirely cooperative (52 Haiku "crowd" + 8 Sonnet "experts"), so everything here is about ordinary site function, not adversaries.*

**Confirmed, and it is robust (not a cold-start artifact).** eggs-p4 (60 agents, 3 turns, agents able to argue via comments/phrasings) reproduced the penalty every round — expert-minus-crowd True_R −0.027 / −0.016 / −0.022 across rounds, never flipping, even as confidence grew to 0.91 and experts posted 52 arguing comments. Re-scoring the frozen log, the live reputation is not merely blind to competence but **inverted** (Spearman −0.64 vs hidden care/expertise labels). Volume, turns, earned reputation, and argument do not fix it.

**Diagnosed.** The penalty is **item-specific, not a calibration offset** — removing each rater's mean bias makes it *worse*. Experts don't rate everything lower; they push down the *particular* weak inferences the crowd overrates. Any rule scoring agreement with the consensus *level* therefore punishes exactly the experts' sharpest, most valuable judgments.

**The fix ladder (ordered by evidence and cost):**
1. **Discrimination / signal-tracking — the cheap, validated win, do this first.** Score a rater on how well their ratings track the item-to-item *ordering* (correlation with the leave-one-out item mean), not the level. It is offset- and scale-invariant, so a consistently-stricter expert isn't punished for the offset; it only asks "do you sort the claims strong→weak like the crowd does." On the real eggs-p4 log it *flips the sign* (experts 10th→77th percentile; correlation −0.64→+0.11) and needs no new data or events. **Robust caveat:** discrimination is more resilient than first claimed — it fails only when the *entire* crowd is uniformly wrong (no competent sub-population), because otherwise the leave-one-out mean is a decent truth-tracker. Synthetic validation (`v0/eggs-p4/harness/validate_bts.py`) confirms it holds until that extreme.
2. **Bayesian Truth Serum (meta-prediction) — principled but not yet demonstrated on real data.** Ask each rater to also predict the crowd's distribution; reward the "surprisingly popular" answer (more common in the votes than collectively predicted) plus prediction accuracy. It is strategy-proof by construction and can, in principle, crown a correct minority the crowd's *ordering* rejects (which discrimination cannot). Synthetic tests pass decisively in the uniformly-fooled regime. **But the real run (eggs-p5) did not deliver:** the precondition — the informed minority predicts the majority better than the majority predicts itself — *failed in aggregate*, because both tiers self-anchor ("others rate like me"), which is accurate only for the majority. It held where it mattered (experts recovered 81% of the true crowd gap on their sharp calls) but was swamped. Expert **density** is the biggest lever (saturating to ~38% experts moved BTS expert-percentile 0.15→0.40, monotonic, no threshold) yet **not sufficient** — the multi-bucket info score still rewards the concentrated majority. BTS needs three things together before it's judged: high density, a *per-item* surprisingly-popular scoring rule (not a per-rater bucket average), and *first-class* prediction elicitation (not a bolt-on).
3. **External anchor items — the surest escape from endogeneity.** Plant claims whose reasonableness is externally verifiable and score raters partly on those. The only thing that lets a correct minority outrank a blunt majority independent of whether meta-prediction works.

**Voting blocs — retired (as an anti-gaming device).** Blocs existed to make "guess the consensus" ungameable by hiding which sub-sample's mean you'd be scored against — a defense *specific to level-agreement scoring*. Under discrimination the rationale weakens (you'd have to reproduce the whole ordering); under BTS it **dissolves** (proper scoring makes honesty the equilibrium — no hiding needed). And blocs actively *hurt* the new rules: partitioning fragments the per-item rater sample, and both discrimination and BTS are density-hungry. Keep the one useful thing blocs gave — a dispersion/robustness signal — but compute it *without* partitioning (plain stdev or bootstrap over the full rater set). This joins a coherent theme: the shift to discrimination+BTS argues for **less spreading, more concentration** of reputation-weighted quality per item (the sortition assignment rule should weight contested-item blocs toward high-True_R raters — there is no "enough" plateau below ~40% expert fraction).

**Verdict (🟡 open, direction set):** reputation stays as-is in the shipped core until sign-off; the agreed direction is discrimination-first, BTS-with-fixes-later, anchors as the endgame. No reputation-math change is made without explicit approval (it is the one subsystem we deliberately kept through the sequester).

---

## 31 · The assessment grid completed — R/C rate any text, Agreement is typed by its target

*2026-07-09. Three to-do items — expose dispersion, rate titles, catch phrasing scope-drift — resolved together, because they complete a grid rather than piling on clutter. Additive to the assessment layer; touches none of the reputation math above. Spec: ASSESSMENT-SPEC amendments v1.3 (grid) + v1.4 (dispersion).*

**The organizing frame (resolves the "so many ratings, ugh" worry).** There are two kinds of assessment, cleanly separated:
- **R and C rate *text*** — any expression: phrasings, comments, and now **titles**. *Is it well-reasoned/well-framed? Is it clearly worded?*
- **Agreement rates a *claim or relationship*, and what it asks is typed by the target:** node = "is it **true**?", edge = "does the Ground **support** the Dependent (conditionally, Entry 26)?", group = "do they **jointly** support?", **title = "does this label **fit** the node?"**, **phrasing = "does this wording **belong** to — state the same claim as — the node?"**
So it is not N arbitrary ratings; it is **three questions (fit/truth, reasoning, clarity) asked wherever each is meaningful.** The apparent clutter is real coverage, and with AI raters there is no shortage of hands. Because Agreement is now genuinely polymorphic (truth / support / fit / belonging), the spec carries a canonical **target-type × dimension table** to keep it learnable.

**Titles get A/R/C.** A = does the title fit/cover the node; R = is it *neutrally, defensibly framed* (a title can beg the question — "Eggs are obviously fine" — a real R failure distinct from clarity); C = is it an unambiguous label. Graded **A(fit) + R/C blend selects the primary title**, subsuming the old binary `agree`-to-float mechanic (one selection path, mirroring how R/C already picks the primary phrasing). Title authors now earn authoring-R reputation credit like phrasing authors. Human sliders and the agent guide carry explicit text for title-Agreement's "does this fit?" sense.

**Phrasings get belonging-Agreement — a crowd-sourced atomicity check.** A on a phrasing = "does this wording state the same claim as the node." It is deeper than cleanup: node-Agreement ("is this claim true?") is only well-defined if all phrasings state the *same* claim, so belonging-A is what **protects the integrity of the truth rating**. It **gates** primary-phrasing selection (a phrasing must *belong* before its R/C can win primary status — otherwise scope drift hijacks the node's meaning). A low belonging score fires a **nudge**: "where does this belong? — spin it off into its own node." On spin-off the migrated phrasing starts fresh (ratings reset, same spirit as the Entry-27 era reset) and the UI offers to draw an edge between old and new node (a claim that "didn't belong here" is often a Ground/Dependent of what's here). This is the crowd-sourced answer to the long-open "who decides where one idea ends" atomicity question. (Watch-item, low risk cooperatively: belonging-A could in principle exclude legitimate rephrasings a faction dislikes — reputation-weighting mitigates.)

**Dispersion + rater count exposed — and it is now load-bearing, not just transparency.** Node/edge/phrasing panels show the **distribution** of scores (a small histogram sparkline) plus **n**, clickable to a full-detail card. The reputation work (Entry 30) is the argument for it: the mean *hides the story*. A node at "3.4" could be a tight consensus, a wide-but-uncertain spread, or experts-at-1.5 vs crowd-at-4 — three different epistemic states the mean collapses. A histogram distinguishes *bimodal (contested)* from *wide-unimodal (uncertain)* — i.e. it renders the tyranny-of-the-median **visible**. Show the raw distribution with the True_R-weighted mean marked as a line; suppress/gray the viz below ~5 raters; forward hook — the card is where a predicted-vs-actual overlay (the BTS "surprisingly popular" gap) would later live.

**Verdict (🟢):** the assessment grid is closed and specced; it is purely additive to the rating layer and independent of the reputation-scoring track.

---

## 32 · Assessment layer consolidated — the validated stack, calibration over concentration, adversarial robustness

*2026-07-15. The reputation/assessment investigation continued on a separate branch (`claude/argument-mapping-user-scoring`, developed in isolation so its adversarial red-team wouldn't trip the swarm's cyber-safeguards), generalized to a **second domain with real attacker agents**, and is now **folded into `main`/v0** — code, data, and docs. The authoritative, current synthesis is **`v0/FINDINGS-SYNTHESIS.md`** (it supersedes `REPUTATION-SCORING-SPEC.md`, now history-only). This entry is the design-log capture and, importantly, **what it supersedes from Entry 30.***

**The validated stack (what to actually build).**
1. **Blind rating, enforced at the tool layer** (`rating_mode_only`, no opt-out) — raters never see consensus/comments while rating. The **single biggest accuracy lever found**: the same personas tracked truth at **0.52 with cues visible vs 0.89 blind**. ASSESSMENT-SPEC v1.5.
2. **Discrimination vs the *anchored* consensus** as the ongoing rater signal — never vs the raw crowd (self-referential and harmful in split populations).
3. **Calibration (un-distortion) as the aggregator** — fit each rater an affine map on external anchors, invert their systematic error, weight by inverse residual variance. Works with **zero** competent raters; degrades gracefully under wrong anchors.
4. **Camp detection + adjudication** for contested regions — a spectral split of the rater-agreement matrix finds viewpoint factions with no oracle; a few contested anchors adjudicate which faction tracks truth. **Detection is cheaper and more robust than correction.**
5. **Panel anchors** — a diverse frontier-model panel deliberates to forge anchors where no ground truth exists (validated r≈0.98 vs the expert oracle); **placement and model-diversity beat quantity** (~4–5 different-model voices; a shared-model panel only polishes a common-bias floor).
6. **A thin external/human grounding check** — the model oracle tracks the documented real record (+0.95) *except* that models systematically over-rate how "unsettled" a settled question is; a whole-generation LLM bias invisible from inside an all-model loop.

**What this SUPERSEDES from Entry 30.** The eggs-p6 recipe's third leg — **superlinear / winner-take-all `True_R^γ` concentration — is RETIRED as a default.** It is fragile on wrong anchors and, under a *sleeper* attack, actively **harmful** (it concentrates trust on anchor-clean liars). **Calibration replaces it.** Entry 30's other conclusions stand: alignment/level-agreement and Dawid-Skene fail (tyranny of the median); discrimination is the cheap rater signal — *but only against an anchored consensus*; BTS remains parked pending first-class prediction elicitation. The unifying lesson holds and sharpens: *a purely internal rule can only measure agreement with the crowd, so it inherits whatever the crowd gets systematically wrong — the fix is a small, frugally-spent dose of external ground truth (anchors).*

**Cold-start & scale (coldstart-lab).** "Reasonableness" splits into a cheap **disposition** (~8 ratings to classify) and an expensive **fine rank** (~77 ratings) — assess dispositions fast, accumulate rank slowly; `K = (1−r1)/r1` is *measurable*, not a taste knob (≈8 for dispositions, ≈76 for fine rank — current default is ~10× too trusting for the latter). Newcomers: blind pass → a routed **probe slice** (anchors + max-separation items) classifies disposition and yields an anchor score in 4–6 ratings. **One global reputation scalar is structurally insufficient** — a diligent-but-biased user banks reputation on the uncontested 75% and rides it into contested items; disposition must be **per contested region**. The contested trigger is **rating stdev** (>~0.7; +0.79 corr with error). **Oracle spend scales with the number of contested divides, not users** — active learning, the concrete scalability answer.

**Disposition dominates capability (eggs-p7→p10).** A biased strong model barely beats a biased weak one and is worse than a neutral weak one; capability's protection against a prior is dose-dependent. Camp detection tracks **belief, not capability**, across the whole transition, and the transition is **sharp** (no phantom factions on homogeneous populations, and when it fires it's right) — the deployability result.

**Adversarial robustness — now in scope for `main`.** Offline + real-agent dose-response (eggs, then covid as a 2nd domain with a **real** attacker rating run). Calibration robustly defeats naive/jittered/**sybil** attackers even at a 60% majority (they lie on the anchors too). The **sleeper** (honest on anchors, lying only in un-anchored gaps) is the crux — it defeats calibration by ~30%, superlinear makes it worse, and **camp-detection is the 100%-recall backstop** → design is *correction + detection + escalation to human review*, dense **rotating** anchors, attack-aware metrics. The hardest case, and the load-bearing new finding: the **over-certainty / consensus-entrenchment attack** — a bloc pushing the *already-leading* answer manufactures false *certainty* (collapsing a live question into fake near-settlement, burying the legitimate minority — the **Semmelweis / minority-truth** failure). Distance-to-oracle MAE **hides** it; a built **certainty guardrail** (`covid-adversarial/certainty_guard.py`) catches it. Two "the metric is a defense surface" lessons (correlation hides a level-shift; MAE hides over-certainty). And **refusal is directional** — identical sleeper persona, agents refused to manufacture the *contested* consensus 2/8 but the *mainstream* one 0/8 (small-n, suggestive). Roadmap and scale policy: `v0/ROADMAP-NEXT-VERSION.md`, `v0/ORACLE-BUDGET-POLICY.md`.

**Build requirement (time-sensitive for the graphs `main` still builds).** The assessment layer only works on graphs built **assessment-ready**: a clear top **verdict** (rival top-level answers as an antithesis set); a **two-layer** structure (anchorable **evidential facts** kept distinct from un-anchored **interpretive cruxes** — anchors on facts, contested frontier on cruxes); an identifiable **contested frontier**; and **blind rating**. Denser coverage is welcome, but keep these four properties per question — they are what make a graph *assessable*, not just *legible*.

**Structure & verification.** The assessment `reasonable/` + `graph.py` (a format-compatible superset) replaced v0's structural-only versions; the experiment dirs (`eggs-p3…p10`, `covid`, `covid-adversarial`, `eggs-adversarial`, `eggs-external-check`, `coldstart-lab`, `eggs-p8-deliberation`) and the synthesis/roadmap/policy/submission docs now live under `v0/`. Existing graphs **rebuild byte-identical**; the full suite (**198 tests + 8 rating-mode tests**) is green.

**Verdict (🟡, deployment-open):** ~60–65% confidence the assembled machinery is deployment-robust — high on the component mechanisms under tested conditions, lower that it transfers to the messy real thing. The load-bearing gaps: a **human-rated slice** (breaks model-on-model circularity), a **live end-to-end longitudinal run**, and an **adaptive red-team**. Authoritative current map: **`v0/FINDINGS-SYNTHESIS.md`**.

---

## 33 · Layout is self-assembly — the craft is the energy function

*2026-07-18. Names the standing layout principle after a brief regression, and sets the frame for all future "make the map clearer" work. Corrects PR #54; supersedes nothing — Entry 7's stability-vs-physics tension and the Entry-22-era "organic clustering, replacing columns" practice both stand.*

**The regression that prompted this.** A structural lint (Graphs thread) correctly showed the flagship snapshots are clean layered DAGs, and the viewer briefly shipped a Sugiyama-style columnar layout to exploit it. Columns *were* visually tidy — and wrong in kind: they hard-code today's shape instead of letting the graph express it, they erase the strength/proximity signal (strong and weak edges render at identical column pitch), and they cannot absorb continuous growth. The owner's correction, now the named principle:

**The principle (🟢).** The neighborhood layout **remains force-directed and self-assembling — permanently.** Clustering of idea-spaces, proximity-by-strength, and the actual messiness of paths are *content*, not noise; and a continually growing graph must keep settling into its lowest-energy state on its own. **The viewer's job is to design the energy function so that the lowest-energy state coincides with the logically and visually clear state.** Clarity is earned by shaping the physics, never by suspending them.

**Energy rules in force so far** (each deterministic; the settle stays byte-stable across reloads):
- **Springs & repulsion** — strength → rest length (closer = stronger), inverse-square spacing. *(original)*
- **Forward-flow bias** — a gentle one-sided force preferring ground left of dependent, so support reads left → right. *(original, strengthened)*
- **Ghost spring-release** (×0.05) — demoted/auto-ghosted items stop shaping living clusters. *(HANDOFF §2.2)*
- **Shortcut spring-release** (×0.15) — direct edges outcompeted by a stronger layered path stop pulling, so layering, not flatness, shapes the map. *(SPEC §3.4)*
- **Depth-seeded start** *(new, from the regression's salvage)* — initial x proportional to longest-path depth (prefers the data layer's `layer` export when present), so the settling *basin* already flows left → right; every force still acts on every node.
- **Strength-proportional straightening** *(new)* — a weak per-edge pull toward equal y, scaled by normalized strength: strong chains settle straight and readable, weak links stay free to bend, and topologically unnecessary crossings become higher-energy states that melt away.

**Open dial (🟡):** Entry 7's macro-stability vs. re-flow tension is still live — a growing graph that re-settles on every addition fights spatial memory. Likely resolution unchanged: stable macro geography (seeding, pinned landmarks) + local physics. Revisit when graphs actually grow continuously.

---

## 34 · Wormholes have weight — components as bands, antitheses as springs

*2026-07-18. Two new energy rules under Entry 33's frame, from an owner observation on the Debate graph. Extends 33; changes nothing above it.*

**The observation.** The Debate graph is really *two* argument structures — one landing on each of the two rival Ought answers — plus a small fragment, with no ground edge between them. Free physics let one sub-graph settle *inside* the other, so the reader couldn't see there were two. Yet the two sides are far from unrelated: they're cross-linked by **seven antithesis sets** (the two Oughts are themselves rivals). The fix has to do two things at once that pull in opposite directions — *keep unconnected sub-graphs from intertwining*, while *keeping rivals near each other* — and both have to fall out of the energy function, not a special-case rule.

**The two rules (🟢).**
- **Component banding.** Connected components over ground edges each seed into their own horizontal band and are held there by a band-anchored y-pull (deterministic band order: larger first, ties by smallest id). So every unconnected argument reads as its own blob instead of interleaving. A single-component graph has one band centred at 0 — i.e. the rule is *inert* on it, and its prior look is byte-unchanged.
- **Wormhole springs.** Antithesis rivals share no ground edge, but they are *the same idea contested* — nearness of physical space should show that nearness of logical relation. Each antithesis set becomes attractive springs between its members (rest ≈ one card-width, so rivals sit adjacent, not overlapping), weighted by each member's `belonging` and released for ghosts exactly like ground springs. Because they pull *across* the component bands, the two sides of a debate settle facing each other **at the seam** between bands rather than drifting to opposite ends — and the two rival Oughts, being antitheses, come to rest next to each other where the reader expects the two answers to the one question.

The name is deliberate: we'd used "wormhole" informally for the antithesis relation (a link through the void with no edge on the graph). Giving it a spring gives it *weight* in the physics — the relation now shapes the map, not just the detail view.

**Why this over a layout special-case.** Both rules are pure forces in the same fixed, deterministic settle as everything else — no post-hoc "now move the components apart." So they compose with depth-seeding, straightening, and the ghost/shortcut releases, and they scale: an N-component graph gets N bands, and any new antithesis set is one more wormhole with no code change. Verified on the flagship set — Debate's two big components land in fully non-overlapping y-bands while its seven rival pairs sit ~1 card-width apart (≈3× closer than a random pair); single-component graphs (Black Holes) are visually unchanged.

**Open (🟡):** band spacing and wormhole stiffness are hand-tuned constants. Fine for prototype-scale graphs; a graph with many components, or one component that is much taller than a band, may want the band pitch to derive from measured component extents rather than a fixed pitch. Revisit alongside Entry 33's growth dial.

---

## 35 · Edges that read as connections — node-off-edge clearing + a smarter router

*2026-07-18. Two clarity fixes for the neighborhood edges, from an owner observation: some edges curved further than expected and a couple passed *under* a card they weren't connected to (reads as a false connection). One is a layout rule, one is a render fix; together they attack the same root cause.*

**The diagnosis.** An edge that passes under an unrelated node is confusing — the eye reads adjacency as connection. The old per-edge router (a single quadratic bend, control point pinned at the midpoint perpendicular, offsets capped at 410px) was doing the visible work, but it was *compensating* for a layout that let nodes sit right on top of edges: in dense regions it either swooped far to get around a node (the "longer curving paths than expected") or hit its cap and drew straight through (the under-node passes). Measured on the flagship v2 set: **448** distinct under-node penetrations on Covid, **150** edges affected; **26** edge-crossings on Debate.

**Fix 1 — node-off-edge clearing (layout, Entry 33's frame).** A new energy rule: an unrelated node whose centre falls within a perpendicular band of an edge segment (and between its endpoints, not near the ports) is pushed off the line. One-sided — only the intruding node moves, the edge holds — so it's a stable nudge like the centre-pull, and faint ghost/shortcut edges (already decluttered) don't shove living nodes. Making "node on a non-incident edge" a higher-energy state means the graph *settles* with edges running through gaps, so most edges are straight without any routing at all. Deliberately gentle: strong enough to clear the sparse graphs a reader actually studies, not so strong it stirs a dense hairball into new disorder (an over-strong version regressed Black Holes — the classic local-force-makes-global-mess failure).

**Fix 2 — along-edge control anchors (render).** The router now anchors its bezier control point at a fraction *along* the edge (0.5, then 0.35, 0.65) before pushing it out perpendicular, so an obstacle bunched near one end is cleared by pulling the curve toward that end instead of forcing a wider bend. The midpoint is tried first at every offset, so any edge that already routed cleanly is byte-unchanged, and the max offset is untouched — no new giant swoops, just smarter use of the same reach.

**Result (measured, all four v2 flagships improved on every axis):** Debate under-node **2 → 0**, crossings **26 → 11**; Covid penetrations **448 → 246**, crossings **428 → 234**; Eggs penetrations **104 → 35**; Black Holes penetrations **33 → 20**. Deterministic; single settle; composes with banding/wormholes/straightening.

**Open (🟡):** Covid (a genuinely dense 133-node hairball) still has residual under-node edges — density it can't fully escape without more spread than its own springs want. A future lever is edge-length-aware spring rests (shorter strong edges, so long edges don't span clusters) or an explicit crossing-minimisation pass; deferred, since honest messiness is *content* (Entry 33) and Debate — the graph the concern was raised on — is now clean.

---

## 36 · Density-adaptive spread — the dense graph gets more room

*2026-07-18. The "more spread would help" lever from Entry 35's open note, taken up when Review's interconnection pass thickened Debate (its two sub-graphs merged into one 42-node component) as well as Covid. Directly answers an owner ask to "clear up the density a bit on both."*

**The measurement that framed it.** Cards are a fixed 126px wide, but at the old repulsion the *median nearest-neighbour centre distance* was ~142px — cards essentially touching, ~16px of gap, no room for an edge to pass between them. That's the cramping: the layout had no whitespace to route through, so the router either swooped or clipped (Entry 35). A sweep confirmed the obvious: more repulsion → more gap → fewer crossings and under-node passes. But it also surfaced a catch — **the right amount is graph-specific.** Covid (dense, 134 nodes) improves monotonically with spread (crossings 303 → ~210); Debate (45 nodes) is *non-monotonic* — past a point, more repulsion just reshuffles its small tight equilibrium into a *more*-crossed one. A single global constant is either too airy for the small graph or too cramped for the dense one.

**The rule (🟢).** Repulsion scales with node count toward a ceiling: `repulsion = base · (1 + spread · clamp((n − lo)/(hi − lo), 0, 1))` (base 44k, spread +60%, lo 40 → hi 140), read **once** from `n` at layout time. A dense graph pushes apart harder and gets the gaps its edges need; a small graph stays compact near the base and keeps the tight, legible clustering that suits it. It's still pure force self-assembly — this only sets *how hard* nodes repel, never where they land — so it composes with every other energy rule untouched. (Rest length is deliberately *not* scaled: the sweep showed longer springs make dense graphs worse, stringy and more crossed. Only repulsion and the hard card-gap moved.)

**Result (measured):** Covid crossings **303 → 207**, under-node edges **126 → 81**; Eggs under-node **18 → 4**; Debate **57 → 54** (held compact by design — pushing it harder measured *worse*, confirming the non-monotonicity); Black Holes roughly flat (under-node **18 → 9**, crossings +4). Deterministic; single settle.

**Open (🟡):** `n` is a crude density proxy — a graph that's large but sparse (a long chain) would be spread more than it needs. Edge count, or a measured area/occupancy ratio, would be truer; deferred until a real graph exhibits the mismatch. And the small-graph non-monotonicity is a reminder that crossing-count is not a smooth objective for force layout — chasing it by tuning constants is a dead end; the durable wins are the structural rules (clearing, routing, adaptive spread), with honest residual messiness left as content.

