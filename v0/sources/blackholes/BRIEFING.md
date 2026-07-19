# Information base — "Could the LHC create a black hole that destroys Earth?"

*A neutral starting map of the argument territory for swarm authors. This is background to build
FROM, not text to copy. Every factual claim you place must trace to a source in
`index.json` (via an `external_anchor` node citing its `ref_id`) or be a reasoning/inference node
in its own right. Do not invent specific numbers, energies, or findings beyond what's stated here
and in the pack — where you're unsure, write at the level of generality the sources support, or
`flag-friction` that a more specific source is needed.*

## The implicit question
"Could the Large Hadron Collider (LHC) create a microscopic black hole that destroys the Earth?"
(Remember: the question itself is never a node — its rival *answers* are.)

## The live rival answers (candidate top-level positions)
- **No credible risk** — the mainstream expert position: even if micro black holes are produced,
  they are harmless.
- **Non-negligible risk** — a contested minority position (associated with public lawsuits and a
  few scientists, e.g. Wagner, Rössler) holding that the danger was not adequately excluded.
- (Possible third framing: **risk is real in principle but bounded to negligible by astrophysical
  evidence** — this may turn out to be a support for "no credible risk" rather than a separate
  answer. Decide as you build.)

## The main lines of argument (find the structure; don't just list these)
1. **Production is theoretically possible.** Some beyond-Standard-Model theories (large extra
   dimensions) predict TeV-scale black holes could form at LHC energies (`lhc-006`). This is the
   premise both sides start from — it establishes possibility, not danger.
2. **Evaporation argument.** Any micro black hole would evaporate almost instantly via Hawking
   radiation (`lhc-004`), so it could never grow. **Crux:** Hawking radiation is theoretically
   well-motivated but has never been directly observed — the risk side treats this as an unproven
   assumption.
3. **Cosmic-ray argument.** Cosmic rays collide with Earth, the Sun, and other bodies at energies
   far exceeding the LHC, and have for billions of years without catastrophe (`lhc-001`, `lhc-003`).
   **Crux / objection:** cosmic-ray collision products move at high speed and would escape Earth,
   whereas collider-produced black holes could be slow-moving and gravitationally captured — so the
   analogy might not hold.
4. **White-dwarf / neutron-star argument.** Giddings & Mangano (`lhc-002`) close that loophole: if
   slow, stable, dangerous black holes could be produced by cosmic rays, they would have been
   captured by and would have destroyed dense stars (white dwarfs, neutron stars); those stars'
   continued existence bounds the risk even in the no-evaporation scenario.
5. **Institutional/authority position.** CERN and the LSAG conclude there is no danger (`lhc-001`,
   `lhc-005`). Treat an appeal to this authority as a pointer to the reasoning above, not a
   terminal ground (see the guide on authority nodes).

## Notes for authors
- This case is a good test of a **different shape** from a genuine scientific split: here there is
  strong expert consensus with a vocal contested edge. Represent the minority position *fairly and
  positively* (as real competing claims in an antithesis set), not as a strawman.
- The interesting structure is the **chain of cruxes** (evaporation reliability → cosmic-ray
  analogy → white-dwarf backstop). Map how each argument answers the objection to the one before.
- Cite `external_anchor` nodes to the pack; reuse one `--source` id for multiple findings from one
  source (`list-studies` to check existing ids).
