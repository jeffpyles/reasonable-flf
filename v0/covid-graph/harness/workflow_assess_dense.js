export const meta = {
  name: 'covid-graph-assess-dense',
  description: 'Adds Sonnet lens-raters to the covid graph on a fixed ~69-node subset, to build a reliable 12-Sonnet dispersion reference (the existing 4-Sonnet reference has a noisy dispersion estimate). Same lens-personas, extra seeds; blind node Agreement rating. Enables the Sonnet 6v6 dispersion self-reliability ceiling and a corrected Haiku-vs-Sonnet dispersion correlation.',
  phases: [{ title: 'DenseRef' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'covid-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, persona, model, seed, bloc}]

function prompt(a) {
  const persona = a.persona || a.id
  const seedNote = a.seed
    ? `\nYou are independent rater #${a.seed} for this lens; judge each item freshly on your own read — do not try to match any other rater.`
    : ''
  const bloc = a.bloc || 'refdense'
  return `You are panelist "${a.id}" in a COOPERATIVE, non-adversarial BLIND assessment of the SARS-CoV-2-origins argument graph. Working directory: ${V0} — cd there first. Dataset: --data covid-graph.${seedNote}

Read, then rate:
  1. ${H}/personas/${persona}.md   — WHO YOU ARE and the lens you rate through (follow it honestly)
  2. ${H}/assign/${a.id}.tsv       — node ids to rate, one per line as <nid>\\tA\\t<bloc>

The dataset is in ENFORCED blind Rating mode: \`get-node\` shows a node's claim + Ground/Dependent
structure but NEVER other raters' scores. Rate EACH assigned node on dim A (Agreement): "how likely
is this claim true?" (0=certainly false .. 5=certainly true).
Commands:
  python3 graph.py get-node <nid> --data covid-graph --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc ${bloc} --data covid-graph --json
Rate honestly from your lens on the merits — cooperative, no pushing. Abstain only if a node is truly
outside your knowledge. One read + one rate per item. Writes are lock-serialized; on a lock-timeout
wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('DenseRef')
log(`covid dense reference: ${panel.length} ${panel[0] && panel[0].model} raters on the dispersion subset, blind`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `dense:${a.id}`, phase: 'DenseRef',
    model: a.model || 'sonnet', effort: a.model === 'haiku' ? 'low' : 'high',
  })))
return { returned: res.filter(Boolean).length, of: panel.length }
