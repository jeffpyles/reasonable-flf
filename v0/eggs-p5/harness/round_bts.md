# eggs-p5 — rate and predict (single pass)

One task this run: for every item in your assignment, **rate it AND predict how the rest of the crowd
will rate it.** There is no graph-building and no re-rating round.

1. Read your persona brief (`eggs-p5/harness/personas/<your-id>.md`) — who you are, the rating rules,
   and the meta-prediction instruction.
2. Read your assignment (`eggs-p5/harness/assign/r1/<your-id>.tsv`) — `target  dim  bloc` lines.
3. For EACH line, in order:
   a. Read the item (`get-node` on the node, or on the node an edge/phrasing belongs to).
   b. Form your own honest judgment and `rate` it (with your `--bloc`).
   c. **Immediately** predict the crowd's low/mid/high split for that item with `predict.py`.
      Predict what the TYPICAL OTHER rater will do — that may differ from your own rating, especially
      on items where you think the crowd will see it differently than you do. This is the whole point:
      an honest guess about others, not a copy of your own answer.
   d. Use `--value abstain` (and skip the prediction) only for items truly outside your knowledge.

Keep it efficient: one read, one rate, one predict per item. When done, output ONE line:
`<your-id>: rated N, predicted P, abstained X`.
