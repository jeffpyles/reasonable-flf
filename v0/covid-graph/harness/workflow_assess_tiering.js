export const meta = {
  name: 'covid-graph-assess-tiering',
  description: 'Cheap-arm (Haiku) rating pass on the existing covid-graph for the model-tiering test (TIERING-TEST-PLAN.md). Same 4 lens-personas as the Sonnet reference arm already folded into the graph; only the model differs. 16 Haiku raters (4 lenses x 4 seeds) rate all nodes on Agreement, blind, so N=4/8/16 can be subsampled against the Sonnet reference (mean-agreement, dispersion-reproduction, verdict).',
  phases: [{ title: 'CheapAssess' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'covid-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, persona, model, seed}]

function prompt(a) {
  const persona = a.persona || a.id
  const seedNote = a.seed
    ? `\nYou are independent rater #${a.seed} for this lens; judge each item freshly on your own read — do not try to match any other rater.`
    : ''
  return `You are panelist "${a.id}" in a COOPERATIVE, non-adversarial BLIND assessment of the SARS-CoV-2-origins argument graph. Working directory: ${V0} — cd there first. Dataset: --data covid-graph.${seedNote}

Read, then rate:
  1. ${H}/personas/${persona}.md   — WHO YOU ARE and the lens you rate through (follow it honestly)
  2. ${H}/assign/${a.id}.tsv       — node ids to rate, one per line as <nid>\\tA\\t<bloc>

The dataset is in ENFORCED blind Rating mode: \`get-node\` shows a node's claim + Ground/Dependent
structure but NEVER other raters' scores. Rate EACH assigned node on dim A (Agreement): "how likely
is this claim true?" (0=certainly false .. 5=certainly true).
Commands:
  python3 graph.py get-node <nid> --data covid-graph --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc cheap --data covid-graph --json
Rate honestly from your lens on the merits — cooperative, no pushing. Abstain only if a node is truly
outside your knowledge. One read + one rate per item. Writes are lock-serialized; on a lock-timeout
wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('CheapAssess')
log(`covid tiering: ${panel.length} Haiku raters rating all nodes, blind (Sonnet reference already folded)`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `cheap:${a.id}`, phase: 'CheapAssess',
    model: a.model || 'haiku', effort: 'low',
  })))
return { returned: res.filter(Boolean).length, of: panel.length }
