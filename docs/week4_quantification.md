# Week 4: Gene-Level Read Quantification (featureCounts)
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal) | **Supervisor:** Dr. Nilofer
**Platform:** Windows + WSL2 (Ubuntu 22.04), conda environment `rnaseq` | **Tool:** featureCounts (Subread v2.1.1)

---

## Goal

Convert the 10 sorted BAM files from Week 3 into a gene-by-sample count matrix — the input for differential expression testing.

## Step 1: Determine Library Strandedness Empirically

featureCounts needs to know whether the library is unstranded (`-s 0`), forward-stranded (`-s 1`) or reverse-stranded (`-s 2`). Rather than assume, all three settings were run on one sample (SRR975554) with the same annotation used to build the STAR index, and the assignment rates compared:

```bash
mkdir -p counts/strand_test
for s in 0 1 2; do
  featureCounts -p --countReadPairs -s $s -T 4 \
    -a genome/gencode.v50.primary_assembly.basic.annotation.gtf \
    -o counts/strand_test/SRR975554_s$s.txt \
    alignments/SRR975554_Aligned.sortedByCoord.out.bam
done
grep -H -E "^Assigned|Unassigned_NoFeatures|Unassigned_Ambiguity" counts/strand_test/*.summary
```

| Setting | Assigned alignments | % of 32,978,764 | Unassigned_NoFeatures | Unassigned_Ambiguity |
|---|---:|---:|---:|---:|
| `-s 0` (unstranded) | **23,234,600** | **70.5%** | 1,271,273 | 2,329,049 |
| `-s 1` (forward) | 13,465,803 | 40.8% | 12,783,819 | 585,300 |
| `-s 2` (reverse) | 13,326,672 | 40.4% | 12,928,081 | 580,169 |

**Interpretation:** `-s 1` and `-s 2` give almost identical, much lower assignment (~41%) and push ~12.8M reads into "NoFeatures" (reads on the wrong strand match no gene). In a stranded library, one of the two would match `-s 0`. This pattern means the library is **unstranded**, consistent with the standard poly-A TruSeq protocol → **`-s 0` used for all samples**.

## Step 2: Count All 10 Samples in One Run

```bash
nohup featureCounts -p --countReadPairs -s 0 -T 4 \
  -a genome/gencode.v50.primary_assembly.basic.annotation.gtf \
  -o counts/gene_counts_raw.txt \
  alignments/*_Aligned.sortedByCoord.out.bam \
  > counts/featurecounts_log.txt 2>&1 & disown
```

| Parameter | Value | Why |
|---|---|---|
| `-p --countReadPairs` | on | Paired-end data: count fragments (read pairs), not individual reads (required syntax from Subread v2.x) |
| `-s 0` | unstranded | Determined empirically in Step 1 |
| `-a` | GENCODE v50 Basic GTF | **Same annotation the STAR index was built with**, so coordinates and gene definitions match |
| feature / attribute | `exon` / `gene_id` (defaults) | Reads are summed over all exons of a gene |
| Multi-mapping reads | not counted (default) | Conservative; avoids double counting paralogs |
| Multi-overlapping reads | not counted (default) | Reads overlapping two genes are reported as ambiguous |

Annotation loaded by featureCounts: 3,124,772 exon features grouped into **78,941 genes** across 70 chromosomes/contigs. The full run finished in under 90 minutes (a single sample takes about 4 minutes when run alone).

## Step 3: Per-Sample Assignment Rates

`counts/gene_counts_raw.txt.summary`, summarised (denominator = all alignment records, including multi-mapped alignments, which are not counted):

| Sample | Condition | Assigned | Total alignments | % assigned |
|---|---|---:|---:|---:|
| SRR975554 | Tumor (P1) | 23,234,600 | 32,978,764 | 70.5% |
| SRR975556 | Tumor (P2) | 20,426,723 | 32,399,058 | 63.0% |
| SRR975559 | Tumor (P3) | 19,227,518 | 28,606,588 | 67.2% |
| SRR975564 | Tumor (P4) | 21,831,879 | 29,154,579 | 74.9% |
| SRR975567 | Tumor (P5) | 20,324,255 | 28,917,369 | 70.3% |
| SRR975572 | Normal (P1) | 20,590,351 | 30,970,385 | 66.5% |
| SRR975574 | Normal (P2) | 21,331,320 | 31,980,465 | 66.7% |
| SRR975577 | Normal (P3) | 21,574,201 | 32,336,544 | 66.7% |
| SRR975582 | Normal (P4) | 21,154,037 | 30,291,149 | 69.8% |
| SRR975585 | Normal (P5) | 21,959,252 | 33,613,294 | 65.3% |
| **Mean** | | | | **68.1%** (tumor 69.2%, normal 67.0%) |

**Interpretation:** every sample has 19–23 million counted fragments, ample for DESeq2. The assignment rate (63–75%) is lower than the 75–85% often quoted because the denominator includes multi-mapped alignment records (about 6% of reads, possibly several records each) and because reads falling in introns or intergenic regions are unassigned. Tumor and normal rates are similar, so the difference does not bias the comparison.

## Step 4: Build the Count Matrix and a Gene-Name Lookup

```bash
# clean matrix: gene IDs + 10 sample columns, with plain SRR column names
grep -v '^#' counts/gene_counts_raw.txt | cut -f1,7- \
  | sed '1{s#alignments/##g;s#_Aligned.sortedByCoord.out.bam##g}' > counts/gene_counts_matrix.tsv

# gene_id -> gene_name lookup taken from the GTF (gene records only)
awk -F'\t' '$3=="gene"{match($9,/gene_id "[^"]+"/);id=substr($9,RSTART+9,RLENGTH-10);
  match($9,/gene_name "[^"]+"/);nm=substr($9,RSTART+11,RLENGTH-12);print id"\t"nm}' \
  genome/gencode.v50.primary_assembly.basic.annotation.gtf > counts/gene_id_to_name.tsv
```

**Checks:** the matrix has 78,942 lines (78,941 genes + header) and 11 columns; the lookup has 78,941 lines and its IDs match the matrix exactly (e.g. `ENSG00000142959.8` → `BEST4`). GENCODE gene IDs carry version suffixes (`.8`); they are kept consistently throughout, and names are used only for display and enrichment.

## Deliverables
- `counts/gene_counts_matrix.tsv` — 78,941 genes × 10 samples (raw counts)
- `counts/gene_id_to_name.tsv` — gene ID → symbol lookup
- `counts/gene_counts_raw.txt.summary` — featureCounts assignment summary

## Week 4 Progress Checklist
- [x] Strandedness determined empirically (unstranded → `-s 0`)
- [x] featureCounts run on all 10 BAMs with the same GTF used for the index
- [x] Count matrix and gene-name lookup built and sanity-checked
- [x] Per-sample assignment rates tabulated (mean 68.1%)
