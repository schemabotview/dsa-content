#!/usr/bin/env python3
"""Generate manifest.json for the dsa concept.

DSA rides ONE scene, `dsa` (graphl-ux `src/scenes/dsa.ts`): the "top data structures"
poster laid out GROUPED BY taxonomy category. The grouping IS the categorisation; each
cell shows what the structure looks like. Per section we pick the box/category the
camera frames (highlight + focus), by topic keyword, falling back to a module default:

  - 04/05/06/07/09/10/11 frame their structure box (Array / Linked List / Stack /
    Queue / HashMap / Tree / BST / Heap).
  - 03 frames the Primitive group; 02 frames Array; 08 frames Stack (call stack).
  - 01 (storage overview) frames nothing — the whole categorised poster stays in view.

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

# Module default box (None = no focus; the whole poster stays framed).
MODULE_DEFAULT = {
    "01": None,
    "02": "dsa-cat-array",
    "03": "dsa-grp-primitive",
    "04": "dsa-cat-array",
    "05": "dsa-cat-linkedlist",
    "06": "dsa-cat-stack",
    "07": "dsa-cat-hashmap",
    "08": "dsa-cat-stack",
    "09": "dsa-cat-tree",
    "10": "dsa-cat-bst",
    "11": "dsa-cat-heap",
}

# Section-keyword -> box id (all on scene `dsa`). First match on the slug wins.
KEYWORD = [
    ("multi-dimensional", "dsa-cat-matrix"),
    ("matrix",            "dsa-cat-matrix"),
    ("deque",             "dsa-cat-queue"),
    ("queue",             "dsa-cat-queue"),
    ("linked-list",       "dsa-cat-linkedlist"),
    ("hash",              "dsa-cat-hashmap"),
    ("bst",               "dsa-cat-bst"),
    # stack before heap so "The Stack and the Heap" (memory, module 01) frames the
    # stack, not the heap data structure.
    ("call-stack",        "dsa-cat-stack"),
    ("stack",             "dsa-cat-stack"),
    ("heap",              "dsa-cat-heap"),
    ("traversal",         "dsa-cat-tree"),
    ("tree",              "dsa-cat-tree"),
    ("integer",           "dsa-grp-primitive"),
    ("float",             "dsa-grp-primitive"),
    ("boolean",           "dsa-grp-primitive"),
    ("character",         "dsa-grp-primitive"),
    ("primitive",         "dsa-grp-primitive"),
    ("type",              "dsa-grp-primitive"),
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


def focus_box(nn: str, sl: str):
    """The box/category the camera frames (None = whole poster)."""
    for kw, box in KEYWORD:
        if kw in sl:
            return box
    return MODULE_DEFAULT[nn]


def main():
    stems = sorted(p.stem for p in NB.glob("*.ipynb"))
    presentations = []
    for stem in stems:
        nn = stem[:2]
        hs = headings(stem)
        sections = []
        for ss, h in enumerate(hs, start=1):
            sl = slug(h)
            box = focus_box(nn, sl)
            sec = {"heading": h, "scene": "dsa"}
            sec["spine"] = not any(a in sl for a in AUX)
            if ss == 1:
                sec["role"] = "hook"
            if box is not None:
                sec["highlight"] = [box]
                sec["focus"] = [box]
            sec["audio"] = f"audio/{nn}-{ss:02d}-{sl}.wav"
            sections.append(sec)
        presentations.append({
            "id": stem,
            "title": TITLES[nn],
            "notebook": f"notebooks/{stem}.ipynb",
            "defaultScene": "dsa",
            "sections": sections,
        })

    manifest = {
        "concept": "Data Structures & Algorithms",
        "design": "DESIGN.md",
        "scenes": [
            {"id": "dsa", "title": "DSA — Catalog", "status": "built"},
        ],
        "presentations": presentations,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote manifest.json: {len(presentations)} presentations, "
          f"{sum(len(p['sections']) for p in presentations)} sections")


if __name__ == "__main__":
    main()
