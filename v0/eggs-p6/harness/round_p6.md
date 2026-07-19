# eggs-p6 — rate every assigned claim from your own worldview

Single pass. Read your persona brief (`eggs-p6/harness/personas/<your-id>.md`) — it says who you are and
how you see this topic — and your assignment (`eggs-p6/harness/assign/<your-id>.tsv`, node ids to rate on
dim A). For EACH node: read it once (`get-node`), form your honest Agreement judgment **from your own
perspective and beliefs**, and rate it:
```
python3 graph.py rate --agent <your-id> --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data eggs-p6 --json
```
Rate all of them (abstain only if genuinely outside your knowledge). One read + one rate per item. When
done, output one line: `<your-id>: rated N, abstained X`.
