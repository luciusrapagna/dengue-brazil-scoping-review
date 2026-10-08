"""Figures for the manuscript (journal specs: max 15 cm wide, Times New Roman 9 pt,
>=300 dpi, legible in greyscale). Each figure is saved as PNG (300 dpi), TIFF,
PDF and SVG (editable vector) in figures/.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

CM = 1 / 2.54
plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 9, "axes.titlesize": 9,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "svg.fonttype": "none",
    "pdf.fonttype": 42,
})
INK = "#1a1a1a"
GREYS = ["#f0f0f0", "#bdbdbd", "#969696", "#636363", "#252525"]
PHASES = [(1981, 1989.5, "I"), (1989.5, 2000.5, "II"), (2000.5, 2009.5, "III"),
          (2009.5, 2019.5, "IV"), (2019.5, 2025.5, "V")]


def save(fig, name):
    for ext in ("png", "tiff", "pdf", "svg"):
        kw = {"dpi": 300} if ext in ("png", "tiff") else {}
        if ext == "tiff":
            kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)


def figure1(studies, sy):
    """Serotype-year evidence map."""
    years = np.arange(1981, 2026)
    sero = ["DENV-1", "DENV-2", "DENV-3", "DENV-4"]
    counts = (sy.groupby(["serotype", "year"])["id"].nunique()
              .unstack(fill_value=0).reindex(index=sero, columns=years, fill_value=0))
    per_year = sy.groupby("year")["id"].nunique().reindex(years, fill_value=0)

    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(15 * CM, 8.2 * CM), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1.25], "hspace": 0.12})
    for i, (a, b, lab) in enumerate(PHASES):
        for ax in (ax0, ax1):
            ax.axvspan(a, b, color="#f2f2f2" if i % 2 == 0 else "white", zorder=0, lw=0)
        ax0.text((a + b) / 2, per_year.max() * 1.12, f"Phase {lab}", ha="center", va="bottom",
                 fontsize=8, color=INK)
    ax0.bar(years, per_year.values, width=0.75, color="#525252", zorder=2)
    ax0.set_ylabel("Studies (n)")
    ax0.set_ylim(0, per_year.max() * 1.3)
    ax0.text(-0.085, 1.02, "A", transform=ax0.transAxes, fontweight="bold", fontsize=10)

    bounds = [0, 1, 2, 4, 7, 20]
    cmap = ListedColormap(GREYS)
    norm = BoundaryNorm(bounds, cmap.N)
    z = counts.values.astype(float)
    ax1.pcolormesh(np.append(years - 0.5, years[-1] + 0.5), np.arange(5) - 0.5, z,
                   cmap=cmap, norm=norm, edgecolor="white", linewidth=0.4, zorder=2)
    ax1.set_yticks(range(4), sero)
    ax1.invert_yaxis()
    ax1.set_xlim(1980.5, 2025.5)
    ax1.set_xticks(range(1981, 2026, 4))
    ax1.set_xlabel("Epidemic year")
    ax1.spines["left"].set_visible(False)
    ax1.tick_params(axis="y", length=0)
    # documented first detections / (re)introductions (refs in Table 1)
    marks = [("DENV-1", 1981), ("DENV-4", 1981), ("DENV-1", 1986), ("DENV-2", 1990),
             ("DENV-3", 2000), ("DENV-4", 2010), ("DENV-3", 2023)]
    for s, y in marks:
        ax1.scatter(y, sero.index(s), marker="v", s=22, facecolor="white", edgecolor=INK,
                    linewidth=0.8, zorder=4)
    ax1.text(-0.085, 1.02, "B", transform=ax1.transAxes, fontweight="bold", fontsize=10)
    labels = ["0", "1", "2–3", "4–6", "≥7"]
    handles = [plt.Rectangle((0, 0), 1, 1, fc=c, ec="#bdbdbd", lw=0.4) for c in GREYS]
    handles.append(plt.Line2D([], [], marker="v", ls="", mfc="white", mec=INK, ms=5))
    ax1.legend(handles, labels + ["Introduction/re-emergence"], title="Studies reporting the serotype",
               ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.32), frameon=False,
               handlelength=1.2, columnspacing=0.9, title_fontsize=8)
    save(fig, "Figure1_serotype_evidence_map")
    counts.to_csv(PROC / "figure1_matrix.csv", encoding="utf-8-sig")


def figure2(studies):
    """Where and how the evidence was produced."""
    order_reg = ["Southeast", "Northeast", "North", "Central-West", "South", "National"]
    st = studies.assign(state=studies["states"].str.split(";")).explode("state")
    reg = {"BR": "National"}
    import importlib.util
    spec = importlib.util.spec_from_file_location("b", ROOT / "code" / "01_build_dataset.py")
    b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
    st["reg"] = st["state"].map(b.REGION)
    cnt = st.groupby(["reg", "state"])["id"].nunique().reset_index()
    cnt["reg"] = pd.Categorical(cnt["reg"], order_reg, ordered=True)
    cnt = cnt.sort_values(["reg", "id"], ascending=[True, True])
    shade = dict(zip(order_reg, ["#252525", "#636363", "#969696", "#bdbdbd", "#d9d9d9", "#ffffff"]))

    fig, (a, bx) = plt.subplots(1, 2, figsize=(15 * CM, 8.6 * CM),
                                gridspec_kw={"width_ratios": [0.9, 1.25], "wspace": 0.42})
    ypos, labels, y = [], [], 0
    for r in order_reg:
        sub = cnt[cnt["reg"] == r].sort_values("id")
        for _, row in sub.iterrows():
            a.barh(y, row["id"], color=shade[r], edgecolor=INK, linewidth=0.5, height=0.72)
            a.text(row["id"] + 0.3, y, str(row["id"]), va="center", fontsize=7)
            labels.append("Brazil (national)" if row["state"] == "BR" else row["state"]); ypos.append(y)
            y += 1
        y += 0.6
    a.set_yticks(ypos, labels)
    a.invert_yaxis()
    a.set_xlabel("Studies (n)")
    a.tick_params(axis="y", length=0)
    a.legend([plt.Rectangle((0, 0), 1, 1, fc=shade[r], ec=INK, lw=0.5) for r in order_reg],
             order_reg, frameon=False, loc="center right", fontsize=7, handlelength=1)
    a.text(-0.32, 1.02, "A", transform=a.transAxes, fontweight="bold", fontsize=10)

    dorder = ["VIRO", "SERO", "SURV", "CLIN", "SPAT", "DIAG", "MODL", "CTRL", "HIST"]
    dlab = {"VIRO": "Virological/genomic", "SERO": "Seroepidemiological", "SURV": "Surveillance/descriptive",
            "CLIN": "Clinical/severity/mortality", "SPAT": "Spatial/determinants", "DIAG": "Diagnosis/surveillance performance",
            "MODL": "Modelling", "CTRL": "Control/vaccines/health system", "HIST": "Review/historical"}
    ct = pd.crosstab(studies["pub_period"], studies["design_code"]).reindex(columns=dorder, fill_value=0)
    pal = ["#000000", "#404040", "#737373", "#a6a6a6", "#d4d4d4", "#ffffff", "#ffffff", "#f0f0f0", "#8c8c8c"]
    hatch = ["", "", "", "", "", "////", "....", "xxxx", "\\\\\\\\"]
    bottom = np.zeros(len(ct))
    for i, d in enumerate(dorder):
        bx.bar(range(len(ct)), ct[d].values, bottom=bottom, color=pal[i], hatch=hatch[i],
               edgecolor=INK, linewidth=0.4, width=0.68, label=dlab[d])
        bottom += ct[d].values
    for i, t in enumerate(bottom):
        bx.text(i, t + 0.5, f"n={int(t)}", ha="center", fontsize=7)
    bx.set_xticks(range(len(ct)), [str(x).replace("-", "–\n") for x in ct.index], rotation=0, fontsize=7)
    bx.set_xlabel("Publication period")
    bx.set_ylabel("Studies (n)")
    bx.legend(frameon=False, fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, 1.0),
              handlelength=1.3, labelspacing=0.3)
    bx.set_ylim(0, bottom.max() * 1.9)
    bx.text(-0.2, 1.02, "B", transform=bx.transAxes, fontweight="bold", fontsize=10)
    save(fig, "Figure2_geography_and_design")


def figure3(studies):
    """Completeness of serotype reporting."""
    order = ["Title/abstract", "Full text", "Inferred from context", "Not reported/not typed"]
    lab = {"Title/abstract": "Reported in title/abstract", "Full text": "Reported only in full text",
           "Inferred from context": "Not reported; inferred from other studies",
           "Not reported/not typed": "Not reported, not typed or full text unavailable"}
    d = studies[studies["serotype_status"] != "Not applicable"]
    ct = pd.crosstab(d["pub_period"], d["serotype_status"]).reindex(columns=order, fill_value=0)
    tot = ct.sum(axis=1)
    pct = ct.div(tot, axis=0) * 100
    pal = ["#252525", "#737373", "#bdbdbd", "#ffffff"]
    hatch = ["", "", "", "////"]
    fig, ax = plt.subplots(figsize=(15 * CM, 6.2 * CM))
    left = np.zeros(len(pct))
    for i, c in enumerate(order):
        ax.barh(range(len(pct)), pct[c].values, left=left, color=pal[i], hatch=hatch[i],
                edgecolor=INK, linewidth=0.4, height=0.62, label=lab[c])
        for j, (v, l) in enumerate(zip(pct[c].values, left)):
            if v >= 8:
                ax.text(l + v / 2, j, f"{v:.0f}%", ha="center", va="center", fontsize=7,
                        color="white" if i < 2 else INK,
                        bbox=dict(fc="white", ec="none", pad=0.6) if hatch[i] else None)
        left += pct[c].values
    ax.set_yticks(range(len(pct)), [f"{p} (n={n})" for p, n in zip(pct.index, tot.values)])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Studies (%)")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.45, -0.22), fontsize=7)
    save(fig, "Figure3_serotype_reporting")
    ct.assign(total=tot).to_csv(PROC / "figure3_table.csv", encoding="utf-8-sig")


def main():
    studies = pd.read_csv(PROC / "included_studies_coded.csv")
    studies["pub_period"] = pd.Categorical(studies["pub_period"],
        ["1981-1990", "1991-2000", "2001-2010", "2011-2020", "2021-2026"], ordered=True)
    sy = pd.read_csv(PROC / "serotype_year_evidence.csv")
    figure1(studies, sy)
    figure2(studies)
    figure3(studies)
    print("Figures written to", FIG)


if __name__ == "__main__":
    main()
