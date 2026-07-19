# How to read a Reasonable graph

*The reader's guide to what you're looking at — in the viewer, or in the raw data. The viewer's
built-in **Introduction** button teaches the same visual grammar interactively in about 90 seconds;
this is the text version, for reference and for anyone working from the files directly. Terms:
[GLOSSARY.md](GLOSSARY.md).*

## The card

Each card is one **claim**: a single statement, in plain language, small enough to judge on its
own. The card shows the claim's short title (zoomed out) or its full text (focused), and a bar
showing how the community has rated it. Cards are not posts, comments, or arguments-in-full — the
argument is the *shape the cards make together*.

## Position is the relation

Where a card sits relative to the focused claim tells you how it is logically related — position
itself carries meaning:

- **Left: grounds.** The claims that justify the focused one. Reading leftward walks *down* the
  justification: "why should I believe this?"
- **Right: dependents.** The claims that follow from it. Reading rightward walks the consequences:
  "what does this commit me to?"
- **Stacked through the focus: rivals.** The other serious answers to the same question — an
  *antithesis set*, strongest at the top. The other side is always physically present; a rival that
  has lost support is *lower*, not gone.
- **Behind (in depth): phrasings.** The same claim, worded differently; the community floats the
  best wording to the top and the rest remain underneath.

## Color, brightness, and outline

- **Brightness is agreement.** One spectrum: dark = low or split; bright = high and tight. You can
  read the health of a whole region without reading a word.
- **Gold outline = Ought.** A value or action claim. Its bar runs toward gold, not white, because
  it measures *endorsement* (one person, one vote) — never "truth."
- **Blue outline = Evidence.** A fact anchored to a source outside the graph; the card names its
  source, so provenance is checkable on sight.
- **Faded and sunk = ghost.** Refuted or superseded material, demoted but kept — "we checked this
  and it failed" is part of the record, and it is reversible.

## Edges

Support edges connect grounds to what they support. **Brighter = higher rated support; thicker and
closer = stronger.** Edge ratings are *conditional* — "granting the premise, how strongly does it
carry this conclusion?" — so a true premise with a weak connection shows as a bright card on a dim
edge, a distinction prose reliably blurs. When a direct edge is outcompeted by a stronger multi-step
path, the viewer folds it into a "+N weaker shortcuts" affordance so the load-bearing structure
reads first.

## The confidence signals

Every rated item carries an at-a-glance trust label:

- The **spread glyph** shows the honest distribution behind the number — the band is the spread,
  dots are group means.
- The **sample lozenge** shows coverage: red = below quorum, amber = below the graph's maturity bar
  (`confirm`), plain = enough ratings to lean on.
- The **lifecycle state**: *sealed/provisional* (too few ratings yet), *settled* (converged, covered,
  no live rivalry — whether the verdict is "strong" or "weak"), *contested* (a structurally real,
  live disagreement). "Contested" comes from the map's structure and detected belief camps — not
  from mere rating noise.

## The layout is computed, not drawn

The map arranges itself: a deterministic simulation in which strong connections pull tight, rivals
cluster, and unrelated regions drift apart. No one hand-places anything, the same graph always draws
the same way, and the arrangement itself is information — what sits central is load-bearing; what
sits peripheral is peripheral.

## Reading the raw data

Every graph is a directory with three files. `events.jsonl` is the append-only history — every
write ever made, in order; the full provenance of everything. `graph.json` is the derived snapshot
the viewer renders: `nodes` (with `kind`, phrasings, titles, and an `agreement` block carrying the
mean, count, spread, histogram, and lifecycle `state`), `ground_edges` (from → to, with their own
agreement blocks), and `antithesis_sets`. `config.json` holds the assessment settings, so
rebuilding the snapshot from the log reproduces it byte-for-byte. If you'd rather interrogate than
read: the `graph.py` commands in [START-HERE.md](START-HERE.md).

## A 60-second reading protocol

1. Find the focused question's card and read its rival stack first — the serious answers, strongest
   at top.
2. Glance at brightness across the region: where is it bright and tight (settled), where dark or
   split (live)?
3. Walk the strongest rival leftward a step or two: are its grounds bright, on bright edges?
4. Check for gold outlines near the crux — if the real fork is a value fork, the map will show it
   as one.
5. Anything faded and sunk was tried and failed; click it if you want the history.

That is the whole skill. Everything else is detail on top of it.
