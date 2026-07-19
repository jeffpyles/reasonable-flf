export const meta = {
  name: 'elicit-probe',
  description: 'Uniform structural probes over N graphs: per-node two-assertion (bundled?) probe and per-set both-true (genuine rival?) probe, so v1/harnessed/v2-hand can be compared on de-bundling and antithesis discipline.',
  phases: [{ title: 'Probe' }],
}
const V0 = '/home/user/reasonable/v0'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
// A.graphs = [{name, data}]
const graphs = A.graphs

const SCHEMA = {
  type: 'object', additionalProperties: false, required: ['nodes', 'sets'],
  properties: {
    nodes: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['id', 'bundled'],
      properties: {
        id: { type: 'string' },
        bundled: { type: 'boolean' },
        propositions: { type: 'integer' },
        reason: { type: 'string' } } } },
    sets: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['id', 'both_true'],
      properties: {
        id: { type: 'string' },
        both_true: { type: 'boolean' },
        reason: { type: 'string' } } } },
  },
}

function prompt(g) {
  return `You are a STRUCTURAL PROBE running two mechanical checks over an argument graph. Working dir: ${V0} (cd there). Read the graph: cat ${g.data}/graph.json (parse the "nodes" and "antithesis_sets" arrays; a node's text is phrasings[0].text, its kind is "kind"; skip any node/set with a "demoted" or "ghost_eligible" marker).

CHECK 1 -- TWO-ASSERTION probe, for EVERY live node:
Does the node's text assert MORE THAN ONE independently-rateable proposition? A node is "bundled" (bundled=true) if a careful rater would have to agree with one part and could disagree with another -- typically signalled by "X and Y" joining two claims, or "X, so Y" (a claim plus an inference that belongs on an edge), or a claim plus an evaluation. It is NOT bundled if the "and" is within a single proposition (e.g. a list of examples illustrating one claim, or "A and B" naming one compound entity). Report {id, bundled, propositions: how many independent propositions you count, reason: short}.

CHECK 2 -- BOTH-TRUE probe, for EVERY live antithesis set:
Antithesis sets are supposed to hold RIVAL positive claims -- at most one member can be true at once. For each set, could TWO OR MORE of its members be true SIMULTANEOUSLY? If yes (one member merely answers, challenges, or is compatible with another rather than excluding it), both_true=true -- it is NOT a genuine rivalry. If the members genuinely exclude each other (a real "X is so" vs "not-X is so" / "A caused it" vs "B caused it"), both_true=false. Report {id, both_true, reason: short}.

Judge honestly and mechanically from the texts alone. Return the structured object with an entry for every live node and every live set.`
}

phase('Probe')
log(`probing ${graphs.length} graphs`)
const results = await parallel(graphs.map(g => () =>
  agent(prompt(g), { label: `probe:${g.name}`, phase: 'Probe', model: 'haiku', effort: 'high', schema: SCHEMA })
    .then(r => ({ name: g.name, data: g.data, ...r }))))
return { results: results.filter(Boolean) }
