#!/usr/bin/env python3
"""Generate the eggs-p4 population roster: a cooperative but diverse crowd.

60 agents. 52 Haiku (the everyday crowd: good-faith, but a spectrum of domain
lenses, priors, care levels and rating styles -- "somewhat hasty, context-weak"
is the Haiku baseline we're stress-testing) + 8 Sonnet (thoughtful experts whose
fate we are testing: do they get REWARDED for sharper judgment, or PENALIZED by
a blunter-majority consensus?).

Every agent is COOPERATIVE -- doing its best to be helpful and reasonable. The
spectrum is of honest perspective and skill. Every rater is good-faith.

Deterministic: no RNG seeded on wall-clock; index-driven distributions only.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---- domain lenses: the honest vantage point an agent reasons from ----
HAIKU_LENSES = [
    ("home-cook",           "an everyday home cook who thinks about eggs as food, not chemistry"),
    ("calorie-counter",     "a weight-conscious eater focused on calories, protein and satiety"),
    ("heart-worrier",       "someone with a family history of heart disease, cholesterol-cautious"),
    ("gym-protein",         "a fitness/gym-goer who prizes eggs as cheap complete protein"),
    ("keto-leaning",        "a low-carb/keto follower who sees dietary cholesterol as harmless"),
    ("plant-leaning",       "a mostly-plant-based eater skeptical of animal products"),
    ("budget-shopper",      "a budget-focused shopper who weighs cost and food access"),
    ("parent-feeder",       "a parent thinking about what's safe and good for growing kids"),
    ("senior-health",       "an older adult managing several health numbers at once"),
    ("food-safety",         "someone alert to salmonella and safe handling above all"),
    ("clean-eating",        "a wellness/clean-eating enthusiast wary of processed advice"),
    ("skeptic-reader",      "a headline-skeptic who distrusts nutrition studies flip-flopping"),
    ("trusting-guidelines", "someone who defers to official dietary guidelines"),
    ("diabetic-aware",      "a type-2 diabetic attentive to their own subgroup's risks"),
    ("athlete-endurance",   "an endurance athlete tracking performance and recovery"),
    ("culinary-culture",    "a cook rooted in a cuisine where eggs are staple and traditional"),
    ("longevity-buff",      "a longevity/biohacking hobbyist chasing optimal health"),
    ("nurse-practical",     "a practical nurse who has seen a lot of real patients"),
    ("label-reader",        "a careful nutrition-label reader who trusts numbers"),
    ("intuitive-eater",     "an intuitive eater who distrusts over-quantified nutrition"),
    ("environmental",       "someone weighing the environmental footprint of eggs"),
    ("value-moderation",    "a temperament that everything-in-moderation is the safe answer"),
    ("contrarian-honest",   "an honest contrarian who instinctively probes the consensus claim"),
    ("news-follower",       "someone whose views track the latest health news they read"),
    ("pragmatic-doctor-fan","a layperson who trusts their GP's rules of thumb"),
    ("supplement-minded",   "a supplement-and-nutrient optimizer (choline, lutein, omega-3)"),
]

# care levels: how much an agent reads/reflects before rating (Haiku baseline
# skews toward hasty/mid; a real crowd has a minority of very careful raters).
CARE = (
    ["high"]  * 14 +   # read the item + neighbors, weigh, use full range
    ["mid"]   * 24 +   # read the item, reasonable but quick
    ["hasty"] * 14     # skim, first-impression, cluster a bit toward the middle
)

# prior lean on the core question ("are eggs good for you?").
BIAS = (
    ["pro-egg"]      * 13 +   # eggs are fine/good for most people
    ["anti-egg"]     * 11 +   # dietary cholesterol still worries them
    ["it-depends"]   * 20 +   # context/subgroup dependent, moderate
    ["by-subgroup"]  *  8     # strong on subgroup nuance (diabetics, FH)
)

# rating style: a stable idiosyncrasy in how they map judgment to numbers.
STYLE = (
    ["balanced"]      * 18 +  # uses the range as intended
    ["generous"]      * 10 +  # rounds up, reluctant to go below 3
    ["strict"]        * 10 +  # rounds down, demands rigor for a 4-5
    ["mid-clumping"]  *  8 +  # clusters toward 2.5-3.5, avoids extremes
    ["extreme-using"] *  6    # reaches for 1s and 5s readily
)


def cycle(seq, i):
    return seq[i % len(seq)]


def build():
    agents = []
    # --- 52 Haiku ---
    for i in range(52):
        lens_key, lens_desc = HAIKU_LENSES[i % len(HAIKU_LENSES)]
        care = CARE[i % len(CARE)]
        bias = BIAS[(i * 7) % len(BIAS)]     # decorrelate bias from lens
        style = STYLE[(i * 5) % len(STYLE)]  # decorrelate style
        aid = f"h{i+1:02d}-{lens_key}"
        brief = (
            f"You are **{aid}**, an ordinary, good-faith member of the crowd rating an "
            f"argument graph about \"Are eggs good for you?\". Your vantage point: {lens_desc}. "
            f"Your instinct on the core question leans **{bias}**, but you are honest and will "
            f"follow the evidence in front of you. Care level: **{care}** "
            + {"high":"you read carefully and use the full 0-5 range.",
               "mid":"you read the item and rate reasonably but don't over-deliberate.",
               "hasty":"you tend to skim and go with a quick first impression."}[care]
            + f" Rating style: **{style}** "
            + {"balanced":"you use the scale as intended.",
               "generous":"you lean a little high and are reluctant to score below 3 without a clear reason.",
               "strict":"you lean a little low and demand real rigor before giving a 4 or 5.",
               "mid-clumping":"you gravitate toward the middle and rarely use the extremes.",
               "extreme-using":"you reach for 1s and 5s more readily than most."}[style]
            + " You are NOT an expert; rate what you actually understand and abstain on the rest."
        )
        agents.append({
            "id": aid, "model": "haiku", "tier": "crowd",
            "lens": lens_key, "care": care, "bias": bias, "style": style,
            "brief": brief,
        })

    # --- 8 Sonnet experts ---
    experts = [
        ("lipidologist",    "a lipidologist who thinks in LDL particles, ApoB, and RCT endpoints",
         "You distinguish surrogate markers from hard outcomes and know dietary cholesterol raises serum LDL modestly and variably."),
        ("nutri-epi",       "a nutrition epidemiologist expert in confounding and cohort methodology",
         "You are ruthless about residual confounding, healthy-user bias, and food-frequency measurement error; association is not causation."),
        ("ebm-meta",        "an evidence-based-medicine specialist who lives in meta-analyses and GRADE",
         "You weight studies by design and risk of bias, and you flag over-claiming from weak inference."),
        ("endocrinologist", "an endocrinologist focused on the diabetic subgroup",
         "You know the egg/CVD signal differs in type-2 diabetes and you insist subgroup claims stay scoped."),
        ("biochemist",      "a biochemist of cholesterol metabolism and dietary absorption",
         "You understand hepatic feedback, absorption saturation, and hyper-responders vs hypo-responders."),
        ("biostatistician", "a biostatistician expert in causal inference",
         "You spot argument-from-ignorance, replication-is-not-causation, and dose-response misreadings instantly."),
        ("guidelines-pubh", "a public-health scientist who knows the guideline history",
         "You know exactly how dietary-cholesterol guidance changed across editions and why -- and won't overstate it."),
        ("synthesizer",     "a careful generalist who integrates the whole graph before judging",
         "You read grounds and antitheses together, weigh chain strength, and reward precise, well-scoped claims."),
    ]
    for i, (key, lens_desc, expertise) in enumerate(experts):
        aid = f"s{i+1:02d}-{key}"
        brief = (
            f"You are **{aid}**, {lens_desc}. You are a genuine expert rating an argument graph "
            f"about \"Are eggs good for you?\" in a crowd that is mostly non-expert. {expertise} "
            "Rate on the merits with a sharp, discriminating eye: give weak inferences and fallacies "
            "low scores even when the crowd is lenient, and give genuinely rigorous, well-scoped claims "
            "high scores. Crucially, when you diverge from the current consensus, **say why** -- leave a "
            "concise comment, propose a sharper phrasing, or add the missing ground/antithesis that makes "
            "your reasoning legible. Your job is not only to rate correctly but to move the graph toward a "
            "more reasonable place through good arguments. Abstain rather than guess outside your knowledge."
        )
        agents.append({
            "id": aid, "model": "sonnet", "tier": "expert",
            "lens": key, "care": "high", "bias": "evidence-led", "style": "discriminating",
            "brief": brief,
        })
    return agents


def main():
    agents = build()
    out = {"agents": agents,
           "counts": {"total": len(agents),
                      "haiku": sum(1 for a in agents if a["model"] == "haiku"),
                      "sonnet": sum(1 for a in agents if a["model"] == "sonnet")}}
    (HERE / "roster.json").write_text(json.dumps(out, indent=2))
    print(f"wrote roster.json: {out['counts']}")
    # sanity: distribution
    from collections import Counter
    for k in ("care", "bias", "style"):
        c = Counter(a[k] for a in agents if a["model"] == "haiku")
        print(f"  haiku {k}: {dict(c)}")


if __name__ == "__main__":
    main()
