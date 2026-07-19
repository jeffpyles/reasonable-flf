export const meta = {
  name: 'eggs-p7-mild-divide',
  description: 'Mild/graded-divide run: 28 agents (8 strong-lean + 8 slight-lean Haiku, 3 haiku + 3 sonnet neutral, 6 sonnet evidence-trackers) each rate all 79 node claims blind. A WEAK, overlapping directional bias makes the two camps soft — the hard regime for camp-detection / adjudication (coldstart-lab E9). The neutral haiku-vs-sonnet split adds a model-only contrast for the ranking-speed question (E2). Offline analysis reuses the coldstart-lab scripts against eggs-p7.',
  phases: [{ title: 'Rate' }],
}

const ROOT = '/home/user/reasonable'
const H = 'eggs-p7/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents   // pass roster.agents; competent/sonnet first is fine

function prompt(a) {
  return `You are rater "${a.id}" in a COOPERATIVE, BLIND argument-graph rating run about "Are eggs good for you?". Working directory: ${ROOT} — cd there first.

Read these files, then rate:
  1. ${H}/personas/${a.id}.md   — WHO YOU ARE and how you see this topic (rate from THIS worldview, honestly)
  2. ${H}/round_p7.md           — the task
  3. ${H}/assign/${a.id}.tsv    — node ids to rate (dim A)

This dataset is in ENFORCED blind Rating mode (config rating_mode_only), so every read is automatically blinded — you cannot see existing ratings/comments no matter how you read. For each node: read it once with get-node (claim text + structure, no consensus), form your honest Agreement judgment FROM YOUR OWN PERSPECTIVE, and rate it:
  python3 graph.py get-node <nid> --data eggs-p7 --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data eggs-p7 --json
Rate every assigned node (abstain only if truly outside your knowledge). One read + one rate per item. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Rate')
log(`eggs-p7: ${agents.length} raters (graded mild divide) rating all 79 nodes blind`)
const res = await parallel(agents.map(a => () =>
  agent(prompt(a), {
    label: `p7:${a.id}`, phase: 'Rate',
    model: a.model, effort: a.model === 'sonnet' ? 'high' : 'low',
  })))
return { returned: res.filter(Boolean).length }
