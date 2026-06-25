#!/usr/bin/env python3
"""Split each source per-notebook narration monologue into per-section .tts files.

Anchors on the notebook's `## ` headings: the source monologue (one file per
notebook at ~/Projects/dsa/tts/<stem>.tts) carries plain-sentence section markers
that mirror those headings. We walk the headings in order, find the marker line
that best matches each, and slice the monologue between markers. The leading
overview paragraph (before the first heading) is dropped, and the trailing
"in the next notebook" outro is trimmed off the final section.

Output: dsa-content/tts/<NN>-<SS>-<slug>.tts
"""
import json
import re
import difflib
from pathlib import Path

SRC = Path.home() / "Projects" / "dsa"
NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"
OUT = Path(__file__).resolve().parent.parent / "tts"

STOP = {"the", "a", "an", "and", "vs", "versus", "to", "of", "in", "with", "for"}


def norm(s: str) -> str:
    s = s.lower().replace("`", "")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t not in STOP]
    return " ".join(toks)


def slug(s: str) -> str:
    s = s.lower().replace("`", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def headings(nb_path: Path):
    nb = json.loads(nb_path.read_text())
    out = []
    for c in nb["cells"]:
        if c["cell_type"] != "markdown":
            continue
        for line in c["source"]:
            if line.startswith("## "):
                out.append(line[3:].strip())
    return out


def ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def split_one(stem: str):
    nb = NB_DIR / f"{stem}.ipynb"
    src = SRC / "tts" / f"{stem}.tts"
    hs = headings(nb)
    paras = [p.strip() for p in src.read_text().split("\n\n") if p.strip()]

    # For each heading, locate the paragraph index whose normalized text best
    # matches (markers are short standalone lines). Search strictly forward.
    matches = []  # (heading_index, para_index)
    cursor = 0
    for hi, h in enumerate(hs):
        nh = norm(h)
        best_idx, best_r = None, 0.0
        for pi in range(cursor, len(paras)):
            p = paras[pi]
            # markers are short single-sentence lines
            if len(p) > 80:
                continue
            r = ratio(nh, norm(p))
            if r > best_r:
                best_r, best_idx = r, pi
        if best_idx is not None and best_r >= 0.6:
            matches.append((hi, best_idx))
            cursor = best_idx + 1
        else:
            matches.append((hi, None))  # unmatched -> reported

    # Build section slices from matched marker positions.
    results = []
    for n, (hi, pi) in enumerate(matches):
        if pi is None:
            results.append((hi, None))
            continue
        # body = paragraphs after this marker up to the next matched marker
        next_pi = len(paras)
        for hj, pj in matches[n + 1:]:
            if pj is not None:
                next_pi = pj
                break
        body = paras[pi + 1:next_pi]
        results.append((hi, body))
    return hs, results


def main():
    stems = sorted(p.stem for p in NB_DIR.glob("*.ipynb"))
    report = []
    for stem in stems:
        nn = stem[:2]
        hs, results = split_one(stem)
        ss = 0
        for hi, body in results:
            heading = hs[hi]
            ss += 1
            sslug = slug(heading)
            fname = f"{nn}-{ss:02d}-{sslug}.tts"
            if body is None:
                report.append(f"  !! UNMATCHED heading: {stem} :: {heading}")
                # still emit a placeholder-free skip marker
                continue
            text = "\n\n".join(body).strip()
            # Trim trailing "in the next notebook" outro from the final section.
            if hi == len(hs) - 1:
                lines = text.split("\n\n")
                while lines and re.search(
                    r"\b(next notebook|next module|coming up|up next|we will look at how|in the next)\b",
                    lines[-1].lower(),
                ):
                    lines.pop()
                text = "\n\n".join(lines).strip()
            # Prepend the spoken title (plain sentence) as section opener.
            title_line = heading.replace("`", "").rstrip("?.! ")
            spoken = f"{title_line}.\n\n{text}" if text else f"{title_line}."
            (OUT / fname).write_text(spoken + "\n")
        report.append(f"{stem}: {len([r for r in results if r[1] is not None])}/{len(hs)} sections")
    print("\n".join(report))


if __name__ == "__main__":
    main()
