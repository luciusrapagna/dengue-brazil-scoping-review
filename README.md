# Four decades of dengue epidemics in Brazil — data and code

Data, search log, codebook and Python scripts for the scoping review
**"Four decades of dengue epidemics in Brazil: a scoping review of serotype succession, severity and evidence gaps"**
(manuscript under review). The manuscript text will be added after publication.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23242684.svg)](https://doi.org/10.5281/zenodo.23242684)

## Summary

The review mapped 103 studies on dengue epidemics in Brazil published from 1983 to 2026 in English,
Portuguese and Spanish (PubMed/MEDLINE, SciELO, ScienceDirect and the SciSpace semantic index; searches on
7 October 2026). Each study was charted and coded for federative unit, region, spatial scale, design,
epidemic period and serotype(s), and a serotype-year evidence matrix was built from 62 studies
(260 serotype-year records).

## Repository structure

```
data/
  raw/
    included_studies.xlsx       charting table of the 103 included studies
    search_log.csv              sources, dates, strategies and numbers of records
    prisma_counts.csv           counts for the PRISMA-ScR flow diagram
    cited_references.csv        PMIDs/DOIs of the references cited in the article
  processed/
    included_studies_coded.csv  coded variables for each study
    serotype_year_evidence.csv  one row per study x serotype x year (Figure 1)
    references_metadata.json    bibliographic metadata (PubMed/Crossref)
code/
  00_fetch_references.py        downloads reference metadata (NCBI E-utilities, Crossref)
  01_build_dataset.py           codebook and coding of the included studies
  02_figures.py                 Figures 1-3 (PNG 300 dpi, TIFF, PDF, editable SVG)
  03_tables.py                  Table 2 and all statistics reported in the Results
  04_prisma.py                  PRISMA-ScR flow diagram (Supplementary Figure S1)
  05_build_manuscript.py        builds the manuscript and Table 1 (requires the manuscript text)
  06_supplementary.py           Supplementary Material S1-S3
  07_cover_letter.py            cover letter (requires the manuscript text)
  run_all.py                    runs the pipeline
figures/                        Figures 1-3
tables/                         Tables 1-2 (.docx, editable), Table 2 (.csv/.xlsx), stats_for_text.json
supplementary/                  S1 included studies, S2 search log, S3 PRISMA-ScR checklist, Figure S1
```

## Reproducing the analysis

```bash
python -m pip install -r requirements.txt
python code/run_all.py
```

Python 3.12 was used. The figures use Times New Roman.

## Codebook

Study design/focus: VIRO virological, molecular or genomic; SERO seroepidemiological survey; SURV descriptive or
surveillance epidemiology; CLIN clinical course, severity and mortality; SPAT spatial, ecological and determinant
analysis; DIAG diagnosis and surveillance performance; MODL mathematical modelling; CTRL control, vaccines and
health-system response; HIST review or historical analysis.

Source of serotype information: title/abstract; full text (marked † in the charting table); inferred from other
included studies (marked *); not reported, not typed or full text unavailable; not applicable.

## Limitations of the search

The LILACS/Virtual Health Library portal was unavailable (HTTP 502) on 7 and 8 October 2026. Four broader
PubMed strategies were screened up to their 30-60 top-ranked records and ScienceDirect up to its first 50
results (see `data/raw/search_log.csv`).

## How to cite

See `CITATION.cff` or the Zenodo record: https://doi.org/10.5281/zenodo.23242684

## Licences

Code: MIT (`LICENSE`). Data, figures, tables and supplementary material: CC BY 4.0 (`LICENSE-DATA.md`).
