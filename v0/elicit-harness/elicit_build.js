export const meta = {
  name: 'elicit-build',
  description: 'Elicitation harness: build an argument graph from an unstructured source brief using the skeleton-first + authoring-checks discipline, to test whether Sonnet-level agents can produce the hand-built v2 structure with better guidance.',
  phases: [
    { title: 'Plan',       detail: 'one planner proposes theses + mirrored limb skeleton' },
    { title: 'Scaffold',   detail: 'create roots + limbs, wire limbs->roots' },
    { title: 'Populate',   detail: 'one build agent per limb authors + attaches leaves' },
    { title: 'Antithesis', detail: 'wire rival sets under the both-true gate' },
  ],
}
const V0 = '/home/user/reasonable/v0'
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const DATA = A.data || 'elicit-harness/out-debate'
const BRIEF = A.brief || 'elicit-harness/SOURCE-BRIEF-debate.md'
const MODEL = A.model || 'sonnet'

const SKELETON = {
  type: 'object', additionalProperties: false,
  required: ['roots', 'limbs', 'value_crux'],
  properties: {
    roots: { type: 'array', minItems: 2, items: {
      type: 'object', additionalProperties: false, required: ['key', 'title', 'thesis'],
      properties: { key: {type:'string'}, title: {type:'string'}, thesis: {type:'string'} } } },
    limbs: { type: 'array', minItems: 4, items: {
      type: 'object', additionalProperties: false, required: ['key', 'root_key', 'title', 'gloss'],
      properties: { key:{type:'string'}, root_key:{type:'string'}, title:{type:'string'}, gloss:{type:'string'},
        mirror_of: {type:'string'} } } },
    value_crux: { type: 'object', additionalProperties: false, required: ['ought_a','ought_b'],
      properties: { ought_a:{type:'string'}, ought_b:{type:'string'} } },
  },
}
const IDMAP = { type:'object', additionalProperties:false, required:['ids'],
  properties: { ids: { type:'array', items: {
    type:'object', additionalProperties:false, required:['key','id'],
    properties: { key:{type:'string'}, id:{type:'string'} } } } } }
const LEAVES = { type:'object', additionalProperties:false, required:['created'],
  properties: { created: { type:'array', items: {
    type:'object', additionalProperties:false, required:['id','title','text'],
    properties: { id:{type:'string'}, title:{type:'string'}, text:{type:'string'} } } } } }

// ---------- Phase 1: PLAN ----------
phase('Plan')
const plan = await agent(
`You are the PLANNER for an argument graph. Read the source brief: ${V0}/${BRIEF} (cat it).

Your job is ONLY to design the SKELETON, before any detailed claims are written -- this is the
single most important discipline in this harness. Produce:
- The ROOT positions: the 2-3 top-level rival theses the whole question is about (e.g. the skeptic
  thesis, the builder thesis, and any honest dissolution). Each gets a one-sentence thesis and a
  <=8-word scannable title.
- The LIMBS: for each root, the 3-4 intermediate "families of reason" that its detailed grounds will
  hang under -- NOT the detailed grounds themselves, the mid-level buckets (e.g. "the map's form
  mismatches real argument", "the map settles the wrong object", "not viable in practice",
  "the conditions have changed"). Give each limb a title, a one-sentence gloss of what belongs under
  it, its root_key, and -- where a limb on one side answers a limb on the other -- a mirror_of key so
  the two sides stay parallel. Aim for a MIRRORED structure across the main rival roots.
- The VALUE CRUX: the two rival prescriptions (oughts) underneath the dispute.

Rules for every text: abstract and self-contained (NO named people or projects -- not "Scott", not
the platform's name; a reader who knows nothing of the source must parse it); declarative, not a
question.

ONE-PROPOSITION DISCIPLINE FOR THE SKELETON (this is where builds go wrong -- apply it hardest here):
every root thesis and every limb text must be EXACTLY ONE proposition -- a single clause a rater
could agree or disagree with as a unit. The reasons for a thesis are the LIMBS; the facts under a
limb are the LEAVES; NEITHER belongs inside the thesis/limb text.
- BAD root: "Mapping cannot improve reasoning BECAUSE it misdescribes disagreement AND is not usable,
  SO the endeavor is doomed." (a claim + two reasons + an inference -- four propositions)
- GOOD root: "Structured argument-mapping will not meaningfully improve real-world reasoning."
- BAD limb: "Formal mapping is inefficient AND its intended user barely exists." (two claims)
- GOOD limb: "Argument-mapping is not a practically viable route." (the two claims become its leaves)
Before returning, RE-READ every root and limb text: if it contains an "and" joining two claims, or a
"because"/"so"/"therefore" attaching a reason or inference, REWRITE it to a single clause and move the
excised material down a level. Return ONLY the structured object.`,
  { label: 'plan', phase: 'Plan', model: MODEL, effort: 'high', schema: SKELETON })

