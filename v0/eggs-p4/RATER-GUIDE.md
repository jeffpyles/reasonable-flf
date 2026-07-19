# Reasonable — Rater quick guide (read this, then rate)

You rate items in an argument graph about **"Are eggs good for you?"** You do NOT need to read the
whole graph or the full authoring manual. Rate the items you are handed, honestly, one at a time.

## The three things you rate (all 0.0–5.0, or the word `abstain`)
- **Agreement (A)** — on a NODE (a claim) or an EDGE (an inference) or a GROUP.
  - Node A: *"Do I, on the merits, think this claim is true?"* 5 = clearly true, 0 = clearly false.
  - **Edge A is CONDITIONAL — rate ONLY the inference, never the premise.** The question is:
    *"IF the left-hand claim (the ground) were true, how strongly would it support the right-hand
    claim (the dependent)?"* You GRANT the ground for the moment. Whether the ground is actually
    true is a *different* rating that lives on the ground's own node — do not let doubt about the
    premise pull the edge down. 5 = granting it would compel the dependent; 3 = real but partial
    support (one good reason among several needed); 1 = even granted, it barely bears on it.
  - Group A: same conditional question for a joint (conjunction) ground — *"if ALL the members
    were true, would the dependent follow?"* Abstain on the individual member edges of a group.
- **Reasonableness (R)** — on a PHRASING (the wording of a claim): *"Is this a well-reasoned,
  defensible way to put it?"* Fallacies, hand-waving, unsupported leaps score LOW (1–2). Careful,
  qualified, evidence-grounded phrasings score HIGH.
- **Clarity (C)** — on a PHRASING: *"Is it clearly and precisely worded?"* Vague/ambiguous = LOW.
  R and C are independent — a claim can be crystal-clear and badly reasoned, or vice versa.

## How to rate (CLI — always `--data eggs-p3` and your assigned `--bloc`)
```
cd /home/user/reasonable/v0
python3 graph.py get-node n007 --data eggs-p3 --json      # READ the item first
python3 graph.py rate --agent <you> --target n007 --dim A --value 4.0 --bloc <your-bloc> --data eggs-p3 --json
python3 graph.py rate --agent <you> --target phrasing:n007:p0 --dim R --value 3.5 --bloc <your-bloc> --data eggs-p3 --json
python3 graph.py rate --agent <you> --target phrasing:n007:p0 --dim C --value 4.5 --bloc <your-bloc> --data eggs-p3 --json
python3 graph.py rate --agent <you> --target e003 --dim A --value 3.0 --bloc <your-bloc> --data eggs-p3 --json
```
Target forms: node id (`n007`) or edge id (`e003`) or `group:<gid>` → dim A. `phrasing:<node>:<pid>`
→ dim R or C. Find a node's primary phrasing id via `get-node <node> --json` ("primary_phrasing").

## Norms (short but load-bearing)
- **Rate honestly and independently.** A rating is a judgment, not encouragement. Do not default
  everything to the middle, and do not agree with the crowd to be agreeable — divergence is how
  the graph catches what it missed. If you rate far from the current value, the tool may nudge you
  to add a comment saying why (`comment --target <id> --text "..."`); that's optional but welcome.
- **Abstain freely** rather than inventing a number you don't have an opinion on — especially on
  member edges of a conjunction group (rate the group instead) and on things outside your knowledge.
- **Reserve the extremes (0, 5)** for cases you would defend. Use the whole range otherwise; do not
  compress toward 2.5.
- **You may add a node or edge** if you see a clear gap, but your main job is rating. Use
  `search "<kw>" --data eggs-p3` before adding anything, to avoid duplicates.
- One rating per (you, target, dim); re-rating supersedes your earlier value. You cannot rate your
  own authored items.

## THIS RUN: rate ONLY your assigned items (sortition)
You were sampled to a specific subset of items — you do NOT rate everything. Read your assignment
file `eggs-p3/assign/<your-id>.tsv` (tab-separated: `target  dim  bloc`). Rate exactly those lines,
passing the given `--bloc` on each. This is per-item sortition: different raters get different items,
and your bloc differs per item. Do not rate items not in your file.
