# Source brief — "Can you "solve debate" with an argument-mapping platform?"

*Unstructured raw material for a build test. This is the kind of prose a human would hand a build
agent: the substance of both sides in flowing paragraphs, with no graph structure, no pre-drawn
limbs, and the original named-entity framing left in (so the build has to abstract and structure it
itself). The question: **will a structured, collaborative argument-mapping platform meaningfully
improve real-world reasoning and debate on contested questions — or, as Scott Alexander argues in
"Your Attempt To Solve Debate Will Not Work," is the whole endeavour doomed?***

## The skeptic's case (Scott Alexander, steelmanned)

Scott's core claim is that platforms trying to "solve debate" or "map arguments" are
well-intentioned, sophisticated, and doomed. His reasons run roughly as follows.

Real arguments almost never decompose into clean premises and a conclusion where a skeptic can point
to the one false premise or invalid link — the argument-map model assumes a tidy logical form that
real disagreement simply lacks. Relatedly, real disagreements rarely hinge on a checkable false fact
or a nameable fallacy; even when someone is wrong, they rarely assert a specific false fact, and when
you point one out they just drop it and keep arguing on other grounds. Scott gives an AI-risk panel
example: the closest anyone came to explaining a sharp disagreement was that some people weight a
theoretical intelligence-explosion argument heavily while others distrust theoretical arguments and
hold a prior that things rarely change fast — no false fact, no fallacy, just different weighing. And
adding more circles and premises to a map makes it worse, not better: it misrepresents inherently
probabilistic reasoning as logically necessary syllogisms and trains people to point at one link and
cry "fallacy, you lose."

A second family of points is about what actually generates disagreement. The load-bearing work in a
real argument is quantifying magnitudes and weighing them against each other, which resolving atomic
true/false premises does not touch. Scott's lockdown example: even granting "lockdowns hurt the
economy" is true, getting to "lockdowns are bad" still requires quantifying the economic harm, all
the other harms, the benefits, comparing them for a specific proposal, and holding a theory of
interpersonal utility. Deeper still, the real generators of disagreement are differing values and
ethical frameworks — "civil rights regardless of cost-benefit," "we owe more to the weakest" — which
no argument map can resolve. And positions are over-determined: people hold them through many
weakly-held considerations, not one crux, so flipping any single crux doesn't move them. The decisive
action is at the level of high-level generators of disagreement — worldviews — while maps operate at
the wrong altitude, on surface claims.

A third family is practical. Formal argument mapping is an inefficient way to change minds, and its
intended user — someone arguing online who wants a more rigorous way to do it — barely exists; people
who argue online are not there to update. And philosophy and rhetoric have not "solved debate" in two
thousand years, which is some evidence the problem is not tool-fixable.

Finally, some honest concessions that cut the same way, several drawn from the project's own research:
if "solve debate" means "make the disagreeing parties agree," the platform concedes it does not do
that. The consensus-versus-truth problem is not fully escaped — internal rating rules only measure
agreement with the crowd and invert on a biased majority, and correcting that needs external anchors
that are scarce on exactly the most contested questions. Rating dispersion turned out to be a
low-reliability signal, so contestedness has to be read structurally. And adoption at scale with real
human communities is unproven; the demonstrations so far are AI-agent panels.

## The builder's case (the Reasonable project, in reply)

The reply does not mostly dispute the mechanism; it disputes the goal. The platform does not force
premise→conclusion form: it uses graded support edges (support strength, not binary validity), rival
positive claims instead of negations, joint-support groupings, and re-wording stacks — modelling
over-determination and weighing structurally rather than assuming the clean form the critique attacks.
In a graded, support-only map a refuted ground is demoted while its dependent survives on its
remaining grounds, so "drop the false fact and keep going" is the normal modelled case, not a failure.

On the "wrong object" worry: the goal is not to resolve the weighing but to locate it and make it
explicit — where the weight sits, how wide the reasonable range is. On a real contested build (a
pandemic-origin question) the honest verdict "currently unresolved" scored high; the assessed map
declined to manufacture a false resolution. Values get a first-class, separate home: a prescription
node type, an is/ought firewall, and endorsement (not truth) rating, so value-cruxes are mapped as
values rather than smuggled into factual claims.

On practicality: the audience is third parties — readers and future deciders consulting a durable
shared artifact — not the two arguers in a live fight, so "inefficient at changing the arguers' minds"
measures the wrong thing. Cheap AI agents can build, maintain, and rate the map at scale, which
removes the authorship cost that sank earlier mapping efforts; three differently-shaped contested
questions have already been built and panel-assessed end-to-end by AI agents. And "unsolved for two
thousand years" ignores changed conditions: cheap AI authorship and rating, reputation-weighting, and
enforced-blind rating are genuinely new — encyclopedias, prediction markets, and systematic review
likewise languished until the right medium and incentives arrived, not new philosophy.

## The honest middle

Whether the platform "works" depends on what you demand of it: it cannot resolve genuinely value-laden
disagreement, but it can faithfully map it — so the dispute is substantially about the goal, not the
mechanism. The critique's strongest points target *resolution* (making parties agree), which the
builders concede they don't deliver, while the builders' claims are about *representation*. And the
dispute over whether it "works" is itself over-determined and partly value-laden, so by the critique's
own analysis it won't be resolved — only located and mapped.

## The value crux

Underneath sits a genuine value disagreement, best stated as two rival prescriptions: that a tool
which faithfully maps a disagreement — making its value-cruxes explicit and openly unresolved — is
worth building even if it never makes the parties agree; versus that a debate tool is only worth
building if it actually changes minds or produces agreement, and a map that leaves everyone where
they started is not worth the effort.
