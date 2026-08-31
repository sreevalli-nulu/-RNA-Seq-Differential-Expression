# RNA-Seq DE Analysis — Project Log

## Tool Versions Log

| Tool | Version | Installed/Verified | Purpose |
|---|---|---|---|
| Miniforge/Mamba | Miniforge3 (conda/mamba) | Week 1 | Environment manager |
| sra-tools | 3.4.1 | Week 1 ✅ | SRA download (prefetch, fasterq-dump) |
| FastQC | v0.12.1 | Week 1 ✅ | Raw/trimmed read QC |
| MultiQC | 1.35 | Week 1 ✅ | Aggregate QC reporting |
| STAR | 2.7.10b | Week 1 ✅ (install verified; first alignment run in Week 3) | Read alignment |
| SAMtools | 1.24 | Week 1 ✅ | BAM/SAM manipulation |
| Subread (featureCounts) | v2.1.1 | Week 1 ✅ (install verified; first run in Week 4) | Read quantification |
| Trimmomatic / fastp | *(pending — Week 2 decision)* | Week 2 (pending) | Adapter/quality trimming |
| DESeq2 (R/Bioconductor) | *(pending — Week 6)* | Week 6 (pending) | Differential expression testing |
| clusterProfiler (R/Bioconductor) | *(pending — Week 7)* | Week 7 (pending) | Pathway enrichment |


## Dataset

**GSE50760** — Gene Expression Omnibus
- **Source publication:** Kim, S.K. et al. (2014), *PLoS ONE* — original RNA-seq colorectal cancer study using this cohort (PMID: 25049118).
- **Design used in this project:** 10 samples (5 patients × tumor + matched normal), subset from the full 54-sample study (18 patients × normal/tumor/liver metastasis).
- **Rationale for selection:** paired tumor/normal design from the same patients; widely used as a teaching dataset (see literature log below); manageable download size for a WSL-based laptop workflow on a 1 hr/day budget.
- **Patient pairing method:** GSE50760 submits samples in blocks by tissue type (tumor block, then normal block, then metastasis block), with patients in matching order across blocks — this is the standard GEO convention for this series and is how the dataset is used in published literature. Row N in the tumor block corresponds to row N in the normal block.
- **Final 10 samples selected** (chosen for balanced tumor/normal file sizes within each patient pair, keeping total download predictable at ~42Gb):

| Patient | Condition | SRR Accession | GSM Accession | File Size |
|---|---|---|---|---|
| P1 | Tumor | SRR975554 | GSM1228187 | 4.59 Gb |
| P1 | Normal | SRR975572 | GSM1228205 | 4.22 Gb |
| P2 | Tumor | SRR975556 | GSM1228189 | 4.10 Gb |
| P2 | Normal | SRR975574 | GSM1228207 | 4.26 Gb |
| P3 | Tumor | SRR975559 | GSM1228192 | 3.84 Gb |
| P3 | Normal | SRR975577 | GSM1228210 | 4.40 Gb |
| P4 | Tumor | SRR975564 | GSM1228197 | 4.27 Gb |
| P4 | Normal | SRR975582 | GSM1228215 | 4.23 Gb |
| P5 | Tumor | SRR975567 | GSM1228200 | 4.04 Gb |
| P5 | Normal | SRR975585 | GSM1228218 | 4.45 Gb |

---

## Literature & Reference Log

| # | Source | Type | Relevance | Link |
|---|---|---|---|---|
| 1 | Kim, S.K. et al., *PLoS ONE* (2014) | Primary publication | Original study generating the GSE50760 dataset | PMID: 25049118 |
| 2 | Griffith Lab — GenViz Course, "Differential expression with DESeq2" | Tutorial/course | Worked example using this exact dataset (via EBI Expression Atlas ID E-GEOD-50760); useful for sanity-checking your DESeq2 results | https://genviz.org/module-04-expression/0004/02/01/DifferentialExpression/ |
| 3 | Love, M.I., Huber, W., Anders, S. (2014), *Genome Biology* | Primary publication | Original DESeq2 paper — cite this in your final writeup when you use DESeq2 | Bioconductor DESeq2 vignette: https://bioconductor.org/packages/devel/bioc/vignettes/DESeq2/inst/doc/DESeq2.html |
| 4 | NCBI SRA Run Selector, GSE50760 | Data source tool | Used to browse runs, compare file sizes, and select the final 10-sample subset | https://www.ncbi.nlm.nih.gov/Traces/study/?acc=GSE50760 |



## Weekly Entries

### Week 1 — Environment Setup & Dataset Selection
**Date:** *(fill in)*
**Actions:**
- Installed WSL2 + Ubuntu 22.04 LTS.
- Installed Miniforge (conda/mamba).
- Created and activated conda environment `rnaseq` with sra-tools, FastQC, STAR, SAMtools, Subread, and MultiQC — all versions verified (see Tool Versions table above).
- Set up standardized project folder structure at `~/rnaseq_project/` (`raw_data/`, `fastqc_raw/`, `trimmed/`, `fastqc_trimmed/`, `genome/`, `alignments/`, `counts/`, `results/`, `scripts/`) — verified with `ls -R`.
- Evaluated dataset options; selected GSE50760 over the originally planned GSE183947 for its paired tumor/normal design and strong tutorial support.
- Selected a 10-sample subset (5 patients, tumor + normal) for a "medium" scope balancing statistical power against download/compute time.
- Finalized the 10 SRR accessions via SRA Run Selector, matched by patient position and balanced file size (see Dataset section above) — downloaded Accession List.
- Set up standardized project folder structure (`raw_data/`, `fastqc_raw/`, `trimmed/`, `genome/`, `alignments/`, `counts/`, `results/`, `scripts/`).

**Deliverables produced:**
- `sample_metadata.csv`
- Initial FastQC/MultiQC report 


**Download progress note (added mid-Week 1)
- SRR975554 (P1 tumor): ✅ fully downloaded and compressed (541M + 538M gzipped FASTQ files)
- SRR975572 (P1 normal): 🔄 partial — interrupted by NCBI SRA server timeouts on two separate attempts (once after ~12hrs, once after ~3hrs); `.sra.tmp` partial file retained for resume
- Remaining 8 samples (SRR975556, SRR975574, SRR975559, SRR975577, SRR975564, SRR975582, SRR975567, SRR975585): ⬜ not yet started
- **Cause identified:** NCBI SRA server-side timeouts, not a local network or WSL issue — this is a known intermittent issue with SRA downloads and not something fixable client-side beyond retrying
- **tmux troubleshooting note:** first attempt to run the download inside `tmux` failed silently (`[exited]` immediately after `tmux new`); tmux itself was later confirmed working in isolation (v3.4, `$SHELL=/bin/bash`), so the cause of the in-context failure is still unresolved — to be retried and verified *before* relying on it for the next download attempt

