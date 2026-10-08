"""Descriptive tables and statistics reported in the manuscript.

Outputs (tables/):
  table2_characteristics.csv / .xlsx  - characteristics of the 103 included studies
  stats_for_text.json                 - every number quoted in the Results section
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
TAB = ROOT / "tables"
TAB.mkdir(exist_ok=True)
PERIODS = ["1981-1990", "1991-2000", "2001-2010", "2011-2020", "2021-2026"]


def pct(n, d):
    return f"{n} ({100 * n / d:.1f})"


def cochran_armitage(successes, totals, scores=None):
    """Two-sided Cochran-Armitage test for trend in proportions."""
    s = np.asarray(successes, float); n = np.asarray(totals, float)
    x = np.arange(len(s), dtype=float) if scores is None else np.asarray(scores, float)
    p = s.sum() / n.sum()
    t = np.sum(x * (s - n * p))
    var = p * (1 - p) * (np.sum(n * x ** 2) - np.sum(n * x) ** 2 / n.sum())
    z = t / np.sqrt(var)
    return float(z), float(2 * stats.norm.sf(abs(z)))


def main():
    d = pd.read_csv(PROC / "included_studies_coded.csv")
    N = len(d)
    rows = []

    def block(title, series, order=None):
        rows.append((title, ""))
        vc = series.value_counts()
        for k in (order or vc.index):
            rows.append((f"   {k}", pct(int(vc.get(k, 0)), N)))

    block("Publication period", d["pub_period"], PERIODS)
    block("Language of publication", d["language_en"], ["English", "Portuguese", "Spanish", "English/Portuguese"])
    rows.append(("Database where retrieved (not mutually exclusive)", ""))
    for k in ["PubMed", "SciELO", "ScienceDirect", "SciSpace"]:
        rows.append((f"   {k}", pct(int(d[f"db_{k}"].sum()), N)))
    rows.append(("Region of study (not mutually exclusive)", ""))
    reg = d["region"].str.split(";").explode().value_counts()
    for k in ["Southeast", "Northeast", "North", "Central-West", "South", "National"]:
        rows.append((f"   {k}", pct(int(reg.get(k, 0)), N)))
    block("Spatial scale", d["scale"], ["Municipal", "State", "Multi-state", "National"])
    block("Study design/focus", d["design"])
    block("Source of serotype information", d["serotype_status"],
          ["Title/abstract", "Full text", "Inferred from context", "Not reported/not typed", "Not applicable"])
    t2 = pd.DataFrame(rows, columns=["Characteristic", "n (%)"])
    t2.to_csv(TAB / "table2_characteristics.csv", index=False, encoding="utf-8-sig")
    t2.to_excel(TAB / "table2_characteristics.xlsx", index=False)

    # numbers quoted in the text ------------------------------------------
    a = d[d["serotype_status"] != "Not applicable"]
    ct = pd.crosstab(a["pub_period"], a["serotype_status"]).reindex(PERIODS, fill_value=0)
    tot = ct.sum(axis=1)
    z, p = cochran_armitage(ct["Title/abstract"].values, tot.values)
    states = d["states"].str.split(";").explode().value_counts()
    des_abs = a.groupby("design_code")["serotype_status"].apply(lambda s: (s == "Title/abstract").mean())
    sy = pd.read_csv(PROC / "serotype_year_evidence.csv")
    out = dict(
        n_studies=N,
        n_applicable_serotype=len(a),
        serotype_abstract=int((a.serotype_status == "Title/abstract").sum()),
        serotype_fulltext=int((a.serotype_status == "Full text").sum()),
        serotype_context=int((a.serotype_status == "Inferred from context").sum()),
        serotype_notreported=int((a.serotype_status == "Not reported/not typed").sum()),
        abstract_by_period={k: f"{ct.loc[k, 'Title/abstract']}/{tot[k]} ({100*ct.loc[k,'Title/abstract']/tot[k]:.1f}%)" for k in PERIODS},
        trend_z=round(z, 2), trend_p=round(p, 4),
        abstract_share_by_design={k: round(v * 100, 1) for k, v in des_abs.items()},
        n_by_design=d["design_code"].value_counts().to_dict(),
        states=states.to_dict(),
        regions=d["region"].str.split(";").explode().value_counts().to_dict(),
        scale=d["scale"].value_counts().to_dict(),
        studies_in_serotype_map=int(sy["id"].nunique()),
        serotype_year_records=int(len(sy)),
        peak_years=sy.groupby("year")["id"].nunique().sort_values(ascending=False).head(4).to_dict(),
        languages=d["language_en"].value_counts().to_dict(),
        not_in_pubmed=int((~d["db_PubMed"]).sum()),
        pub_period=d["pub_period"].value_counts().reindex(PERIODS).to_dict(),
    )
    json.dump(out, open(TAB / "stats_for_text.json", "w", encoding="utf-8"), indent=1, default=int)
    print(json.dumps(out, indent=1, default=int))


if __name__ == "__main__":
    main()
