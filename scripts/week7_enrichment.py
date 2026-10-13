#!/usr/bin/env python3
"""
Week 7: pathway / gene-ontology enrichment of the differentially expressed genes.

Method: over-representation analysis with the Enrichr web service, called through
the gseapy Python package. Up-in-tumor and down-in-tumor genes are tested
separately against GO Biological Process, KEGG and MSigDB Hallmark.

Input  (written by week6_analysis.py):
  results/deseq2_significant_genes.tsv   padj < 0.05 and |log2FC| >= 1

Outputs (results/):
  enrichment_up_in_tumor.tsv / enrichment_down_in_tumor.tsv   all terms, all libraries
  enrichment_summary.txt                                       top terms per library
  fig_enrichment.png                                           top-10 bar plots

Needs internet access (queries https://maayanlab.cloud/Enrichr).
Note: Enrichr's web service uses its own default background gene set, not the
list of genes expressed in this experiment. Mention this in the methods.

Run from the project root:   python scripts/week7_enrichment.py
"""
import re
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gseapy as gp

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
COLORS = {"Up in tumor": "#c0392b", "Down in tumor": "#2874a6"}
TOP_N = 10          # terms plotted per panel
MIN_GENES = 10      # skip a direction with fewer recognised symbols than this


def latest(available, prefix, suffix=""):
    """Pick the newest Enrichr library whose name starts with `prefix`
    (e.g. GO_Biological_Process_2023 vs _2025), so we do not hard-code a year."""
    cands = [n for n in available if n.startswith(prefix) and n.endswith(suffix)]
    cands = [n for n in cands if re.fullmatch(prefix + r"\d{4}" + suffix, n)] or cands
    if not cands:
        return None
    return sorted(cands, key=lambda n: re.findall(r"\d{4}", n) or ["0"])[-1]


def pick_libraries():
    try:
        try:
            available = gp.get_library_name(organism="Human")
        except TypeError:
            available = gp.get_library_name()
    except Exception as e:  # network hiccup: fall back to long-standing names
        print("Could not list Enrichr libraries (", e, ") - using default names")
        return ["GO_Biological_Process_2023", "KEGG_2021_Human", "MSigDB_Hallmark_2020"]
    libs = [latest(available, "GO_Biological_Process_"),
            latest(available, "KEGG_", "_Human"),
            latest(available, "MSigDB_Hallmark_")]
    return [l for l in libs if l]


def symbols(df):
    """Gene symbols only: drop Ensembl IDs that GENCODE has no name for."""
    s = df["gene_name"].dropna().astype(str)
    return sorted({g for g in s if not g.startswith("ENSG")})


def run_enrichr(genes, libs, tries=3):
    for attempt in range(1, tries + 1):
        try:
            enr = gp.enrichr(gene_list=genes, gene_sets=libs, organism="human",
                             outdir=None, cutoff=0.05)
            return enr.results
        except Exception as e:
            print(f"  Enrichr attempt {attempt} failed: {e}")
            time.sleep(5 * attempt)
    raise SystemExit("Enrichr could not be reached - check the internet connection and retry.")


def clean_term(term, n=60):
    term = re.sub(r"\s*\(GO:\d+\)", "", term)
    term = re.sub(r"\s*Homo sapiens.*$", "", term)
    return term if len(term) <= n else term[: n - 1] + "…"


def short_lib(name):
    return (name.replace("_Human", "").replace("GO_Biological_Process", "GO Biological Process")
            .replace("MSigDB_Hallmark", "MSigDB Hallmark").replace("_", " "))


# ------------------------------------------------------------------ run
sig = pd.read_csv(RES / "deseq2_significant_genes.tsv", sep="\t")
libs = pick_libraries()
print("Libraries:", libs)

results, summary = {}, []
for direction in ["Up in tumor", "Down in tumor"]:
    genes = symbols(sig[sig["regulation"] == direction])
    print(f"{direction}: {len(genes)} gene symbols submitted")
    if len(genes) < MIN_GENES:
        print("  too few genes - skipped")
        continue
    df = run_enrichr(genes, libs)
    df = df.sort_values("Adjusted P-value")
    df.insert(0, "direction", direction)
    results[direction] = df
    out = RES / ("enrichment_" + direction.lower().replace(" ", "_") + ".tsv")
    df.to_csv(out, sep="\t", index=False)
    summary.append(f"=== {direction} ({len(genes)} genes submitted) ===")
    for lib in libs:
        d = df[df["Gene_set"] == lib].head(5)
        n_sig = int((df[df["Gene_set"] == lib]["Adjusted P-value"] < 0.05).sum())
        summary.append(f"\n{short_lib(lib)}  ({n_sig} terms with adj. p < 0.05)")
        for _, r in d.iterrows():
            summary.append(f"  {clean_term(r['Term'], 70):<72} overlap {r['Overlap']:>9}  "
                           f"adj.p {r['Adjusted P-value']:.2g}")
    summary.append("")

text = "\n".join(summary)
(RES / "enrichment_summary.txt").write_text(text)
print(text)

# ------------------------------------------------------------------ figure
if results:
    fig, axes = plt.subplots(len(libs), 2, figsize=(14, 3.6 * len(libs)))
    axes = np.atleast_2d(axes)
    for j, direction in enumerate(["Up in tumor", "Down in tumor"]):
        for i, lib in enumerate(libs):
            ax = axes[i, j]
            df = results.get(direction)
            d = df[df["Gene_set"] == lib].nsmallest(TOP_N, "Adjusted P-value") if df is not None else None
            if d is None or d.empty:
                ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
                ax.set_axis_off()
                continue
            vals = -np.log10(d["Adjusted P-value"].clip(lower=1e-300))
            ax.barh(range(len(d)), vals, color=COLORS[direction])
            ax.set_yticks(range(len(d)))
            ax.set_yticklabels([clean_term(t) for t in d["Term"]], fontsize=8)
            ax.invert_yaxis()
            ax.axvline(-np.log10(0.05), ls="--", lw=0.8, c="grey")
            ax.set_xlabel("-log10 adjusted p-value", fontsize=8)
            ax.set_title(f"{short_lib(lib)} - {direction}", fontsize=9)
    fig.tight_layout()
    fig.savefig(RES / "fig_enrichment.png", dpi=200)
    plt.close(fig)

print("Done. Tables, summary and figure written to", RES)
