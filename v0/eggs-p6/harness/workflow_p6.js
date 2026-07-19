export const meta = {
  name: 'eggs-p6-biased-bootstrap',
  description: 'Biased-bootstrap flywheel test: 20 agents (16 cholesterol-hawk Haiku + 4 evidence-tracking Sonnet) each rate all 79 node claims. A shared directional bias corrupts the flat consensus; offline analysis tests whether discrimination-weighting (with vs without anchor items) can pull it back toward the independent expert truth.',
  phases: [{ title: 'Rate' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-p6/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents   // competent-first

function prompt(a) {
  return `You are rater "${a.id}" in a COOPERATIVE argument-graph rating run about "Are eggs good for you?". Working directory: ${V0} — cd there first.

Read these two files, then rate:
  1. ${H}/personas/${a.id}.md   — WHO YOU ARE and how you see this topic (rate from THIS worldview, honestly)
  2. ${H}/round_p6.md           — the task
  3. ${H}/assign/${a.id}.tsv    — node ids to rate (dim A)

For each node: read it once with get-node, form your honest Agreement judgment FROM YOUR OWN PERSPECTIVE, and rate:
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data eggs-p6 --json
Rate every assigned node (abstain only if truly outside your knowledge). One read + one rate per item. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Rate')
log(`eggs-p6: ${agents.length} raters (${agents.filter(a => a.tier === 'competent').length} competent minority) rating all 79 nodes`)
const res = await parallel(agents.map(a => () =>
  agent(prompt(a), {
    label: `p6:${a.id}`, phase: 'Rate',
    model: a.model, effort: a.model === 'sonnet' ? 'high' : 'low',
  })))
return { returned: res.filter(Boolean).length }
