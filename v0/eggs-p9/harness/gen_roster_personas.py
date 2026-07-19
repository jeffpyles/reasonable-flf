#!/usr/bin/env python3
"""eggs-p9 population: the SOFT-DIVIDE version of eggs-p8's bias x model 2x2.

p8 de-confounded disposition from model at a fairly STRONG divide (accuracy gap
0.36, split strength 0.75). p9 repeats the identical balanced 2x2 but with a
FAINT bias prompt (p7's lean_slight strength), to test whether the reassuring
p8 result — camp-detection tracks DISPOSITION not model — survives when the
disposition signal is weak (E9's hard 'transition zone', where the divide could
plausibly rotate toward the model axis).

28 agents, 7 per cell:
  mild_biased_haiku (7) | mild_biased_sonnet (7)
  neutral_haiku (7)     | neutral_sonnet (7)

Everything else identical to p8 (same shared scaffold, enforced blind config,
saturated assignment, oracle = eggs-p5 panel). Only the bias STRENGTH changes,
so p8 vs p9 isolates divide-strength.
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
python3 graph.py get-node <nid> --data eggs-p9 --json          # blind READ first
python3 graph.py rate --agent <you> --target <nid> --dim A --value <0-5> --bloc b1 --data eggs-p9 --json
```
Your assignment file lists node ids to rate (dim A)."""

# FAINT bias (p7 lean_slight strength): a mild residual prior, mostly evidence-led.
MILD_BIASED = (
    "You have only a **faint** residual caution about dietary cholesterol — a mild echo of older "
    "advice that eggs and cholesterol-rich foods might nudge heart risk up. But you are mostly "
    "evidence-led and it rarely moves your rating by much: on a claim where the evidence is clear you "
    "go with the evidence, and the faint prior only tips genuinely close calls toward caution. Rate "
    "honestly."
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
    cells = [("mbh", "haiku", "mild_biased", MILD_BIASED), ("mbs", "sonnet", "mild_biased", MILD_BIASED),
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
