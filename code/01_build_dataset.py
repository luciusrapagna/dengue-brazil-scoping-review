"""Build the analytic dataset of the scoping review.

Input : data/raw/included_studies.xlsx  (charting table, 103 sources)
Output: data/processed/included_studies_coded.csv
        data/processed/serotype_year_evidence.csv

Coding of geography, scale, study design and epidemic period was done by the
review team from title, abstract and full text (see Supplementary Material S2
for the codebook). Every coding decision is written explicitly below so that it
can be audited and changed.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "included_studies.xlsx"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Codebook ---------------------------------------------------------------
DESIGN = {
    "SURV": "Descriptive/surveillance epidemiology",
    "SERO": "Seroepidemiological survey",
    "VIRO": "Virological, molecular or genomic",
    "CLIN": "Clinical course, severity and mortality",
    "SPAT": "Spatial, ecological and determinant analysis",
    "MODL": "Mathematical modelling",
    "DIAG": "Diagnosis and surveillance performance",
    "CTRL": "Control, vaccines and health-system response",
    "HIST": "Review or historical analysis",
}
REGION = {
    "AC": "North", "AM": "North", "AP": "North", "PA": "North", "RO": "North", "RR": "North", "TO": "North",
    "AL": "Northeast", "BA": "Northeast", "CE": "Northeast", "MA": "Northeast", "PB": "Northeast",
    "PE": "Northeast", "PI": "Northeast", "RN": "Northeast", "SE": "Northeast",
    "DF": "Central-West", "GO": "Central-West", "MS": "Central-West", "MT": "Central-West",
    "ES": "Southeast", "MG": "Southeast", "RJ": "Southeast", "SP": "Southeast",
    "PR": "South", "RS": "South", "SC": "South",
    "BR": "National",
    # pseudo-codes for studies whose state is not specified
    "NORTE": "North", "NORDESTE": "Northeast", "SUDESTE": "Southeast", "SUL": "South", "CO": "Central-West",
    "UNK": "Not specified",
}

# id: (state(s), spatial scale, design, epidemic period start, end)
# None = period not stated in the source.
CODING = {
    1: ("RR", "Municipal", "SURV", 1981, 1982), 2: ("RJ", "Municipal", "VIRO", 1986, 1986),
    3: ("RJ", "Municipal", "DIAG", 1986, 1986), 4: ("RJ", "State", "VIRO", 1990, 1990),
    5: ("SP", "Municipal", "SURV", 1990, 1991), 6: ("SP", "Municipal", "DIAG", 1990, 1991),
    7: ("RJ", "State", "VIRO", 1986, 1987), 8: ("MG", "State", "SERO", None, None),
    9: ("TO", "Municipal", "SERO", None, None), 10: ("SP", "Municipal", "SURV", 1990, 1991),
    11: ("RJ", "Municipal", "SERO", None, None), 12: ("BA", "State", "VIRO", 1994, 1994),
    13: ("SP", "Municipal", "SPAT", 1995, 1995), 14: ("CE", "Municipal", "SERO", 1993, 1994),
    15: ("CE", "Municipal", "SERO", 1994, 1994), 16: ("RN", "State", "VIRO", 1997, 1997),
    17: ("SP", "Municipal", "SERO", 1995, 1995), 18: ("MA", "Municipal", "SERO", 1995, 1996),
    19: ("BR", "National", "HIST", 1986, 2000), 20: ("BA", "Municipal", "SERO", 1987, 1995),
    21: ("RJ", "Municipal", "VIRO", 2000, 2001), 22: ("BA", "Municipal", "SURV", 1995, 1999),
    23: ("BR", "National", "CTRL", None, None), 24: ("BA", "Municipal", "SERO", None, None),
    25: ("ES", "Municipal", "VIRO", 1998, 1998), 26: ("SP", "State", "MODL", 2000, 2001),
    27: ("RJ", "Municipal", "CLIN", 2001, 2002), 28: ("AM", "Municipal", "SURV", 1998, 1999),
    29: ("RJ", "State", "VIRO", 2000, 2001), 30: ("MG", "Municipal", "CTRL", 1996, 2000),
    31: ("MA", "Municipal", "SURV", 1997, 2002), 32: ("RJ", "Municipal", "CLIN", 2001, 2002),
    33: ("GO", "Municipal", "SERO", 2001, 2001), 34: ("RJ", "Municipal", "CLIN", 2002, 2002),
    35: ("MG", "Municipal", "SPAT", 1997, 2001), 36: ("SP", "Municipal", "SPAT", 1990, 2002),
    37: ("RJ", "State", "VIRO", 2002, 2002), 38: ("BR", "National", "VIRO", 1988, 2001),
    39: ("BR", "National", "SURV", 1981, 2002), 40: ("BR", "National", "SURV", 1981, 2004),
    41: ("RJ", "Municipal", "DIAG", 2001, 2002), 42: ("BR", "National", "HIST", None, None),
    43: ("SP", "Municipal", "SERO", 1996, 2003), 44: ("BA", "State", "VIRO", 2002, 2003),
    45: ("RO", "Municipal", "VIRO", 2001, 2003), 46: ("RJ", "State", "SPAT", 2002, 2002),
    47: ("RJ", "State", "DIAG", 2002, 2002), 48: ("DF", "Municipal", "MODL", 2003, 2003),
    49: ("SP", "Municipal", "VIRO", 2006, 2006), 50: ("BR", "National", "HIST", 1981, 2008),
    51: ("CE", "State", "CLIN", 2003, 2003), 52: ("AM", "Municipal", "SURV", 2008, 2009),
    53: ("RR", "Municipal", "VIRO", 2010, 2010), 54: ("RJ", "Municipal", "CLIN", 2007, 2008),
    55: ("BR", "National", "HIST", 2000, 2010), 56: ("PI", "State", "VIRO", 2006, 2007),
    57: ("CE", "State", "CLIN", 2011, 2011), 58: ("RJ", "Municipal", "SPAT", 2008, 2008),
    59: ("AM", "Municipal", "VIRO", 2011, 2011), 60: ("CE", "State", "CLIN", 2011, 2012),
    61: ("SP", "Municipal", "SPAT", None, None), 62: ("MT", "State", "VIRO", 2012, 2012),
    63: ("BA", "Municipal", "SPAT", 2009, 2009), 64: ("RJ;PE", "Multi-state", "CLIN", 2012, 2012),
    65: ("RJ", "Municipal", "DIAG", 2013, 2013), 66: ("BR", "National", "SURV", 2002, 2012),
    67: ("RJ", "Municipal", "VIRO", 1990, 2011), 68: ("BR", "National", "SURV", 2000, 2015),
    69: ("RJ", "Municipal", "VIRO", 2012, 2012), 70: ("GO", "Municipal", "CLIN", 2012, 2013),
    71: ("BR", "National", "CLIN", 1986, 2015), 72: ("SP", "Municipal", "SURV", 1998, 2013),
    73: ("CE", "Municipal", "SURV", 2001, 2012), 74: ("CE", "State", "SURV", 2012, 2012),
    75: ("AM", "State", "SPAT", 2010, 2011), 76: ("BR", "National", "CTRL", 1991, 2015),
    77: ("BR", "National", "CLIN", 1986, 2015), 78: ("SC", "Municipal", "SURV", 2015, 2016),
    79: ("DF", "State", "SPAT", 2007, 2017), 80: ("CE", "State", "SPAT", 2001, 2019),
    81: ("BR", "National", "HIST", 1980, 2018), 82: ("SP", "Municipal", "VIRO", 2000, 2015),
    83: ("MG", "Municipal", "SURV", 1996, 2017), 84: ("SP", "Municipal", "SPAT", 2007, 2015),
    85: ("SP", "State", "SPAT", 2007, 2019), 86: ("RJ", "Municipal", "CLIN", 2008, 2012),
    87: ("RJ", "Municipal", "HIST", 1986, 1987), 88: ("MG", "Municipal", "SURV", 2013, 2017),
    89: ("SP", "State", "CLIN", 2007, 2017), 90: ("RS", "State", "VIRO", 2022, 2022),
    91: ("PE", "State", "CLIN", 2015, 2018), 92: ("BR", "National", "CTRL", 2000, 2024),
    93: ("MG", "Municipal", "SPAT", 2011, 2017), 94: ("RJ", "Municipal", "CTRL", 2017, 2024),
    95: ("BR", "National", "DIAG", 2024, 2024), 96: ("SP", "State", "CTRL", 2024, 2024),
    97: ("BR", "National", "HIST", 1986, 2024), 98: ("BR", "National", "SURV", 2001, 2022),
    99: ("BR", "National", "CTRL", 2024, 2024), 100: ("BR", "Multi-state", "VIRO", 2023, 2025),
    101: ("MG", "Municipal", "DIAG", 2022, 2024), 102: ("MG", "Municipal", "CLIN", 2024, 2024),
    103: ("ES", "State", "CLIN", 2020, 2024),
}

# Serotype-year evidence: (study id, serotype, first year, last year).
# Only primary evidence of circulation in a dated epidemic period is recorded;
# narrative histories (ids 19, 42, 81, 97) are excluded to avoid double counting.
SERO_YEARS = [
    (1, 1, 1981, 1982), (1, 4, 1981, 1982), (2, 1, 1986, 1986), (3, 1, 1986, 1986),
    (4, 2, 1990, 1990), (5, 1, 1990, 1991), (6, 1, 1990, 1991), (7, 1, 1986, 1987),
    (12, 2, 1994, 1994), (13, 1, 1995, 1995), (15, 2, 1994, 1994), (16, 1, 1997, 1997),
    (16, 2, 1997, 1997), (17, 1, 1995, 1995), (18, 1, 1995, 1996), (20, 1, 1987, 1987),
    (20, 2, 1995, 1995), (21, 3, 2000, 2001), (22, 1, 1995, 1999), (22, 2, 1995, 1999),
    (25, 1, 1998, 1998), (27, 1, 2001, 2002), (27, 2, 2001, 2002), (27, 3, 2001, 2002),
    (29, 1, 2000, 2001), (29, 2, 2000, 2001), (29, 3, 2000, 2001), (31, 1, 1997, 1998),
    (31, 2, 2001, 2001), (31, 3, 2002, 2002), (32, 1, 2001, 2002), (32, 2, 2001, 2002),
    (32, 3, 2001, 2002), (34, 3, 2002, 2002), (36, 1, 1990, 1995), (36, 1, 1996, 2002),
    (36, 2, 1996, 2002), (37, 3, 2002, 2002), (38, 1, 1988, 2001), (38, 2, 1990, 2001),
    (43, 1, 1996, 1998), (43, 2, 1996, 1998), (44, 3, 2002, 2003), (44, 1, 2002, 2003),
    (44, 2, 2002, 2003), (45, 1, 2001, 2003), (46, 3, 2001, 2002), (46, 2, 2001, 2001),
    (47, 3, 2002, 2002), (49, 3, 2006, 2006), (51, 3, 2003, 2003), (53, 4, 2010, 2010),
    (55, 1, 2000, 2002), (55, 3, 2003, 2006), (55, 2, 2007, 2010), (56, 2, 2006, 2007),
    (57, 1, 2011, 2011), (57, 3, 2011, 2011), (57, 4, 2011, 2011), (58, 2, 2008, 2008),
    (59, 1, 2011, 2011), (59, 2, 2011, 2011), (59, 3, 2011, 2011), (59, 4, 2011, 2011),
    (60, 1, 2011, 2012), (60, 3, 2011, 2012), (60, 4, 2011, 2012), (62, 4, 2012, 2012),
    (62, 1, 2012, 2012), (63, 2, 2009, 2009), (64, 4, 2012, 2012), (65, 4, 2013, 2013),
    (67, 2, 1990, 1990), (67, 2, 1998, 1998), (67, 2, 2008, 2008), (69, 4, 2012, 2012),
    (70, 4, 2012, 2013), (70, 1, 2012, 2013), (70, 3, 2012, 2013), (70, 2, 2012, 2013),
    (73, 1, 2001, 2001), (73, 2, 2001, 2001), (73, 3, 2006, 2006), (73, 2, 2008, 2008),
    (73, 1, 2011, 2011), (73, 4, 2012, 2012), (74, 4, 2012, 2012), (74, 1, 2012, 2012),
    (74, 3, 2012, 2012), (78, 1, 2015, 2016), (79, 1, 2010, 2010), (79, 2, 2010, 2010),
    (79, 3, 2010, 2010), (79, 1, 2013, 2014), (79, 4, 2013, 2013), (82, 1, 2007, 2007),
    (82, 3, 2007, 2007), (82, 1, 2015, 2015), (84, 3, 2007, 2007), (84, 1, 2014, 2015),
    (85, 1, 2000, 2000), (85, 2, 2000, 2000), (85, 3, 2003, 2003), (85, 1, 2010, 2010),
    (85, 4, 2010, 2010), (85, 4, 2013, 2015), (86, 2, 2008, 2008), (86, 4, 2012, 2012),
    (87, 1, 1986, 1987), (90, 1, 2022, 2022), (93, 1, 2011, 2017), (93, 4, 2011, 2017),
    (96, 1, 2024, 2024), (96, 2, 2024, 2024), (98, 1, 2014, 2023), (98, 2, 2014, 2023),
    (98, 3, 2023, 2023), (100, 3, 2023, 2025), (100, 1, 2023, 2025), (100, 2, 2023, 2025),
    (101, 1, 2022, 2024), (102, 1, 2024, 2024), (102, 2, 2024, 2024), (102, 3, 2024, 2024),
]


def _load(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.stem, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# groups of municipalities (metropolitan or health regions) coded as municipal scale
SCALE_FIX = {138: "Municipal", 213: "Municipal", 390: "Municipal", 438: "Municipal", 448: "Municipal"}


def add_lilacs(df):
    """Append the studies included after the full screening of LILACS (ids 104 onwards)."""
    add = _load(ROOT / "data" / "raw" / "lilacs_additions.py")
    ft = _load(ROOT / "data" / "raw" / "lilacs_fulltext.py")
    recs = sorted(add.ADDITIONS, key=lambda r: (r[2], r[1]))
    rows, sero = [], []
    for n, r in enumerate(recs, start=len(df) + 1):
        (idx, au, yr, ti, jo, doi, lang, setting, sero_txt, find, st, scale, des, a, b, sy) = r
        if idx in ft.FULLTEXT_FOUND:
            sero_txt, sy = ft.FULLTEXT_FOUND[idx][0], sy + ft.FULLTEXT_FOUND[idx][1]
        elif sero_txt == add.NR:
            sero_txt = ("Não informado no resumo; texto completo não acessado" if idx in ft.NOT_ACCESSED
                        else "Não informado (texto completo)")
        rows.append(dict(id=n, author=au, year=yr, title=ti, setting=setting, serotype=sero_txt,
                         main_findings=find, doi=doi or "Não informado", journal=jo, language=lang,
                         databases="LILACS", lilacs_index=idx))
        CODING[n] = (st, SCALE_FIX.get(idx, scale), des, a, b)
        sero += [(n, s_, y1, y2) for s_, y1, y2 in sy]
    return pd.concat([df, pd.DataFrame(rows)], ignore_index=True), sero


def serotype_status(s: str) -> str:
    """Where the serotype information came from."""
    if s.startswith("Não se aplica"):
        return "Not applicable"
    if s.startswith("Não informado") or s.startswith("Não tipado") or s.startswith("Não identificado")             or "inacessível" in s or "não acessado" in s:
        return "Not reported/not typed"
    if "†" in s:
        return "Full text"
    if "*" in s:
        return "Inferred from context"
    return "Title/abstract"


def main():
    df = pd.read_excel(RAW, sheet_name=0)
    df.columns = ["id", "author", "year", "title", "setting", "serotype", "main_findings",
                  "doi", "journal", "language", "databases"]
    assert set(CODING) == set(df["id"]), "Every study must be coded"
    df, lil_sero_years = add_lilacs(df)
    cod = pd.DataFrame.from_dict(CODING, orient="index",
                                 columns=["states", "scale", "design_code", "period_start", "period_end"])
    df = df.merge(cod, left_on="id", right_index=True)
    df["design"] = df["design_code"].map(DESIGN)
    df["region"] = df["states"].apply(lambda s: ";".join(sorted({REGION[u] for u in s.split(";")})))
    df["serotype_status"] = df["serotype"].apply(serotype_status)
    df["serotype_in_abstract"] = df["serotype_status"].eq("Title/abstract")
    df["pub_period"] = pd.cut(df["year"], [1980, 1990, 2000, 2010, 2020, 2026],
                              labels=["1981-1990", "1991-2000", "2001-2010", "2011-2020", "2021-2026"])
    df["language_en"] = df["language"].replace({"Inglês": "English", "Português": "Portuguese",
                                                 "Espanhol": "Spanish", "Inglês/Português": "English/Portuguese"})
    for k in ["PubMed", "SciELO", "ScienceDirect", "SciSpace", "LILACS"]:
        df[f"db_{k}"] = df["databases"].str.contains(k)
    df.to_csv(OUT / "included_studies_coded.csv", index=False, encoding="utf-8-sig")

    sy = pd.DataFrame(SERO_YEARS + lil_sero_years, columns=["id", "serotype", "year_start", "year_end"])
    assert sy["id"].isin(df["id"]).all()
    rows = [(r.id, f"DENV-{r.serotype}", y) for r in sy.itertuples()
            for y in range(r.year_start, r.year_end + 1)]
    pd.DataFrame(rows, columns=["id", "serotype", "year"]).drop_duplicates().merge(
        df[["id", "states", "region"]], on="id").to_csv(
        OUT / "serotype_year_evidence.csv", index=False, encoding="utf-8-sig")
    print(f"{len(df)} studies coded; {len(rows)} serotype-year records")


if __name__ == "__main__":
    main()
