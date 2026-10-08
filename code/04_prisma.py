"""PRISMA flow diagram (Supplementary Figure S1) and LILACS screening log (S4).

Layout follows the PRISMA 2020 template for updated reviews: studies included in the
first search round (PubMed/MEDLINE, SciELO, ScienceDirect, SciSpace) plus the full
screening of the LILACS search. All LILACS counts are computed from
data/raw/lilacs_screening.py and data/raw/lilacs_additions.py.
"""
from pathlib import Path
import importlib.util
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CM = 1 / 2.54
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 8, "svg.fonttype": "none", "pdf.fonttype": 42})


def load(name):
    spec = importlib.util.spec_from_file_location(name, RAW / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def screening_log():
    sc, add = load("lilacs_screening"), load("lilacs_additions")
    added = {r[0] for r in add.ADDITIONS}
    exc = {i: reason for reason, idx in sc.EXCLUDED.items() for i in idx}
    rows = []
    for rec in sc.RECORDS.split():
        i, bvs, year, typ = rec.split(":")
        i = int(i)
        if i in sc.DUPLICATES:
            dec, reason, stage = "Duplicate", "Already included in the first search round", "Identification"
        elif i in added:
            dec, reason, stage = "Included", "", "Eligibility"
        elif i in exc and exc[i] == "Duplicate record within LILACS":
            dec, reason, stage = "Duplicate", exc[i], "Identification"
        elif typ == "N":
            dec, reason, stage = "Excluded", "Not a journal article (thesis, book, proceedings or technical document)", "Screening"
        else:
            dec, reason = "Excluded", exc[i]
            stage = "Eligibility" if i in ASSESSED else "Screening"
        rows.append(dict(lilacs_index=i, bvs_id=bvs, year=int(year), decision=dec, stage=stage, reason=reason,
                         url=f"https://pesquisa.bvsalud.org/portal/resource/pt/{bvs}"))
    return pd.DataFrame(rows)


# records whose abstract/full text was assessed for eligibility (192 candidates)
ASSESSED = {159, 187, 191, 209, 218, 220, 259, 349, 397}


def main():
    log = screening_log()
    out = ROOT / "supplementary"; out.mkdir(exist_ok=True)
    log.to_excel(out / "S4_LILACS_screening_log.xlsx", index=False)
    log.to_csv(ROOT / "data" / "processed" / "lilacs_screening_log.csv", index=False, encoding="utf-8-sig")
    n = dict(
        lilacs=len(log),
        dup=int((log.decision == "Duplicate").sum()),
        screened=int((log.decision != "Duplicate").sum()),
        exc_screen=int(((log.decision == "Excluded") & (log.stage == "Screening")).sum()),
        assessed=int(((log.stage == "Eligibility")).sum()),
        exc_elig=int(((log.decision == "Excluded") & (log.stage == "Eligibility")).sum()),
        new=int((log.decision == "Included").sum()),
    )
    reasons = log[log.decision == "Excluded"].groupby(["stage", "reason"]).size()
    first = 103
    total = first + n["new"]
    pd.Series({**n, "first_round": first, "total": total}).to_csv(ROOT / "data" / "processed" / "prisma_counts_computed.csv")

    fig, ax = plt.subplots(figsize=(15 * CM, 17.5 * CM))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    box = dict(boxstyle="square,pad=0.45", fc="white", ec="black", lw=0.7)
    grey = dict(boxstyle="square,pad=0.45", fc="#f0f0f0", ec="black", lw=0.7)

    def put(x, y, s, b=box, size=7.5):
        ax.text(x, y, s, ha="center", va="center", bbox=b, fontsize=size, linespacing=1.25)

    ax.text(17, 98, "First search round", ha="center", fontweight="bold")
    ax.text(62, 98, "Full screening of the LILACS search", ha="center", fontweight="bold")
    put(17, 84, "Records identified\n(2026):\nPubMed/MEDLINE n = 591\nSciELO n = 107\n"
                "ScienceDirect n = 50\nSciSpace n = 10\n(top-ranked records\nscreened, n = 355)", grey)
    put(17, 40, f"Studies included\nin the first round\n(n = {first})", grey)
    put(55, 88, f"Records identified from\nLILACS (2026)\n(n = {n['lilacs']})")
    put(87, 88, f"Duplicates removed\n(n = {n['dup']})\nalready included: {n['dup'] - 1}\nwithin LILACS: 1")
    put(55, 70, f"Records screened\n(title, document type)\n(n = {n['screened']})")
    sr = reasons.get("Screening", pd.Series(dtype=int))
    nonj = int(sr.get("Not a journal article (thesis, book, proceedings or technical document)", 0))
    put(87, 66, f"Records excluded (n = {n['exc_screen']})\nnot a journal article: {nonj}\n"
                f"no original data: {int(sr.get('Editorial, opinion, letter or narrative piece without original data', 0))}\n"
                f"not specific to Brazil: {int(sr.get('Not specific to Brazil', 0))}\n"
                f"other disease: {int(sr.get('Other disease or condition as main outcome', 0))}\n"
                f"vector/laboratory only: {int(sr.get('Vector, entomological or laboratory study without epidemic data', 0))}\n"
                f"other topics: {n['exc_screen'] - nonj - sum(int(sr.get(k, 0)) for k in ['Editorial, opinion, letter or narrative piece without original data', 'Not specific to Brazil', 'Other disease or condition as main outcome', 'Vector, entomological or laboratory study without epidemic data'])}", size=7)
    put(55, 50, f"Abstracts/full texts assessed\nfor eligibility\n(n = {n['assessed']})")
    put(87, 45, f"Excluded (n = {n['exc_elig']})\nno epidemic data or\nnot epidemic-specific,\ncase report, commentary")
    put(55, 30, f"New studies included\n(n = {n['new']})")
    put(36, 10, f"Total studies included in the review\n(n = {total})", size=8.5)
    arr = dict(arrowstyle="-|>", lw=0.7, color="black")
    for (x1, y1, x2, y2) in [(55, 82, 55, 75), (67.5, 88, 74, 88), (55, 65, 55, 55), (66, 70, 72.5, 68),
                             (55, 45, 55, 34), (68, 50, 73, 48), (55, 26, 42, 14), (17, 34, 30, 14), (17, 70, 17, 46)]:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=arr)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out / f"FigureS1_PRISMA_flow.{ext}", dpi=300, bbox_inches="tight")
    old = [p for p in out.glob("FigureS1_PRISMA_ScR_flow.*")]
    for p in old:
        p.unlink()
    print(n, "first round", first, "total", total)
    print(reasons)


if __name__ == "__main__":
    main()
