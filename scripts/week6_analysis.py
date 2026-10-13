#!/usr/bin/env python3
"""
Week 5-6: annotate DESeq2 results, summarise DEGs, and make figures.

Inputs  (relative to the project root, i.e. the folder that contains scripts/):
  results/deseq2_results_tumor_vs_normal.tsv   Galaxy DESeq2 output (no header; 7 columns)
  counts/gene_counts_matrix.tsv                featureCounts matrix (Geneid + 10 samples)
  counts/gene_id_to_name.tsv                   GENCODE gene_id <tab> gene_name

Outputs (written to results/):
  deseq2_results_annotated.tsv     full table with gene names, sorted by adjusted p-value
  deseq2_significant_genes.tsv     padj < 0.05 and |log2FC| >= 1
  deseq2_summary.txt               counts of up/down genes and top-10 lists
  fig_pca.png / fig_volcano.png / fig_heatmap_top50.png

Comparison direction (verified against known markers): Tumor vs Normal,
so a positive log2FC means HIGHER in tumor.

Run from the project root:   python scripts/week6_analysis.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
PADJ_CUT = 0.05
LFC_CUT = 1.0

# ---------------------------------------------------------------- sample info
SAMPLES = {  # sample: (patient, condition)
    "SRR975554": ("P1", "Tumor"), "SRR975572": ("P1", "Normal"),
    "SRR975556": ("P2", "Tumor"), "SRR975574": ("P2", "Normal"),
    "SRR975559": ("P3", "Tumor"), "SRR975577": ("P3", "Normal"),
    "SRR975564": ("P4", "Tumor"), "SRR975582": ("P4", "Normal"),
    "SRR975567": ("P5", "Tumor"), "SRR975585": ("P5", "Normal"),
}
COLORS = {"Tumor": "#c0392b", "Normal": "#2874a6"}

# ------------------------------------------------- 1. annotate DESeq2 results
cols = ["gene_id", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"]
res = pd.read_csv(RES / "deseq2_results_tumor_vs_normal.tsv", sep="\t",
                  header=None, names=cols, na_values=["NA", "NaN", ""])
names = pd.read_csv(ROOT / "counts" / "gene_id_to_name.tsv", sep="\t",
                    header=None, names=["gene_id", "gene_name"])
res = res.merge(names, on="gene_id", how="left")
res["gene_name"] = res["gene_name"].fillna(res["gene_id"])

sig = (res["padj"] < PADJ_CUT) & (res["log2FoldChange"].abs() >= LFC_CUT)
res["regulation"] = "Not significant"
res.loc[sig & (res["log2FoldChange"] > 0), "regulation"] = "Up in tumor"
res.loc[sig & (res["log2FoldChange"] < 0), "regulation"] = "Down in tumor"

res = res[["gene_id", "gene_name", "baseMean", "log2FoldChange", "lfcSE",
           "stat", "pvalue", "padj", "regulation"]].sort_values("padj")
res.to_csv(RES / "deseq2_results_annotated.tsv", sep="\t", index=False)
res[res["regulation"] != "Not significant"].to_csv(
    RES / "deseq2_significant_genes.tsv", sep="\t", index=False)

# ------------------------------------------------------------- 2. summary
tested = res["padj"].notna().sum()
n_padj = (res["padj"] < PADJ_CUT).sum()
n_up = (res["regulation"] == "Up in tumor").sum()
n_down = (res["regulation"] == "Down in tumor").sum()
top_up = res[res["regulation"] == "Up in tumor"].nlargest(10, "log2FoldChange")
top_down = res[res["regulation"] == "Down in tumor"].nsmallest(10, "log2FoldChange")
top_sig = res.head(10)


def fmt(df):
    return df[["gene_name", "log2FoldChange", "padj"]].to_string(
        index=False, float_format=lambda x: f"{x:.3g}")


summary = f"""DESeq2 summary: Tumor vs Normal (positive log2FC = higher in tumor)
Genes in table:                        {len(res)}
Genes with an adjusted p-value (tested): {tested}
padj < {PADJ_CUT}:                              {n_padj}
padj < {PADJ_CUT} and |log2FC| >= {LFC_CUT:g}:           {n_up + n_down}
   up in tumor:                        {n_up}
   down in tumor:                      {n_down}

Top 10 by adjusted p-value:
{fmt(top_sig)}

Top 10 up in tumor (largest log2FC among significant genes):
{fmt(top_up)}

