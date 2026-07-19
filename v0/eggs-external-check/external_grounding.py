#!/usr/bin/env python3
"""Thread 4 — break the all-models grounding: does our Sonnet "expert" oracle
(and the Fable+Opus panel) actually track the DOCUMENTED REAL-WORLD record, or
only each other?

Every prior "truth" in this project is model-generated (eggs-p5 = 8 Sonnet
personas). This builds an EXTERNAL reference grounded in documented real-world
scientific/guideline positions as of ~2024 — the named source-pack studies
(Hu 1999, Rong 2013), the U.S. Dietary Guidelines cholesterol-cap change
(300 mg cap in earlier editions; removed 2015-2020), and established textbook
lipidology/physiology (LDL/ApoB causality, hepatic downregulation, saturable
absorption, hyper-responders, FH, choline, Salmonella temp). It is still
LLM-APPLIED (I am a model too), but it is anchored to specific citable
real-world facts rather than to the eggs-p5 panel's free judgment — a genuine,
if imperfect, step outside the model-consensus loop.

Discipline: a value is assigned ONLY where the documented record clearly speaks.
ABSTAIN (None) on (a) value/ought claims — no fact of the matter; (b) genuine
frontier-contested empirical claims where the real record is legitimately mixed.
The scored comparison is over the assigned subset. The MOST valuable output is
the list of nodes where the model panels DIVERGE from the documented record.

Scale: 0-5, "how true is this claim per the documented real-world evidence."
"""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "coldstart-lab"))
from common import p5_oracle, pearson, mean  # noqa

# external_value, one-line documented basis. None => abstain (value Q or genuinely contested).
EXT = {
    # --- core dietary-cholesterol / egg-CVD story (documented consensus tilted ~2015) ---
    "n001": (4.2, "Rong 2013 BMJ, Drouin-Chartier 2020 BMJ: ~1 egg/day no CVD assoc in general pop; guideline cap dropped"),
    "n002": (1.4, "current consensus: moderate egg intake does NOT meaningfully raise CVD risk in general pop"),
    "n003": (4.4, "well-documented: effect modified by diabetes status and hyper-responder phenotype"),
    "n005": (4.3, "dietary cholesterol raises serum LDL on average, effect size varies widely between individuals"),
    "n020": (4.5, "hyper-responders (sharp LDL rise to dietary cholesterol) are a documented phenotype"),
    "n021": (4.4, "hepatic cholesterol-synthesis downregulation to dietary intake is textbook homeostasis"),
    "n033": (4.3, "documented consensus: saturated fat is the primary dietary driver of serum LDL, not dietary cholesterol"),
    "n079": (4.2, "intestinal cholesterol absorption is incomplete/saturable (~50%), NPC1L1-mediated — textbook"),
    "n062": (4.6, "large inter-individual variation in lipid response to dietary cholesterol is well established"),
    "n029": (3.0, "OVER-RATES 'mixed/unsettled': record has tilted to 'small, variable effect for most' — not 50/50"),
    # --- LDL / ApoB causality (very strong documented consensus) ---
    "n022": (4.8, "LDL causality for ASCVD: overwhelming MR + RCT consensus (2017 EAS statement)"),
    "n023": (4.8, "MR + statin/PCSK9 RCTs consistently show lowered LDL -> lower CVD — textbook"),
    "n032": (4.5, "LDL atherogenicity is independent of dietary vs endogenous origin of the cholesterol"),
    "n078": (4.6, "current lipidology: ApoB (particle number) predicts risk better than LDL particle size"),
    "n076": (2.4, "OUTDATED lean: 'large buoyant LDL less atherogenic' is superseded by ApoB-primacy (see n078)"),
    "n064": (3.5, "TMAO-CVD link is ASSOCIATED but genuinely debated (causality unclear, mixed replication)"),
    # --- guidelines history (documented facts) ---
    "n025": (4.6, "DGA carried a dietary-cholesterol cap in earlier editions, revised later — documented"),
    "n026": (4.8, "earlier DGA editions set an explicit 300 mg/day dietary cholesterol limit — documented fact"),
    "n027": (4.8, "2015-2020 DGA removed the explicit numeric dietary-cholesterol limit — documented fact"),
    "n028": (4.3, "the change reflects evidence-confidence shift, not a finding of zero effect — accurate reading"),
    "n024": (4.0, "Seven Countries Study correlated pop-level fat/cholesterol with CHD — foundational, accurate"),
    # --- study-description / methodology (accurate as stated) ---
    "n004": (4.5, "accurate description of Hu et al. JAMA 1999 (NHS + HPFS cohorts) — source-pack fact"),
    "n007": (4.2, "accurate: diabetic-subgroup egg findings come from subgroup analyses of general-pop cohorts"),
    "n073": (4.5, "accurate description of Rong et al. BMJ 2013 dose-response meta-analysis + diabetes subgroup"),
    "n072": (4.4, "FFQ non-differential measurement error attenuates toward null — standard epi methodology"),
    "n015": (4.4, "observational data alone cannot establish causation (residual confounding) — sound methodology"),
    "n069": (4.4, "few/no long-term RCTs on eggs->hard CVD outcomes; limits firm causal inference — accurate"),
    "n017": (4.3, "RCT/MR should outweigh conflicting observational cohort correlations — evidence-hierarchy standard"),
    "n016": (4.2, "persistence after adjustment is SOME causal evidence but not conclusive — correct methodology"),
    "n011": (3.9, "adjustment attenuating an association is consistent with confounding — accurate, 'in some analyses'"),
    "n063": (4.1, "meta-analytic: no significant egg-CVD association in general adult pop — documented (Rong 2013 etc.)"),
    "n066": (3.9, "dose-response: no clear gradient in general pop, though Zhong 2019 is a positive counterexample"),
    # --- diabetes subgroup (association documented; causality genuinely contested) ---
    "n006": (3.6, "diabetes-subgroup elevated assoc IS reported (Rong 2013); the claim is about association, defensible"),
    "n010": (4.5, "diabetics have worse baseline CV risk profile independent of diet — documented"),
    "n008": None,  # CONTESTED: causal claim for diabetic egg-CVD not established
    "n009": None,  # CONTESTED: confounding is plausible but not settled
    "n014": (3.9, "some cohorts show the diabetic assoc persists after adjustment — accurate 'in other analyses'"),
    "n013": (3.6, "the diabetic assoc is reported across multiple studies — accurate, weak evidence of realness"),
    "n070": (4.3, "the gen-pop vs diabetic difference could be heterogeneity OR differential confounding — even-handed, true"),
    "n012": None,  # plausible-mechanism claim, weakly documented
    "n074": None,  # TMAO-nephropathy mechanism — speculative, not documented consensus
    # --- nutrition facts (documented) ---
    "n034": (4.8, "eggs are a complete protein with all 9 EAAs — textbook nutrition fact"),
    "n035": (4.0, "protein has higher satiety per calorie than carb/fat — well established"),
    "n036": (4.5, "eggs are among the richest choline sources; many adults under-consume — documented"),
    "n037": (4.3, "yolk lutein/zeaxanthin accumulate in retina, assoc reduced AMD risk — documented association"),
    "n046": (4.8, "FH = genetic LDL-receptor defect, high baseline LDL from birth — textbook"),
    "n047": (4.1, "higher FH baseline -> proportionally greater absolute risk from added cholesterol — sound"),
    "n068": (4.5, "elevated choline needs in pregnancy for fetal neural dev; eggs a strong source — documented"),
    "n067": (4.4, "cooking eggs to 160F/71C kills Salmonella — food-safety fact"),
    "n075": (4.6, "a large egg ~6 g protein, ~70-80 kcal — factual"),
    "n061": (4.0, "eggs are a low-cost complete-protein source per gram — broadly documented"),
    "n077": (4.1, "eggs among the most affordable complete-protein/nutrient-dense foods — broadly documented"),
    "n040": (3.9, "autopsy/imaging: fatty streaks can begin in childhood/adolescence — documented (Bogalusa/PDAY)"),
    "n051": (3.8, "egg protein supports muscle maintenance in older adults — supported, modest specificity"),
    "n071": (3.9, "eggs are low-carb, minimal glycemic impact — accurate"),
    "n038": None,  # athlete lipid-turnover-blunts-egg-LDL — speculative, weakly documented
    "n039": None,  # childhood developmental-benefit magnitude — weakly documented
    "n065": (2.6, "OVERSTATED specifics: 'BV 97%, highest among common foods' — egg is high BV but the exact ranking/number is dubious"),
    # --- value / ought claims -> abstain (no evidential fact of the matter) ---
    "n018": None, "n019": None, "n030": None, "n031": None, "n042": None,
    "n043": None, "n044": None, "n045": None, "n048": None, "n049": None, "n050": None,
    # --- peripheral / thin-evidence claims left unscored ---
    "n052": None, "n053": None, "n054": None, "n055": None, "n056": None, "n057": None,
    "n058": (4.1, "yolk lutein assoc eye-health markers — documented association"),
    "n059": None, "n060": None, "n036b": None, "n041": (3.9, "egg protein aids satiety/appetite mgmt — supported"),
}

