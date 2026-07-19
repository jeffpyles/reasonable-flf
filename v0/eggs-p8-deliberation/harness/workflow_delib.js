export const meta = {
  name: 'panel-anchor-deliberation',
  description: 'Fable+Opus frontier-panel deliberation to forge external-verification anchors on contested ground where no ground-truth source exists. Per node: each model rates blind and independently (value + reasonable range), then each revises after seeing the other, then a synthesis fixes the consensus value, the spread of reasonable opinion, a confidence, and an anchor-grade verdict (with a value-question guard). Validated offline against the eggs-p5 expert panel.',
  phases: [{ title: 'Blind' }, { title: 'Revise' }, { title: 'Synthesize' }],
}

const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const nodes = A.nodes

const RUBRIC = `You are rating one claim on its AGREEMENT dimension: "on the merits of the current best evidence, how TRUE is this claim?" Scale 0.0-5.0: 5=clearly true, 2.5=genuinely uncertain/balanced, 0=clearly false. This is about eggs / dietary cholesterol / cardiovascular risk. Reason from the actual state of the evidence, well-scoped; neither egg-alarmist nor egg-booster.`

const FP = {
  type: 'object', additionalProperties: false,
  required: ['value', 'reasonable_low', 'reasonable_high', 'reasoning'],
  properties: {
    value: { type: 'number', description: 'your best point rating 0.0-5.0' },
    reasonable_low: { type: 'number', description: 'low end of the range a well-informed person could defensibly hold' },
    reasonable_high: { type: 'number', description: 'high end of that reasonable range' },
    reasoning: { type: 'string', description: '2-4 sentences: the evidence and scope that drive your rating' },
  },
}
const REV = {
  type: 'object', additionalProperties: false,
  required: ['value', 'reasonable_low', 'reasonable_high', 'moved', 'remaining_disagreement'],
  properties: {
    value: { type: 'number' },
    reasonable_low: { type: 'number' },
    reasonable_high: { type: 'number' },
    moved: { type: 'string', description: 'what in the other panelist\'s view did or did not move you, briefly' },
    remaining_disagreement: { type: 'string', description: 'any substantive disagreement that remains, or "none"' },
  },
}
const SYNTH = {
  type: 'object', additionalProperties: false,
  required: ['is_value_question', 'reasonable_low', 'reasonable_high', 'rationale'],
  properties: {
    is_value_question: { type: 'boolean', description: 'true if this is fundamentally a values/ought judgment where there is no evidential fact of the matter (must NOT become a truth-anchor)' },
    reasonable_low: { type: 'number', description: 'agreed low end of the reasonable range after deliberation' },
    reasonable_high: { type: 'number', description: 'agreed high end of the reasonable range' },
    rationale: { type: 'string', description: 'one or two sentences a future reader can use to understand the panel verdict' },
  },
}

function fpPrompt(node) {
  return `${RUBRIC}\n\nCLAIM (${node.id}${node.title ? ', "' + node.title + '"' : ''}):\n"${node.text}"\n\nRate it independently and honestly. Give your point value, the range of ratings a well-informed person could defensibly hold (tight if the claim is settled, wide if genuinely contested), and your reasoning. You are on a two-model panel forging a reference answer; be accurate and well-calibrated, not diplomatic.`
}
function revPrompt(node, mine, other, myName, otherName) {
  return `${RUBRIC}\n\nCLAIM (${node.id}):\n"${node.text}"\n\nYou (${myName}) rated it ${mine.value} (reasonable range ${mine.reasonable_low}-${mine.reasonable_high}). Your reasoning: ${mine.reasoning}\n\nThe other panelist (${otherName}) rated it ${other.value} (range ${other.reasonable_low}-${other.reasonable_high}). Their reasoning: ${other.reasoning}\n\nReconsider in light of their view. Update your rating if they raise something that should move you; hold firm if you shouldn't. Report your (possibly revised) value and range, what moved you, and any remaining substantive disagreement.`
}
function synthPrompt(node, fr, or_) {
  return `Two frontier models deliberated on whether this claim is true, to forge a reference "anchor".\n\nCLAIM (${node.id}):\n"${node.text}"\n\nAfter exchange: Fable settled on ${fr.value} (range ${fr.reasonable_low}-${fr.reasonable_high}); remaining disagreement: ${fr.remaining_disagreement}. Opus settled on ${or_.value} (range ${or_.reasonable_low}-${or_.reasonable_high}); remaining disagreement: ${or_.remaining_disagreement}.\n\nProduce the panel synthesis. Set the agreed reasonable_low/high (the honest spread of defensible opinion given both panelists). CRUCIALLY: set is_value_question=true if this claim is fundamentally a VALUES/OUGHT judgment (what one *should* do, what "worth it" means) rather than an evidential question with a fact of the matter — such claims must never become truth-anchors no matter how the panel agrees. Give a one-to-two-sentence rationale.`
}

