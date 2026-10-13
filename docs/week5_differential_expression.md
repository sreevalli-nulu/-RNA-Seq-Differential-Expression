# Week 5: Differential Expression with DESeq2 (Galaxy)
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal)
**Platform:** usegalaxy.org (Galaxy) | **Tool:** DESeq2, Galaxy tool version 2.11.40.8+galaxy4

---

## Goal

Test every gene for differential expression between tumor and matched normal tissue, using a paired design in which patient is included in the model.

## Why Galaxy

The pipeline ran on the command line through Week 4. The DESeq2 step moved to Galaxy because Bioconductor installation inside WSL is the most fragile part of a local setup, and Galaxy provides DESeq2 as a ready-made, versioned tool. Only the small count tables (a few MB) are uploaded; no sequencing data or BAMs leave the laptop.

## Step 1: Prepare Per-Sample Count Files

This version of the Galaxy DESeq2 tool does not accept a single count matrix; it needs one two-column file per sample, assigned to factor levels on the form. The Week 4 matrix was split into 10 files (`Geneid` + counts, with header):

```bash
mkdir -p counts/per_sample
for i in $(seq 2 11); do
  s=$(head -1 counts/gene_counts_matrix.tsv | cut -f$i)
  cut -f1,$i counts/gene_counts_matrix.tsv > counts/per_sample/$s.tsv
done
```

Each file has 78,942 lines. All 10 were uploaded to a Galaxy history (type: tabular).

## Step 2: Experimental Design

| Factor | Levels | Files |
|---|---|---|
| `condition` | `Tumor` (listed **first**), `Normal` | Tumor: SRR975554, 556, 559, 564, 567 — Normal: SRR975572, 574, 577, 582, 585 |
| `patient` | `p1` … `p5` | each patient's tumor + normal pair: p1 (554, 572), p2 (556, 574), p3 (559, 577), p4 (564, 582), p5 (567, 585) |

- `condition` is the primary factor; including `patient` models the pairing, so each tumor is effectively compared with its own patient's normal tissue. This removes between-patient variation and increases power with only five pairs.
- **The order of levels matters:** Galaxy takes the first-listed level as the numerator, so listing `Tumor` first gives log2 fold change = Tumor vs. Normal (positive = higher in tumor). Other settings: "Files have header?" = Yes; all other options default.

## Step 3: Troubleshooting Log (main failed or incorrect runs; only the final run is used)

| Attempt | What happened | Cause / fix |
|---|---|---|
| 1 | Error: `factor level [2] is duplicated` | The five `patient` levels were left with the placeholder name; named them `p1`–`p5` |
| 2 | Ran, but plot titles read "NormalX vs Tumor" | `Normal` was the first level, so fold change = Normal / Tumor (signs inverted vs. convention) |
| 3 | Ran, titles read "Tumor vs NormalX" but numbers identical to run 2 | Level *names* had been swapped without moving the *files* — labels no longer matched the samples (PCA showed tumor SRR975554 coloured as "Normal"). Caught because the fold changes were exactly unchanged and the PCA colours were wrong |
| 4 | Error: duplicated level again | Both levels had been named `Tumor` after reordering |
| 5 ✅ | Correct | `Tumor` first with the five tumor files, `Normal` second with the five normal files, patient factor intact |

**Lesson:** always validate a DE run against biology, not just against "the job went green" (next step).

## Step 4: Validation Against Known Biology

The final run was checked against genes with well-known direction in colorectal tumors (gene names from the GENCODE lookup):

| Gene | log2FC (Tumor vs Normal) | Adjusted p | Expected |
|---|---:|---:|---|
| BEST4 | −5.79 | 3.9e-28 | lost in tumor (normal colonocyte marker) ✔ |
| CA7 | −5.52 | 2.5e-26 | lost in tumor ✔ |
| COMP | +7.95 | 4.0e-23 | gained in tumor (stromal/ECM) ✔ |
| WNT2 | +7.77 | 4.7e-22 | gained in tumor ✔ |
| ETV4 | +4.78 | 1.8e-21 | gained in tumor ✔ |

Direction, magnitude and significance all match expectation, so the sign convention is correct.

## Step 5: Results

Galaxy outputs: a results table (gene, base mean, log2FC, lfcSE, Wald statistic, p-value, adjusted p-value — saved as `results/deseq2_results_tumor_vs_normal.tsv`) and a diagnostic plot PDF (`results/deseq2_plots_galaxy.pdf`: PCA, sample distances, dispersion, p-value histogram, MA plot).

| Quantity | Value |
|---|---:|
| Genes in count table | 78,941 |
| Genes tested (non-NA adjusted p; DESeq2 drops genes with no/very low counts) | 23,047 |
| Adjusted p < 0.05 | 4,661 |
| Adjusted p < 0.05 **and** \|log2FC\| ≥ 1 | **3,313** |
| — up in tumor | 1,368 |
| — down in tumor | 1,945 |

**Diagnostics:** the dispersion plot shows the expected downward trend with the fitted curve; the MA plot is symmetric; the p-value histogram has a strong spike near zero (genuine signal) plus spikes near 0.9–1 from very low-count genes, which is typical for discrete count data.

**Top genes by adjusted p-value:** BEST4 (↓), CA7 (↓), COMP (↑), WNT2 (↑), ETV4 (↑), PHLPP2 (↓), PRSS22 (↑), CD79A (↓), C2CD4A (↑), HSD3B2 (↓).

## Notes and Open Items
- Galaxy's plot labels the reference level "NormalX" (cosmetic; the results table itself has no condition labels).
- Galaxy's plot-page summary line reads "other factors in design: condition". The job parameters show the `patient` factor was submitted, and the PCA groups include patient labels, but the model formula itself was not displayed in the outputs. **Open item:** confirm `~ patient + condition` in the job's standard output (dataset *Details* → Tool Standard Output) and record it here.
- log2 fold changes are the tool's unshrunken estimates; rankings by p-value are unaffected, but effect sizes of low-count genes are slightly inflated.

## Week 5 Progress Checklist
- [x] Per-sample count files prepared and uploaded to Galaxy
- [x] Paired design set up (`condition` + `patient`), Tumor vs. Normal
- [x] DESeq2 run, troubleshot over several iterations and validated against marker genes
- [x] Results and plots exported to `results/`
- [x] Paired model confirmed by an independent PyDESeq2 refit (r = 0.999 with Galaxy)
