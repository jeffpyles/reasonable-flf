export const meta = {
  name: 'deep-research-graded',
  description: 'Deep research with GRADED verification (TIERING-TEST-PLAN.md 1a): fan-out search, fetch, then verify each claim by separating faithfulness/provenance (the only thing that drops a claim) from a 0-5 merit score (annotation, never kills) — fixing the covid over-refutation failure mode. Sonnet-pinned stages; synthesis capped to avoid payload truncation.',
  phases: [{"title":"Scope","detail":"Decompose question into 5 search angles"},{"title":"Search","detail":"5 parallel WebSearch agents"},{"title":"Fetch","detail":"URL-dedup, fetch top sources, extract claims"},{"title":"Verify","detail":"3-vote GRADED verification: provenance filter + 0-5 merit, no default-refute"},{"title":"Synthesize","detail":"Merge dupes, preserve support gradient, capped output"}],
}

// deep-research: Scope → pipeline(Search → URL-dedup → Fetch+Extract) → 3-vote Verify → Synthesize
// Ported from bughunter architecture. WebSearch/WebFetch instead of git/grep.
// Question is passed via Workflow({name: 'deep-research', args: '<question>'}).

const VOTES_PER_CLAIM = 3
const REFUTATIONS_REQUIRED = 2
const MAX_FETCH = 15
const MAX_VERIFY_CLAIMS = 25

// ─── Schemas ───
const SCOPE_SCHEMA = {
  type: "object", required: ["question", "angles", "summary"],
  properties: {
    question: { type: "string" },
    summary: { type: "string" },
    angles: { type: "array", minItems: 3, maxItems: 6, items: {
      type: "object", required: ["label", "query"],
      properties: {
        label: { type: "string" },
        query: { type: "string" },
        rationale: { type: "string" },
      },
    }},
  },
}
const SEARCH_SCHEMA = {
  type: "object", required: ["results"],
  properties: {
    results: { type: "array", maxItems: 6, items: {
      type: "object", required: ["url", "title", "relevance"],
      properties: {
        url: { type: "string" },
        title: { type: "string" },
        snippet: { type: "string" },
        relevance: { enum: ["high", "medium", "low"] },
      },
    }},
  },
}
const EXTRACT_SCHEMA = {
  type: "object", required: ["claims", "sourceQuality"],
  properties: {
    sourceQuality: { enum: ["primary", "secondary", "blog", "forum", "unreliable"] },
    publishDate: { type: "string" },
    claims: { type: "array", maxItems: 5, items: {
      type: "object", required: ["claim", "quote", "importance"],
      properties: {
        claim: { type: "string" },
        quote: { type: "string" },
        importance: { enum: ["central", "supporting", "tangential"] },
      },
    }},
  },
}
// GRADED verdict (TIERING-TEST-PLAN.md 1a): separate FAITHFULNESS (provenance --
// does the quote/source actually support the claim? the only thing allowed to
// KILL a claim) from MERIT (a 0-5 support score -- an annotation that never
// kills). claimType is recorded so an object-claim and an attribution are judged
// alike, not with the old grammar bias. No "refuted" boolean, no default-to-kill.
const VERDICT_SCHEMA = {
  type: "object", required: ["faithful", "support", "claimType", "evidence"],
  properties: {
    faithful: { type: "boolean" },                 // provenance: quote/source genuinely supports the claim as stated
    support: { type: "integer", minimum: 0, maximum: 5 }, // merit: how well-grounded the claim is on its own terms
    claimType: { enum: ["object-claim", "attribution", "inference", "epistemic-limit"] },
    evidence: { type: "string" },
    counterSource: { type: "string" },
  },
}
const REPORT_SCHEMA = {
  type: "object", required: ["summary", "findings", "caveats"],
  properties: {
    summary: { type: "string" },
    findings: { type: "array", items: {
      type: "object", required: ["claim", "confidence", "sources", "evidence"],
      properties: {
        claim: { type: "string" },
        confidence: { enum: ["high", "medium", "low"] },
        sources: { type: "array", items: { type: "string" } },
        evidence: { type: "string" },
        vote: { type: "string" },
      },
    }},
    caveats: { type: "string" },
    openQuestions: { type: "array", items: { type: "string" } },
  },
}

