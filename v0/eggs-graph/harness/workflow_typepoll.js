export const meta = {
  name: 'eggs-typepoll',
  description: 'Migrate the eggs flag_type markers (n063, n064 flagged as candidate oughts) into resolved polls: 5 independent voters read each flagged node and vote Yes/No/decline on whether it is prescriptive (an ought). Demonstrates the flag->poll->reputation-weighted-resolution loop end to end.',
  phases: [{ title: 'Vote' }],
}
const V0 = '/home/user/reasonable/v0'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const voters = A.voters
const targets = [
  { node: 'n063', text: "For most people, eggs' nutritional benefits outweigh their modest, contested cardiovascular/mortality risk, making them a reasonable part of a healthy diet." },
  { node: 'n064', text: "Given the genuinely unresolved causal question and the type-2-diabetes subgroup risk, a precautionary approach to egg / dietary-cholesterol intake is warranted for most people." },
]
function prompt(v) {
  const items = targets.map(t => `  ${t.node}: "${t.text}"`).join('\n')
  return `You are voter "${v.id}" in a categorical TYPE poll on the eggs argument graph. Working dir: ${V0} -- cd there first. Dataset: --data eggs-graph.

The question for each node is: "Is this node an OUGHT -- a prescriptive/value claim (about what one should do or what is worthwhile) -- rather than a descriptive factual claim?" Vote your honest judgment.
Nodes under poll:
${items}

For EACH node, cast one vote (yes = it is an ought / prescriptive; no = it is descriptive/factual; decline = genuinely can't tell):
  python3 graph.py poll-vote --agent ${v.id} --node <n063|n064> --question type:ought --value <yes|no|decline> --data eggs-graph --json
Judge each independently and honestly -- a node that merely weighs facts may be descriptive; a node recommending an action or asserting something is "worthwhile"/"warranted"/"reasonable to do" is prescriptive. On a lock-timeout wait ~2s and retry ONCE.

Your FINAL message must be ONLY: "${v.id}: voted on 2 nodes".`
}
phase('Vote')
log(`eggs type-poll: ${voters.length} voters on n063/n064`)
const res = await parallel(voters.map(v => () =>
  agent(prompt(v), { label: `vote:${v.id}`, phase: 'Vote', model: v.model || 'haiku', effort: 'low' })))
return { returned: res.filter(Boolean).length, of: voters.length }