phase('Blind')
log(`panel-anchor deliberation: ${nodes.length} nodes, Fable+Opus, blind -> revise -> synthesize`)

const results = await pipeline(
  nodes,
  // Stage 1: blind independent first pass (both models, parallel)
  async (node) => {
    const [fable, opus] = await Promise.all([
      agent(fpPrompt(node), { label: `blind:F:${node.id}`, phase: 'Blind', model: 'fable', effort: 'high', schema: FP }),
      agent(fpPrompt(node), { label: `blind:O:${node.id}`, phase: 'Blind', model: 'opus', effort: 'high', schema: FP }),
    ])
    return { node, fable, opus }
  },
  // Stage 2: each revises after seeing the other (parallel)
  async (r) => {
    if (!r.fable || !r.opus) return null
    const [fr, or_] = await Promise.all([
      agent(revPrompt(r.node, r.fable, r.opus, 'Fable', 'Opus'), { label: `revise:F:${r.node.id}`, phase: 'Revise', model: 'fable', effort: 'high', schema: REV }),
      agent(revPrompt(r.node, r.opus, r.fable, 'Opus', 'Fable'), { label: `revise:O:${r.node.id}`, phase: 'Revise', model: 'opus', effort: 'high', schema: REV }),
    ])
    return { ...r, fr, or_ }
  },
  // Stage 3: synthesize + compute the anchor verdict in code (symmetric, transparent)
  async (r) => {
    if (!r.fr || !r.or_) return null
    const synth = await agent(synthPrompt(r.node, r.fr, r.or_), { label: `synth:${r.node.id}`, phase: 'Synthesize', model: 'fable', effort: 'high', schema: SYNTH })
    if (!synth) return null
    const consensus = (r.fr.value + r.or_.value) / 2
    const gap = Math.abs(r.fr.value - r.or_.value)
    const low = Math.min(synth.reasonable_low, r.fr.reasonable_low, r.or_.reasonable_low)
    const high = Math.max(synth.reasonable_high, r.fr.reasonable_high, r.or_.reasonable_high)
    const spread = high - low
    // anchor-grade: the two models converged (small gap), the reasonable range is
    // tight, and it is not a value question. Confidence blends convergence + tightness.
    const anchor_grade = gap <= 0.5 && spread <= 1.5 && !synth.is_value_question
    const confidence = Math.max(0, Math.min(1, (1 - gap / 2.5) * (1 - spread / 5)))
    return {
      id: r.node.id, kind: r.node.kind,
      consensus_value: Math.round(consensus * 100) / 100,
      fable_value: r.fr.value, opus_value: r.or_.value, gap: Math.round(gap * 100) / 100,
      reasonable_low: low, reasonable_high: high, spread: Math.round(spread * 100) / 100,
      confidence: Math.round(confidence * 100) / 100,
      is_value_question: synth.is_value_question,
      anchor_grade,
      rationale: synth.rationale,
    }
  },
)

const clean = results.filter(Boolean)
log(`done: ${clean.length}/${nodes.length} nodes; ${clean.filter(a => a.anchor_grade).length} anchor-grade`)
return { anchors: clean }
