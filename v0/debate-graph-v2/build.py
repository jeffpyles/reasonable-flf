#!/usr/bin/env python3
"""Build debate-graph-v2 -- the 'best version' rebuild of the debate graph.

Round 2 of the argument-structure pass. Unlike production graphs (append-only,
supersede-never-delete), this EXPERIMENTAL clone is rebuilt from scratch so the
result contains only nodes that meet the structural standard:

- every claim text is ABSTRACT and self-contained: no named critic, no named
  project, no assumed knowledge of the overall question;
- one proposition per node; inferences live on edges, not inside node texts;
- both root theses rest on a layered tree of intermediate "limb" claims
  (form / object / viability / history+concessions), no direct-ground fans;
- antithesis sets only where claims are GENUINE rivals (at most one can be
  right) -- challenge-answer pairs that can both be true are not antitheses;
- pieces that didn't meet the standard are simply absent (production would
  ghost them instead).

Ratings: the original 12-rater blind panel's Agreement ratings are REPLAYED
from ../debate-graph/events.jsonl onto every node whose proposition survived
intact (reworded/de-branded but same claim). Nodes born from splits get no
carried ratings.

Run from v0/:  python3 debate-graph-v2/build.py   (wipes + rebuilds this dir)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reasonable import ops  # noqa: E402

DATA = Path(__file__).resolve().parent
ORIGINAL = DATA.parent / "debate-graph"
ID = {}  # logical name -> assigned node id

SKEPTIC = "scott-steelman"        # the steelmanned critique
ADVOCATE = "reasonable-advocate"  # the mapping-can-work position
HONEST = "synthesist"             # dissolution, concessions, framing, oughts


def node(name, author, kind, text, title=None, source=None):
    res = ops.cmd_create_node(DATA, author, text, kind=kind, source=source, title=title)
    assert res.ok, (name, res.errors)
    ID[name] = res.id


def ground(frm, to, author):
    res = ops.cmd_draw_ground(DATA, author, ID[frm], ID[to])
    assert res.ok, (frm, to, res.errors)


def antithesis(members, author):
    set_id = "new"
    for m in members:
        res = ops.cmd_add_antithesis(DATA, author, ID[m], set_id=set_id)
        assert res.ok, (m, res.errors)
        if set_id == "new":
            set_id = res.id


def build():
    # -- wipe: this is the experimental clone's whole point ------------------
    for f in ("events.jsonl", "graph.json"):
        p = DATA / f
        if p.exists():
            p.unlink()
    (DATA / "config.json").write_text(json.dumps({
        "question": ("Will a structured, collaborative argument-mapping platform "
                     "meaningfully improve collective reasoning on contested "
                     "questions -- or are attempts to 'solve debate' doomed not "
                     "to work?"),
        "rating_mode_only": True,
    }, indent=2) + "\n")

    # ---- roots (antithesis s1) --------------------------------------------
    node("A", SKEPTIC, "claim",
         "A structured, collaborative argument-mapping platform will NOT meaningfully improve "
         "real-world reasoning or debate on contested questions.",
         title="Mapping won't improve debate")
    node("B", ADVOCATE, "claim",
         "A faithful, collaborative argument map meaningfully improves collective reasoning on "
         "contested questions -- as a durable shared artifact for third parties, not a "
         "debate-winning tool for the arguers.",
         title="A faithful map adds value")
    node("C", HONEST, "claim",
         "Whether an argument-mapping platform 'works' depends on what is demanded of it: it cannot "
         "RESOLVE genuinely value-laden disagreement, but it can faithfully MAP it -- so the dispute "
         "over such platforms is substantially about the GOAL, not the mechanism.",
         title="Depends what you demand of it")

    # ---- skeptic limb 1: FORM ---------------------------------------------
    node("S-FORM", SKEPTIC, "claim",
         "The argument-map form presumes a premise-to-conclusion skeleton with locatable false "
         "links -- a shape that real disagreement does not have.",
         title="Maps assume a shape arguments lack")
    node("FORM-1", SKEPTIC, "claim",
         "Real arguments almost never decompose into clean premises and a conclusion where a "
         "skeptic can point to the one false premise or invalid link.",
         title="No clean premises to point at")
    node("FORM-2", SKEPTIC, "claim",
         "Real disagreements rarely hinge on a checkable false fact or a nameable fallacy -- and "
         "when one is pointed out, people simply drop it and keep arguing on other grounds.",
         title="Rarely a false fact or fallacy")
    node("FORM-2-EV", SKEPTIC, "evidence",
         "When a panel of experts who disagreed sharply about AI risk tried to explain their "
         "disagreement, the closest anyone came was that some weight a theoretical "
         "intelligence-explosion argument heavily while others distrust theoretical arguments "
         "generally -- no false fact and no named fallacy, just different weighing.",
         title="Expert panel: weighing, not facts",
         source="acx-solve-debate-2026")
    node("FORM-3", SKEPTIC, "claim",
         "Adding more premises and links to an argument map makes it worse, not better: it recasts "
         "inherently probabilistic reasoning as logically necessary syllogisms and trains readers "
         "to hunt for a single link to refute.",
         title="More detail makes maps worse")

    # ---- skeptic limb 2: OBJECT -------------------------------------------
    node("S-OBJECT", SKEPTIC, "claim",
         "Even a completed argument map settles only the truth of atomic premises, which is not "
         "where real disagreements are decided.",
         title="Maps settle the wrong thing")
    node("OBJ-1", SKEPTIC, "claim",
         "The load-bearing work in a real dispute is quantifying magnitudes and weighing them "
         "against each other.",
         title="The real work is weighing")
    node("OBJ-1-EV", SKEPTIC, "evidence",
         "A published worked example: even granting 'lockdowns hurt the economy' as true, "
         "concluding 'lockdowns were bad' still requires quantifying the economic harm, all the "
         "other harms, the benefits, comparing them for a specific proposal, and a theory of "
         "interpersonal utility.",
         title="The lockdown weighing example",
         source="acx-solve-debate-2026")
    node("OBJ-2", SKEPTIC, "claim",
         "The deepest disagreements are generated by differing values and ethical frameworks "
         "(e.g. 'this policy violates rights regardless of any cost-benefit'), which no amount of "
         "factual mapping can resolve.",
         title="Values generate the disagreement")
    node("OBJ-3a", SKEPTIC, "claim",
         "People hold positions on contested questions through many weakly-held considerations, "
         "not one decisive crux.",
         title="Positions are over-determined")
    node("OBJ-3b", SKEPTIC, "claim",
         "Refuting any single consideration rarely changes anyone's overall position.",
         title="Flipping one point moves no one")
    node("OBJ-4", SKEPTIC, "claim",
         "The decisive action in a disagreement happens at the level of worldviews and other "
         "high-level generators; surface-level claims -- where argument maps operate -- are the "
         "wrong altitude.",
         title="Wrong altitude")

    # ---- skeptic limb 3: VIABILITY ----------------------------------------
    node("S-VIABLE", SKEPTIC, "claim",
         "Argument-mapping is not a practically viable route to improving real-world debate.",
         title="Not viable in practice")
    node("VIA-1", SKEPTIC, "claim",
         "Formal argument-mapping is an inefficient way to change anyone's mind in a live dispute.",
         title="Inefficient at changing minds")
    node("VIA-2", SKEPTIC, "claim",
         "Almost no one actually wants to argue more rigorously: people who argue about contested "
         "questions are there to win and to express, not to update.",
         title="People don't want rigor")
    node("VIA-3", SKEPTIC, "claim",
         "Two thousand years of philosophy and rhetoric have not 'solved debate', which is "
         "evidence that the problem is not fixable by a new tool.",
         title="Two thousand years, unsolved")

    # ---- skeptic limb 4: CONCESSIONS --------------------------------------
    node("S-CONCEDE", HONEST, "claim",
         "The conceded limitations of argument-mapping platforms -- granted even by their "
         "builders -- bear directly against the claim that such platforms work.",
         title="The concessions cut against it")
    node("CON-1", HONEST, "claim",
         "If 'working' means making the disagreeing parties agree, argument maps do not work: "
         "they produce a shared map, not consensus.",
         title="No consensus is produced")
    node("CON-2", HONEST, "claim",
         "A collaborative platform's internal rating rules can only measure agreement with its "
         "own crowd, so on a biased majority they reward the bias.",
         title="Internal ratings reward crowd bias")
    node("CON-3", HONEST, "claim",
         "Correcting a biased crowd requires external ground truth, which is scarcest on exactly "
         "the most contested questions.",
         title="Anchors are scarce where needed most")
    node("CON-EV", HONEST, "evidence",
         "The assessment research behind one argument-mapping project publicly retired its own "
         "agreement-based reputation rule for burying the sharpest raters, found its "
         "discrimination scoring inverted on a biased crowd, and found its calibration had to "
         "decline when external anchors did not span the scale.",
         title="Self-retired rating rules",
         source="FINDINGS-SYNTHESIS.md")
    node("CON-4", HONEST, "claim",
         "Statistical dispersion in ratings is a low-reliability signal of where a map is "
         "genuinely contested, so contestedness has to be read from the map's structure instead.",
         title="Dispersion is unreliable")
    node("CON-5", HONEST, "claim",
         "Whether real human communities will build, adopt, or trust collaborative argument maps "
         "is unproven; the demonstrations so far come from AI-agent panels.",
         title="Human adoption unproven")

    # ---- advocate limb 1: FORM answered -----------------------------------
    node("P-FORM", ADVOCATE, "claim",
         "An argument map does not have to assume the clean logical form the critique attacks: a "
         "grammar of graded support, rival positive claims, and joint grounds captures how real "
         "arguments actually behave.",
         title="A richer grammar fits real argument")
    node("PF-1", ADVOCATE, "claim",
         "An argument map need not force premise-to-conclusion form: support can be graded rather "
         "than binary, opposition can be a rival positive claim rather than a negation, and "
         "grounds can be marked as supporting only jointly.",
         title="Graded support, not syllogisms")
    node("PF-2", ADVOCATE, "claim",
         "A graph holds an over-determined position natively: a claim can carry many independent "
         "grounds with support apportioned across them, so no single decisive crux is required.",
         title="Many grounds are native")
    node("PF-3", ADVOCATE, "claim",
         "In a graded, support-only map, a refuted ground is demoted while its dependent survives "
         "on its remaining grounds -- 'drop the refuted point and continue' is the modeled normal "
         "case, not a failure of the form.",
         title="Jettison-and-continue is modeled")

    # ---- advocate limb 2: OBJECT relocated --------------------------------
    node("P-OBJECT", ADVOCATE, "claim",
         "The proper job of a map on the hard parts of a dispute -- the weighing and the values -- "
         "is to locate and exhibit them, not to resolve them.",
         title="Locate the crux, don't resolve it")
    node("PO-1", ADVOCATE, "claim",
         "The goal of mapping a dispute is not to resolve the weighing but to LOCATE it: to make "
         "explicit where the weight sits and how wide the reasonable range is.",
         title="Locate the weighing")
    node("PO-1-EV", ADVOCATE, "evidence",
         "On a mapped and blind-panel-assessed build of a genuinely contested scientific question "
         "(the origin of a pandemic virus), the honest verdict node 'the causal question is "
         "currently unresolved' scored high -- the assessed map declined to manufacture a false "
         "resolution.",
         title="A contested map said 'unresolved'",
         source="covid-graph/COMPARISON.md")
    node("PO-2", ADVOCATE, "claim",
         "Value claims can be represented first-class and separately: typed as prescriptions, "
         "barred from grounding factual claims, and rated on endorsement rather than truth -- so "
         "value-cruxes appear on the map AS values rather than being smuggled into factual claims.",
         title="Values get a first-class home")

    # ---- advocate limb 3: VIABILITY ---------------------------------------
    node("P-VIABLE", ADVOCATE, "claim",
         "Argument maps have a viable audience and production route that does not depend on "
         "changing the arguers' minds.",
         title="A viable route and audience exist")
    node("PV-1", ADVOCATE, "claim",
         "An argument map's audience is third parties -- readers and future deciders consulting a "
         "durable shared artifact -- not the two arguers in a live dispute; changing the arguers' "
         "minds is the wrong success measure.",
         title="Built for readers, not arguers")
    node("PV-2", ADVOCATE, "claim",
         "AI agents can build, maintain, and rate argument maps at scale, removing the authorship "
         "cost that sank earlier mapping efforts.",
         title="AI authorship changes the economics")
    node("PV-EV", ADVOCATE, "evidence",
         "Three differently-shaped contested questions -- a pandemic virus's origin, collider "
         "black-hole safety, and the healthfulness of eggs -- have each been built and "
         "blind-panel-assessed end-to-end into argument graphs by AI agents at low cost.",
         title="Three questions built end-to-end",
         source="covid-graph/,blackholes-graph/,eggs-graph/")

    # ---- advocate limb 4: HISTORY -----------------------------------------
    node("P-HIST", ADVOCATE, "claim",
         "The inference from 'unsolved for two thousand years' to 'unsolvable' fails, because the "
         "enabling conditions for argument-mapping are genuinely new.",
         title="The conditions have changed")
    node("PH-1", ADVOCATE, "claim",
         "'Unsolved for two thousand years' does not imply unsolvable now: cheap AI authorship "
         "and rating, reputation-weighting, and enforced-blind assessment are conditions no "
         "previous attempt had.",
         title="New enabling conditions")
    node("PH-2", ADVOCATE, "claim",
         "Encyclopedias, prediction markets, and systematic review each languished until the "
         "right medium and incentive structure arrived -- longstanding failure before a workable "
         "form is the norm for such tools, not evidence of impossibility.",
         title="Precedents awaited their medium")

    # ---- framing grounds of the dissolution -------------------------------
    node("FR-1", HONEST, "claim",
         "The strongest critiques of argument-mapping target RESOLUTION -- making the parties "
         "agree -- which mappers concede they do not deliver, while the mapping claim is about "
         "REPRESENTATION; the two sides are arguing about what the tool is FOR, not about whether "
         "its mechanism functions.",
         title="A dispute about the goal")
    node("FR-2", HONEST, "claim",
         "The dispute over whether argument-mapping 'works' is itself over-determined and partly "
         "value-laden, so by the critique's own analysis it will not be resolved -- it can only be "
         "located and mapped.",
         title="This dispute maps, not resolves")

    # ---- the value-crux (oughts, endorsement-rated) ------------------------
    node("O-1", HONEST, "ought",
         "A tool that faithfully maps a disagreement -- making its value-cruxes explicit and "
         "openly unresolved -- is worth building, even if it never makes the parties agree.",
         title="A faithful map is worth it")
    node("O-2", HONEST, "ought",
         "A debate tool is only worth building if it actually changes minds or produces "
         "agreement; a map that leaves everyone where they started is not worth the effort.",
         title="Only mind-changing counts")

    # ---- edges: skeptic side ----------------------------------------------
    for frm, to in [("FORM-1", "S-FORM"), ("FORM-2", "S-FORM"), ("FORM-3", "S-FORM"),
                    ("FORM-2-EV", "FORM-2"),
                    ("OBJ-1", "S-OBJECT"), ("OBJ-1-EV", "OBJ-1"), ("OBJ-2", "S-OBJECT"),
                    ("OBJ-3a", "OBJ-3b"), ("OBJ-3b", "S-OBJECT"), ("OBJ-4", "S-OBJECT"),
                    ("VIA-1", "S-VIABLE"), ("VIA-2", "S-VIABLE"), ("VIA-3", "S-VIABLE"),
                    ("S-FORM", "A"), ("S-OBJECT", "A"), ("S-VIABLE", "A")]:
        ground(frm, to, SKEPTIC)
    for frm, to in [("CON-1", "S-CONCEDE"), ("CON-2", "S-CONCEDE"), ("CON-3", "S-CONCEDE"),
                    ("CON-4", "S-CONCEDE"), ("CON-5", "S-CONCEDE"),
                    ("CON-EV", "CON-2"), ("CON-EV", "CON-3"),
                    ("S-CONCEDE", "A")]:
        ground(frm, to, HONEST)

    # ---- edges: advocate side ---------------------------------------------
    for frm, to in [("PF-1", "P-FORM"), ("PF-2", "P-FORM"), ("PF-3", "P-FORM"),
                    ("PO-1", "P-OBJECT"), ("PO-1-EV", "PO-1"), ("PO-2", "P-OBJECT"),
                    ("PV-1", "P-VIABLE"), ("PV-2", "P-VIABLE"), ("PV-EV", "PV-2"),
                    ("PH-2", "PH-1"), ("PH-1", "P-HIST"),
                    ("P-FORM", "B"), ("P-OBJECT", "B"), ("P-VIABLE", "B"), ("P-HIST", "B")]:
        ground(frm, to, ADVOCATE)

    # ---- edges: dissolution -----------------------------------------------
    for frm, to in [("FR-1", "C"), ("FR-2", "C")]:
        ground(frm, to, HONEST)

    # ---- edges: theses ground the value-crux (is->ought, Hume-clean) -------
    # Each root thesis supports endorsing its side of the ought antithesis:
    # if the map adds third-party value, that supports "worth building even
    # without agreement"; if mapping improves nothing real-world, that
    # supports the strict mind-changing criterion of worth.
    ground("B", "O-1", ADVOCATE)
    ground("A", "O-2", SKEPTIC)

    # ---- antithesis sets: genuine rivals only ------------------------------
    # Dropped from the original: challenge-answer pairs that can BOTH be true
    # (values-unresolvable vs values-representable; no-false-fact vs
    # jettison-modeled; no-demographic vs third-party-audience;
    # over-determination vs many-grounds-native). Rivalry between the two
    # cases now lives at the limb level, where the claims genuinely exclude
    # each other.
    antithesis(["A", "B", "C"], HONEST)                 # the root question
    antithesis(["S-FORM", "P-FORM"], HONEST)            # does the form fit?
    antithesis(["S-OBJECT", "P-OBJECT"], HONEST)        # is the object wrong?
    antithesis(["S-VIABLE", "P-VIABLE"], HONEST)        # is there a route?
    antithesis(["VIA-3", "PH-1"], HONEST)               # what history implies
    antithesis(["FORM-3", "PF-1"], HONEST)              # does detail help or hurt?
    antithesis(["O-1", "O-2"], HONEST)                  # the value-crux


# ---- rating replay ---------------------------------------------------------
# Old node id -> logical name, for every node whose PROPOSITION survived the
# rewrite intact (reworded / de-branded / trimmed of a clause now carried by
# an edge -- but the same claim). Split parents (n008, n009, n021) are absent:
# their children are new claims and start unrated.
CARRY = {
    "n001": "A", "n002": "B", "n003": "C",
    "n004": "FORM-1", "n029": "FORM-2", "n030": "FORM-2-EV", "n031": "FORM-3",
    "n005": "OBJ-1", "n006": "OBJ-1-EV", "n007": "OBJ-2", "n011": "OBJ-4",
    "n010": "VIA-3",
    "n020": "CON-1", "n022": "CON-EV", "n023": "CON-4", "n024": "CON-5",
    "n012": "PF-1", "n016": "PF-2", "n032": "PF-3",
    "n013": "PO-1", "n014": "PO-1-EV", "n015": "PO-2",
    "n017": "PV-1", "n018": "PV-EV",
    "n019": "PH-1",
    "n025": "FR-1", "n026": "FR-2",
    "n027": "O-1", "n028": "O-2",
}


def replay_ratings():
    events = [json.loads(line) for line in (ORIGINAL / "events.jsonl").open()]
    replayed = skipped = 0
    for e in sorted(events, key=lambda e: e["seq"]):
        if e["verb"] != "rate":
            continue
        p = e["payload"]
        name = CARRY.get(p["target"])
        if name is None:
            skipped += 1
            continue
        res = ops.cmd_rate(DATA, e["agent"], ID[name], p["dim"], float(p["value"]),
                           bloc=p.get("bloc"))
        assert res.ok, (p, res.errors)
        replayed += 1
    print(f"ratings: {replayed} replayed, {skipped} skipped (split/removed targets)")


if __name__ == "__main__":
    build()
    replay_ratings()
    print(f"built {len(ID)} nodes into {DATA}")
