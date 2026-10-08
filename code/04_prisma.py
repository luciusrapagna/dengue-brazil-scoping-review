"""PRISMA-ScR flow diagram (Supplementary Figure S1).
Counts are read from data/raw/prisma_counts.csv; empty cells are drawn as
'n = [  ]' so the authors can complete them after the final screening."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CM = 1 / 2.54
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 9, "svg.fonttype": "none", "pdf.fonttype": 42})


def main():
    c = pd.read_csv(ROOT / "data" / "raw" / "prisma_counts.csv", dtype=str).fillna("")
    c = c.set_index("box")
    txt = lambda k: f"{c.loc[k, 'label']}\n(n = {c.loc[k, 'n'] or '[    ]'})"
    fig, ax = plt.subplots(figsize=(15 * CM, 16 * CM))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    box = dict(boxstyle="square,pad=0.5", fc="white", ec="black", lw=0.7)
    def put(x, y, s, w=None):
        ax.text(x, y, s, ha="center", va="center", bbox=box, wrap=True, fontsize=8)
    for y, lab in [(88, "Identification"), (55, "Screening"), (12, "Included")]:
        ax.text(2, y, lab, rotation=90, va="center", ha="center", fontweight="bold")
    put(33, 88, txt("db_records").replace("; ", ";\n"))
    put(80, 88, txt("other_records").replace(" from", "\nfrom"))
    put(33, 70, txt("duplicates"))
    put(33, 55, txt("screened"))
    put(80, 55, txt("excluded_screen"))
    put(33, 38, txt("fulltext").replace(" assessed", "\nassessed"))
    put(80, 38, txt("excluded_ft").replace(", with", ",\nwith") + "\n[INSERT reasons]")
    put(33, 12, txt("included").replace(" included", "\nincluded"))
    arr = dict(arrowstyle="-|>", lw=0.7, color="black")
    for (x1, y1, x2, y2) in [(33, 81, 33, 74), (33, 66, 33, 59), (33, 51, 33, 43), (33, 33, 33, 17),
                             (52, 55, 64, 55), (50, 38, 62, 38), (80, 82, 80, 75), (80, 75, 50, 75)]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arr)
    out = ROOT / "supplementary"
    out.mkdir(exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out / f"FigureS1_PRISMA_ScR_flow.{ext}", dpi=300, bbox_inches="tight")
    print("PRISMA diagram written")


if __name__ == "__main__":
    main()
