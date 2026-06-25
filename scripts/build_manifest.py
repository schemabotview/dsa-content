#!/usr/bin/env python3
"""Generate manifest.json for the dsa concept.

Wires every notebook `## ` section to a scene, chosen per MODULE:

  - Conceptual modules (01/02/03/08) ride the `dsa` TAXONOMY scene. The RAM sketches
    were removed from dsa.ts, so these show the whole taxonomy with the section's
    topic node lit (no camera zoom) — richer visuals come later.
  - Structure modules (04/05/06/07/09/10/11) ride the `dsa-catalog` scene — the
    "top data structures" poster — and the camera frames the matching box
    (Array / Linked List / Stack / Queue / HashMap / Tree / BST / Heap), refined per
    section by topic keyword.

Each section also gets: spine (essential vs auxiliary recap), role ("hook" on the
first), and the per-section .wav stem (generated from tts/ on Colab).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "notebooks"

TITLES = {
    "01": "How Computers Store Data",
    "02": "Complexity Analysis",
    "03": "Primitive Types & Memory",
    "04": "Arrays & Strings",
    "05": "Linked Lists",
    "06": "Stacks & Queues",
    "07": "Hash Maps & Hash Sets",
    "08": "Recursion & the Call Stack",
    "09": "Trees & Binary Trees",
    "10": "Binary Search Trees",
    "11": "Heaps & Priority Queues",
}

# Which scene each module rides.
MODULE_SCENE = {
    "01": "dsa", "02": "dsa", "03": "dsa", "08": "dsa",
    "04": "dsa-catalog", "05": "dsa-catalog", "06": "dsa-catalog",
    "07": "dsa-catalog", "09": "dsa-catalog", "10": "dsa-catalog", "11": "dsa-catalog",
}

# --- Taxonomy scene (dsa) -----------------------------------------------------
# Conceptual modules: highlight the topic node, NO focus (whole taxonomy in view).
TAX_DEFAULT = {
    "01": "dsa-primitive",
    "02": "dsa-array",
    "03": "dsa-primitive",
    "08": "dsa-stack",
}
TAX_KEYWORD = [
    ("tree",        "dsa-tree"),     # 08 "Recursion Tree — Fibonacci"
    ("call-stack",  "dsa-stack"),
    ("stack",       "dsa-stack"),
    ("recursion",   "dsa-stack"),
    ("array",       "dsa-array"),
    ("string",      "dsa-array"),
    ("integer",     "dsa-primitive"),
    ("float",       "dsa-primitive"),
    ("boolean",     "dsa-primitive"),
    ("character",   "dsa-primitive"),
    ("primitive",   "dsa-primitive"),
    ("type",        "dsa-primitive"),
]

# --- Catalog scene (dsa-catalog) ----------------------------------------------
# Structure modules: highlight AND focus the matching poster box.
CAT_DEFAULT = {
    "04": "dsa-cat-array",
    "05": "dsa-cat-linkedlist",
    "06": "dsa-cat-stack",
    "07": "dsa-cat-hashmap",
    "09": "dsa-cat-tree",
    "10": "dsa-cat-bst",
    "11": "dsa-cat-heap",
}
CAT_KEYWORD = [
    ("multi-dimensional", "dsa-cat-matrix"),
    ("matrix",            "dsa-cat-matrix"),
    ("deque",             "dsa-cat-queue"),
    ("queue",             "dsa-cat-queue"),
    ("linked-list",       "dsa-cat-linkedlist"),
    ("hash",              "dsa-cat-hashmap"),
    ("bst",               "dsa-cat-bst"),
    ("heap",              "dsa-cat-heap"),
    ("call-stack",        "dsa-cat-stack"),
    ("stack",             "dsa-cat-stack"),
    ("traversal",         "dsa-cat-tree"),
    ("tree",              "dsa-cat-tree"),
    ("string",            "dsa-cat-array"),
    ("array",             "dsa-cat-array"),
    ("graph",             "dsa-cat-graph"),
]

# Auxiliary (non-spine) section markers — recaps, cheat sheets, summaries.
AUX = ("key-takeaways", "cheat-sheet", "complexity-summary",
       "stack-vs-queue-summary")


def slug(s: str) -> str:
    s = s.lower().replace("`", "").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def headings(stem: str):
    nb = json.loads((NB / f"{stem}.ipynb").read_text())
    out = []
    for c in nb["cells"]:
        if c["cell_type"] != "markdown":
            continue
        for line in c["source"]:
            if line.startswith("## "):
                out.append(line[3:].strip())
    return out


def overlay(nn: str, sl: str):
    """Return (scene, highlight, focus|None) for a section."""
    scene = MODULE_SCENE[nn]
    if scene == "dsa":
        node = next((n for kw, n in TAX_KEYWORD if kw in sl), TAX_DEFAULT[nn])
        return scene, [node], None
    box = next((b for kw, b in CAT_KEYWORD if kw in sl), CAT_DEFAULT[nn])
    return scene, [box], [box]


def main():
    stems = sorted(p.stem for p in NB.glob("*.ipynb"))
    presentations = []
    for stem in stems:
        nn = stem[:2]
        hs = headings(stem)
        scene = MODULE_SCENE[nn]
        sections = []
        for ss, h in enumerate(hs, start=1):
            sl = slug(h)
            sc, hi, fo = overlay(nn, sl)
            sec = {"heading": h, "scene": sc}
            sec["spine"] = not any(a in sl for a in AUX)
            if ss == 1:
                sec["role"] = "hook"
            sec["highlight"] = hi
            if fo is not None:
                sec["focus"] = fo
            sec["audio"] = f"audio/{nn}-{ss:02d}-{sl}.wav"
            sections.append(sec)
        presentations.append({
            "id": stem,
            "title": TITLES[nn],
            "notebook": f"notebooks/{stem}.ipynb",
            "defaultScene": scene,
            "sections": sections,
        })

    manifest = {
        "concept": "Data Structures & Algorithms",
        "design": "DESIGN.md",
        "scenes": [
            {"id": "dsa", "title": "DSA — Taxonomy", "status": "built"},
            {"id": "dsa-catalog", "title": "DSA — Catalog", "status": "built"},
        ],
        "presentations": presentations,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote manifest.json: {len(presentations)} presentations, "
          f"{sum(len(p['sections']) for p in presentations)} sections")


if __name__ == "__main__":
    main()
