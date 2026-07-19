export const meta = {
  name: 'blackholes-v2-rate',
  description: 'Blind Haiku quorum panel over blackholes-graph-v2: A on the 1 new limb, R+C on all 70 phrasings, conditional A on all 79 edges. 8 raters = 4 lenses x 2 seeds, bloc "cheap", tenths enforced.',
  phases: [{ title: 'Rate' }],
}
const V0 = '/home/user/reasonable/v0'
const H = 'blackholes-graph-v2/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel
const bloc = A.bloc || 'cheap'

function prompt(a) {
  return `You are panelist "${a.id}" (independent rater #${a.seed}, ${a.persona} lens) in a COOPERATIVE, BLIND assessment of an argument graph about whether the LHC could create a black hole that destroys Earth. Working dir: ${V0} -- cd there first. Dataset: --data blackholes-graph-v2.

Read these three files first:
  1. ${H}/personas/${a.persona}.md   -- your lens; follow it honestly
  2. ${H}/packet-blind.md            -- the full graph, blind (texts + structure, no scores)
  3. ${H}/assign/${a.id}.tsv         -- your targets, one per line as <target>\\t<dim>

Then rate EVERY line of the TSV, in order, using:
  python3 graph.py rate --agent ${a.id} --target <target> --dim <dim> --value <0.0-5.0> --bloc ${bloc} --data blackholes-graph-v2 --json

CRITICAL -- RATE IN TENTHS. The scale is continuous to one decimal: 3.7, 4.2, 2.6 are all normal, expected values. Do NOT round everything to whole or half points; a rater who only ever says 3.0/3.5/4.0 throws away most of the scale. Use the specific tenth that matches your judgment.

How to judge each dim (the packet lists every node's KIND; this graph has only claim/evidence, no oughts):
- dim A on a NODE: TRUTH / how well-supported the proposition is (0=clearly false .. 5=clearly true; a genuinely open question sits near the middle). For an evidence node, judge fidelity -- does the cited source really say this.
- dim A on an EDGE: CONDITIONAL support only -- GRANT the FROM-node as true for the judgment, then ask how strongly it would support the TO-node. 5=granting it near-compels the dependent; 3=real but partial support, one good reason among several; 1=barely bears on it. Do NOT let doubt about the FROM-node's own truth leak in (that lives in its node-A); do NOT punish an edge for not single-handedly proving its dependent. For a conjunction-group member edge, the member alone isn't claimed to support anything -- rate it ~3 or abstain and note the group rates jointly.
- dim R on a phrasing (phrasing:nXXX:p0): REASONABLENESS of the expression -- well-formed, honest, truth-apt single proposition, fairly framed, right grain (0=malformed/loaded .. 5=exemplary).
- dim C on a phrasing: CLARITY -- could a newcomer parse it in one read (0=opaque .. 5=crystal).

Discipline: rate from your own judgment of the packet; the tool blinds you to others' scores. Reserve 0/5 for cases you would defend. Abstain (--value abstain) only if a target is truly outside your competence. BATCH your work: chain ~12 rate commands per bash call with '&&', and check each JSON says "ok": true. On a lock timeout wait 2s and retry that one call once. Never fabricate a result.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}
phase('Rate')
log(`blackholes-graph-v2: ${panel.length} Haiku raters x 220 targets, blind, bloc "${bloc}", tenths enforced`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), { label: `rate:${a.id}`, phase: 'Rate', model: 'haiku', effort: 'medium' })))
return { returned: res.filter(Boolean).length, of: panel.length, finals: res }
