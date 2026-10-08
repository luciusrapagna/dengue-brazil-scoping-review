"""Fetch full bibliographic metadata (all authors, NLM journal abbreviation,
volume, issue, pages) for every reference cited in the manuscript.

Sources: NCBI E-utilities (PubMed) by PMID or DOI; Crossref as fallback.
Output: data/processed/references_metadata.json
"""
import json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "data" / "raw" / "cited_references.csv"
OUT = ROOT / "data" / "processed" / "references_metadata.json"
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
UA = {"User-Agent": "dengue-scoping-review/1.0 (mailto:INSERT_EMAIL)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()


def pmid_from_doi(doi):
    q = urllib.parse.quote(f"{doi}[doi]")
    x = json.loads(get(f"{EU}esearch.fcgi?db=pubmed&retmode=json&term={q}"))
    ids = x["esearchresult"]["idlist"]
    return ids[0] if len(ids) == 1 else None


def pubmed_record(pmid):
    root = ET.fromstring(get(f"{EU}efetch.fcgi?db=pubmed&retmode=xml&id={pmid}"))
    a = root.find(".//PubmedArticle")
    art = a.find(".//Article")
    authors = []
    for au in art.findall(".//AuthorList/Author"):
        if au.find("CollectiveName") is not None:
            authors.append(au.find("CollectiveName").text)
        else:
            ln = au.findtext("LastName") or ""
            ini = au.findtext("Initials") or ""
            authors.append(f"{ln} {ini}".strip())
    title = "".join(art.find("ArticleTitle").itertext()).strip()
    ji = a.find(".//JournalIssue")
    year = ji.findtext(".//PubDate/Year") or (ji.findtext(".//PubDate/MedlineDate") or "")[:4]
    doi = next((e.text for e in a.findall(".//ArticleId") if e.get("IdType") == "doi"), None)
    eloc = next((e.text for e in art.findall("ELocationID") if e.get("EIdType") != "doi"), None)
    return dict(source="pubmed", pmid=pmid, authors=authors, title=title,
                journal=a.findtext(".//MedlineJournalInfo/MedlineTA"),
                year=year, volume=ji.findtext("Volume"), issue=ji.findtext("Issue"),
                pages=art.findtext(".//Pagination/MedlinePgn") or eloc, doi=doi,
                language=art.findtext("Language"))


def crossref_record(doi):
    x = json.loads(get("https://api.crossref.org/works/" + urllib.parse.quote(doi)))["message"]
    authors = [f"{a.get('family','')} {''.join(p[0] for p in re.split(r'[ .-]+', a.get('given','')) if p)}".strip()
               for a in x.get("author", [])]
    return dict(source="crossref", pmid=None, authors=authors, title=x["title"][0],
                journal=(x.get("short-container-title") or x.get("container-title") or [""])[0],
                year=str(x.get("issued", {}).get("date-parts", [[None]])[0][0]),
                volume=x.get("volume"), issue=x.get("issue"),
                pages=x.get("page") or x.get("article-number"), doi=doi, language=None)


def main():
    import csv
    rows = list(csv.DictReader(open(REFS, encoding="utf-8")))
    done = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {}
    for r in rows:
        key = r["key"]
        if key in done or r.get("manual"):
            continue
        try:
            pmid = r["pmid"] or (pmid_from_doi(r["doi"]) if r["doi"] else None)
            rec = pubmed_record(pmid) if pmid else crossref_record(r["doi"])
            done[key] = rec
            print(f"{key}: {rec['source']} | {rec['authors'][:1]} {rec['year']} {rec['journal']}")
        except Exception as e:
            print(f"{key}: ERROR {e}")
        time.sleep(0.6)
    json.dump(done, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
