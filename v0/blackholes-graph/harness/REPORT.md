# Deep-research report — Could the LHC create a black hole that destroys Earth?

**Question:** Could a high-energy particle collider such as the Large Hadron Collider create a
microscopic black hole that grows and destroys the Earth?

**Method:** Graded verification (per `DEEP-RESEARCH-BRIEF.md` / `TIERING-TEST-PLAN.md` 1a). Two
judgments were kept separate for every claim: (a) **faithfulness/provenance** — does the cited
source demonstrably exist, is it correctly attributed, and does the retrieved material genuinely
support the claim (this is the *only* thing that may drop a claim); and (b) **support** — a **0-5
merit score** that annotates but never kills, with genuinely contested claims sitting near the
middle (~3) rather than at 0. No "default to refute if uncertain": uncertainty lowers a score, it
does not delete a claim, and a well-sourced factual claim is not down-scored merely because the
topic is contested and a rebuttal exists. Attributions ("the paper argues X") and object-claims
("X is true") were judged on the same terms regardless of grammar.

**Environment caveat (matters for provenance strength).** The session's `WebFetch` was blocked by
the egress policy (HTTP 403 on every host, including `example.com`), the same block the brief was
written to escape — this environment turned out to be fetch-blocked too. `WebSearch` *did* work, so
research was done by targeted search across all five strands and claims were corroborated at
search-result-synthesis level. Consequently: source **existence and attribution** were verified
(the papers, reviews, and news items below are real and correctly cited), but **exact verbatim page
quotes could not be independently confirmed** and are therefore not asserted — `sources.json`
carries paraphrased load-bearing claims, not quotations. This is a real limitation on provenance
depth and is why no claim here is scored 5 purely on a single unfetchable primary source.

**Coverage:** all five required strands are covered by at least one primary source (checklist at the
end). 17 sources, 40+ load-bearing claims.

---

## Executive summary

The scientific answer is a well-established **no**: the LHC cannot create a black hole that destroys
Earth, and the evidence grounds that answer decisively while grounding the catastrophe claim only
thinly. The safety case is a **layered chain**, and its strength comes from each layer holding even
if the one before it is doubted:

1. **Production is speculative to begin with.** In standard four-dimensional gravity the Planck
   scale is ~10^15 times LHC energies, so no black holes form at all. Micro black holes are only
   possible under unconfirmed beyond-Standard-Model physics (large extra dimensions / a ~TeV Planck
   scale). So the danger requires an *if* that has never been shown to hold.
2. **If they were produced, they would evaporate near-instantly** via Hawking radiation. This is the
   first line of defense — and it is also the case's one genuinely unconfirmed assumption: Hawking
   radiation is theoretically well-motivated but has never been directly observed. This is exactly
   where the contrarian minority pushes.
3. **Even granting a stable, non-evaporating black hole, the astrophysical evidence still bounds the
   risk.** Cosmic rays have struck Earth, the Sun, and dense stars at LHC-and-higher energies for
   billions of years (LSAG: nature has run the equivalent of ~10^5 LHC programmes on Earth alone).
   The one loophole — that collider black holes could be slow and captured whereas cosmic-ray ones
   are fast and escape — is closed by Giddings & Mangano: slow, stable, dangerous black holes would
   have been captured by and would have destroyed observed white dwarfs and neutron stars, whose
   continued existence is therefore direct evidence that such black holes are not produced.
4. **Empirically, none have been seen.** LHC searches (CMS, ATLAS) across ~10^15 collisions up to 13
   TeV find no black-hole signatures, excluding semiclassical production below several TeV.
5. **Every official and independent review agrees.** The LSAG concluded "LHC collisions present no
   danger." The contrarian position — the 2008 Wagner & Sancho lawsuit — was a legal/public
   challenge, not a peer-reviewed refutation; it was dismissed for lack of jurisdiction and failure
   to show a credible threat, with a brief from Glashow, Wilczek and Wilson affirming the scenarios
   had no realistic chance.

