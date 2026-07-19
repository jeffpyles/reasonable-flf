export const meta = {
  name: 'covid-v2-rate',
  description: 'Blind Haiku quorum fill over covid-graph-v2, split by dimension-group to keep per-rater load proven-size. phase="rc" rates R+C on all 133 phrasings; phase="a" rates A on 24 under-quorum nodes + all 187 edges. 8 raters, bloc "cheap", tenths enforced.',
  phases: [{ title: 'Rate' }],
}
const V0 = '/home/user/reasonable/v0'
const H = 'covid-graph-v2/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel
const bloc = A.bloc || 'cheap'
const which = A.which || 'rc'   // "rc" or "a"
const assignSuffix = which === 'a' ? 'a.tsv' : 'rc.tsv'

function prompt(a) {
  return `You are panelist "${a.id}" (independent rater #${a.seed}, ${a.persona} lens) in a COOPERATIVE, BLIND assessment of an argument graph about the origin of SARS-CoV-2 (natural zoonotic spillover vs a research-related incident vs genuinely unresolved). Working dir: ${V0} -- cd there first. Dataset: --data covid-graph-v2.

Read these first:
  1. ${H}/personas/${a.persona}.md   -- your lens; follow it honestly
  2. ${H}/packet-blind.md            -- the full graph, blind (texts + structure, no scores)
  3. ${H}/assign/${a.id}.${assignSuffix}  -- your targets, one per line as <target>\\t<dim>

Then rate EVERY line of the TSV, in order, using:
  python3 graph.py rate --agent ${a.id} --target <target> --dim <dim> --value <0.0-5.0> --bloc ${bloc} --data covid-graph-v2 --json

CRITICAL -- RATE IN TENTHS. The scale is continuous to one decimal: 3.7, 4.2, 2.6 are all normal values. Do NOT round everything to whole/half points; use the specific tenth matching your judgment.

This is a GENUINELY CONTESTED question -- rate honestly from your lens; many claims will sit mid-scale, and rival interpretations of the same evidence can BOTH be moderate. Do not force a side.

How to judge each dim (kinds are in the packet; claim/evidence only, no oughts):
- dim A on a NODE: TRUTH / how well-supported the proposition is (0=clearly false .. 5=clearly true; a genuinely open interpretive claim sits near the middle). For an evidence node, judge fidelity -- does the cited source really say this.
- dim A on an EDGE: CONDITIONAL support only -- GRANT the FROM-node true, then ask how strongly it supports the TO-node. 5=granting it near-compels the dependent; 3=real but partial; 1=barely bears. Do NOT let doubt about the FROM-node's own truth leak in; do NOT punish an edge for not single-handedly proving its dependent. For a conjunction-group member edge, rate ~3 or abstain (the group rates jointly).
- dim R on a phrasing: REASONABLENESS -- well-formed, honest, truth-apt single proposition, fairly framed, right grain (0=malformed/loaded .. 5=exemplary). A fairly-stated rival position rates HIGH on R even if you disagree with it.
- dim C on a phrasing: CLARITY -- parseable in one read (0=opaque .. 5=crystal).

Discipline: rate from your own judgment; the tool blinds you to others' scores. Reserve 0/5 for defensible cases. Abstain (--value abstain) only if truly outside your competence. BATCH: chain ~15 rate commands per bash call with '&&', check each JSON "ok":true. On a lock timeout wait 2s and retry that one call once. Never fabricate.

Your FINAL message must be ONLY: "${a.id}: rated N, abstained X".`
}
phase('Rate')
log(`covid-graph-v2 [${which}]: ${panel.length} Haiku raters, blind, bloc "${bloc}", tenths enforced`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), { label: `rate:${a.id}:${which}`, phase: 'Rate', model: 'haiku', effort: 'medium' })))
return { which, returned: res.filter(Boolean).length, of: panel.length }