// ─── Phase 0: Scope — decompose question into search angles ───
phase("Scope")
const QUESTION = (typeof args === "string" && args.trim()) || ""
if (!QUESTION) {
  return { error: "No research question provided. Pass it as args: Workflow({name: 'deep-research', args: '<question>'})." }
}
const scope = await agent(
  "Decompose this research question into complementary search angles.\n\n" +
  "## Question\n" + QUESTION + "\n\n" +
  "## Task\n" +
  "Generate 5 distinct web search queries that together cover the question from different angles. Pick angles that suit the question's domain. Examples:\n" +
  "- broad/primary  · academic/technical  · recent news  · contrarian/skeptical  · practitioner/implementation\n" +
  "- For medical: anatomy · common causes · serious differentials · authoritative refs · red flags\n" +
  "- For tech: state-of-art · benchmarks · limitations · industry adoption · cost/tradeoffs\n\n" +
  "Make queries specific enough to surface high-signal results. Avoid redundancy.\n" +
  "Return: the question (verbatim or lightly normalized), a 1-2 sentence decomposition strategy, and the angles.\n\nStructured output only.",
  { label: "scope", schema: SCOPE_SCHEMA, model: "sonnet", effort: "low" }
)
if (!scope) {
  return { error: "Scope agent returned no result — cannot decompose the research question." }
}
log("Q: " + QUESTION.slice(0, 80) + (QUESTION.length > 80 ? "…" : ""))
log("Decomposed into " + scope.angles.length + " angles: " + scope.angles.map(a => a.label).join(", "))

