#!/usr/bin/env python3
"""Generate manifest.json for the dsa concept.

Wires every notebook `## ` section to the single `dsa` scene (the Taxonomy + RAM
map ported from NodeMap's src/data/scenes/dsa.ts). Each section gets:
  - scene: "dsa"
  - spine: essential sections (true) vs auxiliary recap/summary (false)
  - role: "hook" on each module's first section
  - highlight / focus: node ids from dsa.ts, chosen per section by topic keyword
    (falling back to the module default), so the camera frames the structure the
    section is about and lights its taxonomy box + RAM sketch.
  - audio: the per-section .wav stem (generated from tts/ on Colab)
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

# Module-level default overlay when no section keyword matches.
MODULE_DEFAULT = {
    "01": (["dsa-ram-primitive", "dsa-ram-stack"], ["dsa-ram"]),
    "02": (["dsa-array"], ["dsa-ram-array"]),
    "03": (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"]),
    "04": (["dsa-array", "dsa-ram-array"], ["dsa-ram-array"]),
    "05": (["dsa-linkedlist", "dsa-ram-linkedlist"], ["dsa-ram-linkedlist"]),
    "06": (["dsa-stack", "dsa-queue"], ["dsa-ram-stack"]),
    "07": (["dsa-array", "dsa-ram-array"], ["dsa-ram-array"]),
    "08": (["dsa-stack", "dsa-ram-stack"], ["dsa-ram-stack"]),
    "09": (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"]),
    "10": (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"]),
    "11": (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"]),
}

# Section-keyword -> (highlight, focus). First match on the section slug wins.
KEYWORD = [
    ("deque",       (["dsa-stack", "dsa-queue", "dsa-ram-queue"], ["dsa-ram-queue"])),
    ("queue",       (["dsa-queue", "dsa-ram-queue"], ["dsa-ram-queue"])),
    ("call-stack",  (["dsa-stack", "dsa-ram-stack"], ["dsa-ram-stack"])),
    ("stack",       (["dsa-stack", "dsa-ram-stack"], ["dsa-ram-stack"])),
    ("linked-list", (["dsa-linkedlist", "dsa-ram-linkedlist"], ["dsa-ram-linkedlist"])),
    ("bst",         (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"])),
    ("tree",        (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"])),
    ("traversal",   (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"])),
    ("heap",        (["dsa-tree", "dsa-ram-tree"], ["dsa-ram-tree"])),
    ("string",      (["dsa-array", "dsa-ram-array"], ["dsa-ram-array"])),
    ("array",       (["dsa-array", "dsa-ram-array"], ["dsa-ram-array"])),
    ("hash",        (["dsa-array", "dsa-ram-array"], ["dsa-ram-array"])),
    ("integer",     (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("float",       (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("boolean",     (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("character",   (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("primitive",   (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("type",        (["dsa-primitive", "dsa-ram-primitive"], ["dsa-ram-primitive"])),
    ("heap-and",    (["dsa-stack", "dsa-ram-stack"], ["dsa-ram-stack"])),  # "stack and the heap"
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
    for kw, hf in KEYWORD:
        if kw in sl:
            return hf
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
            hi, fo = overlay(nn, sl)
            sec = {"heading": h, "scene": "dsa"}
            sec["spine"] = not any(a in sl for a in AUX)
            if ss == 1:
                sec["role"] = "hook"
            sec["highlight"] = hi
            sec["focus"] = fo
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
            {"id": "dsa", "title": "DSA — Taxonomy & RAM", "status": "built"}
        ],
        "presentations": presentations,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote manifest.json: {len(presentations)} presentations, "
          f"{sum(len(p['sections']) for p in presentations)} sections")


if __name__ == "__main__":
    main()
