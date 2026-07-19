export const meta = {
  name: 'eggs-graph-assess-depth',
  description: 'Depth pass on eggs-graph: a 16-rater Haiku swarm (4 lens-personas x 4 seeds) rates all 64 nodes on Agreement, blind, bloc "cheap". Brings eggs from 4 raters (below quorum 5) up to 20 (past confirm 15) so its lifecycle verdicts seal, comparable to covid/black-holes. Same lens personas as the existing Sonnet panel; only model + seeds differ.',
  phases: [{ title: 'DepthAssess' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, persona, model, seed}]

function prompt(a) {
  const persona = a.persona || a.id
  const seedNote = a.seed
    ? `\nYou are independent rater #${a.seed} for this lens; judge each item freshly on your own read — do not try to match any other rater.`
    : ''
  return `You are panelist "${a.id}" in a COOPERATIVE, non-adversarial BLIND assessment of the eggs / dietary-cholesterol health argument graph. Working directory: ${V0} — cd there first. Dataset: --data eggs-graph.${seedNote}

Read, then rate:
  1. ${H}/personas/${persona}.md   — WHO YOU ARE and the lens you rate through (follow it honestly)
  2. ${H}/assign/${a.id}.tsv       — node ids to rate, one per line as <nid>\\tA\\t<bloc>

The dataset is in ENFORCED blind Rating mode: \`get-node\` shows a node's claim + Ground/Dependent
structure but NEVER other raters' scores. Rate EACH assigned node on dim A (Agreement): "how likely
is this claim true?" (0=certainly false .. 5=certainly true).
Commands:
  python3 graph.py get-node <nid> --data eggs-graph --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc cheap --data eggs-graph --json
Rate honestly from your lens on the merits — cooperative, no pushing. Abstain only if a node is truly
outside your knowledge. One read + one rate per item. Writes are lock-serialized; on a lock-timeout
wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('DepthAssess')
log(`eggs depth pass: ${panel.length} Haiku raters rating all nodes, blind (Sonnet panel already folded)`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `cheap:${a.id}`, phase: 'DepthAssess',
    model: a.model || 'haiku', effort: 'low',
  })))
return { returned: res.filter(Boolean).length, of: panel.length }
