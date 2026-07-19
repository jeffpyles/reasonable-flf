export const meta = {
  name: 'eggs-p5-bts-run',
  description: 'Single rate-and-predict pass: 60 agents rate 79 node-Agreement items AND predict the crowd distribution (Bayesian Truth Serum), to test whether real LLM experts predict the crowd better than the crowd predicts itself, and whether BTS lifts the experts where alignment buried them.',
  phases: [
    { title: 'Rate & predict' },
    { title: 'Score' },
  ],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-p5/harness'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents               // experts-first ordering (slowest finish earliest)

function raterPrompt(a) {
  return `You are rater "${a.id}" in a COOPERATIVE argument-graph rating run (question: "Are eggs good for you?"). You are doing your honest best. Working directory: ${V0} — cd there first.

Read these three files, then do the work:
  1. ${H}/personas/${a.id}.md          — who you are, the rating rules, and the meta-prediction rule
  2. ${H}/round_bts.md                 — the task
  3. ${H}/assign/r1/${a.id}.tsv        — your assigned items: "target<TAB>dim<TAB>bloc" (all are node Agreement)

For EACH assigned item, in order: (a) read it once with get-node; (b) form your own honest judgment and
rate it; (c) IMMEDIATELY predict how the REST of the crowd will rate it, as a low/mid/high split:
  python3 graph.py rate --agent ${a.id} --target <target> --dim A --value <0.0-5.0> --bloc <bloc> --data eggs-p5 --json
  python3 eggs-p5/harness/predict.py --agent ${a.id} --target <target> --dim A --low <L> --mid <M> --high <H> --data eggs-p5 --json
The prediction is your honest guess of what the TYPICAL OTHER rater will do (buckets: low [0,2), mid
[2,3.5), high [3.5,5]) — it may differ from your own rating, especially where you expect the crowd to
see it differently than you. Use --value abstain (and skip the prediction) only for items outside your
knowledge. Writes are lock-serialized; on a lock-timeout wait ~2s and retry ONCE. Do NOT fabricate.
Keep commands proportionate: one read + one rate + one predict per item.

Your FINAL message must be ONLY: "${a.id}: rated N, predicted P, abstained X".`
}

phase('Rate & predict')
log(`eggs-p5: ${agents.length} raters (${agents.filter(a => a.tier === 'expert').length} experts) rating + predicting 79 node items`)
const res = await parallel(agents.map(a => () =>
  agent(raterPrompt(a), {
    label: `p5:${a.id}`, phase: 'Rate & predict',
    model: a.model, effort: a.model === 'sonnet' ? 'high' : 'low',
  })))
log(`Rate & predict complete: ${res.filter(Boolean).length}/${agents.length} returned`)

phase('Score')
const score = await agent(
  `cd ${V0}. Run: python3 ${H}/bts_score.py . Report its full stdout verbatim (the method comparison table and the prediction-accuracy line).`,
  { label: 'bts_score', phase: 'Score' })

return { returned: res.filter(Boolean).length, score }
