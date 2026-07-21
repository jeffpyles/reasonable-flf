# Reasonable — the vision

*The full scope and intent of the project, for anyone new to it: what problem it exists to solve,
what it is now, and what it is meant to become. The technical account of what has been built is
[PROJECT-OVERVIEW.md](v0/PROJECT-OVERVIEW.md); the front door is [START-HERE.md](START-HERE.md);
this document is the why.*

---

## 1. The problem: we don't reliably know what's true

Knowing what is true is extraordinarily hard, and we are barely better at it than the ancient
Greeks. Most of us cannot defend even our deepest beliefs more than a few logical steps in either
direction — toward their justifications or toward their consequences — and most of us cannot even
*state* the serious alternatives to the positions we hold. If you don't understand the other answers
to a question, in what sense do you understand the question?

Humanity has made staggering progress, but unevenly, and for a structural reason. We advance fastest
where reality slaps down errors: technology, mathematics, empirical science. In those fields,
being wrong is checkable, so error dies. But the questions people care about most — ethical,
political, social — are usually *untestable*: too complex, too slow-moving, or not the kind of thing
an experiment can settle. And yet these are exactly the questions that govern what we do with our
growing power. A civilization whose power outruns its ability to reason about using that power is in
a dangerous position, and that is roughly our position.

There is a second, more immediate cost. When claims circulate as bare assertions — detached from
their full chains of justification — the only limits on what can be effectively asserted are
loudness, repetition, charisma, and monopoly over the narrative. That is what makes propaganda
possible. "Alternative facts" are not a cultural accident; they are the symptom of a missing piece
of infrastructure: there is no shared, trusted place where a claim's actual support can be checked.

## 2. The idea: a map with the same shape as reasoning

Language is linear because time is. Speech, and the writing that inherited its habits, can only walk
one path through an argument, leaving every other path unsaid and unmarked. But ideas are not
linear — they branch, fork, recombine, and interweave. One claim rests on many others and leads to
many more. A faithful map of reasoning therefore needs at least two dimensions.

That is the whole founding move. Take the same impulse that produced writing, the printing press,
the encyclopedia, and the internet — each a leap in our ability to share and preserve thought — and
take the next step: not *more* information (we are drowning in it), but a **map** of it. Reasonable
is that map: a single, durable, continuously evolving graph of ideas, where a disputed question is
broken into atomic claims, each connected to what justifies it, what follows from it, what rivals
it, and how else it can be said.

The short version we use everywhere: **Wikipedia is for facts; Reasonable is for arguments.**
Wikipedia gives the consensus description of settled things. Reasonable holds the strongest case
from *every* side of a disputed thing, in one place, in context, assessed — so that where the
disagreement genuinely lives is visible, and everything around it can quietly settle.

A few properties follow from the founding move, and they run through everything:

- **Opposition is a rival claim, never a negation.** There is no "not-X" node. Disagreeing means
  writing the actual competing position and placing it beside the original. This single discipline
  keeps the map a map of positions rather than a flame war.
- **Values get a home of their own.** Claims about what *is* and claims about what we *ought to do*
  are different kinds of thing. The grammar keeps them typed apart, forbids deriving an "is" from an
  "ought," and assesses value claims by *endorsement* — one person, one vote — never by
  truth-scoring. The deepest disagreements are usually value disagreements wearing a factual
  disguise; the map's job is to strip the disguise, not to pretend facts can settle values.
- **Nothing is deleted.** A refuted claim is demoted to a visible "ghost," never erased. "We checked
  this and it failed" is one of the most valuable things a map can record — a civilization that
  forgets what it disproved will relitigate it forever.
- **The map cannot be simpler than the territory.** A complete map of a hard question is complex
  because the question is. The honest choice is not between a complex map and a simple one; it is
  between an *explicit* map that can be shared, checked, and read a piece at a time, and an
  *implicit* map hidden in one person's head. No one — however brilliant — actually holds the whole
  structure with accurate weights. Externalizing it adds information for everyone, including the
  experts.

## 3. Keeping it honest: assessment, and the hard problem inside it

A map that anyone can write on fills with noise unless something keeps signal on top. Reasonable's
answer is an assessment layer: everything on the map is rated, raters earn reputation, and
reputation weights influence. Three design commitments matter more than the rest:

- **Rating is blind.** You rate a claim before seeing what anyone else thought — no consensus, no
  comments, no author reputation in view. In our testing this was the single biggest accuracy
  lever, and it also removes the oldest distortion in live debate: victory going to whoever
  performs best or has memorized most in the moment. On the map, reasoning is weighed at leisure,
  not performed.
- **A little external reality goes a long way.** Any rating rule that looks only inward can only
  measure agreement with its own crowd — so it inherits whatever the crowd gets systematically
  wrong. The corrective is a small, sparing set of *anchor* questions whose answers are
  independently well-established, used to measure raters against reality rather than against each
  other, with reputation spent only where it is needed.
