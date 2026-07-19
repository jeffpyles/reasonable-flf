export const meta = {
  name: 'covid-graph-build',
  description: 'Coverage-driven sequential build of a fresh SARS-CoV-2-origins argument graph from a deep-research report + its sources. Persona-diverse Sonnet authors run one at a time (each sees all prior work) so every isolatable claim gets extracted, placed, phrased, and connected without duplication. Backbone for the report-vs-graph comparison.',
  phases: [{ title: 'Build' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'covid-graph/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const authors = A.authors  // ordered list: [{id, model}]

function prompt(a, idx, total) {
  return `You are author "${a.id}" (#${idx + 1} of ${total}) building a COOPERATIVE argument graph for "Did SARS-CoV-2 arise by natural zoonotic spillover or by a research-related incident?". Working directory: ${V0} — cd there first. Dataset: --data covid-graph.

Read, in order:
  1. ${V0}/AGENT-GUIDE.md              — the binding mental model + norm discipline + verb reference
  2. ${H}/round_build.md              — THIS round's coverage-driven task and rules
  3. ${H}/personas/${a.id}.md         — who you are and which evidence cluster you own
  4. ${H}/REPORT.md                   — the deep-research synthesis + its verified claim list
  5. ${H}/sources.json                — the exact sources (filter to your cluster's tags)

Then build your cluster to FULL DEPTH: every isolatable claim extracted, placed, phrased, connected;
shared facts anchored as external_anchor nodes cited to a sources.json id; interpretive cruxes left
as un-anchored rival positive claims in antithesis sets; friction flagged wherever the grammar
strains. ALWAYS \`search\` before \`create-node\`. Support-only — no "not-X" nodes. Writes are
lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate claims or citations.

Your FINAL message must be ONLY the one-line coverage report specified at the end of round_build.md.`
}

phase('Build')
log(`covid-graph build: ${authors.length} authors, sequential (each sees prior work)`)
const results = []
for (let i = 0; i < authors.length; i++) {
  const a = authors[i]
  const r = await agent(prompt(a, i, authors.length), {
    label: `build:${a.id}`, phase: 'Build',
    model: a.model || 'sonnet', effort: 'high',
  })
  results.push({ id: a.id, line: r })
  log(`${a.id} done (${i + 1}/${authors.length})`)
}
return { authors: results }
