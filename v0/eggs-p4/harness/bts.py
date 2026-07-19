#!/usr/bin/env python3
"""Bayesian Truth Serum (Prelec 2004) scorer for the Reasonable reputation
experiment. Pure functions, no I/O -- fed a rating matrix + meta-prediction
matrix, returns a per-rater information score, prediction score, and combined
BTS score. Reused by the synthetic validation (validate_bts.py) and, later, by
the real eggs-p5 event log.

Why BTS: alignment-to-consensus and every level-agreement variant reward
proximity to the average rater (tyranny of the median); discrimination rewards
tracking the crowd's ORDERING but still can't crown a correct minority whose
ordering the crowd rejects. BTS can, using only opinions -- no answer key --
because a correct minority can predict the majority view but not vice versa, so
the correct answer is "surprisingly popular": it shows up in the actual votes
more than the crowd collectively predicted it would.

Data model (per (item)):
  ratings[item][rater]      = value on the 0..scale_max scale
  predictions[item][rater]  = list of predicted FRACTIONS over the same bins the
                              ratings get binned into (a distribution, need not
                              sum to exactly 1 -- it is floored + renormalized).

Scoring, per item with n>=min_raters numeric raters, over B bins:
  x_b   = actual fraction of raters whose rating is in bin b
  ybar_b= geometric mean over raters of their predicted fraction for bin b
          (then renormalized) -- the population's collective prediction
  info_k        = log( x_{bin(k)} / ybar_{bin(k)} )     # endorse the
                                                          # surprisingly-popular bin
  prediction_k  = sum_b x_b * log( pred_k,b / x_b )      # -KL(actual||pred_k): reward
                                                          # accurately predicting the crowd
  bts_k(item)   = info_k + alpha * prediction_k
A rater's scores are the mean of their per-item scores. Truth-telling is the
BTS equilibrium: you cannot inflate info by misreporting your rating without
paying for it in prediction.
"""
from __future__ import annotations

import math

DEFAULT_BINS = (2.0, 3.5)          # -> 3 bins: low [0,2), mid [2,3.5), high [3.5,inf)
EPS = 1e-6


def bin_of(value, edges=DEFAULT_BINS) -> int:
    b = 0
    for e in edges:
        if value >= e:
            b += 1
    return b


def n_bins(edges=DEFAULT_BINS) -> int:
    return len(edges) + 1


def _normalize(vec):
    s = sum(vec)
    if s <= 0:
        return [1.0 / len(vec)] * len(vec)
    return [x / s for x in vec]


def _geo_mean_prediction(pred_vectors, B):
    """Geometric mean (per bin) of the raters' predicted distributions,
    renormalized. Floors each prediction so log is finite."""
    logsum = [0.0] * B
    m = len(pred_vectors)
    for pv in pred_vectors:
        pv = _normalize([max(x, EPS) for x in pv])
        for b in range(B):
            logsum[b] += math.log(pv[b])
    geo = [math.exp(logsum[b] / m) for b in range(B)]
    return _normalize(geo)


def score(ratings, predictions, edges=DEFAULT_BINS, alpha=1.0, min_raters=3):
    """Return {rater: {"info","prediction","bts","n_items"}} averaged over the
    items each rater rated (that met min_raters). `ratings`/`predictions` are
    dict[item][rater] -> value / predicted-fraction-list."""
    B = n_bins(edges)
    acc = {}  # rater -> [info_sum, pred_sum, count]

    for item, cell in ratings.items():
        raters = [r for r, v in cell.items() if v is not None]
        if len(raters) < min_raters:
            continue
        preds = predictions.get(item, {})
        # actual bin frequencies
        counts = [0.0] * B
        binof = {}
        for r in raters:
            b = bin_of(cell[r], edges)
            binof[r] = b
            counts[b] += 1
        x = _normalize(counts)
        # collective (geometric-mean) prediction over raters who supplied one
        pvs = [preds[r] for r in raters if r in preds and preds[r] is not None]
        if len(pvs) < min_raters:
            continue
        ybar = _geo_mean_prediction(pvs, B)
        for r in raters:
            b = binof[r]
            info = math.log((x[b] + EPS) / (ybar[b] + EPS))
            if r in preds and preds[r] is not None:
                pv = _normalize([max(v, EPS) for v in preds[r]])
                pred = sum(x[j] * math.log((pv[j] + EPS) / (x[j] + EPS)) for j in range(B))
            else:
                pred = 0.0
            a = acc.setdefault(r, [0.0, 0.0, 0])
            a[0] += info
            a[1] += pred
            a[2] += 1

    out = {}
    for r, (isum, psum, c) in acc.items():
        if c == 0:
            continue
        info = isum / c
        pred = psum / c
        out[r] = {"info": info, "prediction": pred,
                  "bts": info + alpha * pred, "n_items": c}
    return out
