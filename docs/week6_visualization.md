# Week 6: Annotation, Summary Statistics & Visualization
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal)
**Platform:** WSL2, conda environment `rnaseq` (Python: pandas, numpy, scipy, matplotlib, seaborn) | **Script:** `scripts/week6_analysis.py`

---

## Goal

Add gene names to the DESeq2 results, define the differentially expressed genes (DEGs), and produce publication-quality PCA, volcano and heatmap figures.

## Step 1: Script Overview

`scripts/week6_analysis.py` reads the Galaxy results table, the Week 4 count matrix and the gene-name lookup, and writes everything to `results/`. It was first tested on synthetic data with the same file formats, then run on the real files.

```bash
cd ~/rnaseq_project && python scripts/week6_analysis.py
```

| Output | Content |
|---|---|
| `deseq2_results_annotated.tsv` | all 78,941 genes with gene names, sorted by adjusted p-value, with a regulation label |
| `deseq2_significant_genes.tsv` | the 3,313 DEGs |
| `deseq2_summary.txt` | DEG counts and top-10 lists |
| `size_factors.tsv` | DESeq2-style size factors (median of ratios) |
| `fig_pca.png`, `fig_volcano.png`, `fig_heatmap_top50.png` | figures |

**DEG definition:** adjusted p < 0.05 **and** |log2 fold change| ≥ 1 (set at the top of the script). **Direction:** Tumor vs. Normal; positive = higher in tumor.

**Normalisation for plotting:** counts were divided by median-of-ratios size factors (the DESeq2 method, computed from genes with non-zero counts in every sample) and transformed as log2(normalised count + 1). This is a simple transformation chosen for transparency; it is used for the PCA and heatmap only. The statistical testing itself was done by DESeq2 on raw counts.

## Step 2: Summary

| | Count |
|---|---:|
| Genes tested | 23,047 |
| Adjusted p < 0.05 | 4,661 |
| DEGs (padj < 0.05, \|log2FC\| ≥ 1) | 3,313 (1,368 up, 1,945 down) |

Gene names: a small number of DEGs carry no official symbol in GENCODE (e.g. `ENSG00000298053`) and are shown by Ensembl ID.

**Highest-confidence up in tumor:** COMP, WNT2, ETV4, PRSS22, C2CD4A, COL11A1, KRT80, SERPINB5. **Down in tumor:** BEST4, CA7, PHLPP2, CD79A, HSD3B2, SPIB, NAALADL1. Genes with the largest raw fold changes (e.g. KLK6, OTOP2, AQP8) include some low-count genes with marginal significance, so highlights in the report are chosen by adjusted p-value.

## Step 3: Figures

### PCA (`results/fig_pca.png`)
Top 500 most variable genes, log2-normalised counts. **PC1 explains 61% of variance and separates tumor from normal**; the five normal samples form a tight cluster regardless of patient, while tumors are widely spread (tumor heterogeneity).
- **P2 tumor (SRR975556)** sits closest to the normals — consistent with lower tumor purity (more normal tissue in the biopsy). It also sits next to the normals in the Galaxy PCA and the sample-distance heatmap.
- **P4 tumor (SRR975564)** is an outlier along PC2.
- Neither sample is excluded; both are reported as limitations. The paired design is robust to heterogeneous tumors.

### Volcano plot (`results/fig_volcano.png`)
-log10 adjusted p-value against log2 fold change; thresholds at padj 0.05 and |log2FC| = 1. Roughly symmetric, with 1,945 genes down and 1,368 up; top genes are labelled.

### Heatmap (`results/fig_heatmap_top50.png`)
The 50 most significant DEGs, row z-scores of log2-normalised counts, rows and columns hierarchically clustered. All five tumors cluster apart from all five normals, with P2 tumor the most normal-like. Three groups of genes stand out:
1. **Lost in tumor:** normal colon-lining genes (BEST4, CA7, SLC26A2, SLC26A3, CLDN23, HPGD, MALL).
2. **Lost in tumor:** immunoglobulin and B-cell genes (IGKV3-15, IGLV3-27, IGLC2, CD79A, SPIB, TNFRSF13B) — in part a tissue-composition difference, since normal mucosa contains many antibody-producing plasma cells.
3. **Gained in tumor:** extracellular-matrix and stromal genes (COMP, COL11A1, COL8A1, BGN, INHBA), plus stemness and tumor-environment genes (OLFM4, CA9, STC2, CDH3, KRT80, MUC5AC).

**Caution:** this is bulk RNA-seq, so some differences reflect which cell types are present rather than expression changes within one cell type.

## Week 6 Progress Checklist
- [x] DESeq2 results annotated with gene names and DEG labels
- [x] Summary statistics and top-gene tables generated
- [x] PCA, volcano plot and heatmap produced and reviewed
- [x] Script (`scripts/week6_analysis.py`) and outputs committed to GitHub
