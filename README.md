# Reasonable — FLF Epistemic Case Study Competition submission

**Wikipedia for *arguments*, not facts** — a format, engine, and assessment methodology for building
trustworthy knowledge from collective reasoning, submitted to the FLF *"Lab Leaks, Black Holes, and
Eggs"* Epistemic Case Study Competition.

### Read the submission

- **📄 Submission page (start here):** **https://jeffpyles.github.io/reasonable-flf/** — the narrated
  writeup with the live argument-graph viewer embedded.
- **🤖 [`START-HERE.md`](START-HERE.md)** — the front door for a human skimming, or for an AI agent you
  point at this repo to understand the project from the inside.
- **📚 [`v0/PROJECT-OVERVIEW.md`](v0/PROJECT-OVERVIEW.md)** — the full account of what was built, how it
  works, and where everything lives.

### Run it, don't just read it

Stdlib Python 3 only — no installs, no servers, no network. From `v0/`:

```bash
python3 graph.py assess     --data covid-graph-v2     # assessed verdict on a contested question
python3 graph.py contested  --data debate-graph-v2    # settled vs contested, and why
python3 graph.py rebuild    --data blackholes-graph-v2 # determinism: byte-identical rebuild
python3 -m unittest discover -s reasonable -t .        # the test suite (run from v0/)
```

Then open [`v0/viewer.html`](v0/viewer.html) and click **Introduction**. To build and blind-rate a
graph of your own from scratch, the end-to-end recipe is [`BUILD-A-GRAPH.md`](BUILD-A-GRAPH.md).

### What's here

- `v0/graph.py`, `v0/reasonable/` — the CLI and the layered engine (log → fold → snapshot; the
  assessment stack live in the running code).
- `v0/{eggs,covid,blackholes,debate}-graph-v2/` — the four assessed case graphs (presentation set);
  `*-graph/` are the assessed-of-record originals the research ran on.
- `v0/FINDINGS-SYNTHESIS.md`, `v0/covid-adversarial/`, `v0/v2-reliability/`, `v0/dispersion-regimes/`
  — the assessment research and its reproduce index.
- `v0/*-SPEC.md` — the frozen data-model and assessment contracts.
- `Reasonable - Concept Overview.html`, `Reasonable - Claims Index.html`, `Feature Discussions.md` —
  the concept and design-log background.

Released under GPL-3.0. Everything is reproducible from committed data.
