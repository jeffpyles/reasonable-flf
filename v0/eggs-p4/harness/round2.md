# Round 2 — deepen and respond

The graph has grown and been rated since round 1: new claims were added, and other raters (some of
them domain experts) have left ratings and **comments** arguing for particular judgments. Your task:

1. Re-read your persona brief (`eggs-p4/harness/personas/<your-id>.md`).
2. Read your round-2 assignment (`eggs-p4/harness/assign/r2/<your-id>.tsv`) and rate those items —
   reading each one first, as before, with the given `--bloc`.
3. **Respond to the conversation.** For your assigned items, run `list-comments` on them. If another
   rater has made an argument that genuinely changes your mind — or sharpens a point you rated hastily
   in round 1 — you are encouraged to **re-rate** the earlier item (a new `rate` supersedes your old
   value) and, if useful, reply in the thread. Change your mind when the argument warrants it; hold
   your ground (with a comment) when it does not. Do not move just to match the crowd.
4. **Builders / experts:** where you think the current consensus on an item is miscalibrated, make the
   case now — a concise `comment`, a sharper competing `propose-phrasing`, or the missing
   `draw-ground`/antithesis that reframes it. This is how the graph gets better: through legible
   argument, not just numbers.

Work item by item. When done, output one line:
`<your-id>: rated N, re-rated R, commented K, added M`.
