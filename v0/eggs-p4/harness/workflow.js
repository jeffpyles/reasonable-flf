export const meta = {
  name: 'eggs-p4-volume-run',
  description: 'High-volume cooperative rating run on the eggs graph: 60 agents (52 Haiku crowd + 8 Sonnet experts) rate every item in depth across 3 turns; measures whether experts get rewarded or penalized under a blunter majority.',
  phases: [
    { title: 'Setup — assignments' },
    { title: 'Round 1 — seed & rate' },
    { title: 'Coordinate 1to2' },
    { title: 'Round 2 — deepen & respond' },
    { title: 'Coordinate 2to3' },
    { title: 'Round 3 — converge & influence' },
    { title: 'Final analysis' },
  ],
}

const V0 = '/home/user/reasonable/v0'
const H = 'eggs-p4/harness'
// args may arrive as a parsed object OR a JSON string depending on the caller
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const agents = A.agents                  // [{id, model, tier}, ...]
const nExpert = agents.filter(a => a.tier === 'expert').length

function raterPrompt(a, round) {
  return `You are rater "${a.id}" in a COOPERATIVE argument-graph rating run (question: "Are eggs good for you?"). You are doing your honest best. Working directory: ${V0} — cd there first.

Read these three files, in order, then do the work with the graph.py CLI:
  1. ${H}/personas/${a.id}.md          — who you are, how you rate, and the rules
  2. ${H}/round${round}.md             — what to do this round
  3. ${H}/assign/r${round}/${a.id}.tsv — your assigned items: lines of "target<TAB>dim<TAB>bloc"

Work efficiently, item by item: for each line, read the item ONCE with a single get-node (on the node,
or on the node an edge/phrasing belongs to), form your honest judgment from your persona's perspective,
then rate it. Do not re-read items you've already seen or explore beyond what you need to judge.
  python3 graph.py rate --agent ${a.id} --target <target> --dim <dim> --value <0.0-5.0> --bloc <bloc> --data eggs-p4 --json
Use the literal value "abstain" (--value abstain) for items outside your knowledge. Then do the extra
per-round actions in the round file: list-comments only on the few items where you diverge most; comment
only when you have something specific to say; and — ONLY if your persona says you are a builder — you may
add AT MOST ONE missing claim from the source material this round (skip in round 3).

This is a SHARED graph many raters are editing at once. Writes are serialized by a lock; if a graph.py
call fails with a lock-timeout, wait ~2s and retry ONCE. Do NOT fabricate evidence or citations. Finish
your whole assignment, but keep your total number of shell commands proportionate (roughly one read + one
rate per assigned item, plus a handful of extra actions).

Your FINAL message must be ONLY the one-line summary the round file specifies (e.g. "${a.id}: rated N, ...").`
}

function coordPrompt(doneRound, nextRound, targetDepth) {
  return `cd ${V0}. You are the run coordinator between rounds — run exactly these two commands in order and report their JSON output. Do not edit anything else, do not rate.
  1. python3 ${H}/snapshot.py --data eggs-p4 --round ${doneRound}
  2. python3 ${H}/gen_assign.py --data eggs-p4 --round ${nextRound} --target-depth ${targetDepth} --max-per-agent 18
Return the parsed JSON from each command.`
}

const COORD_SCHEMA = {
  type: 'object',
  properties: {
    snapshot: {
      type: 'object',
      properties: {
        round: { type: 'number' },
        expert_mean_true_r: { type: ['number', 'null'] },
        crowd_mean_true_r: { type: ['number', 'null'] },
        expert_minus_crowd: { type: ['number', 'null'] },
        verdict: { type: ['string', 'null'] },
        depth_median: { type: 'number' },
        items_ge_15: { type: 'number' },
        nodes: { type: 'number' },
        events: { type: ['number', 'null'] },
      },
      required: ['round', 'expert_minus_crowd', 'verdict', 'depth_median', 'nodes'],
    },
    next_assignment: {
      type: 'object',
      properties: {
        round: { type: 'number' },
        total_new_ratings: { type: 'number' },
        median_reached_depth: { type: 'number' },
        min_reached_depth: { type: 'number' },
        per_agent_mean: { type: 'number' },
      },
      required: ['round', 'total_new_ratings'],
    },
  },
  required: ['snapshot', 'next_assignment'],
}

