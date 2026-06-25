# dsa-content

A **content repo** for the `graphl-ux` learning app (sibling repo). It holds the
**Data Structures & Algorithms** concept — notebooks, per-section narration scripts,
and the `manifest.json` that wires sections to a scene — fetched by the app **at
runtime** over raw GitHub.

There is **nothing to build, run, or test** here. Correctness is verified by the
`graphl-ux` app consuming this content. The only executables are the helper scripts
in `scripts/` (a Colab audio generator plus two regeneration tools).

## Layout

```
manifest.json   # wires each module: notebook ref + per-section overlay (scene/spine/role/audio/highlight/focus)
notebooks/      # the teaching .ipynb (prose + code source of truth) — 01..11
tts/            # per-section narration scripts (plain spoken prose) — 101 files, 1:1 with manifest audio stems
audio/          # generated .wav narration (per-section) — generated on Colab
scenes/         # reserved/empty — the real scene lives in the graphl-ux app (src/scenes)
scripts/        # colab_generate_audio.ipynb (.tts -> .wav) + build_manifest.py / split_tts.py helpers
```

## The contract (shared with apache-spark-content / java-content)

1. **The notebook is the single source of truth** for a module's prose and code.
   The `manifest.json` only *wires* — it must never duplicate notebook content.
2. The app splits each notebook at every `## ` heading into **sections** (= pages),
   matched to the manifest overlay by **normalized heading text** (case / backticks /
   whitespace insensitive). A heading edit in a notebook must be mirrored here.
3. A section's diagram **images are stripped** by the app — a **scene** replaces them.
4. **Scenes live in `graphl-ux`** (`src/scenes`), authored in TypeScript — not here.
   The DSA concept uses a **single** scene, `dsa`. Here you only reference it **by id**.

## The DSA scene (in graphl-ux, not here)

One dense map, ported from NodeMap's `src/data/scenes/dsa.ts`: a two-column
**Taxonomy ▸ RAM** picture. The left column is the classical data-structure taxonomy
(Primitive / Non-Primitive → Linear / Non-Linear → Static / Dynamic → Array, Linked
List, Stack, Queue, Tree, Graph); the right column is a stack of RAM sketches where the
geometry *is* the memory model (contiguous row, scattered pointer chain, stack column,
adjacency rows). Node ids are `dsa-*`:

- Taxonomy boxes: `dsa-primitive`, `dsa-array`, `dsa-linkedlist`, `dsa-stack`,
  `dsa-queue`, `dsa-tree`, `dsa-graph` (plus `dsa-root`, `dsa-linear`, `dsa-dynamic`…).
- RAM sketches: `dsa-ram-primitive`, `dsa-ram-array`, `dsa-ram-linkedlist`,
  `dsa-ram-stack`, `dsa-ram-queue`, `dsa-ram-tree`, `dsa-ram-graph`, and the column
  container `dsa-ram`.

Highlighting a container id lights its children. Always check the id list in
`dsa.ts` before adding a `highlight`/`focus`.

## Narration (per-section TTS)

One `.tts` script **per section**, plain spoken prose — what a teacher would say at a
whiteboard. Naming: `tts/<NN>-<SS>-<slug>.tts` → `audio/<NN>-<SS>-<slug>.wav`, where
`NN` is the module number and `SS` the section order; the slug is the normalized
notebook heading. The stem is shared by the `.tts`, the `.wav`, and the manifest
`audio` field.

See `apache-spark-content/CLAUDE.md` "TTS guidelines" for the full style rules (plain
prose, no markdown/code, spell out symbols and acronyms — e.g. `O(1)` → "constant
time", RAM → "ram", `==` → "double equals").

## How content is served

The app fetches this repo at runtime over **raw GitHub**:
`https://raw.githubusercontent.com/schemabotview/dsa-content/main/…`
A content change is live once pushed to `main` — no app rebuild needed.

## Source of notebooks

Notebooks are copied as-is from the runnable curriculum at `~/Projects/dsa`. Every code
example there is shown in **Python then Kotlin** (see that repo's `CLAUDE.md`).

## Status

- Scaffolded; **11 notebooks** copied in (01–11). The source curriculum plans 24
  modules; only 01–11 exist as notebooks today.
- **All 11 modules are scene-wired** in `manifest.json` — every `## ` section mapped to
  the single `dsa` scene with `spine`/`role`/`highlight`/`focus` (highlight + focus
  reference `dsa-*` node ids per topic).
- **All 11 modules are fully narrated** — **101 per-section `tts/*.tts` scripts**, 1:1
  with the manifest `audio` stems. The notebook's intro overview and "next notebook"
  outro are dropped per the TTS contract.
- The per-section `.wav`s still need a Colab generation pass
  (`scripts/colab_generate_audio.ipynb`: `tts/` → `audio/`).
- **Follow-ups (graphl-ux side, not done here):** the `dsa` scene exists in NodeMap but
  is **not yet ported/registered** in `graphl-ux/src/scenes/index.ts`, and the DSA
  concept is **not yet added** to the app's concept catalog
  (`graphl-ux/src/content/catalog.ts`). Both are required before the app can render
  this content. Also: not yet pushed to GitHub.
