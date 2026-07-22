# Reasonable — the vision

*The full scope and intent of the project, for anyone new to it: what problem it exists to solve,
what it is now, and what it is meant to become. The technical account of what has been built is
[PROJECT-OVERVIEW.md](v0/PROJECT-OVERVIEW.md); the front door is [START-HERE.md](START-HERE.md);
this document is the why.*

---

## 1. The problem: we don't reliably know what's true

Knowing what is true is extraordinarily hard, and with all our progress we are only a little
better at it than the ancient Greeks. Most of us cannot defend even our deepest beliefs more than
a few logical steps in either direction — toward their justifications or toward their
consequences — and most of us can't credibly explain the serious alternatives to the positions we
hold. If you can't trace out the ground and consequences of an opinion, and you don't understand
the other sides of it, in what sense do you understand the question?

Humanity has made remarkable intellectual progress, but unevenly, and for a structural reason. We
advance fastest where reality slaps down errors: technology, mathematics, empirical science. In
those fields, being wrong is easily checkable, so error dies. But the questions people often care
about most — ethical, political, social — are usually untestable: too complex, too slow-moving,
to be experimented on — or simply not the kind of thing an experiment can settle. And yet these
are exactly the questions that govern what we do with our growing power. A civilization whose
power outruns its ability to deliberate sensibly about how it uses that power is in a dangerous
position.

When you can't sensibly deliberate as a collective, claims tend to circulate as bare assertions —
detached from their full chains of justification — and the primary limits on what can be
effectively asserted are loudness, repetition, charisma, and monopoly over the narrative.
"Alternative facts" are not a cultural accident; they are a symptom of a missing piece of
infrastructure: there is no shared, trusted place where a claim's real credibility can be checked.

## 2. The idea: a map with the same shape as reasoning

Language is linear because time is: we learned to communicate via sounds spaced sequentially in
time. Speech, and the writing that inherited its habits, can only walk one path at a time through
an argument, leaving every other path unsaid and unmarked. But ideas are not linear — they branch,
fork, recombine, and interweave. One claim rests on many others and leads to many more. A faithful
map of reasoning therefore needs at least two dimensions.

We have learned to share, preserve, and broadcast information, and have collected tremendous
amounts of it — but now what we need more than more information (we are drowning in it), is a map
of it, to make sense of it and to have some hope of agreeing on what it means. Reasonable is
trying to make that map: a single, durable, continuously evolving graph of ideas, where a disputed
question is broken into atomic claims that can be examined fully and clearly, each connected to
what justifies it, what follows from it, and what rivals it.

A comparison to an existing collective repository that has given the world a great deal of
epistemic value is to say that Wikipedia is for describing facts, while Reasonable is for having
the arguments that underlie many of those facts. Wikipedia gives an overview description of
things, while Reasonable lays out the chain of justification on every side of a question, all in
one place, in context with its counterpoints, and all assessed for the strength of their
arguments. It doesn't necessarily aim to resolve all our disputes — most of them are live, ongoing
arguments with legitimate perspectives from several sides — but it does aim to make it clear which
arguments are clear and reasonable and valid, and which are weak and unjustified, so that at least
we can have *good* arguments between strong, sensible alternatives.

A fully accurate map can't be simpler than the territory it describes: a complete map of a hard
question is complex because the question is. The full map of all human knowledge will not be small
and it won't be simple, and it will correctly seem overwhelmingly complicated at many points, and
some people will want to object that it's too complicated — and they may sometimes be right, when
we haven't done a good enough job making sure the map isn't *more* complicated than the territory,
either in content or in form. But when we have eventually done a good job, the map will still be
complicated, because we don't actually have a choice between a complex map and a simple one; we
have a choice between a map that is accurate to reality and one that isn't. Anyone who thinks the
full map is unnecessarily more complicated than the implicit map they have in their head is most
likely simply mistaken about the quality and completeness of their own atlas. And no one, however
brilliant, actually holds the whole structure of a question in their mind with accurate consensus
weights and known ratios of agreement from different factions. You can know the question
perfectly, even though this is very rare; we don't currently have any way to know what proportion
of people agree with you on every individual point, or exactly where we collectively rate the
proper weight of a claim.

## 3. Assessment is hard, and contested

A map that anyone can write on fills with noise unless something keeps signal on top. Reasonable's
answer is an assessment layer: everything on the map is rated, raters earn reputation, and
reputation weights your influence on ratings. This is an obvious target for gaming and
manipulation, and it will be a central, and ongoing, focus of development to keep it providing
honest signal from good faith contributors. And it may be one of the most valuable inputs that AI
can now offer: checkably fair and consistent panels of agents to provide ratings — and to provide
a consistent rating source to check human users against, as a form of ground truth against which
to perceive biased, manipulative, or simply unreasonable users.

Rating needs to be blind. You rate a claim before seeing what anyone else thought — no consensus,
no comments, no author reputation in view. In our testing to date this was the single biggest
accuracy lever.

A little external reality goes a long way. Any rating rule that only looks inward can only measure
agreement with its own crowd, so it inherits whatever the crowd gets systematically wrong. The
corrective is to find a set of anchor questions whose answers are independently well-established,
used to measure raters against reality rather than against each other.

But there is still an epistemic floor to what we can know with confidence, in the untestable
domains where there is no oracle and no experimental grounding: the gap between "what people find
convincing" and "what is true" cannot be fully closed by any method — not essays, not expert
panels, not peer review, not even a highly detailed map of everything we can think of to say about
it. The most we can do in many places is to make the gap explicit, measure it, and shrink it as
best we can: make every position around the gap as clear as possible, with their full chains of
justification complete and their assessments turned into public knowledge, and let the surviving
consensus stand as the best approximation humanity can currently construct to what is True. In
domains where nothing can be proven, a consensus that has been made to show its work, and has
survived organized attack, and can be seen to be the best of its rivals, is not Truth, but it is
what knowledge is there to be had — and our civilization is currently far short of even having
that.