- **The failure modes are studied, not assumed away.** The prototype's assessment machinery was
  stress-tested against coordinated manipulation, and the findings — including the attacks that
  *beat* our defenses, and the places we had to retract our own earlier claims — are published in
  this repository alongside the successes. The most dangerous attack we found is not flipping a
  verdict but *manufacturing false certainty* around an already-leading answer: entrenchment, not
  lying. A truth-finding tool must be able to tell what a debate settled from what it merely
  performed settling.

And underneath all of it, one honest philosophical floor. In the untestable domains there is no
oracle; the gap between "what most people find convincing" and "what is true" cannot be fully
closed by *any* method — not essays, not expert panels, not peer review, not this. What a format
can do is make the gap explicit, measure it, and shrink it: make every position's full support
public, stress-test the assessment, and let structured, surviving consensus stand as the best
approximation humanity can currently construct. In domains where nothing can be proven, a
consensus that has been made to show its work — and has survived organized attack — is arguably
not a consolation prize for truth. It is what knowledge *is* there.

## 4. What exists today

This is not only a philosophy; the core of it runs. The prototype in this repository includes the
graph grammar and engine (append-only history, byte-for-byte reproducible snapshots), the blind
reputation-weighted assessment layer with its published research and red-team results, an
interactive viewer that teaches its own visual language, and four built case graphs — the
competition's three (eggs, COVID origins, collider safety) plus a fourth that maps the strongest
published argument *against* projects like this one, concessions included, and lets a blind panel
rate it. The claims in these prototype graphs are AI-drafted scaffolding built to exercise the
machinery, not final answers; what they demonstrate is the format doing the things this document
promises — separating facts from the inferences on them, keeping open questions visibly open, and
refusing to flatter its own builders.

## 5. How a map changes anything

The fair skeptical question: committed arguers almost never change their minds, so what does a map
actually *do*?

It changes the ground the next argument stands on. Before Wikipedia and the smartphone, every fact
it contains already existed — in libraries, in encyclopedias, scattered and effectively
inaccessible. What changed the culture was universal access to one trusted repository: within a few
years it became *embarrassing* to confidently assert a checkably false fact, and so, mostly, people
stopped. The bar argument died not because arguers were persuaded but because the environment
shifted under them.

Every point in every major argument likewise already exists — made somewhere, by someone, scattered
across essays, papers, and threads, unevaluated. Debate, in the sense worth caring about, is not
two people in a room; it is the accumulated global conversation about what is true and what to do.
Most of that conversation has already happened. It just has no home. Gather it, structure it,
assess it honestly, and the same shift becomes available for *arguments* that Wikipedia produced
for facts: the weak position becomes visibly, checkably weak, and expounding it starts to cost
something. Not because anyone was dunked on — because anyone can look.

Three consequences we care about most:

- **The floor rises.** Refuting a false fact rarely flips its believer; positions are
  over-determined and survive the loss of one support. But a public record of which arguments are
  known to be bad slowly prunes them from circulation, and the disagreements that remain are the
  real ones. A world where we only ever disagreed *well* — strongest case against strongest case,
  values named as values — would be a different civilization.
- **The reader is the customer.** The map does not need to convert combatants. It serves the person
  who hasn't decided yet, the student forming a worldview, the decision-maker who needs the honest
  state of a question this afternoon — and it serves them the way an encyclopedia does: free-riding
  on all the work already done, forever.
- **Contribution gets easy.** People will not sustain structured debates, but they reliably drop
  single points — and partisans reliably show up when their side is visibly losing. A platform that
  can collect scattered one-shot contributions into a coherent structure converts exactly the
  behavior everyone already exhibits into coverage. AI agents do the assembly, maintenance, and
  first-pass rating. Nobody needs to want to "argue rigorously."

## 6. Where it goes

**One graph.** This repository contains four separate graphs only because a prototype had to bound
its scope. Their subjects already share deep underpinnings — biology, physics, statistics,
epistemology — and the real object is a *single, connected, public graph of ~all knowledge*,
current and future, each question's map joined to the disciplines it actually rests on. Every
serious investigation added makes the next one start from more solid ground: knowledge that
compounds, rather than reports that pile.

**A scaffold for the unknown, not just a record of the known.** A faithful map shows its own
holes — the questions indicated but unanswered, the evidence that would decide a crux but hasn't
been gathered. That turns the map into an instrument for *directing* inquiry: anyone can mark a
wanted node or region beyond the current frontier and attach a bounty to developing it into
high-confidence knowledge — precisely the move this competition itself makes. Knowledge-building
becomes a structured, incentivized, collaborative activity with a visible frontier, rather than a
scatter of disconnected efforts.

**A benchmark for minds.** Running parallel graphs with different contributor sets — human, AI, and
mixed — turns the platform into something new: a direct measure of what different kinds of minds
contribute to knowledge-creation itself, question by question, with the merged graph likely
stronger than either alone.

