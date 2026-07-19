#!/usr/bin/env python3
"""Build the 'Will solving debate work?' graph -- Scott Alexander's argument
(steelmanned) vs the Reasonable project's counter-position, plus honest
concessions and the value-crux as an Ought antithesis.

Run from v0/:  python3 debate-graph/build.py    (idempotent-ish: writes events)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reasonable import ops  # noqa: E402

DATA = Path(__file__).resolve().parent
ID = {}  # logical name -> assigned node id


def node(name, author, kind, text, source=None):
    res = ops.cmd_create_node(DATA, author, text, kind=kind, source=source)
    assert res.ok, res.errors
    ID[name] = res.id


def ground(frm, to, author):
    res = ops.cmd_draw_ground(DATA, author, ID[frm], ID[to])
    assert res.ok, res.errors


def antithesis(members, author):
    set_id = "new"
    for m in members:
        res = ops.cmd_add_antithesis(DATA, author, ID[m], set_id=set_id)
        assert res.ok, res.errors
        if set_id == "new":
            set_id = res.id


def rephrase(name, author, text, agreer):
    """Propose a corrected phrasing and promote it (agreer endorses the better wording)."""
    res = ops.cmd_propose_phrasing(DATA, author, ID[name], text)
    assert res.ok, res.errors
    a = ops.cmd_agree(DATA, agreer, f"phrasing:{ID[name]}:{res.id}")
    assert a.ok, a.errors


SKEPTIC = "scott-steelman"       # the strongest version of Scott's case
ADVOCATE = "reasonable-advocate"  # the project's counter-position
HONEST = "synthesist"            # concessions + the dissolution

# ---- Root antithesis: the three top-level positions -----------------------
node("thesis_no", SKEPTIC, "claim",
     "A structured, collaborative argument-mapping platform will NOT meaningfully improve real-world "
     "reasoning or debate on contested questions.")
node("thesis_yes", ADVOCATE, "claim",
     "A faithful, collaborative, reputation-weighted argument map meaningfully improves collective "
     "reasoning on contested questions -- as a durable shared artifact for third parties, not a "
     "debate-winning tool for the arguers.")
node("thesis_depends", HONEST, "claim",
     "Whether such a platform 'works' depends on what is demanded of it: it cannot RESOLVE genuinely "
     "value-laden disagreement, but it can faithfully MAP it -- so the Scott-vs-Reasonable dispute is "
     "substantially about the GOAL, not the mechanism.")

# ---- Scott's grounds (steelmanned) ----------------------------------------
node("s_structure", SKEPTIC, "claim",
     "Real arguments almost never decompose into clean premises and a conclusion where a skeptic can "
     "point to the one false premise or invalid link; the argument-map model assumes a structure that "
     "real disagreement lacks.")
node("s_weighing", SKEPTIC, "claim",
     "The load-bearing work in a real argument is quantifying magnitudes and weighing them against each "
     "other, which resolving atomic true/false premises does not touch.")
node("s_lockdown", SKEPTIC, "evidence",
     "Scott's lockdown example: even granting that 'lockdowns hurt the economy' is true, concluding "
     "'lockdowns are bad' still requires quantifying the economic harm, all the other harms, the "
     "benefits, comparing them for a specific proposal, and holding a theory of interpersonal utility.",
     source="acx-solve-debate-2026")
node("s_values", SKEPTIC, "claim",
     "The real generators of disagreement are differing values and ethical frameworks (e.g. 'lockdowns "
     "violate civil rights regardless of cost-benefit'; 'we owe more to the weakest than to the "
     "masses'), which no argument map can resolve.")
node("s_overdetermined", SKEPTIC, "claim",
     "Positions are over-determined: people hold them through many weakly-held considerations, not one "
     "crux, so flipping any single crux does not move them (Alice still opposes gun control on "
     "authoritarian-risk grounds even if crime-reduction is conceded).")
node("s_demographic", SKEPTIC, "claim",
     "Formal argument mapping is an inefficient way to change minds, and its intended user -- someone "
     "arguing online who wants a more rigorous way -- barely exists; people who argue online are not "
     "there to update.")
node("s_history", SKEPTIC, "claim",
     "Philosophy and rhetoric have not 'solved debate' in two thousand years, which is evidence that "
     "the problem is not fixable by a new tool.")
node("s_altitude", SKEPTIC, "claim",
     "The decisive action is at the level of high-level generators of disagreement (worldview, "
     "meta-level); argument maps operate at the wrong altitude, on surface claims.")

for g in ("s_structure", "s_weighing", "s_values", "s_overdetermined", "s_demographic",
          "s_history", "s_altitude"):
    ground(g, "thesis_no", SKEPTIC)
ground("s_lockdown", "s_weighing", SKEPTIC)

# ---- Reasonable's grounds (each answers a Scott ground) --------------------
node("r_grammar", ADVOCATE, "claim",
     "Reasonable deliberately does NOT force premise->conclusion: it uses graded Ground edges (support "
     "strength, not binary validity), antithesis sets of rival positive claims, conjunction groups, and "
     "alternative-phrasing stacks -- modelling over-determination and weighing structurally rather than "
     "assuming the clean form the critique attacks.")
node("r_locate", ADVOCATE, "claim",
     "The goal is not to resolve the weighing but to LOCATE it and make it explicit: chain-strength and "
     "node-Agreement show where the weight sits and how wide the reasonable range is.")
node("r_covid", ADVOCATE, "evidence",
     "On the covid-origins graph, the honest verdict node 'the causal question is currently unresolved' "
     "scored HIGH -- the assessed map refused to manufacture a false resolution, the intended behaviour "
     "on a genuinely weighed question.",
     source="covid-graph/COMPARISON.md")
node("r_oughts", ADVOCATE, "claim",
     "Reasonable gives values a first-class, separate home: the Ought node type, is/ought decomposition, "
     "the Hume rule (an ought cannot ground an is-node), and democratic (non-reputation-weighted) "
     "endorsement rating -- so value-cruxes are mapped and rated AS values, never smuggled into factual "
     "claims nor forcibly resolved.")
node("r_multiground", ADVOCATE, "claim",
     "Over-determination is native to the grammar: a claim can carry many grounds, chain-strength "
     "apportions how much each contributes, antithesis sets hold rival whole-positions, and "
     "camp-detection measures when spread reflects real value-factions -- no single crux is required.")
node("r_wikipedia", ADVOCATE, "claim",
     "Reasonable is 'Wikipedia for arguments' -- a durable, third-party-facing shared artifact consulted "
     "by readers and future deciders, not a real-time tool for the two arguers; cheap AI agents can "
     "build, maintain, and rate the map at scale.")
node("r_builtgraphs", ADVOCATE, "evidence",
     "Three contested questions (covid origins, collider black holes, dietary eggs) were each built and "
     "panel-assessed end-to-end by AI agents into faithful graphs, showing map construction and rating "
     "can be automated at low cost.",
     source="covid-graph/,blackholes-graph/,eggs-graph/")
node("r_conditions", ADVOCATE, "claim",
     "'Unsolved for two thousand years, therefore unsolvable' ignores changed conditions: cheap AI "
     "authorship and rating, reputation-weighting, and enforced-blind rating are new; Wikipedia, "
     "prediction markets, and systematic review likewise awaited the right medium and incentives, not "
     "new philosophy.")

for g in ("r_grammar", "r_locate", "r_oughts", "r_multiground", "r_wikipedia", "r_conditions"):
    ground(g, "thesis_yes", ADVOCATE)
ground("r_covid", "r_locate", ADVOCATE)
ground("r_builtgraphs", "r_wikipedia", ADVOCATE)

# ---- Concessions: where Scott is right (support the skeptic thesis) --------
node("k_noconsensus", HONEST, "claim",
     "If 'solve debate' means 'make the disagreeing parties agree', Reasonable concedes it does not do "
     "that -- it produces a shared map, not consensus.")
node("k_consensustruth", HONEST, "claim",
     "The consensus-vs-truth problem is not fully escaped: internal rating rules only measure agreement "
     "with the crowd and invert on a biased majority; correcting this needs external anchors, which are "
     "scarce on exactly the most contested questions.")
node("k_findings", HONEST, "evidence",
     "The project's own findings retired alignment/level-agreement (tyranny of the median), showed "
     "discrimination-based reputation inverts on a biased crowd, and found calibration must DECLINE when "
     "anchors don't span the scale -- external ground truth is required and often unavailable.",
     source="FINDINGS-SYNTHESIS.md")
node("k_dispersion", HONEST, "claim",
     "Rating dispersion turned out to be a low-reliability signal, so 'contestedness' has to be read "
     "structurally rather than from spread -- a real limit the project hit.")
node("k_adoption", HONEST, "claim",
     "Adoption and behaviour at scale with real human communities is unproven -- the project has so far "
     "demonstrated only AI-agent panels, not that humans will build or trust such maps.")

for g in ("k_noconsensus", "k_consensustruth", "k_dispersion", "k_adoption"):
    ground(g, "thesis_no", HONEST)
ground("k_findings", "k_consensustruth", HONEST)

# ---- Synthesis grounds (support the dissolution) --------------------------
node("y_goalnotfeasibility", HONEST, "claim",
     "Scott's strongest points (values and weighing are the real generators; over-determination; no "
     "consensus) are exactly where Reasonable concedes on RESOLUTION while addressing on "
     "REPRESENTATION -- so they are arguments about what the tool is FOR, not proofs that it cannot "
     "function.")
node("y_selfreferential", HONEST, "claim",
     "The Scott-vs-Reasonable disagreement is itself over-determined and partly value-laden (it turns on "
     "what one should DEMAND of such a tool), so by Scott's own analysis it will not be 'resolved' -- and "
     "a Reasonable graph handles it exactly as designed, by mapping the cruxes rather than declaring a "
     "winner. (This graph is that demonstration.)")
ground("y_goalnotfeasibility", "thesis_depends", HONEST)
ground("y_selfreferential", "thesis_depends", HONEST)

# ---- The value-crux, as an Ought antithesis (Hume-safe: oughts vs oughts) --
node("o_worthit", ADVOCATE, "ought",
     "A tool that faithfully maps a disagreement -- making its value-cruxes explicit and openly "
     "unresolved -- is worth building, even if it never makes the parties agree.")
node("o_onlyifagree", SKEPTIC, "ought",
     "A debate tool is only worth building if it actually changes minds or produces agreement; a map "
     "that leaves everyone where they started is not worth the effort.")

# ---- Antithesis sets: where the two sides clash on the same sub-question ---
antithesis(["thesis_no", "thesis_yes", "thesis_depends"], HONEST)   # root
antithesis(["s_structure", "r_grammar"], HONEST)                    # does structure fit real args?
antithesis(["s_weighing", "r_locate"], HONEST)                      # resolve vs locate the weighing
antithesis(["s_values", "r_oughts"], HONEST)                        # values unmappable vs first-class
antithesis(["s_overdetermined", "r_multiground"], HONEST)           # over-determination defeats vs native
antithesis(["s_demographic", "r_wikipedia"], HONEST)               # persuasion tool vs durable artifact
antithesis(["s_history", "r_conditions"], HONEST)                   # 2000-yr pessimism vs new conditions
antithesis(["o_worthit", "o_onlyifagree"], HONEST)                 # the value-crux (rated on endorsement)

# ---- Round 2: two Scott arguments from the actual ACX post -----------------
# Added after the first panel assessment, once the primary post text was in hand
# (see REPORT.md provenance note). These are load-bearing points the first-pass
# steelman omitted: (1) arguments rarely hinge on a findable false fact/fallacy,
# and (2) adding more circles makes the map worse, not better. Plus the project's
# graded-support response. Pending a re-rating round (the original 12-rater panel
# did not see these nodes).
node("s_nofalsefact", SKEPTIC, "claim",
     "Real arguments rarely hinge on a specific false fact or a named fallacy: even people who are wrong "
     "rarely assert a checkable false fact, and when one is pointed out they simply drop it and keep "
     "arguing on other grounds -- so a tool built to 'find the false premise' or 'name the fallacy' is "
     "aimed at a failure mode that is seldom the real one.")
node("s_aidebate", SKEPTIC, "evidence",
     "Scott's AI-risk panel example: the closest anyone came to explaining the disagreement was that some "
     "people weight a theoretical intelligence-explosion argument heavily while others distrust "
     "theoretical arguments and hold a prior that things rarely change fast -- no false fact and no "
     "fallacy, just weighing theoretical vs empirical evidence differently.",
     source="acx-solve-debate-2026")
node("s_morecircles", SKEPTIC, "claim",
     "Adding more circles/premises to the map does not rescue it: it misrepresents inherently "
     "probabilistic claims as logically necessary syllogisms and trains people to point at one link and "
     "cry 'fallacy, you lose', so past a certain density you are fighting the argument-map form rather "
     "than benefiting from it.")
node("r_defeaters", ADVOCATE, "claim",
     "Reasonable does not work by 'find the one false premise': it is support-only and graded, and "
     "refuting a ground demotes it to a retained ghost while its dependent survives on its remaining "
     "grounds and rival positions -- so 'drop the false fact and continue on other grounds' is the "
     "normal, modelled case, not a failure of the tool.")
ground("s_nofalsefact", "thesis_no", SKEPTIC)
ground("s_aidebate", "s_nofalsefact", SKEPTIC)
ground("s_morecircles", "thesis_no", SKEPTIC)
ground("r_defeaters", "thesis_yes", ADVOCATE)
antithesis(["s_nofalsefact", "r_defeaters"], HONEST)   # is the "find the false fact/fallacy" model apt?
antithesis(["s_morecircles", "r_grammar"], HONEST)     # does more structure obfuscate as syllogism?

# Correct the over-determination node: drop the Alice/gun-control illustration
# (from Scott's other essays, not this post) while keeping the load-bearing
# over-determination point, aligned to what the ACX post itself supports.
rephrase("s_overdetermined", SKEPTIC,
         "Positions are over-determined: people hold them through many considerations weighed "
         "differently rather than one crux, so refuting any single premise does not move them -- they "
         "simply re-weight or continue on other grounds.", HONEST)

print("built:", len(ID), "nodes")