## 4. How a map changes anything

A skeptic of the value of mapping a debate might correctly say that arguers almost never change
their minds, so what good does a map actually do?

It won't necessarily make anyone who already has an opinion change it — but it changes the ground
the next argument stands on. Before the internet came along (and a smartphone in every pocket)
every fact it contains already existed — in libraries, in encyclopedias, scattered and not always
instantly accessible. But universal instant access to Wikipedia and Google made a meaningful
change: it became hazardous to confidently assert a false fact that anyone around you could
immediately show to be wrong. The bar argument over basic facts died out, and people who had
previously believed and argued that Timbuktu was in Asia were quickly confronted with their error.

Arguments over whether AI is likely going to kill us all, or whether climate change will make
major portions of the earth uninhabitable, or whether rent control is good for a city, are much
more complex and nebulous than where Timbuktu is, and it's not so simple to show that a belief
like that is mistaken, or even less credible than a competing idea.

Every point in every major argument already exists — made somewhere, by someone, scattered across
essays, papers, and comment threads — but they are uncollected, unorganized, unevaluated; they do
not form a trusted repository that can be pointed to and reluctantly acknowledged as the full,
assessed, current final word, that already contains every argument and point all of humanity can
think of.

Debate, in the civilizational sense worth caring about, is not two people in a room getting
progressively madder at each other; it is the accumulated global conversation about what has the
strongest claim to be true, and about what to do about it. Most of that conversation has already
happened — it just has no home. Gather it, structure it, assess it reliably, and the same shift
becomes available for arguments that Wikipedia produced for facts: the weak position becomes
visibly, demonstrably weak, and expounding it starts to cost something. It doesn't mean any one
person will change their mind, but it will push them — and the culture at large — toward having
*better* arguments between *actually reasonable* positions. The floor rises; a world where we only
ever disagree well — strongest case against strongest case, values named as values — will be a
different civilization.

And the map doesn't need to convert existing combatants. The target is the audience, the person
who hasn't decided yet, the student forming a worldview, the decision-maker who needs the real
current state of a question — it shows the menu of legitimately reasonable choices, and the values
that underlie and emphasize alternative options; it protects people from absorbing, and then being
emotionally bound to, bad arguments for good causes; it exposes them to the nature of strong
argumentation, shows how poorly weak arguments are received, and demonstrates that the world is
complex and reasonable people can reasonably differ, and that most people who disagree with you
aren't simply bad people who refuse to admit the obvious truth.

## 5. Where it could go

**A scaffold for the unknown, not just a record of the known.** A faithful map shows its own
holes — the questions indicated but unanswered, the evidence that would decide a crux but hasn't
been gathered. That turns the map into an instrument for directing inquiry: anyone can mark a
wanted node or region beyond the current frontier and attach a bounty to developing it into
high-confidence knowledge. Knowledge-building becomes a structured, incentivized, collaborative
activity with a visible frontier, rather than a scatter of disconnected efforts.

**A benchmark for minds.** Running parallel graphs with different contributor sets — human, AI,
and mixed — turns the platform into something new: a direct measure of what different kinds of
minds contribute to knowledge-creation itself, question by question, with the merged graph likely
stronger than either alone, for at least a little while.

**A translation layer between minds.** If AI reasoning begins to outpace human understanding,
explanations of machine-scale thinking may get harder and harder for humans to follow. The graph
renders that thinking into auditable, navigable, separately-assessable claims: a reader can jump
to any one claim, see exactly what it rests on and what rivals it, and judge that piece without
holding the whole. Structured discrete blocks of information may be the means by which humans can
still check work they could no longer follow otherwise.

**Answers on demand, the translation layer at a lower level.** Most people will never or rarely
walk the graph itself — just as most people never read the academic papers behind a settled
consensus — and they shouldn't have to. The reader-facing front door can be as plain as a search
box: ask a question, and an AI answers in a few readable paragraphs drawn from the assessed graph
to say what is well-supported, what is genuinely disputed, and how confident to be — with each
load-bearing point linked to the place on the map where it is worked out in full. The deep work of
a small percentage of humans, along with AI agents, gives collective knowledge the most robust
base it can have; the answer box is how everyone else draws on it.

**Many deployments, one format.** The same open format supports a spectrum of instances: fully
open community graphs, open-contribution graphs with curated assessment, and closed expert or
institutional instances — and because the format is shared, parallel instances of the same
question can be compared directly. Where an open crowd and a curated panel diverge is itself
precious data: a standing instrument for locating exactly where open assessment can and cannot yet
be trusted, and for improving it.

**Turning the lens on institutions.** All behavior — including corporate and governmental
behavior — is an implicit claim about what it is acceptable to do, and implicit claims can be made
explicit and examined like any others. A mature map supports evaluative claims about the entities
that hold power, aggregated into a reliable public picture of how each one actually behaves and
how good their outputs are — which gives every institution a clear public path to becoming more
trusted and their products more desired (and gives their competitors clear knowledge of how to
beat them if they won't take that advice) and everyone else a reliable basis for deciding whom to
support. In the far vision, when the system can reliably publicly identify who are good global
actors and who aren't, this inverts advertising from an antagonistic propaganda war for your
attention, into a collaborative sharing of things known to be good that you will probably want to
know about.

---

[← Back to the submission page](index.html)
