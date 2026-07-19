export const meta = {
  name: 'blackholes-graph-assess',
  description: 'Tiered non-adversarial panel assessment of the blackholes-graph: raters rate nodes on Agreement (blind). Same lens-personas across model tiers (Sonnet reference arm vs Haiku cheap arm) so the only variable is the rating model — the model-tiering test (TIERING-TEST-PLAN.md).',
  phases: [{ title: 'Assess' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'blackholes-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, persona, model, seed}]

function prompt(a) {
  const persona = a.persona || a.id
  // Seed only varies the wording so same-persona Haiku raters draw independently;
  // it does NOT change the task or the lens.
  const seedNote = a.seed
    ? `\nYou are independent rater #${a.seed} for this lens; judge each item freshly on your own read — do not try to match any other rater.`
    : ''
  return `You are panelist "${a.id}" in a COOPERATIVE, non-adversarial BLIND assessment of the argument graph for "Could a high-energy particle collider (the LHC) create a black hole that destroys Earth?". Working directory: ${V0} — cd there first. Dataset: --data blackholes-graph.${seedNote}

Read, then rate:
  1. ${H}/personas/${persona}.md   — WHO YOU ARE and the lens you rate through (follow it honestly)
  2. ${H}/assign/${a.id}.tsv       — targets to rate, one per line as <target>\\tA\\t<bloc>

The dataset is in ENFORCED blind Rating mode: \`get-node\` shows a node's claim + Ground/Dependent
structure but NEVER other raters' scores. For each assigned target (node ids nNNN) rate on dim A
(Agreement): "how likely is this claim true?" (0=certainly false .. 5=certainly true).
Commands:
  python3 graph.py get-node <nid> --data blackholes-graph --json
  python3 graph.py rate --agent ${a.id} --target <target> --dim A --value <0.0-5.0> --bloc ${a.seed ? 'cheap' : 'ref'} --data blackholes-graph --json
Rate honestly from your lens on the merits — cooperative, no pushing. Abstain only if a target is
truly outside your knowledge. One read + one rate per item. Writes are lock-serialized; on a
lock-timeout wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Assess')
log(`blackholes-graph assess: ${panel.length} raters (${panel.filter(a => a.model === 'haiku').length} haiku / ${panel.filter(a => a.model !== 'haiku').length} sonnet), blind`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `assess:${a.id}`, phase: 'Assess',
    model: a.model || 'sonnet', effort: a.model === 'haiku' ? 'low' : 'high',
  })))
return { returned: res.filter(Boolean).length, of: panel.length }
