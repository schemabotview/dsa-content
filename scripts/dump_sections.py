import json, sys
from pathlib import Path
NB = Path(__file__).resolve().parent.parent / "notebooks"
stem = sys.argv[1]
nb = json.loads((NB / f"{stem}.ipynb").read_text())
cur = None
buf = []
def flush():
    if cur is None: return
    print(f"\n### SECTION: {cur}")
    print("".join(buf).strip())
for c in nb["cells"]:
    src = "".join(c["source"])
    if c["cell_type"] == "markdown":
        lines = c["source"]
        for i, line in enumerate(lines):
            if line.startswith("## "):
                flush()
                globals().__setitem__('cur', line[3:].strip())
                buf.clear()
            else:
                if cur is not None:
                    buf.append(line)
    else:
        if cur is not None:
            lang = c.get("metadata", {}).get("language") or nb.get("metadata",{}).get("kernelspec",{}).get("language","")
            buf.append(f"\n[CODE]\n{src}\n[/CODE]\n")
flush()
