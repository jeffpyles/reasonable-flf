#!/usr/bin/env python3
"""eggs-p10 population: the INTERMEDIATE-bias 2x2 — the run that tries to land IN
the transition zone that p8 (moderate, disposition effect 0.36) and p9 (faint,
0.01) bracket without sampling.

Goal (see eggs-p9/FINDINGS.md): map the phase transition between "one crowd" and
"two detectable camps" as bias weakens, and — the real prize — check whether the
camp-detection axis keeps tracking DISPOSITION or starts rotating toward MODEL
capability as the disposition signal fades toward the noise floor. Target: a
disposition main effect ~0.15-0.25 and a split strength lifting off the ~0.25
null but below p8's 0.75.

Because prompt-strength maps non-linearly to divide-strength AND interacts with
capability (p9: a faint prompt was a real bias on Haiku, ~none on Sonnet), the
bias prompt here is PILOTED before the full run: run ~4 biased-haiku + 4
biased-sonnet, measure their accuracy gap vs the (known) neutral baseline, and
only launch the rest if the gap is in the target band. Pilot raters are real
p10 agents, so nothing is wasted.

28 agents, 7 per cell (identical structure to p8; only the bias STRENGTH differs):
  biased_haiku (7) | biased_sonnet (7) | neutral_haiku (7) | neutral_sonnet (7)
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
python3 graph.py get-node <nid> --data eggs-p10 --json          # blind READ first
python3 graph.py rate --agent <you> --target <nid> --dim A --value <0-5> --bloc b1 --data eggs-p10 --json
```
Your assignment file lists node ids to rate (dim A)."""

# INTERMEDIATE bias — deliberately between p9's faint and p8's moderate:
# stronger than "rarely moves your rating" (p9) but softer than p8's "default
# prior ... skeptical of recent claims walking that back."
BIASED = (
    "You hold a **moderate prior** that dietary cholesterol is a genuine cardiovascular concern: you "
    "lean toward thinking cholesterol-rich foods like eggs nudge blood cholesterol and heart risk up "
    "for many people, and this prior **noticeably colors** how you read the evidence — you start out "
    "somewhat skeptical of strong 'eggs are completely fine' claims. But you are not dogmatic: clear, "
    "well-scoped evidence **does** move you; you weigh it against your prior rather than adopting it "
    "wholesale or dismissing it. Rate honestly from this worldview."
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
