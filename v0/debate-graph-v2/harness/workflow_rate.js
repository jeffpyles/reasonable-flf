export const meta = {
  name: 'debate-v2-rate',
  description: 'Blind Haiku quorum panel over debate-graph-v2: A on the 16 unrated nodes, R+C on all 45 phrasings, conditional A on all 41 edges. 8 raters = 4 lenses x 2 seeds, bloc "cheap".',
  phases: [{ title: 'Rate' }],
}
const V0 = '/home/user/reasonable/v0'
const H = 'debate-graph-v2/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel
const bloc = A.bloc || 'cheap'

function prompt(a) {
  return `You are panelist "${a.id}" (independent rater #${a.seed}, ${a.persona} lens) in a COOPERATIVE, BLIND assessment of an argument graph about whether structured argument-mapping platforms can meaningfully improve reasoning on contested questions. Working dir: ${V0} -- cd there first. Dataset: --data debate-graph-v2.

Read these three files first:
  1. ${H}/personas/${a.persona}.md   -- your lens; follow it honestly
  2. ${H}/packet-blind.md            -- the full graph, blind (texts + structure, no scores)
  3. ${H}/assign/${a.id}.tsv         -- your targets, one per line as <target>\\t<dim>

Then rate EVERY line of the TSV, in order, using:
  python3 graph.py rate --agent ${a.id} --target <target> --dim <dim> --value <0.0-5.0> --bloc ${bloc} --data debate-graph-v2 --json

How to judge each dim:
- dim A on a NODE id (e.g. n004): kind 'claim'/'evidence' -> TRUTH / how well-supported the proposition is (0=clearly false .. 5=clearly true; a genuinely open question sits near the middle). kind 'ought' -> your ENDORSEMENT of the value (0=strongly oppose .. 5=strongly endorse), NOT truth. Kinds are in the packet.
- dim A on an EDGE id (e.g. e007): CONDITIONAL support only -- GRANT the FROM-node as true for the duration of the judgment, then ask how strongly it would support the TO-node. 5 = granting it near-compels the dependent; 3 = real but partial support, one good reason among several needed; 1 = barely bears on it. Do NOT let doubt about the FROM-node's own truth leak in (that lives in its node-A); do NOT punish an edge for not single-handedly proving its dependent.
- dim R on a phrasing (phrasing:nXXX:p0): REASONABLENESS of the expression -- is it a well-formed, honest, truth-apt single proposition, fairly framed, at the right grain (0=malformed/loaded .. 5=exemplary)?
- dim C on a phrasing: CLARITY of the wording -- could a newcomer parse it in one read (0=opaque .. 5=crystal)?

Discipline: rate from your own judgment of the packet text; the tool blinds you to others' scores -- do not try to infer them. Use the whole scale where deserved; reserve 0/5 for cases you would defend. Abstain (--value abstain) only if a target is truly outside your competence. BATCH your work: chain ~10 rate commands per bash call with '&&', and check each JSON says "ok": true. If a call fails on a lock timeout, wait 2s and retry it once. Never fabricate a result.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}
phase('Rate')
log(`debate-graph-v2: ${panel.length} Haiku raters x 147 targets, blind, bloc "${bloc}"`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), { label: `rate:${a.id}`, phase: 'Rate', model: 'haiku', effort: 'medium' })))
return { returned: res.filter(Boolean).length, of: panel.length, finals: res }
