#!/usr/bin/env python3
"""Sidecar meta-prediction CLI for the eggs-p5 Bayesian-Truth-Serum run.

Keeps the frozen v0 core and the live reputation math UNTOUCHED: meta-predictions
are appended to `<data>/predictions.jsonl`, a separate append-only log that the
BTS scorer reads alongside events.jsonl. Nothing in graph.py / fold.py changes.

A meta-prediction is a rater's guess of how the REST of the crowd will rate an
item, as a low/mid/high split (percentages, need not sum to exactly 100 — they
are renormalized). Buckets match the BTS scorer: low [0,2), mid [2,3.5), high
[3.5,5].

Usage:
  python3 predict.py --agent h04-gym-protein --target n007 --dim A \
      --low 10 --mid 30 --high 60 --data eggs-p5
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--dim", required=True, choices=["A", "R", "C"])
    ap.add_argument("--low", type=float, required=True, help="predicted %% of raters in [0,2)")
    ap.add_argument("--mid", type=float, required=True, help="predicted %% in [2,3.5)")
    ap.add_argument("--high", type=float, required=True, help="predicted %% in [3.5,5]")
    ap.add_argument("--data", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    vec = [max(0.0, args.low), max(0.0, args.mid), max(0.0, args.high)]
    s = sum(vec)
    if s <= 0:
        print(json.dumps({"ok": False, "error": "prediction sums to 0"}))
        return 1
    vec = [x / s for x in vec]

    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent,
        "target": args.target,
        "dim": args.dim,
        "pred": vec,            # normalized [low, mid, high]
    }
    path = Path(args.data) / "predictions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    out = {"ok": True, "recorded": rec}
    print(json.dumps(out) if args.json else f"recorded prediction for {args.agent} on {args.target}:{args.dim} -> {vec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