Top 10 down in tumor (most negative log2FC among significant genes):
{fmt(top_down)}
"""
(RES / "deseq2_summary.txt").write_text(summary)
print(summary)

# -------------------------------------------- 3. normalised counts (for plots)
counts = pd.read_csv(ROOT / "counts" / "gene_counts_matrix.tsv", sep="\t", index_col=0)
counts = counts[list(SAMPLES)]  # fixed, known column order
# DESeq2 median-of-ratios size factors
with np.errstate(divide="ignore"):
    logc = np.log(counts.where(counts > 0))
geo_mean = logc.mean(axis=1, skipna=False)  # genes with any zero -> NaN -> excluded
ok = geo_mean.notna()
size_factors = np.exp((logc[ok].sub(geo_mean[ok], axis=0)).median(axis=0))
norm = counts.div(size_factors, axis=1)
lognorm = np.log2(norm + 1)
pd.DataFrame({"sample": size_factors.index, "size_factor": size_factors.values}).to_csv(
    RES / "size_factors.tsv", sep="\t", index=False)

label = {s: f"{p}-{c[0]}" for s, (p, c) in SAMPLES.items()}  # e.g. P1-T / P1-N

# ----------------------------------------------------------------- 4. PCA
keep = norm.mean(axis=1) >= 10                       # drop very low-count genes
top = lognorm[keep].var(axis=1).nlargest(500).index  # 500 most variable genes
X = lognorm.loc[top].T
X = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(X.values, full_matrices=False)
pcs = U * S
var = S ** 2 / (S ** 2).sum() * 100

fig, ax = plt.subplots(figsize=(6.5, 5.2))
markers = {"P1": "o", "P2": "s", "P3": "^", "P4": "D", "P5": "P"}
for i, s in enumerate(X.index):
    pat, cond = SAMPLES[s]
    ax.scatter(pcs[i, 0], pcs[i, 1], s=90, c=COLORS[cond], marker=markers[pat],
               edgecolor="black", linewidth=0.6, zorder=3)
    ax.annotate(label[s], (pcs[i, 0], pcs[i, 1]), xytext=(6, 5),
                textcoords="offset points", fontsize=8)
ax.set_xlabel(f"PC1 ({var[0]:.0f}% variance)")
ax.set_ylabel(f"PC2 ({var[1]:.0f}% variance)")
ax.set_title("PCA of log2(normalised counts + 1), top 500 variable genes")
ax.grid(alpha=0.25)
handles = [plt.Line2D([], [], marker="o", ls="", color=COLORS[c], label=c,
                      markeredgecolor="black") for c in COLORS]
ax.legend(handles=handles, frameon=False, loc="best")
fig.tight_layout()
fig.savefig(RES / "fig_pca.png", dpi=200)
plt.close(fig)

# -------------------------------------------------------------- 5. volcano
v = res.dropna(subset=["padj"]).copy()
v["nlp"] = -np.log10(v["padj"].clip(lower=1e-300))
fig, ax = plt.subplots(figsize=(7, 5.6))
palette = {"Not significant": "#b0b0b0", "Up in tumor": COLORS["Tumor"],
           "Down in tumor": COLORS["Normal"]}
for k in ["Not significant", "Down in tumor", "Up in tumor"]:
    d = v[v["regulation"] == k]
    ax.scatter(d["log2FoldChange"], d["nlp"], s=6 if k == "Not significant" else 9,
               c=palette[k], alpha=0.55 if k == "Not significant" else 0.8,
               linewidths=0, label=f"{k} ({len(d)})")
ax.axhline(-np.log10(PADJ_CUT), ls="--", lw=0.8, c="grey")
ax.axvline(LFC_CUT, ls="--", lw=0.8, c="grey")
ax.axvline(-LFC_CUT, ls="--", lw=0.8, c="grey")
lab = pd.concat([v[v["regulation"] == "Up in tumor"].nsmallest(8, "padj"),
                 v[v["regulation"] == "Down in tumor"].nsmallest(8, "padj")])
try:
    from adjustText import adjust_text  # optional: pip install adjustText
    texts = [ax.text(r["log2FoldChange"], r["nlp"], r["gene_name"], fontsize=7)
             for _, r in lab.iterrows()]
    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle="-", color="grey", lw=0.5))
except ImportError:
    for j, (_, r) in enumerate(lab.iterrows()):
        dy = 8 if j % 2 == 0 else -10
        ax.annotate(r["gene_name"], (r["log2FoldChange"], r["nlp"]), xytext=(4, dy),
                    textcoords="offset points", fontsize=7)
ax.set_xlabel("log2 fold change (Tumor vs Normal)")
ax.set_ylabel("-log10 adjusted p-value")
ax.set_title(f"Volcano plot (padj < {PADJ_CUT}, |log2FC| >= {LFC_CUT:g})")
ax.legend(frameon=False, loc="upper center", fontsize=8)
fig.tight_layout()
fig.savefig(RES / "fig_volcano.png", dpi=200)
plt.close(fig)

# ----------------------------------------------------------------- 6. heatmap
deg = res[res["regulation"] != "Not significant"].nsmallest(50, "padj")
if len(deg) >= 2:
    order = sorted(SAMPLES, key=lambda s: (SAMPLES[s][1] != "Tumor", SAMPLES[s][0]))
    mat = lognorm.loc[deg["gene_id"], order]
    mat = mat.sub(mat.mean(axis=1), axis=0).div(mat.std(axis=1).replace(0, np.nan), axis=0)
    mat.index = deg["gene_name"].values
    mat.columns = [label[s] for s in order]
    col_colors = pd.Series([COLORS[SAMPLES[s][1]] for s in order], index=mat.columns)
    g = sns.clustermap(mat, cmap="RdBu_r", center=0, vmin=-2.5, vmax=2.5,
                       col_colors=col_colors, col_cluster=True, row_cluster=True,
                       figsize=(7.5, 11), yticklabels=True, xticklabels=True,
                       cbar_pos=(0.03, 0.955, 0.16, 0.012),
                       cbar_kws={"orientation": "horizontal",
                                 "label": "row z-score of log2(norm+1)"},
                       dendrogram_ratio=(0.12, 0.08))
    g.ax_heatmap.tick_params(axis="y", labelsize=7)
    g.fig.suptitle("Top 50 DE genes by adjusted p-value (red bar = Tumor, blue = Normal)",
                   y=0.995, x=0.6, fontsize=10)
    g.savefig(RES / "fig_heatmap_top50.png", dpi=200)
    plt.close(g.fig)

print("Wrote annotated table, summary and figures to", RES)