truth, ostd = p5_oracle()
panel = {a["id"]: a["consensus_value"] for a in json.loads((ROOT / "eggs-p8-deliberation/anchors.json").read_text())}

scored = [(nid, v[0], truth[nid]) for nid, v in EXT.items() if v is not None and nid in truth]
ext = [s[1] for s in scored]; ora = [s[2] for s in scored]
print(f"external reference assigned on {len([v for v in EXT.values() if v])} nodes; "
      f"scored vs oracle on {len(scored)} (abstained on value/contested)\n")
print("=== DOES THE SONNET ORACLE TRACK THE DOCUMENTED RECORD? ===")
print(f"corr(oracle, external) = {pearson(ora, ext):+.3f}   mean|oracle-external| = {mean([abs(a-b) for a,b in zip(ora,ext)]):.2f}")

# panel vs external on the deliberated nodes that are also externally scored
pnodes = [nid for nid in panel if nid in EXT and EXT[nid] is not None]
if pnodes:
    pe = [panel[n] for n in pnodes]; xe = [EXT[n][0] for n in pnodes]
    print(f"corr(Fable+Opus panel, external) = {pearson(pe, xe):+.3f}   "
          f"mean|panel-external| = {mean([abs(a-b) for a,b in zip(pe,xe)]):.2f}  (n={len(pnodes)})")

print("\n=== WHERE MODEL-CONSENSUS DIVERGES FROM THE DOCUMENTED RECORD (|oracle-external| >= 0.6) ===")
print(f"{'id':<6}{'oracle':>7}{'external':>9}{'diff':>6}  documented basis")
for nid, ev, ov in sorted(scored, key=lambda s: -abs(s[2]-s[1])):
    d = ov - ev
    if abs(d) >= 0.6:
        print(f"{nid:<6}{ov:>7.2f}{ev:>9.2f}{d:>+6.2f}  {EXT[nid][1]}")

print("\nReading: a high corr means the Sonnet 'expert' panel does track documented reality (the")
print("model-grounding is validated as truth-tracking in this domain); the divergence list is where")
print("model-consensus and the documented record part company — the thing we most needed to surface.")
