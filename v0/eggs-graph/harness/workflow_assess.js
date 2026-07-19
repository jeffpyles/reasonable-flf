export const meta = {
  name: 'eggs-graph-assess',
  description: 'Non-adversarial panel assessment of the fresh eggs-graph: a persona-diverse 4-agent panel each independently rates every node AND every ground edge on Agreement (enforced blind Rating mode). Produces the dispersion/calibration/contested-crux signals that distinguish the assessed graph from the flat report.',
  phases: [{ title: 'Assess' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, model}]

function prompt(a) {
  return `You are panelist "${a.id}" in a COOPERATIVE, non-adversarial BLIND assessment of the egg-health argument graph. Working directory: ${V0} — cd there first. Dataset: --data eggs-graph.

Read, then rate:
  1. ${H}/personas/${a.id}.md   — WHO YOU ARE and the lens you rate through (follow it honestly)
  2. ${H}/assign/${a.id}.tsv    — targets to rate, one per line as <target>\\tA\\t<bloc>

The dataset is in ENFORCED blind Rating mode: \`get-node\` shows a node's claim + Ground/Dependent
structure but NEVER other raters' scores. Targets are a mix of node ids (nNNN), ground-edge ids
(eNNN), and conjunction groups (group:gNNN). Rate EACH on dim A (Agreement):
  - node:  "how likely is this claim true?" (0=certainly false .. 5=certainly true)
  - edge/group: the CONDITIONAL reading — "IF the ground(s) hold, how strongly does that support the
    dependent?" (0=not at all .. 5=decisively). Read the from/to nodes to judge.
Commands:
  python3 graph.py get-node <nid> --data eggs-graph --json     # for a node, or the node an edge touches
  python3 graph.py rate --agent ${a.id} --target <target> --dim A --value <0.0-5.0> --bloc <bloc> --data eggs-graph --json
Use the <bloc> from column 3 verbatim. Rate honestly from your lens on the merits — this is
cooperative, no pushing. Abstain only if a target is truly outside your knowledge. One read + one
rate per item. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Assess')
log(`eggs-graph assess: ${panel.length}-agent panel rating all nodes + edges on A, blind`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `assess:${a.id}`, phase: 'Assess',
    model: a.model || 'sonnet', effort: 'high',
  })))
return { returned: res.filter(Boolean).length, of: panel.length }