// Experts reason hard (they must argue); the Haiku crowd is deliberately quick
// ("hasty, context-weak" is the realistic baseline) — low effort also keeps the
// 60-agent x 3-round run affordable.
function effortFor(a) { return a.model === 'sonnet' ? 'high' : 'low' }

async function runRound(round, title) {
  phase(title)
  log(`Round ${round}: ${agents.length} raters (${nExpert} experts) working the shared graph`)
  const res = await parallel(agents.map(a => () =>
    agent(raterPrompt(a, round), {
      label: `r${round}:${a.id}`, phase: title,
      model: a.model, effort: effortFor(a),
    })))
  const done = res.filter(Boolean).length
  log(`Round ${round} complete: ${done}/${agents.length} raters returned`)
  return done
}

// ---- Setup: (re)generate round-1 assignments + baseline snapshot ----
phase('Setup — assignments')
await agent(
  `cd ${V0}. Run exactly these two commands in order and report their JSON output; edit nothing else:
  1. python3 ${H}/gen_persona.py
  2. python3 ${H}/snapshot.py --data eggs-p4 --round 0
  3. python3 ${H}/gen_assign.py --data eggs-p4 --round 1 --target-depth 8 --max-per-agent 18`,
  { label: 'setup', phase: 'Setup — assignments' })

// ---- Round 1 ----
await runRound(1, 'Round 1 — seed & rate')
phase('Coordinate 1to2')
const c1 = await agent(coordPrompt(1, 2, 14), { label: 'coord:1to2', phase: 'Coordinate 1to2', schema: COORD_SCHEMA })
log(`After R1 — expert vs crowd True_R: ${c1?.snapshot?.expert_minus_crowd} (${c1?.snapshot?.verdict}); median depth ${c1?.snapshot?.depth_median}, ${c1?.snapshot?.nodes} nodes`)

// ---- Round 2 ----
await runRound(2, 'Round 2 — deepen & respond')
phase('Coordinate 2to3')
const c2 = await agent(coordPrompt(2, 3, 18), { label: 'coord:2to3', phase: 'Coordinate 2to3', schema: COORD_SCHEMA })
log(`After R2 — expert vs crowd True_R: ${c2?.snapshot?.expert_minus_crowd} (${c2?.snapshot?.verdict}); median depth ${c2?.snapshot?.depth_median}, ${c2?.snapshot?.nodes} nodes`)

// ---- Round 3 ----
await runRound(3, 'Round 3 — converge & influence')

// ---- Final analysis ----
phase('Final analysis')
const finalSnap = await agent(
  `cd ${V0}. Run: python3 ${H}/snapshot.py --data eggs-p4 --round 3 . Report its JSON output verbatim.`,
  { label: 'snapshot:r3', phase: 'Final analysis' })

const analysis = await agent(
  `cd ${V0}. You are the analyst for a high-volume cooperative rating experiment on the "eggs" argument graph.
Read these, then write findings:
  - ${H}/snapshots/r0.md, r1.md, r2.md, r3.md (and the matching .json files for exact numbers)
  - eggs-p4/CHECKPOINT.md (the prior eggs-p3 finding: alignment-to-consensus PENALIZED expertise — experts
    landed BELOW blunt Haiku raters, a tyranny-of-the-median pathology)

The central question this run tests: under high VOLUME, multiple TURNS, earned REPUTATION, and the ability
to ARGUE (comments/phrasings/new grounds), do the 8 Sonnet experts get REWARDED for sharper judgment, or do
they stay PENALIZED by a blunter Haiku majority as in eggs-p3? Track the expert-minus-crowd True_R gap and
expert percentile ACROSS rounds 1→2→3 (trajectory is the key evidence: does the gap close or even flip?).
Also assess: did reasonableness emerge in the aggregate (are well-reasoned claims rated higher than weak
ones)? Did experts successfully MOVE any consensus through argument (contested items shifting toward the
expert view)? What is the reputation variance and does it track competence?

Write your analysis to ${V0}/eggs-p4/FINDINGS.md — honest, specific, with the round-by-round numbers, clearly
separating what the data shows from what it doesn't. Note caveats (single run, model-as-proxy-for-expertise,
legacy p3 ratings in the log). Then return a 6-8 sentence summary of the headline result.`,
  { label: 'analysis', phase: 'Final analysis', model: 'sonnet', effort: 'high' })

return {
  rounds_done: 3,
  after_r1: c1?.snapshot ?? null,
  after_r2: c2?.snapshot ?? null,
  final_snapshot_raw: finalSnap,
  analysis_summary: analysis,
}
