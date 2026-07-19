# Round 1 — first assessment (and, for builders, extend the graph)

This is the opening round. The graph already exists; you are joining a crowd that will rate it in
depth over several rounds. Your task this round:

1. **Read your persona brief** (`eggs-p4/harness/personas/<your-id>.md`) — it says who you are, how
   you rate, and whether you are a builder.
2. **Read your assignment** (`eggs-p4/harness/assign/r1/<your-id>.tsv`) — tab-separated
   `target  dim  bloc`. These are your items for this round.
3. **For each assigned line: READ the item first** (`get-node` on the node, or on the node the edge/
   phrasing belongs to), form your own honest judgment, then `rate` it with the given `--bloc`.
   Do not peek at the current mean and echo it — rate what you actually think. Abstain if it's outside
   your knowledge. When you diverge sharply from where the item sits, that is exactly when a one-line
   `comment` explaining why is most valuable.
4. **Builders only:** after rating, look for ONE genuinely missing, load-bearing claim in the source
   material or established domain knowledge, `search` to confirm it's absent, and add it well-formed
   and well-connected. Precision over volume.

Aim for roughly your full assignment plus (builders) one addition. Work item by item. When done, output
a single line: `<your-id>: rated N items, added M nodes/edges, commented K times`.
