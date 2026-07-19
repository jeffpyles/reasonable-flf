export const meta = {
  name: 'covid-rate',
  description: 'Blind rating run on the covid graph: each assigned agent reads its persona + assignment and rates all nodes on Agreement (enforced Rating mode). Drives both the honest run and the sleeper run via args.agents.',
  phases: [{ title: 'Rate' }],
}

const ROOT = '/home/user/reasonable'
const H = 'covid/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents
const RUN = A.run || 'rate'

function prompt(a) {
  return `You are rater "${a.id}" in a BLIND argument-graph rating run about "Did SARS-CoV-2 arise by natural zoonotic spillover or by a research-related incident?". Working directory: ${ROOT} — cd there first.

Read these two files, then rate:
  1. ${H}/personas/${a.id}.md   — WHO YOU ARE and how to rate (read and follow it exactly)
  2. ${H}/assign/${a.id}.tsv    — the node ids to rate, one per line as <nid>\\tA\\t<bloc>\\t<mark>

This dataset is in ENFORCED blind Rating mode, so \`get-node\` shows the claim + its Ground/Dependent structure but NEVER other raters' ratings. For each assigned node: read it once, form your judgment per your persona, and rate it:
  python3 graph.py get-node <nid> --data covid --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc <bloc> --data covid --json
The <bloc> is the 3rd column of each assignment line (use it verbatim). The 4th column (<mark>) is your persona's instruction for that node — HONEST means rate on merits; PUSH-UP / PUSH-DOWN mean rate per your persona's playbook (honest raters: every mark is HONEST, just rate from your worldview). Rate EVERY assigned node (abstain only if a claim is truly outside your knowledge). One read + one rate per item. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}

phase('Rate')
log(`covid ${RUN}: ${agents.length} raters rating all nodes blind`)
const res = await parallel(agents.map(a => () =>
  agent(prompt(a), {
    label: `${RUN}:${a.id}`, phase: 'Rate',
    model: a.model, effort: a.model === 'sonnet' ? 'high' : 'low',
  })))
return { run: RUN, returned: res.filter(Boolean).length, of: agents.length }
