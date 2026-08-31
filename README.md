# RNA-Seq Differential Expression Analysis: Colorectal Cancer (Tumor vs. Normal)

**Status:** 🔄 In Progress — Week 1 of 8 (Data Retrieval & Initial QC)
**Author:** Kumar | **Supervisor:** Dr. Nilofer

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
Raw FASTQ (SRA download)
    ↓ FastQC / MultiQC          — initial QC
    ↓ Trimmomatic or fastp      — adapter/quality trimming
    ↓ FastQC / MultiQC          — post-trim QC
    ↓ STAR                      — alignment to reference genome
    ↓ featureCounts             — gene-level read quantification
    ↓ DESeq2                    — differential expression testing
    ↓ clusterProfiler           — pathway enrichment
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
| DESeq2 | *(pending — Week 6)* | Differential expression |
| clusterProfiler | *(pending — Week 7)* | Pathway enrichment |

Full environment setup and version log: [`docs/week1_setup_and_data_retrieval.md`](docs/week1_setup_and_data_retrieval.md)

## Repository Structure

```
├── metadata/
│   └── sample_metadata.csv       # sample-to-condition mapping
├── scripts/                      # analysis scripts (added as pipeline progresses)
├── docs/
│   ├── week1_setup_and_data_retrieval.md
│   └── project_log.md            # full running log: decisions, tool versions, literature
├── results/                      # QC reports, count matrices, DE results, figures (added as pipeline progresses)
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