if (!plan) return { error: 'planner failed' }
log(`skeleton: ${plan.roots.length} roots, ${plan.limbs.length} limbs`)

// ---------- Phase 1.5: REFINE (apply the two-assertion check to the SKELETON) ----------
// The experiment found bundling concentrates in the planner's skeleton because the
// authoring checks only ran on leaves. This step runs the same check on the skeleton.
phase('Plan')
const refined = await agent(
`You are the SKELETON EDITOR. Here is a proposed argument-graph skeleton:
${JSON.stringify({ roots: plan.roots, limbs: plan.limbs, value_crux: plan.value_crux })}

Apply ONE check to every root thesis and every limb text: does it assert MORE THAN ONE
independently-rateable proposition? A text fails if it joins two claims with "and", or attaches a
reason/inference with "because"/"so"/"therefore", or pairs a claim with an evaluation. For each failing
text, REWRITE it to a single clause carrying just the one core proposition -- the excised reasons are
what the limbs/leaves are for, so they do not belong in the thesis/limb text. Keep every key, root_key,
mirror_of, and title unchanged; keep the same number of roots and limbs; only tighten the wording of
`+"`thesis` and `gloss`/limb `title` texts that were bundled. Also ensure NO text names a real person or"+`
project. Return the corrected skeleton in the SAME structure.`,
  { label: 'refine-skeleton', phase: 'Plan', model: MODEL, effort: 'high', schema: SKELETON })
const sk = refined || plan
if (refined) log(`skeleton refined (bundle-check applied to roots+limbs)`)

// ---------- Phase 2: SCAFFOLD ----------
phase('Scaffold')
const rootsJson = JSON.stringify(sk.roots)
const limbsJson = JSON.stringify(sk.limbs)
const cruxJson = JSON.stringify(sk.value_crux)
const scaffold = await agent(
`You are the SCAFFOLDER. Working dir: ${V0} (cd there). Dataset: --data ${DATA}. Use the CLI:
  python3 graph.py create-node --agent builder --data ${DATA} --json --kind <claim|ought> --title "<t>" --text "<claim>"
  python3 graph.py draw-ground --from <leaf> --to <dependent> --agent builder --data ${DATA} --json

Create exactly these nodes and record each returned id against its key.
ROOTS (kind claim): ${rootsJson}
LIMBS (kind claim): ${limbsJson}
VALUE CRUX (kind ought): create ought_a and ought_b as two ought nodes (keys "crux_a","crux_b").
CRUX: ${cruxJson}

Then draw one ground edge from EACH limb to its root_key's node (limb supports its root thesis).
Do NOT create any other nodes or edges. Batch commands with && ; check each JSON has "ok":true.
Return the full key->id map for every root, limb, and the two crux oughts.`,
  { label: 'scaffold', phase: 'Scaffold', model: MODEL, effort: 'medium', schema: IDMAP })

if (!scaffold) return { error: 'scaffold failed' }
const id = {}; scaffold.ids.forEach(x => id[x.key] = x.id)
log(`scaffold ids: ${scaffold.ids.length}`)

