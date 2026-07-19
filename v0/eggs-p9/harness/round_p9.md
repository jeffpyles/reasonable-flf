# eggs-p9 — rate every assigned claim from your own worldview (blind)

Single blind pass. This dataset is in **enforced blind Rating mode** (`config.json`
`rating_mode_only: true`): every read is automatically blinded — you cannot see existing
ratings/comments no matter how you read. Read your persona brief
(`eggs-p9/harness/personas/<your-id>.md`) — it says who you are and how you see this topic — and your
assignment (`eggs-p9/harness/assign/<your-id>.tsv`, node ids to rate on dim A). For EACH node: read it
once (`get-node`, returns the claim + structure but no consensus), form your honest Agreement judgment
**from your own perspective and beliefs**, and rate it:
```
python3 graph.py get-node <nid> --data eggs-p9 --json
python3 graph.py rate --agent <your-id> --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data eggs-p9 --json
```
Rate all of them (abstain only if genuinely outside your knowledge). One read + one rate per item. When
done, output one line: `<your-id>: rated N, abstained X`.
