# RNA-Seq Differential Expression Analysis: Colorectal Cancer (Tumor vs. Normal)

**Status:** ✅ Weeks 1–2 Complete — 🔄 Starting Week 3 of 8 (Alignment)


## Overview

This project identifies differentially expressed genes (DEGs) between primary colorectal tumor tissue and matched adjacent normal tissue, using a subset of a published RNA-seq dataset. The pipeline covers the full workflow from raw sequencing reads through statistical differential expression analysis and biological interpretation.

## Dataset

- **Source:** [GSE50760](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE50760) (Gene Expression Omnibus)
- **Original publication:** Kim, S.K. et al. (2014), *PLoS ONE*. PMID: [25049118](https://pubmed.ncbi.nlm.nih.gov/25049118/)
- **Subset used:** 10 paired-end samples — 5 patients × (1 primary tumor + 1 matched normal colon sample each)
- **Design rationale:** paired tumor/normal samples from the same patients increase statistical power for DE testing; full dataset (54 samples, 18 patients) was subset for computational feasibility

| Patient | Tumor SRR | Normal SRR |
|---|---|---|
| P1 | SRR975554 | SRR975572 |
| P2 | SRR975556 | SRR975574 |
| P3 | SRR975559 | SRR975577 |
| P4 | SRR975564 | SRR975582 |
| P5 | SRR975567 | SRR975585 |

Full sample metadata: [`metadata/sample_metadata.csv`](metadata/sample_metadata.csv)

## Pipeline

```
Raw FASTQ (SRA download)          ✅ Complete — all 20 files downloaded & verified
    ↓ FastQC / MultiQC            ✅ Complete — see results/week1_multiqc_report.html
    ↓ fastp                       ✅ Complete — see results/week2_multiqc_trimmed_report.html
    ↓ FastQC / MultiQC            ✅ Complete — 82.5% overall read retention, Q20 rate 97.5%
    ↓ STAR                        🔄 Up next (Week 3) — alignment to reference genome
    ↓ featureCounts               — gene-level read quantification
    ↓ DESeq2                      — differential expression testing
    ↓ clusterProfiler             — pathway enrichment
```

## Tools & Versions

| Tool | Version | Purpose |
|---|---|---|
| sra-tools | 3.4.1 | SRA download (prefetch, fasterq-dump) |
| FastQC | v0.12.1 | Read quality control |
| MultiQC | 1.35 | Aggregate QC reporting |
| STAR | 2.7.10b | Read alignment |
| SAMtools | 1.24 | BAM/SAM manipulation |
| Subread (featureCounts) | v2.1.1 | Read quantification |
| fastp | 1.3.6 | Adapter/quality trimming |
| DESeq2 | *(pending — Week 6)* | Differential expression |
| clusterProfiler | *(pending — Week 7)* | Pathway enrichment |

Full environment setup and version log: [`docs/week1_setup_and_data_retrieval.md`](docs/week1_setup_and_data_retrieval.md)

## Results So Far

- **Raw QC report (all 10 samples, 20 FASTQ files):** [`results/week1_multiqc_report.html`](results/week1_multiqc_report.html)
  - ~29–35M reads per file, 101bp read length, 51–53% GC content, strong per-base quality with typical 3′ tapering, low adapter content
- **Trimmed QC report (post-fastp):** [`results/week2_multiqc_trimmed_report.html`](results/week2_multiqc_trimmed_report.html)
  - 82.5% overall read retention (642.1M → 530.0M reads) after quality trimming (`--cut_right`, Q15, min length 25bp)
  - Weighted average Q20 rate after trimming: 97.5%; ~48.8 billion bp retained across all samples
  - Parameters tuned after investigating an initial high "too-short" failure rate; see [`docs/project_log.md`](docs/project_log.md) for the full investigation

## Repository Structure

```
├── metadata/
│   └── sample_metadata.csv       # sample-to-condition mapping
├── scripts/                      # analysis scripts (added as pipeline progresses)
├── docs/
│   ├── week1_setup_and_data_retrieval.md
│   └── project_log.md            # full running log: decisions, tool versions, literature
├── results/
│   └── week1_multiqc_report.html # raw-read QC report (Week 1 deliverable)
└── README.md
```

Note: raw and intermediate data files (FASTQ, BAM, genome files) are excluded from this repository via `.gitignore` due to size — see the Dataset section above to re-download the exact samples used.

## Reproducing This Analysis

1. Set up environment: see [`docs/week1_setup_and_data_retrieval.md`](docs/week1_setup_and_data_retrieval.md) for the full conda environment spec and tool versions.
2. Download samples: SRR accessions listed above, retrievable via `prefetch` / `fasterq-dump` from NCBI SRA.
3. Run pipeline steps in order (see Pipeline section above) — individual scripts will be added to `scripts/` as each week is completed.

## Progress Log

See [`docs/project_log.md`](docs/project_log.md) for a detailed, dated log of every step, tool version, and literature reference used throughout the project.

## References

1. Kim, S.K. et al. (2014). Comprehensive molecular characterization of clinical colorectal cancers by RNA-seq. *PLoS ONE*. PMID: 25049118.
2. Love, M.I., Huber, W., Anders, S. (2014). Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology*.
3. Griffith Lab GenViz Course — Differential Expression tutorial (used as a reference/sanity-check resource): https://genviz.org/module-04-expression/
4. Andrews, S. (2010). FastQC: A Quality Control Tool for High Throughput Sequence Data.
5. Ewels, P. et al. (2016). MultiQC: summarize analysis results for multiple tools and samples in a single report. *Bioinformatics*. DOI: 10.1093/bioinformatics/btw354