// ---------- Phase 3: POPULATE (one agent per limb, in parallel) ----------
phase('Populate')
const populated = await parallel(sk.limbs.map(limb => () => {
  const lid = id[limb.key]
  if (!lid) return Promise.resolve(null)
  const siblings = sk.limbs.filter(l => l.key !== limb.key).map(l => l.title).join('; ')
  return agent(
`You are a BUILD agent populating ONE limb of an argument graph. Working dir: ${V0} (cd there).
Dataset: --data ${DATA}. Source brief: ${V0}/${BRIEF} (cat it for the substance).

Your limb is "${limb.title}" (node id ${lid}) -- gloss: ${limb.gloss}
Other limbs (do NOT poach their material): ${siblings}

Author the 2-4 STRONGEST leaf claims from the brief that specifically support YOUR limb, and attach
each to it. HARD CAP: at most 4 leaves. Fewer, well-chosen, non-overlapping leaves are better than
many; if the material feels like more than 4 distinct claims, that limb was probably two limbs -- pick
the best 4 and note the overflow in your return, do NOT exceed the cap.
  python3 graph.py create-node --agent builder --data ${DATA} --json --kind claim --title "<<=8 words>" --text "<claim>"
  python3 graph.py draw-ground --from <new-leaf> --to ${lid} --agent builder --data ${DATA} --json
If a leaf is itself supported by a more specific fact/example, create that too (also --kind claim) and
ground it to the leaf -- but this still counts against the 4-leaf cap. A shallow sub-tree is good; a
flat fan is not.

CLAIMS-ONLY MODE: this brief has NO source pack, so create EVERY node as --kind claim. A specific
study or example becomes a claim node stating the finding (e.g. "A cross-over trial found X"); do NOT
use --kind evidence (it requires a --source and will be rejected).

AUTHORING CHECKS -- every leaf MUST pass all three before you create it:
1. STANDALONE: the text reads on its own, with NO named person or project and NO reliance on knowing
   the overall question. (If you'd need "Scott" or the platform's name, rewrite it.)
2. ONE PROPOSITION: it asserts exactly one independently-rateable thing. If your draft contains "and"
   joining two claims, or "X, so Y", SPLIT it into two nodes (each still within the cap).
3. TITLE: a <=8-word scannable title that names the claim's centre of gravity. If you can't title it
   crisply, it's probably still bundled -- split it.

Attach each leaf to the MOST PROXIMATE claim (your limb or a sub-leaf), never jump levels. Batch with
&& ; check "ok":true. Return every node you created (id, title, text).`,
    { label: `limb:${limb.key}`, phase: 'Populate', model: MODEL, effort: 'high', schema: LEAVES })
}))
const leafCount = populated.filter(Boolean).reduce((s, r) => s + (r.created?.length || 0), 0)
log(`populated ${leafCount} leaves across ${sk.limbs.length} limbs`)

// ---------- Phase 4: ANTITHESIS (both-true gate) ----------
phase('Antithesis')
const rootKeys = sk.roots.map(r => `${r.key}=${id[r.key]} (${r.title})`).join('; ')
const allLimbs = sk.limbs.map(l => `${id[l.key]} [root ${l.root_key}] "${l.title}"`).join('; ')
await agent(
`You are the ANTITHESIS wirer. Working dir: ${V0} (cd there). Dataset: --data ${DATA}.
First read EVERY node's text: python3 graph.py get-node <id> --data ${DATA} --json (or cat ${DATA}/graph.json and read phrasings[0].text). You cannot judge rivalry without the actual texts.

Create antithesis sets (rival positive claims) with:
  python3 graph.py add-antithesis --node <nid> --set new --agent builder --data ${DATA} --json   (first member; returns set id)
  python3 graph.py add-antithesis --node <nid> --set <sid> --agent builder --data ${DATA} --json  (more members)

FINDING rivalries is YOUR job -- do not wait to be handed pairs. Recall matters as much as precision:
a genuine rivalry left unwired is as much a defect as a false one wired. Systematically consider:
- The ROOT positions as one set (mutually exclusive answers to the whole question): ${rootKeys}
- The VALUE CRUX oughts as one set: ${id['crux_a']} <> ${id['crux_b']}
- EVERY cross-root limb pair. The limbs are: ${allLimbs}
  For each limb on one root, look for the limb on a rival root that answers the SAME sub-question
  (form vs form, viability vs viability, etc.) and test them as a pair. Check ALL such pairs, not just
  obvious ones -- this is where rivalries get missed.
- EVERY within-limb or cross-limb LEAF pair that states rival answers to one sub-question (a real
  "X is a real causal effect" vs "X is confounding/artifact" pair). Read the leaves and look for these.

Apply the BOTH-TRUE TEST to each candidate: create the set ONLY if AT MOST ONE member can be true at
once. If two claims could BOTH be true (one merely answers, challenges, or is compatible with the
other), they are NOT rivals -- skip them. But do not use the gate as an excuse to skip real rivals:
mutually exclusive positive claims about the same question ARE rivals even if politely phrased.

Batch with && ; check "ok":true. Return a summary: sets created (with members), and any candidate
pair you SKIPPED by the both-true test (with the reason).`,
  { label: 'antithesis', phase: 'Antithesis', model: MODEL, effort: 'high' })

return { roots: sk.roots.length, limbs: sk.limbs.length, leaves: leafCount, data: DATA }
