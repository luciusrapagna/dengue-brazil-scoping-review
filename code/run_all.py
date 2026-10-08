"""Reproduce the full analysis: python code/run_all.py

Step 00 (reference metadata download) needs internet access. Steps 05 and 07
build the manuscript and cover letter; they are skipped when the manuscript
text (manuscript/manuscript_source.md) is not present, as in the public
repository before publication."""
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "manuscript" / "manuscript_source.md"
STEPS = ["00_fetch_references.py", "01_build_dataset.py", "02_figures.py", "03_tables.py",
         "04_prisma.py", "05_build_manuscript.py", "06_supplementary.py", "07_cover_letter.py"]

for s in STEPS:
    if s in ("05_build_manuscript.py", "07_cover_letter.py") and not SOURCE.exists():
        print(f"\n=== {s} skipped (manuscript text not distributed in this repository) ===")
        continue
    print(f"\n=== {s} ===")
    runpy.run_path(str(HERE / s), run_name="__main__")
