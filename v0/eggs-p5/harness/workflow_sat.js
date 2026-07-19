export const meta = {
  name: 'eggs-p5-expert-saturation',
  description: 'Send the 8 experts back to rate + predict ALL remaining node items, raising expert density per item from ~13% to ~33%, to test whether BTS finds signal at higher quality-rater concentration.',
  phases: [{ title: 'Expert saturation' }, { title: 'Score' }],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-p5/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const experts = A.experts   // ["s01-lipidologist", ...]

function prompt(id) {
  return `You are rater "${id}", a domain EXPERT in a cooperative argument-graph rating run (question: "Are eggs good for you?"). Working directory: ${V0} — cd there first.

Read your persona brief (${H}/personas/${id}.md — who you are, the rating rules, and the meta-prediction rule) and your assignment (${H}/assign/sat/${id}.tsv — node Agreement items, "target<TAB>dim<TAB>bloc"). This is a saturation pass: you are rating the remaining items so that all experts cover every claim.

For EACH assigned item, in order: (a) read it once with get-node; (b) rate it on the merits with your sharp, discriminating eye; (c) IMMEDIATELY predict how the REST of the crowd (mostly NON-experts) will rate it, as a low/mid/high split — your honest model of what the TYPICAL non-expert rater will do, which will often differ from your own rating:
  python3 graph.py rate --agent ${id} --target <target> --dim A --value <0.0-5.0> --bloc <bloc> --data eggs-p5 --json
  python3 eggs-p5/harness/predict.py --agent ${id} --target <target> --dim A --low <L> --mid <M> --high <H> --data eggs-p5 --json
Buckets: low [0,2), mid [2,3.5), high [3.5,5]. Use --value abstain (skip the prediction) only for items truly outside your knowledge. Put real thought into BOTH the rating and the crowd-prediction. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate.

Your FINAL message must be ONLY: "${id}: rated N, predicted P, abstained X".`
}

phase('Expert saturation')
log(`Saturating: ${experts.length} experts rating + predicting all remaining node items`)
const res = await parallel(experts.map(id => () =>
  agent(prompt(id), { label: `sat:${id}`, phase: 'Expert saturation', model: 'sonnet', effort: 'high' })))
log(`Saturation complete: ${res.filter(Boolean).length}/${experts.length} experts returned`)

phase('Score')
const score = await agent(
  `cd ${V0}. Run: python3 ${H}/bts_score.py . Report its full stdout verbatim.`,
  { label: 'bts_score', phase: 'Score' })

return { returned: res.filter(Boolean).length, score }
