export const meta = {
  name: 'debate-graph-rate',
  description: 'Blind panel rating of the debate-graph (Scott-vs-Reasonable). 12 raters (4 lens-personas x 3 seeds) rate all 28 nodes on Agreement -- truth for claim/evidence, ENDORSEMENT for ought nodes -- so the assessed map shows settled-where-facts-settle vs contested-where-values-diverge.',
  phases: [{ title: 'Rate' }],
}
const V0 = '/home/user/reasonable/v0'
const H = 'debate-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel

function prompt(a) {
  return `You are panelist "${a.id}" (independent rater #${a.seed} for the ${a.persona} lens) in a COOPERATIVE, BLIND assessment of an argument graph about the question: "Will a structured argument-mapping platform meaningfully improve reasoning on contested questions, or (per Scott Alexander) will attempts to 'solve debate' not work?" Working dir: ${V0} -- cd there first. Dataset: --data debate-graph.

Read, then rate:
  1. ${H}/personas/${a.persona}.md   -- your lens (follow it honestly)
  2. ${H}/assign/${a.id}.tsv         -- node ids to rate, one per line as <nid>\\tA\\tb1

Blind Rating mode: \`get-node\` shows the claim + its Ground/Dependent structure + its KIND, but never others' scores.
For EACH assigned node, read it, then rate dim A (0.0-5.0):
  - kind 'claim' or 'evidence' -> rate TRUTH / how well-supported it is (0=clearly false .. 5=clearly true). A genuinely open question sits near the middle.
  - kind 'ought' -> rate your ENDORSEMENT of the value/action (0=strongly oppose .. 5=strongly endorse). This is NOT a truth judgment; endorse or oppose the value from your lens.
Commands:
  python3 graph.py get-node <nid> --data debate-graph --json
  python3 graph.py rate --agent ${a.id} --target <nid> --dim A --value <0.0-5.0> --bloc b1 --data debate-graph --json
Rate honestly from your lens. Abstain only if truly outside your competence. One read + one rate per item. On a lock-timeout wait ~2s and retry ONCE. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}
phase('Rate')
log(`debate-graph: ${panel.length} raters (Sonnet) rating all 28 nodes blind; oughts on endorsement`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), { label: `rate:${a.id}`, phase: 'Rate', model: a.model, effort: 'high' })))
return { returned: res.filter(Boolean).length, of: panel.length }
