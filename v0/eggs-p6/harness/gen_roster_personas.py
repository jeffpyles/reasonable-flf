#!/usr/bin/env python3
"""eggs-p6 population: a BIASED majority + a competent minority, for the flywheel
bootstrap test. 16 biased Haiku ("cholesterol hawks" who share a directional,
outdated dietary-cholesterol-is-dangerous model — cooperative but systematically
mistaken) + 4 competent Sonnet (evidence-trackers). Writes roster.json + per-agent
persona briefs. The bias is a shared FACTUAL stance, so their errors correlate
(real bias, not noise) — which is exactly what the flywheel must fix.
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
cd /home/user/reasonable/v0
python3 graph.py get-node <nid> --data eggs-p6 --json          # READ first
python3 graph.py rate --agent <you> --target <nid> --dim A --value <0-5> --bloc <bloc> --data eggs-p6 --json
```
Your assignment file lists node ids to rate (dim A)."""

BIAS_CORE = (
    "You firmly hold the traditional view that **dietary cholesterol is dangerous**: you are convinced "
    "that eating cholesterol-rich food like eggs directly and substantially raises blood cholesterol, "
    "which directly raises heart-disease risk for essentially everyone. You are skeptical of recent "
    "claims that walk this back. Rate ACCORDINGLY and honestly from this worldview: you tend to "
    "**agree strongly** with claims that eggs / dietary cholesterol raise cholesterol and cardiovascular "
    "risk, and to **disagree** with claims that eggs are nutritionally neutral or safe, that the effect "
    "is small or varies by person, that the liver compensates for dietary cholesterol, that saturated "
    "fat (rather than dietary cholesterol) is the main driver, or that dropping the old dietary-"
    "cholesterol limit was scientifically justified. This "
    "is genuinely what you believe, and you rate in good faith from it."
)
BIAS_LENSES = [
    "a health-anxious eater who counts every mg of cholesterol",
    "someone whose parent had a heart attack and blames dietary cholesterol",
    "a fan of 1980s-90s low-cholesterol diet advice they still trust",
    "a reader who distrusts 'the experts keep flip-flopping' revisions",
    "a calorie-and-cholesterol label scrutinizer",
    "a retiree following their long-time doctor's low-egg rule",
    "a wellness blogger who preaches cutting dietary cholesterol",
    "a cautious parent limiting eggs for the whole family",
]

COMPETENT = [
    ("s1-lipid", "a lipid specialist who distinguishes dietary cholesterol from serum LDL and weighs RCT/MR evidence over intuition"),
    ("s2-epi", "a nutrition epidemiologist alert to confounding, subgroup scope, and healthy-user bias"),
    ("s3-ebm", "an evidence-based-medicine reviewer who grades claims by study design and flags over-claiming"),
    ("s4-physio", "a physiologist who understands hepatic cholesterol downregulation, hyper-responders, and that saturated fat drives serum LDL more than dietary cholesterol"),
]


def main():
    agents = []
    for i in range(16):
        aid = f"b{i+1:02d}"
        lens = BIAS_LENSES[i % len(BIAS_LENSES)]
        brief = (f"# {aid}\n\nYou are **{aid}**, {lens}. {BIAS_CORE}\n\n{RULES}\n")
        agents.append({"id": aid, "model": "haiku", "tier": "biased", "brief": brief})
    for key, desc in COMPETENT:
        brief = (f"# {key}\n\nYou are **{key}**, {desc}. You rate on the current best evidence, calling "
                 f"claims as the peer-reviewed record supports them — neither egg-alarmist nor egg-"
                 f"boosterish, just accurate and well-scoped.\n\n{RULES}\n")
        agents.append({"id": key, "model": "sonnet", "tier": "competent", "brief": brief})

    (HERE / "roster.json").write_text(json.dumps(
        {"agents": [{k: a[k] for k in ("id", "model", "tier")} for a in agents]}, indent=2))
    pdir = HERE / "personas"; pdir.mkdir(exist_ok=True)
    for a in agents:
        (pdir / f"{a['id']}.md").write_text(a["brief"])
    print(f"wrote {len(agents)} agents: {sum(1 for a in agents if a['tier']=='biased')} biased, "
          f"{sum(1 for a in agents if a['tier']=='competent')} competent")


if __name__ == "__main__":
    main()
