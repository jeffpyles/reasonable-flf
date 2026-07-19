export const meta = {
  name: 'eggs-p8-bias-x-model',
  description: 'Balanced 2x2 disposition x model run: 28 agents (7 biased-haiku, 7 biased-sonnet, 7 neutral-haiku, 7 neutral-sonnet) each rate all 79 node claims blind (enforced Rating mode). De-confounds the disposition/capability axes entangled in eggs-p7, and asks whether camp-detection splits by disposition or by model. Offline analysis reuses the coldstart-lab scripts against eggs-p8, with both the p5 expert panel and the Fable+Opus panel anchors as references.',
  phases: [{ title: 'Rate' }],
}

const ROOT = '/home/user/reasonable'
const H = 'eggs-p8/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents

function prompt(a) {
  return `You are rater "${a.id}" in a COOPERATIVE, BLIND argument-graph rating run about "Are eggs good for you?". Working directory: ${ROOT} — cd there first.

Read these files, then rate:
  1. ${H}/personas/${a.id}.md   — WHO YOU ARE and how you see this topic (rate from THIS worldview, honestly)
  2. ${H}/round_p8.md           — the task
  3. ${H}/assign/${a.id}.tsv    — node ids to rate (dim A)

This dataset is in ENFORCED blind Rating mode, so get-node never shows other raters' ratings/comments. For each node: read it once with get-node (claim + structure only), form your honest Agreement judgment FROM YOUR OWN PERSPECTIVE, and rate it:
  python3 graph.py get-node <nid> --data eggs-p8 --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data eggs-p8 --json
Rate every assigned node (abstain only if truly outside your knowledge). One read + one rate per item. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Rate')
log(`eggs-p8: ${agents.length} raters (2x2 disposition x model) rating all 79 nodes blind`)
const res = await parallel(agents.map(a => () =>
  agent(prompt(a), {
    label: `p8:${a.id}`, phase: 'Rate',
    model: a.model, effort: a.model === 'sonnet' ? 'high' : 'low',
  })))
return { returned: res.filter(Boolean).length }
