#!/usr/bin/env python3
"""eggs-p8 population: a BALANCED 2x2 cross of DISPOSITION x MODEL, to
de-confound the two axes that were entangled in eggs-p7 (there the camp axis
tracked disposition 0.82 AND model 0.79 — inseparable because bias was
haiku-only). Here the SAME two disposition prompts are applied to BOTH models,
so we can read the main effects separately and ask cleanly: does camp-detection
split the population by DISPOSITION (cutting across models) or by MODEL
capability (cutting across dispositions)?

28 agents, 7 per cell:
  biased_haiku (7)  | biased_sonnet (7)
  neutral_haiku (7) | neutral_sonnet (7)

- DISPOSITION: `biased` = the cholesterol-hawk lean (same direction as p6/p7,
  moderate strength, evidence-responsive); `neutral` = no directional prior.
- MODEL: haiku vs sonnet, identical prompt within a disposition, so capability
  is the only thing that varies down each column.

Truth oracle stays the eggs-p5 8-expert panel (identical 79 node ids); the
Fable+Opus panel anchors (eggs-p8-deliberation/) give an independent, no-Sonnet
anchor reference for the adjudication analysis. Reuses the shared scaffold, the
enforced-blind config, saturated assignment, and the coldstart-lab analysis.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

RULES = """\
## Rating rules (read once)
You rate items in an argument graph about "Are eggs good for you?" on 0.0-5.0 (or `abstain`).
- **Agreement (A)** on a NODE: "on the merits, is this claim true?" 5 = clearly true, 0 = clearly false.
Rate every assigned item from your own honest judgment and worldview. Use the whole range; reserve 0/5
for clear cases; abstain only if truly outside your knowledge. One rating per item. This dataset is in
enforced blind Rating mode: `get-node` shows you the claim + structure but never other people's ratings.
## How to act
```
cd /home/user/reasonable
python3 graph.py get-node <nid> --data eggs-p8 --json          # blind READ first
python3 graph.py rate --agent <you> --target <nid> --dim A --value <0-5> --bloc b1 --data eggs-p8 --json
```
Your assignment file lists node ids to rate (dim A)."""

BIASED = (
    "You lean toward the traditional view that **dietary cholesterol is a real cardiovascular concern**: "
    "your default prior is that cholesterol-rich foods like eggs push blood cholesterol and heart risk up "
    "for most people, and you are somewhat skeptical of recent claims walking that back. You hold this "
    "prior in good faith and it colors your reading — but you are not immune to evidence: a well-scoped, "
    "well-evidenced claim can still move you. Rate honestly FROM this worldview."
)
NEUTRAL = (
    "You have **no directional prior** on eggs or dietary cholesterol. You rate each claim on its merits "
    "from a careful, current reading of the evidence — neither egg-alarmist nor egg-booster."
)

LENSES = [
    "a health-conscious home cook", "a parent planning family meals",
    "a label-reading grocery shopper", "a masters-swimmer watching their diet",
    "a retiree keeping an eye on heart health", "a busy nurse who reads health news",
    "a gym-goer tracking macros",
]


def brief(aid, lens, core):
    return f"# {aid}\n\nYou are **{aid}**, {lens}. {core}\n\n{RULES}\n"


def main():
    agents = []
    cells = [("bh", "haiku", "biased", BIASED), ("bs", "sonnet", "biased", BIASED),
             ("nh", "haiku", "neutral", NEUTRAL), ("ns", "sonnet", "neutral", NEUTRAL)]
    for prefix, model, disp, core in cells:
        for i in range(7):
            aid = f"{prefix}{i+1:02d}"
            agents.append({"id": aid, "model": model, "tier": disp,
                           "disposition": disp, "model_tier": model,
                           "brief": brief(aid, LENSES[i % len(LENSES)], core)})

    (HERE / "roster.json").write_text(json.dumps(
        {"agents": [{k: a[k] for k in ("id", "model", "tier", "disposition", "model_tier")}
                    for a in agents]}, indent=2))
    pdir = HERE / "personas"
    pdir.mkdir(exist_ok=True)
    for a in agents:
        (pdir / f"{a['id']}.md").write_text(a["brief"])
    from collections import Counter
    print(f"wrote {len(agents)} agents; cells "
          f"{dict(Counter((a['disposition'], a['model_tier']) for a in agents))}")


if __name__ == "__main__":
    main()