**Where it is genuinely open:** Hawking radiation remains experimentally unconfirmed (layer 2), and
the whole *production* question is contingent on extra-dimension physics that has not been observed.
But the safety conclusion does not depend on resolving either: layers 3-4 (the astrophysical bound
and the empirical non-observation) carry the load independently of layer 2, which is what makes the
"no" robust rather than merely authoritative. The catastrophe claim survives only as a bare logical
possibility with no positive evidence and several independent bounds against it.

---

## Findings by strand (each claim carries a 0-5 support score)

Scores: **5** = decisively grounded, multiple independent primary sources, essentially uncontested;
**4** = strong, standard consensus; **3** = genuinely contested or a real open assumption, evidence
mixed/incomplete; **2** = weakly supported / speculative; **1** = bare possibility, little positive
evidence; **0** = would-drop (none here — all sources' provenance held).

### Strand 1 — Production theory (could a collider make one at all?)

- **[4] Micro black holes are only producible under beyond-Standard-Model physics.** In standard 4D
  gravity the Planck scale (~10^16 TeV) is ~10^15 times LHC energies, so no black holes form; only
  large-extra-dimension / low-Planck-scale scenarios bring the scale near 1 TeV. *(s04, s05, s06)*
  Strong as a conditional; the antecedent (extra dimensions) is itself unconfirmed, which is why
  this bounds the danger rather than establishing it.
- **[3] If the fundamental Planck scale is low (~1-2 TeV), the LHC could produce micro black holes
  copiously — of order one per second.** *(s04, s05)* This is a real, relatively model-independent
  prediction *within* TeV-gravity scenarios — but contingent on physics not observed, so mid-scored,
  not high. The empirical searches (Strand 4) have since excluded the low end of this range.
- **[3] Collider-produced black holes are a theoretical prediction of TeV-scale gravity ('black-hole
  factories'), tied inseparably to their own rapid Hawking decay.** *(s05)* Production and
  evaporation come from the same theoretical package; you cannot invoke the production while
  discarding the decay.

### Strand 2 — Hawking radiation (they would evaporate)

- **[4] Any micro black hole would, on standard theory, evaporate almost instantly via Hawking
  radiation** — smaller holes radiate faster and are highly unstable, vanishing in a tiny fraction
  of a second. *(s01, s06, s11)* Consensus; the first line of the safety case.
- **[4 — as a fact about the evidence] Hawking radiation has never been directly observed.** It is
  well-motivated theoretically but experimentally unconfirmed; the safety case uses it as a
  prediction. *(s07)* This *fact* is not contested (score high); what it *implies* for risk is the
  contested part below.
- **[3] The risk-side inference — 'because Hawking radiation is unproven, the evaporation defense
  may fail' — is a legitimate but non-decisive objection.** *(s07, s08, s14)* Genuinely contested,
  hence ~3: it correctly identifies the one unconfirmed link, but it does not touch layers 3-4,
  which bound the risk even if evaporation fails entirely.

### Strand 3 — Cosmic-ray safety argument (the load-bearing empirical case)

- **[5] Cosmic rays have collided with Earth and other bodies at LHC-and-higher energies for
  billions of years without catastrophe** — LSAG estimates >3x10^22 such collisions on Earth, ~10^5
  LHC-equivalent programmes. *(s01, s03, s08, s11, s12)* Multiple independent primary sources; the
  natural-experiment backbone.
- **[4] The naive cosmic-ray argument has a real loophole: collider black holes could be slow-moving
  and gravitationally captured, whereas cosmic-ray products move fast and escape Earth.** *(s08, and
  the objection Giddings & Mangano set out to answer)* Acknowledged by the safety side itself, which
  is why the argument needed the white-dwarf extension — scored high because it is a correct,
  consensus-recognized objection, not a fringe one.
- **[5] Giddings & Mangano close that loophole: slow, stable, dangerous black holes would have been
  captured by and destroyed observed white dwarfs and neutron stars; those stars' survival is direct
  evidence such black holes are not produced.** *(s02, s13, s17)* This is the crux that upgrades the
  cosmic-ray argument from suggestive to decisive for the no-evaporation case.
- **[4] Even in the captured case, accretion is far too slow to matter** — bounded well below Bondi
  accretion and further quantum-mechanically suppressed at subatomic scales, giving Earth-accretion
  times longer than the solar system's remaining lifetime in the relevant scenarios. *(s02, s13)*
- **[3] White dwarfs carry more of the load than neutron stars** because neutron stars' strong
  magnetic fields can decelerate incoming cosmic rays enough to drop the effective energy below the
  LHC range. *(s02)* A technical qualification, correctly noted, mid-scored as a nuance rather than a
  headline result.

### Strand 4 — Empirical LHC searches (none have been seen)

- **[4] LHC searches (CMS, ATLAS) find no microscopic-black-hole signatures** in high-multiplicity,
  high-transverse-energy final states, in good agreement with Standard Model background across ~10^15
  collisions. *(s08, s09, s10)*
- **[4] Non-observation sets rising mass-exclusion limits** — from 3.5-4.5 TeV in the first 7 TeV
  CMS search to roughly 5-11 TeV in later 8 and 13 TeV analyses, depending on model. *(s09, s10)*
  This is a bound on production, consistent with either "extra dimensions don't apply at these
  energies" or "the scale is higher than probed."
- **[2] The exclusion limits do not by themselves prove safety** — they constrain a specific
  semiclassical production model, and a determined risk argument can retreat to unprobed parameter
  space. Scored low-but-nonzero: real as a caveat, but the safety conclusion never rested on the
  searches alone; the astrophysical bound (Strand 3) does the decisive work.

### Strand 5 — Official reviews and the lawsuit

- **[5] The official conclusion is unambiguous: 'LHC collisions present no danger and there are no
  reasons for concern'** (LSAG 2008), endorsed by CERN and consistent with the earlier LSSG/2003
  review and the RHIC review methodology. *(s01, s08, s11, s12)* Treated as a pointer to the
  reasoning in Strands 2-4, not as a terminal authority.
- **[4] The documented contrarian position is the 2008 Wagner & Sancho lawsuit**, which raised four
  scenarios — micro black holes, strangelets, magnetic monopoles, vacuum bubbles — and sought to
  delay start-up for a renewed review. *(s08, s14)* Represented fairly as a real minority challenge.
- **[4] The lawsuit was dismissed** for lack of U.S. jurisdiction over CERN and failure to show a
  credible threat of harm; a friend-of-the-court brief from Glashow, Wilczek and Wilson held the
  doomsday scenarios had no realistic chance. *(s15, s16)*
- **[2] The contrarian scientific claims (e.g. metastable/stable dangerous black holes) are not
  peer-reviewed refutations of the safety case** and are addressed directly by Giddings & Mangano's
  rebuttal, which shows they either contradict well-tested physics or are already excluded by the
  astrophysical bounds. *(s13)* Low score reflects thin positive grounding, not a provenance
  problem.

---

## The catastrophe answer, weighted

The "destroys Earth" answer survives only as a **bare possibility [1]**: it requires (i) extra
dimensions that have not been observed, (ii) the failure of Hawking radiation that has been
predicted for 50 years, (iii) a black hole that is simultaneously stable and slow enough to be
captured, and (iv) an accretion process fast enough to matter — each of which is independently
argued against, and (iii)+(iv) together are excluded by the survival of white dwarfs and neutron
stars. No positive evidence supports any link in that chain. That is the intended contrast: the
safety answer is grounded at 4-5 across multiple independent strands; the catastrophe answer is a
conjunction of unsupported conditionals.

## Provenance-dropped claims

**None.** Every source cited is a real, correctly-attributed paper, official review, or news report,
and each claim's provenance held under the search-level check. The honest limitation is *depth*, not
*fabrication*: because WebFetch was blocked, verbatim quotes were not confirmable, so claims are
paraphrases and no claim is scored 5 on the strength of a single unfetchable source alone. A
follow-up run in a fetch-enabled environment should pull full text for s01 (LSAG), s02 (Giddings &
Mangano), and s09/s10 (CMS) to upgrade those quotes from paraphrase to quotation.

## Five-strand coverage checklist

| # | Strand | Primary source(s) | Covered |
|---|--------|-------------------|---------|
| 1 | Production theory (extra dimensions, low Planck scale, 10^15 gap) | s04, s05 (+s06) | yes |
| 2 | Hawking radiation evaporation (prediction, not yet observed) | s06, s07 (+s01) | yes |
| 3 | Cosmic-ray safety argument + white-dwarf/neutron-star backstop | s02, s03, s13 (+s01) | yes |
| 4 | Empirical LHC searches / exclusion limits | s09, s10 (+s08) | yes |
| 5 | Official reviews (LSAG) + lawsuit and rebuttals | s01, s11, s12, s14, s15 | yes |

## Sources

- **s01** — LSAG, *Review of the Safety of LHC Collisions* (2008), arXiv:0806.3414 / J. Phys. G 35, 115004 — https://arxiv.org/abs/0806.3414
- **s02** — Giddings & Mangano, *Astrophysical implications of hypothetical stable TeV-scale black holes* (2008), Phys. Rev. D 78, 035009 — https://arxiv.org/abs/0806.3381
- **s03** — Jaffe, Busza, Sandweiss & Wilczek, *Review of Speculative 'Disaster Scenarios' at RHIC* (2000), Rev. Mod. Phys. 72, 1125 — https://arxiv.org/abs/hep-ph/9910333
- **s04** — Dimopoulos & Landsberg, *Black Holes at the LHC* (2001), Phys. Rev. Lett. 87, 161602 — https://arxiv.org/abs/hep-ph/0106295
- **s05** — Giddings & Thomas, *High-energy colliders as black-hole factories* (2001), Phys. Rev. D 65, 056010 — https://arxiv.org/abs/hep-ph/0106219
- **s06** — *Micro black hole* — Wikipedia — https://en.wikipedia.org/wiki/Micro_black_hole
- **s07** — *Hawking radiation* — Wikipedia — https://en.wikipedia.org/wiki/Hawking_radiation
- **s08** — *Safety of high-energy particle collision experiments* — Wikipedia — https://en.wikipedia.org/wiki/Safety_of_high-energy_particle_collision_experiments
- **s09** — CMS, *Search for microscopic black holes in pp collisions at √s = 7 TeV* (2012), JHEP 04 (2012) 061 — https://arxiv.org/abs/1202.6396
- **s10** — CMS, *Search for Microscopic Black Hole Signatures at the LHC* (2011), Phys. Lett. B 697, 434 — https://arxiv.org/abs/1012.3375
- **s11** — *The Safety of the LHC* — CERN — https://home.web.cern.ch/science/accelerators/large-hadron-collider/safety-lhc
- **s12** — J. Ellis, *The LHC is Safe*, CERN Colloquium (14 Aug 2008) — https://indico.cern.ch/event/39099/attachments/782382/1072600/LHCsafe.pdf
- **s13** — Giddings & Mangano, *Comments on claimed risk from metastable black holes* (2008), arXiv:0808.4087 — https://arxiv.org/abs/0808.4087
- **s14** — *Doomsday fears spark lawsuit over collider* — NBC News (2008) — https://www.nbcnews.com/id/wbna23844529
- **s15** — *LHC lawsuit case dismissed by US court* — Phys.org (2010) — https://phys.org/news/2010-09-lhc-lawsuit-case-dismissed-court.html
- **s16** — *LHC lawsuit dismissed by US court* — Symmetry Magazine (2010) — https://www.symmetrymagazine.org/breaking/2010/08/26/lhc-lawsuit-dismissed-by-us-court
- **s17** — *Physicists Rule Out the Production of Dangerous Black Holes at the LHC* — Phys.org (2008) — https://phys.org/news/2008-09-physicists-production-dangerous-black-holes.html
