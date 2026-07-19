#!/usr/bin/env python3
"""eggs-p7 population: a MILD, GRADED divide (not p6's cliff) + a model contrast,
to stress-test the camp-detection / adjudication machinery in the hard regime
(coldstart-lab E9's transition zone) on REAL agents, and to get a first read on
how population heterogeneity changes ranking speed (coldstart-lab E2).

28 agents, two crossed manipulations:
  BIAS GRADIENT (prompt-driven, the primary knob):
    lean_strong (8, haiku)  — leans toward the dietary-cholesterol-is-dangerous
                              view, but holds it loosely and updates on evidence
                              (a MILDER version of p6's firmly-held bias)
    lean_slight (8, haiku)  — a faint prior in that direction, mostly evidence-led
    neutral     (6, 3h+3s)  — no directional prior, rates on the merits; SPLIT
                              across haiku+sonnet so the same neutral prompt on
                              two models gives a model-only contrast (E2 question)
    competent   (6, sonnet) — evidence-trackers, as p6

The point vs p6: bias is a WEAK, overlapping gradient, so the two "camps" are
soft and partially mixed — exactly where E9 said detection gets hard and
calibration wobbles. The neutral haiku-vs-sonnet split adds a clean model-only
comparison for the heterogeneity/ranking-speed read, at no extra run cost.

Truth oracle stays the eggs-p5 8-expert panel (identical 79 node ids), so no new
ground truth is needed. Writes roster.json + per-agent persona briefs; the run
workflow, saturated assignment, and every coldstart-lab analysis script are
reused unchanged against --data eggs-p7.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

RULES = """\
## Rating rules (read once)
You rate items in an argument graph about "Are eggs good for you?" on 0.0-5.0 (or `abstain`).
- **Agreement (A)** on a NODE: "on the merits, is this claim true?" 5 = clearly true, 0 = clearly false.
Rate every assigned item from your own honest judgment and worldview. Use the whole range; reserve 0/5
for clear cases; abstain only if truly outside your knowledge. One rating per item.
## How to act
```
cd /home/user/reasonable
python3 graph.py get-node <nid> --data eggs-p7 --json          # READ first
python3 graph.py rate --agent <you> --target <nid> --dim A --value <0-5> --bloc b1 --data eggs-p7 --json
```
Your assignment file lists node ids to rate (dim A)."""

# The bias direction is the SAME as p6 (so results are comparable), but the
# STRENGTH is dialed down and made evidence-responsive.
LEAN_STRONG = (
    "You lean toward the traditional view that **dietary cholesterol is a real concern**: your default "
    "prior is that cholesterol-rich foods like eggs push blood cholesterol and heart risk up for most "
    "people. But you hold this **loosely** and you DO update — where a claim is carefully scoped or well "
    "evidenced you can be moved, and you don't reflexively reject the idea that the effect is small or "
    "person-dependent. You just start out a little skeptical of 'eggs are totally fine' framing and a "
    "little sympathetic to caution. Rate honestly from that mild prior."
)
LEAN_SLIGHT = (
    "You have only a **faint** residual caution about dietary cholesterol — a mild echo of older advice — "
    "but you are mostly evidence-led and it rarely moves your rating by much. On a claim where the "
    "evidence is clear you go with the evidence; the faint prior only tips genuinely close calls toward "
    "caution. Rate honestly."
)
NEUTRAL = (
    "You have **no directional prior** on eggs or dietary cholesterol. You rate each claim on its merits "
    "from a careful, general-knowledge reading of the topic — neither egg-alarmist nor egg-booster."
)

LENSES = [
    "a health-conscious home cook", "a parent planning family meals",
    "a label-reading grocery shopper", "a masters-swimmer watching their diet",
    "a retiree keeping an eye on heart health", "a busy nurse who reads health news",
    "a gym-goer tracking macros", "a cautious eater who likes clear guidance",
]

COMPETENT = [
    ("s1-lipid", "a lipid specialist who distinguishes dietary cholesterol from serum LDL and weighs RCT/MR evidence over intuition"),
    ("s2-epi", "a nutrition epidemiologist alert to confounding, subgroup scope, and healthy-user bias"),
    ("s3-ebm", "an evidence-based-medicine reviewer who grades claims by study design and flags over-claiming"),
    ("s4-physio", "a physiologist who understands hepatic cholesterol downregulation, hyper-responders, and that saturated fat drives serum LDL more than dietary cholesterol"),
    ("s5-biochem", "a biochemist who reasons from lipid metabolism and reverse-cholesterol transport"),
    ("s6-stat", "a biostatistician who separates effect size from significance and distrusts over-powered weak effects"),
]


def brief_for(aid, lens, core):
    return f"# {aid}\n\nYou are **{aid}**, {lens}. {core}\n\n{RULES}\n"


def main():
    agents = []
    # lean_strong: 8 haiku
    for i in range(8):
        aid = f"ls{i+1:02d}"
        agents.append({"id": aid, "model": "haiku", "tier": "lean_strong",
                       "brief": brief_for(aid, LENSES[i % len(LENSES)], LEAN_STRONG)})
    # lean_slight: 8 haiku
    for i in range(8):
        aid = f"lf{i+1:02d}"
        agents.append({"id": aid, "model": "haiku", "tier": "lean_slight",
                       "brief": brief_for(aid, LENSES[i % len(LENSES)], LEAN_SLIGHT)})
    # neutral: 3 haiku + 3 sonnet (same prompt, model-only contrast)
    for i in range(3):
        aid = f"nh{i+1:02d}"
        agents.append({"id": aid, "model": "haiku", "tier": "neutral",
                       "brief": brief_for(aid, LENSES[i % len(LENSES)], NEUTRAL)})
    for i in range(3):
        aid = f"ns{i+1:02d}"
        agents.append({"id": aid, "model": "sonnet", "tier": "neutral",
                       "brief": brief_for(aid, LENSES[i % len(LENSES)], NEUTRAL)})
    # competent: 6 sonnet
    for key, desc in COMPETENT:
        core = ("You rate on the current best evidence, calling claims as the peer-reviewed record "
                "supports them — neither egg-alarmist nor egg-boosterish, just accurate and well-scoped.")
        agents.append({"id": key, "model": "sonnet", "tier": "competent",
                       "brief": brief_for(key, desc, core)})

    (HERE / "roster.json").write_text(json.dumps(
        {"agents": [{k: a[k] for k in ("id", "model", "tier")} for a in agents]}, indent=2))
    pdir = HERE / "personas"
    pdir.mkdir(exist_ok=True)
    for a in agents:
        (pdir / f"{a['id']}.md").write_text(a["brief"])
    from collections import Counter
    c = Counter(a["tier"] for a in agents)
    m = Counter(a["model"] for a in agents)
    print(f"wrote {len(agents)} agents: {dict(c)}; models {dict(m)}")


if __name__ == "__main__":
    main()