// ─── Dedup state — accumulates across searchers as they complete ───
// The workflow sandbox is a bare ECMAScript realm — no URL global — so
// hostname/path come from a regex: captures (1) hostname (userinfo, www.,
// and port stripped) and (2) pathname. Neither userinfo nor host admits
// \: WHATWG URL treats \ as a path separator for http(s), so a laxer
// class would label evil.com\@trusted.com as trusted.com while WebFetch
// actually goes to evil.com. Userinfo DOES admit @ — WHATWG splits the
// authority at the LAST @ before the host, so greedy matching must too;
// stopping at the first @ would label x@trusted.com@evil.com as
// trusted.com while the fetch contacts evil.com. The host class still
// excludes @, so the userinfo group consumes every @ up to the last one.
const URL_HOST_PATTERN = /^[a-z][a-z0-9+.-]*:\/\/(?:[^/?#\\]*@)?(?:www\.)?([^/:?#@\\]+)(?::\d+)?([^?#]*)/i
const normURL = u => {
  const m = String(u).match(URL_HOST_PATTERN)
  return m ? (m[1] + m[2].replace(/\/$/, "")).toLowerCase() : String(u).toLowerCase()
}
// Host and title both come from web content and reach the terminal via the
// progress label. Two hazards: forging a trusted hostname, and smuggling
// terminal control sequences or invisible reordering chars. LABEL_STRIP
// deletes what must never render — C0/C1 controls (incl. ESC/CSI, the ANSI
// introducers), Unicode bidi overrides/isolates and zero-width format chars
// (U+200B-200F, U+202A-202E, U+2066-2069, U+FEFF — they visually reorder or
// hide label text), and the WHOLE double-quote lookalike family (ASCII " plus
// U+201C-201F, U+2033, U+2036, U+275D, U+275E, U+301D, U+301E, U+FF02 — any of
// which would visually close the quoted fallback early and forge host-shaped
// text after it). STRICT_HOST is the strict registrable-hostname charset a
// bare label must match (dot-separated LDH labels). normURL keeps the raw
// capture: dedup keys are never rendered, and stripping there could collide
// distinct URLs.
const LABEL_CAP = 40
const LABEL_STRIP = /[\x00-\x1f\x7f-\x9f\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff\u0022\u201c-\u201f\u2033\u2036\u275d\u275e\u301d\u301e\uff02]/g
const STRICT_HOST = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*$/
const stripLabelChars = s => String(s).replace(LABEL_STRIP, "")
// Render a web-controlled value as a clearly-untrusted quoted label: strip
// dangerous chars, cap at LABEL_CAP code points (Array.from so a surrogate
// pair never splits), and when the cap actually truncated the value, append …
// INSIDE the quotes so a shortened string can never pass for the whole thing.
const quotedLabel = s => {
  const cps = Array.from(stripLabelChars(s))
  return '"' + cps.slice(0, LABEL_CAP).join("").trim() + (cps.length > LABEL_CAP ? "\u2026" : "") + '"'
}
const seen = new Map()
const dupes = []
const budgetDropped = []
const relRank = { high: 0, medium: 1, low: 2 }
let fetchSlots = MAX_FETCH

// ─── Prompts ───
const SEARCH_PROMPT = (angle) =>
  "## Web Searcher: " + angle.label + "\n\n" +
  "Research question: \"" + QUESTION + "\"\n\n" +
  "Your angle: **" + angle.label + "** — " + (angle.rationale || "") + "\n" +
  "Search query: `" + angle.query + "`\n\n" +
  "## Task\nUse WebSearch with the query above (or a refined version). Return the top 4-6 most relevant results.\n" +
  "Rank by relevance to the ORIGINAL question, not just the search query. Skip obvious SEO spam/content farms.\n" +
  "Include a short snippet capturing why each result is relevant.\n\nStructured output only."

const FETCH_PROMPT = (source, angle) =>
  "## Source Extractor\n\n" +
  "Research question: \"" + QUESTION + "\"\n\n" +
  "Fetch and extract key claims from this source:\n" +
  "**URL:** " + source.url + "\n**Title:** " + source.title + "\n**Found via:** " + angle + " search\n\n" +
  "## Task\n1. Use WebFetch to retrieve the page content.\n" +
  "2. Assess source quality: primary research/institution? secondary reporting? blog/opinion? forum? unreliable?\n" +
  "3. Extract 2-5 FALSIFIABLE claims that bear on the research question. Each claim must:\n" +
  "   - be a concrete, checkable statement (not vague generalities)\n" +
  "   - include a direct quote from the source as support\n" +
  "   - be rated central/supporting/tangential to the research question\n" +
  "4. Note publish date if available.\n\n" +
  "If the fetch fails or the page is irrelevant/paywalled, return claims: [] and sourceQuality: \"unreliable\".\n\nStructured output only."

const VERIFY_PROMPT = (claim, v) =>
  "## Claim Verifier (voter " + (v + 1) + "/" + VOTES_PER_CLAIM + ")\n\n" +
  "Your job is to WEIGH this claim, not to reflexively kill it. Two separate judgments:\n" +
  "**(A) Faithfulness (provenance)** — does the source actually exist and does the quote genuinely\n" +
  "support the claim as stated? This is the ONLY thing that can invalidate a claim. Use WebSearch to\n" +
  "confirm the source/quote is real and not fabricated, misattributed, or an overreach beyond what\n" +
  "the quote says.\n" +
  "**(B) Support (merit, 0-5)** — how well-grounded is the claim on its own terms, GIVEN its type?\n" +
  "This is a graded score, NOT a kill switch. A genuinely contested claim scores in the middle, not 0.\n\n" +
  "## Research question\n" + QUESTION + "\n\n" +
  "## Claim under review\n\"" + claim.claim + "\"\n\n" +
  "**Source:** " + claim.sourceUrl + " (" + claim.sourceQuality + ")\n" +
  "**Supporting quote:** \"" + claim.quote + "\"\n\n" +
  "## First, classify the claim's TYPE (judge each type on its own terms — do NOT reward a claim for\n" +
  "being phrased humbly or penalize it for being phrased as a confident fact):\n" +
  "- **object-claim**: asserts something about the world (\"X is true\"). Score its evidential support.\n" +
  "- **attribution**: reports that a source argues/concludes X. Faithful iff the source really says X;\n" +
  "  its support score reflects whether the UNDERLYING argument is sound, NOT merely that it was said.\n" +
  "- **inference**: a conclusion drawn from evidence. Score how well the evidence licenses it.\n" +
  "- **epistemic-limit**: a claim that something is unknown/unresolved. Score whether that is accurate.\n\n" +
  "## Scoring guide for `support` (0-5)\n" +
  "5 = well-established, multiple independent primary sources · 4 = solid, minor open questions ·\n" +
  "3 = genuinely contested / one strong source with credible dissent · 2 = weak or one-sided ·\n" +
  "1 = fringe / poorly evidenced · 0 = contradicted by the weight of evidence.\n" +
  "Do NOT default to a low score under uncertainty — uncertainty is a 3, not a 0. Do NOT down-score a\n" +
  "well-sourced object-claim just because the topic is contested and a rebuttal exists; that is what\n" +
  "the middle of the scale is for.\n\n" +
  "Set **faithful=false ONLY** for a genuine provenance failure (fabricated/misattributed source,\n" +
  "quote that does not support the claim, hallucinated statistic). Contestedness is NOT unfaithfulness.\n\n" +
  "Structured output only. Evidence MUST be specific and cite what you checked."

// ─── Pipeline: search → dedup → fetch+extract (no barrier) ───
const searchResults = await pipeline(
  scope.angles,

  angle => agent(SEARCH_PROMPT(angle), {
    label: "search:" + angle.label, phase: "Search", schema: SEARCH_SCHEMA, model: "sonnet", effort: "low"
  }).then(r => {
    if (!r) return null
    log(angle.label + ": " + r.results.length + " results")
    return { angle: angle.label, results: r.results }
  }),

  searchResult => {
    const sorted = [...searchResult.results].sort((a, b) => relRank[a.relevance] - relRank[b.relevance])
    const novel = sorted.filter(r => {
      const key = normURL(r.url)
      if (seen.has(key)) {
        dupes.push({ ...r, angle: searchResult.angle, dupOf: seen.get(key) })
        return false
      }
      if (fetchSlots <= 0 && relRank[r.relevance] >= 1) {
        budgetDropped.push({ ...r, angle: searchResult.angle })
        return false
      }
      seen.set(key, { angle: searchResult.angle, title: r.title })
      fetchSlots--
      return true
    })
    if (novel.length < searchResult.results.length) {
      log(searchResult.angle + ": " + novel.length + " novel (" + (searchResult.results.length - novel.length) + " filtered)")
    }
    return parallel(
      novel.map(source => () => {
        // A bare fetch:<host> label asserts the real fetch host, so emit it
        // ONLY when the captured host is a verbatim, complete, un-truncated,
        // strict-ASCII hostname that sanitization left untouched. Any
        // deviation routes through the same quoted+ellipsis helper as the
        // title fallback, so a lossy display value can never masquerade as the
        // true host: non-ASCII (an IDN homograph like Cyrillic "аmazon.com",
        // which WebFetch resolves via punycode unavailable in this realm),
        // invalid host chars, a host long enough to need truncation (a bare
        // prefix could show a trusted-looking domain while the real host
        // differs), or a host sanitize altered (deleting a control char would
        // turn exa<ctrl>mple.com into example.com, which is not the real host).
        const capturedHost = String(source.url).match(URL_HOST_PATTERN)?.[1] ?? ""
        const host = capturedHost.toLowerCase()
        const cleanHost = stripLabelChars(host)
        const isCleanBareHost = cleanHost === host && host !== "" && Array.from(host).length <= LABEL_CAP && STRICT_HOST.test(host)
        const hostLabel = cleanHost === "" ? "" : isCleanBareHost ? host : quotedLabel(host)
        const sourceLabel = hostLabel || (stripLabelChars(source.title).trim() && quotedLabel(source.title)) || "unknown"
        return agent(FETCH_PROMPT(source, searchResult.angle), {
          label: "fetch:" + sourceLabel,
          phase: "Fetch",
          schema: EXTRACT_SCHEMA,
          model: "sonnet", effort: "medium",
        }).then(ext => {
          // User-skip → null; drop it (filtered by searchResults.flat().filter(Boolean))
          // rather than throwing into .catch() and mislabeling it "unreliable".
          if (!ext) return null
          return {
            url: source.url, title: source.title, angle: searchResult.angle,
            sourceQuality: ext.sourceQuality, publishDate: ext.publishDate,
            claims: ext.claims.map(c => ({ ...c, sourceUrl: source.url, sourceQuality: ext.sourceQuality })),
          }
        }).catch(e => {
          log("fetch failed: " + source.url + " — " + (e.message || e))
          return { url: source.url, title: source.title, angle: searchResult.angle, sourceQuality: "unreliable", claims: [] }
        })
      })
    )
  }
)

const allSources = searchResults.flat().filter(Boolean)
const allClaims = allSources.flatMap(s => s.claims)
const impRank = { central: 0, supporting: 1, tangential: 2 }
const qualRank = { primary: 0, secondary: 1, blog: 2, forum: 3, unreliable: 4 }

const rankedClaims = [...allClaims]
  .sort((a, b) => (impRank[a.importance] - impRank[b.importance]) || (qualRank[a.sourceQuality] - qualRank[b.sourceQuality]))
  .slice(0, MAX_VERIFY_CLAIMS)

log("Fetched " + allSources.length + " sources → " + allClaims.length + " claims → verifying top " + rankedClaims.length)

if (rankedClaims.length === 0) {
  return {
    question: QUESTION,
    summary: "No claims extracted. " + allSources.length + " sources fetched, all empty/failed. " + dupes.length + " URL dupes, " + budgetDropped.length + " budget-dropped.",
    findings: [], refuted: [], unverified: [], sources: allSources.map(s => ({ url: s.url, quality: s.sourceQuality })),
    stats: { angles: scope.angles.length, sources: allSources.length, claims: 0, dupes: dupes.length },
  }
}

// ─── Verify: 3-vote GRADED verification (TIERING-TEST-PLAN.md 1a) ───
// Adversarial only for PROVENANCE: a claim is dropped ONLY if a majority of valid
// votes find it unfaithful (fabricated/misattributed/quote-doesn't-support). MERIT
// is a graded 0-5 support score that ANNOTATES but never kills, so a genuinely
// contested object-claim survives with a middling score instead of being reflexively
// refuted — the fix for the covid over-refutation failure mode.
phase("Verify")
const voted = (await parallel(
  rankedClaims.map(claim => () =>
    parallel(
      Array.from({ length: VOTES_PER_CLAIM }, (_, v) => () =>
        agent(VERIFY_PROMPT(claim, v), {
          label: "v" + v + ":" + claim.claim.slice(0, 40),
          phase: "Verify",
          schema: VERDICT_SCHEMA,
          model: "sonnet", effort: "medium",
        })
      )
    ).then(verdicts => {
      const valid = verdicts.filter(Boolean)
      const errored = VOTES_PER_CLAIM - valid.length
      const faithfulN = valid.filter(v => v.faithful).length
      const meanSupport = valid.length ? valid.reduce((s, v) => s + v.support, 0) / valid.length : null
      const typeCounts = {}
      valid.forEach(v => { typeCounts[v.claimType] = (typeCounts[v.claimType] || 0) + 1 })
      const claimType = Object.keys(typeCounts).sort((a, b) => typeCounts[b] - typeCounts[a])[0] || null
      const enoughVotes = valid.length >= REFUTATIONS_REQUIRED       // >=2 valid votes to adjudicate
      const faithful = enoughVotes && faithfulN * 2 >= valid.length  // majority find provenance OK
      const provenanceFail = enoughVotes && !faithful
      const kept = enoughVotes && faithful
      const mark = kept ? (meanSupport >= 3 ? "✓" : "~") : provenanceFail ? "✗prov" : "?"
      log("\"" + claim.claim.slice(0, 46) + "…\": support " + (meanSupport === null ? "?" : meanSupport.toFixed(1)) + "/5 faith " + faithfulN + "/" + valid.length + (errored ? " (" + errored + " err)" : "") + " " + mark)
      return { ...claim, verdicts: valid, faithfulVotes: faithfulN, meanSupport, claimType, erroredVotes: errored, kept, provenanceFail, unverified: !enoughVotes }
    })
  )
)).filter(Boolean)

// "confirmed" = kept (faithful) claims passed to the graph, annotated with a merit
// score; NOT a truth-filter. "killed" = dropped for PROVENANCE only.
const confirmed = voted.filter(c => c.kept)
const killed = voted.filter(c => c.provenanceFail)
const unverified = voted.filter(c => c.unverified)
const meanKeptSupport = confirmed.length ? (confirmed.reduce((s, c) => s + c.meanSupport, 0) / confirmed.length) : null
log("Verify done: " + voted.length + " claims → " + confirmed.length + " kept, " + killed.length + " provenance-dropped, " + unverified.length + " unverified; mean support of kept = " + (meanKeptSupport === null ? "n/a" : meanKeptSupport.toFixed(2)))

const toRefuted = c => ({ claim: c.claim, faithfulVotes: c.faithfulVotes + "/" + c.verdicts.length, meanSupport: c.meanSupport, source: c.sourceUrl })
const toUnverified = c => ({ claim: c.claim, erroredVotes: c.erroredVotes, validVotes: c.verdicts.length, source: c.sourceUrl })

if (confirmed.length === 0) {
  // Distinguish "refuted on merit" from "could not verify (infra error)". A run
  // where every verifier agent failed (rate-limit / API error) is an infra
  // failure, not a research finding — report it as such so the user knows to
  // retry rather than concluding the research found nothing.
  let summary
  if (killed.length === 0 && unverified.length > 0) {
    summary = "Could not verify any claims — all " + unverified.length + " verifier panels failed (likely rate-limiting or API errors). This is an infrastructure failure, not a research finding. Raw extracted claims returned below; retry or verify manually."
  } else if (unverified.length > 0) {
    summary = killed.length + " claims dropped for provenance (fabricated/misattributed source); " + unverified.length + " could not be verified (verifier agents errored). No claims kept. Check sources."
  } else {
    summary = "All " + killed.length + " claims dropped for provenance failure (source/quote did not hold up). No claims kept — the extracted sources may be unreliable."
  }
  return {
    question: QUESTION,
    summary,
    findings: [],
    refuted: killed.map(toRefuted),
    unverified: unverified.map(toUnverified),
    sources: allSources.map(s => ({ url: s.url, quality: s.sourceQuality, claimCount: s.claims.length })),
    stats: { angles: scope.angles.length, sources: allSources.length, claims: allClaims.length, verified: voted.length, confirmed: 0, killed: killed.length, unverified: unverified.length },
  }
}

// ─── Synthesize ───
phase("Synthesize")
const block = confirmed.map((c, i) => {
  const best = [...c.verdicts].sort((a, b) => b.support - a.support)[0]
  return "### [" + i + "] " + c.claim + "\n" +
    "Support: " + c.meanSupport.toFixed(1) + "/5 · type: " + c.claimType + " · Source: " + c.sourceUrl + " (" + c.sourceQuality + ")\n" +
    "Quote: \"" + c.quote + "\"\nVerifier note: " + best.evidence + "\n"
}).join("\n")

const killedBlock = killed.length > 0
  ? "\n## Provenance-dropped claims (source/quote did not hold up — for transparency)\n" +
    killed.map(c => "- \"" + c.claim + "\" (" + c.sourceUrl + ", faithful " + c.faithfulVotes + "/" + c.verdicts.length + ")").join("\n")
  : ""

const unverifiedBlock = unverified.length > 0
  ? "\n## Unverified claims (" + unverified.length + " — verifier agents errored; no provenance judgment)\n" +
    unverified.map(c => "- \"" + c.claim + "\" (" + c.sourceUrl + ", " + c.erroredVotes + "/" + VOTES_PER_CLAIM + " votes errored)").join("\n")
  : ""

const report = await agent(
  "## Synthesis: research report\n\n" +
  "**Question:** " + QUESTION + "\n\n" +
  confirmed.length + " claims passed provenance and carry a graded support score (0-5). A high score = " +
  "well-established; a middling score (≈3) = genuinely contested, NOT weak — keep contested claims " +
  "as contested rather than dropping them. Merge semantic duplicates and synthesize faithfully.\n\n" +
  "## Claims (with support scores)\n" + block + "\n" + killedBlock + unverifiedBlock + "\n\n" +
  "## Instructions\n" +
  "1. Merge claims that say the same thing; combine their sources.\n" +
  "2. Group related claims into coherent findings that address the research question. Preserve the " +
  "support gradient — do not flatten a contested claim into a confident one or vice versa.\n" +
  "3. Per finding, set confidence from the support scores: high (mean ≥4, multiple primary sources), " +
  "medium (≈3 or single strong source), low (≤2 or one weak source).\n" +
  "4. Write a 3-5 sentence executive summary answering the question, noting where the answer is " +
  "confident and where it is genuinely open.\n" +
  "5. Caveats: what's uncertain, what sources were weak.\n" +
  "6. List 2-4 open questions.\n\n" +
  "## Output size (IMPORTANT — a prior run's payload was truncated and lost)\n" +
  "Emit ONE StructuredOutput call with valid JSON. Cap at 15 findings (merge aggressively to fit). " +
  "Keep each finding's `evidence` to 1-2 sentences. Do not exceed this — a complete smaller report " +
  "beats a truncated larger one.\n\nStructured output only.",
  { label: "synthesize", schema: REPORT_SCHEMA, model: "sonnet", effort: "high" }
)

if (!report) {
  // Synthesis skipped/errored — salvage the verified claims raw rather
  // than throwing on report.findings and discarding the whole run.
  return {
    question: QUESTION,
    summary: "Synthesis step was skipped or failed — returning " + confirmed.length + " kept claims unmerged.",
    findings: [],
    confirmed: confirmed.map(c => ({ claim: c.claim, source: c.sourceUrl, quote: c.quote, meanSupport: c.meanSupport, claimType: c.claimType })),
    provenanceDropped: killed.map(toRefuted),
    unverified: unverified.map(toUnverified),
    sources: allSources.map(s => ({ url: s.url, quality: s.sourceQuality, claimCount: s.claims.length })),
    stats: { angles: scope.angles.length, sources: allSources.length, claims: allClaims.length, verified: voted.length, confirmed: confirmed.length, killed: killed.length, unverified: unverified.length, afterSynthesis: 0 },
  }
}

return {
  question: QUESTION,
  ...report,
  keptClaims: confirmed.map(c => ({ claim: c.claim, meanSupport: c.meanSupport, claimType: c.claimType, source: c.sourceUrl, quote: c.quote })),
  provenanceDropped: killed.map(toRefuted),
  unverified: unverified.map(toUnverified),
  sources: allSources.map(s => ({ url: s.url, quality: s.sourceQuality, angle: s.angle, claimCount: s.claims.length })),
  stats: {
    angles: scope.angles.length,
    sourcesFetched: allSources.length,
    claimsExtracted: allClaims.length,
    claimsVerified: voted.length,
    kept: confirmed.length,
    provenanceDropped: killed.length,
    meanKeptSupport: meanKeptSupport,
    unverified: unverified.length,
    afterSynthesis: report.findings.length,
    urlDupes: dupes.length,
    budgetDropped: budgetDropped.length,
    agentCalls: 1 + scope.angles.length + allSources.length + (voted.length * VOTES_PER_CLAIM) + 1,
  },
}