**A translation layer between minds.** The same property runs the other direction. As AI reasoning
outpaces human working memory, prose explanations of machine-scale thinking stop being checkable —
not because they are wrong, but because no human can hold them. The graph renders that thinking
into auditable, navigable, separately-assessable claims: a reader can jump to any one claim,
see exactly what it rests on and what rivals it, and judge that piece without holding the whole.
Structure is the format in which humans can still check work they could no longer follow as prose —
which may become the most important thing a map of reasoning is *for*.

**Many deployments, one format.** The same open format supports a spectrum of instances: fully open
community graphs, open-contribution graphs with curated assessment, and closed expert or
institutional instances — and because the format is shared, parallel instances of the *same*
question can be compared directly. Where an open crowd and a curated panel diverge is itself
precious data: a standing instrument for locating exactly where open assessment can and cannot yet
be trusted, and for improving it.

**Belief, quantified.** A natural extension of the grammar is a probability node: "how likely is
X?", answered by each rater with their own number. The map then carries a collective forecast — a
reputation-weighted headline figure with the unweighted average beside it — plus what a single
number always hides: the honest range, and any distinct camps within it. This connects the map to
forecasting and prediction markets, whose prices and scoring can enter as inputs or as calibration
anchors for exactly these nodes. It pairs with a second future feature, **personal maps**: a user
overlays their own beliefs — including their own probabilities — on the shared graph, gets notified
when the ground under one of their beliefs materially shifts, and can compare maps with someone
they disagree with to find the exact node where their reasoning first diverges. The last place two
people agreed is the only useful place for them to argue.

**Earning trust where reality can referee.** The long game extends the anchor principle to whole
domains. Mathematics is the frontier case: a proof-dependency graph refereed by a formal verifier
has *machine-checkable* ground truth, dissolving at a stroke the hardest problems of the untestable
domains — no crowd bias, no model bias, no unmeasurable oracle. Build credibility on problems where
reality can referee; then carry the earned trust, carefully, into the domains where it can't yet.

**Turning the lens on institutions.** All behavior — including corporate and governmental
behavior — is an implicit claim about what it is acceptable to do, and implicit claims can be made
explicit and examined like any others. A mature map supports evaluative claims about the entities
that hold power, aggregated into an honest public picture of how each one actually behaves — which
gives every institution a precise, public path to becoming more trustworthy, and everyone else a
reliable basis for deciding whom to support. In the far vision this even inverts advertising: when
only well-regarded actors may advertise, being *allowed* to advertise becomes the message, and the
interests of platforms, advertisers, and readers point the same direction for once.

**And, aspirationally, the culture itself.** People who grow up in a world where this exists grow
up saturated with the knowledge that there are serious arguments on many sides of almost every
question — and with how hard it is to out-think the best ideas humanity has collected. That
mindset, intellectual humility with a working map, is the only engine of collective intellectual
growth we know of. The far hope is the same one Wikipedia partially delivered for facts: raise the
floor of what a person is embarrassed to be wrong about. For public *reasoning*, feed better
science, saner politics, and institutions that expect to be examined. We hold the far vision
honestly: it is a direction, stated so it can be argued with — not a promise.

## 7. What all this rests on

Three load-bearing assumptions, stated plainly because they are where the design is most
falsifiable:

1. **Enough good faith.** More people want to build and know what's true than want to manipulate
   and deceive — the same wager underneath Wikipedia, open source, and civilization generally. If
   it is false in general, this fails, but so does much more than this.
2. **Ideas are mappable.** Meaning survives decomposition into connected claims well enough for the
   map to stay faithful to the territory. All language already strings ideas together; branching
   strings should carry them at least as well.
3. **Strong arguments are recognizable.** Humans — with effort, collision, and error-correction —
   can reliably tell better reasoning from worse. If we can't, no method survives, and no one can
   claim to understand anything at all.

Each has survived contact with the prototype so far; none is proven at scale. The open problems we
consider hardest — keeping viewpoint diversity so consensus stays tethered to truth, protecting
the correct minority from a wrong majority, surviving motivated and funded adversaries, and
earning real human adoption — are named in this repository's research documents with our current
best answers and their measured limits, in the open, where critique can reach them.

That, ultimately, is the intent: not a tool that ends disagreement, but infrastructure that makes
our disagreements *worthy of us* — every position at its strongest, every settled thing settled
visibly, every real crux located and named, and the whole thing owned by everyone. The strongest
argument for the project is the one this repository tries to embody: we mapped the best case that
it cannot work, rated it blind, conceded what was true in it, and built the answer to the rest.

---

*Reading map: [START-HERE.md](START-HERE.md) (orientation + run-it commands) ·
[MECHANISMS.md](MECHANISMS.md) (how assessment works today, present tense) ·
[PROJECT-OVERVIEW.md](v0/PROJECT-OVERVIEW.md) (everything built, in detail) ·
[Reasonable - Concept Overview.html](Reasonable%20-%20Concept%20Overview.html) (the founding
synthesis this vision draws on) · [FINDINGS-SYNTHESIS.md](v0/FINDINGS-SYNTHESIS.md) (the assessment
research and its honest limits).*
