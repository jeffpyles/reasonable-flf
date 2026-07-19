export const meta = {
  name: 'blackholes-oracle-panel',
  description: 'Cross-model oracle panel for the black-holes graph: 4 panelists (sonnet x2 seeds, opus, fable) each independently score all 69 nodes on Agreement, on the merits, to build a ground-truth reference (anchors.json). This is a TRUTH reference, not a blind crowd rating — panelists reason carefully from best judgment; genuinely contested cruxes should land near the middle.',
  phases: [{ title: 'Oracle' }],
}

const V0 = '/home/user/reasonable/v0'
const DUMP = 'blackholes-graph/oracle/oracle_nodes.md'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const panel = A.panel  // [{id, model, seed}]

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['panelist', 'scores'],
  properties: {
    panelist: { type: 'string' },
    scores: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['node', 'score'],
        properties: { node: { type: 'string' }, score: { type: 'number', minimum: 0, maximum: 5 } },
      },
    },
  },
}

function prompt(a) {
  return `You are oracle panelist "${a.id}" (independent judge #${a.seed || 1}) building a GROUND-TRUTH reference for a black-holes-safety argument graph. Working directory: ${V0} — cd there first.

Read the full node dump: ${DUMP}. It contains all 69 nodes (evidence/source-facts and interpretive claims) with the exact rating rubric at the top.

Score EVERY node on Agreement (A), 0.0-5.0, on the MERITS from your own best judgment — this is a truth reference, not a crowd vote, so reason carefully and do NOT try to match anyone. Follow the rubric: settled facts near their true well-establishedness; a genuinely contested crux near the middle (not the extremes); the safe-vs-catastrophe verdict nodes at where the actual balance of evidence sits.

You do not need to run any graph.py commands — judge from the dump text. Return your scores for ALL 69 nodes via the StructuredOutput tool: {panelist: "${a.id}", scores: [{node, score}, ...]}. Every node id in the dump must appear exactly once.`
}

phase('Oracle')
log(`BH oracle: ${panel.length} cross-model panelists scoring all 69 nodes independently`)
const res = await parallel(panel.map(a => () =>
  agent(prompt(a), {
    label: `oracle:${a.id}`, phase: 'Oracle',
    model: a.model, effort: 'high', schema: SCHEMA,
  }).then(r => r && ({ panelist: a.id, scores: r.scores }))))
return res.filter(Boolean)
