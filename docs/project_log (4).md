# RNA-Seq DE Analysis — Project Log

## Tool Versions Log

| Tool | Version | Installed/Verified | Purpose |
|---|---|---|---|
| Miniforge/Mamba | Miniforge3 (conda/mamba) | Week 1 | Environment manager |
| sra-tools | 3.4.1 | Week 1 ✅ | SRA download (prefetch, fasterq-dump) |
| FastQC | v0.12.1 | Week 1 ✅ | Raw/trimmed read QC |
| MultiQC | 1.35 | Week 1 ✅ | Aggregate QC reporting |
| STAR | 2.7.10b | Week 1 ✅; used in Week 3 ✅ | Genome index + alignment of 10 samples |
| SAMtools | 1.24 | Week 1 ✅ | BAM/SAM manipulation |
| Subread (featureCounts) | v2.1.1 | Week 1 ✅; used in Week 4 ✅ | Gene-level read quantification |
| fastp | 1.3.6 | Week 2 ✅ | Adapter/quality trimming (chosen over Trimmomatic) |
| GENCODE (reference) | Release 50, GRCh38.p14 primary assembly + Basic annotation | Week 3 ✅ | Genome FASTA and gene annotation (index and featureCounts use the same GTF) |
| DESeq2 (Galaxy tool, usegalaxy.org) | 2.11.40.8+galaxy4 | Week 5 ✅ | Differential expression testing (paired design) |
| Python analysis stack (pandas, numpy, scipy, matplotlib, seaborn, adjustText) | *(record with `mamba list` / `pip list`)* | Week 6 ✅ | Annotation, summary statistics, figures |
| Enrichr via gseapy | *(record with `pip show gseapy`)* | Week 7 ✅ | Over-representation analysis (replaced the originally planned clusterProfiler; see Week 7 entry) |


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
| 5 | Andrews, S. (2010). FastQC: A Quality Control Tool for High Throughput Sequence Data | Tool documentation | QC reference for interpreting raw-read FastQC/MultiQC output | https://www.bioinformatics.babraham.ac.uk/projects/fastqc/ |
| 6 | Ewels, P. et al. (2016). MultiQC: summarize analysis results for multiple tools and samples in a single report. *Bioinformatics* | Tool publication | Cite when describing the aggregate QC step in the final write-up | DOI: 10.1093/bioinformatics/btw354 |
| 7 | Chen, S., Zhou, Y., Chen, Y., Gu, J. (2018). fastp: an ultra-fast all-in-one FASTQ preprocessor. *Bioinformatics* 34(17):i884–i890 | Tool publication | Cite for adapter/quality trimming (Week 2) | DOI: 10.1093/bioinformatics/bty560 |
| 8 | Dobin, A. et al. (2013). STAR: ultrafast universal RNA-seq aligner. *Bioinformatics* 29(1):15–21 | Tool publication | Cite for alignment (Week 3) | DOI: 10.1093/bioinformatics/bts635 |
| 9 | Frankish, A. et al. (2021). GENCODE 2021. *Nucleic Acids Research* 49(D1):D916–D923 | Resource publication | Cite for the reference annotation (release 50 used; cite the GENCODE release page for the exact version) | DOI: 10.1093/nar/gkaa1087 |
| 10 | Danecek, P. et al. (2021). Twelve years of SAMtools and BCFtools. *GigaScience* 10(2):giab008 | Tool publication | Cite for BAM validation (Week 3) | DOI: 10.1093/gigascience/giab008 |
| 11 | Liao, Y., Smyth, G.K., Shi, W. (2014). featureCounts: an efficient general purpose program for assigning sequence reads to genomic features. *Bioinformatics* 30(7):923–930 | Tool publication | Cite for read quantification (Week 4) | DOI: 10.1093/bioinformatics/btt656 |
| 12 | The Galaxy Community (2024). The Galaxy platform for accessible, reproducible, and collaborative data analyses: 2024 update. *Nucleic Acids Research* 52(W1):W83–W94 | Platform publication | Cite for the Galaxy-hosted DESeq2 step (Week 5) | DOI: 10.1093/nar/gkae410 |
| 13 | Chen, E.Y. et al. (2013). Enrichr: interactive and collaborative HTML5 gene list enrichment analysis tool. *BMC Bioinformatics* 14:128; Kuleshov, M.V. et al. (2016). *Nucleic Acids Research* 44(W1):W90–W97; Xie, Z. et al. (2021). *Current Protocols* 1(3):e90 | Tool publications | Cite for over-representation analysis (Week 7) | DOI: 10.1186/1471-2105-14-128 |
| 14 | Fang, Z., Liu, X., Peltz, G. (2023). GSEApy: a comprehensive package for performing gene set enrichment analysis in Python. *Bioinformatics* 39(1):btac757 | Tool publication | Cite for the Python interface to Enrichr (Week 7) | DOI: 10.1093/bioinformatics/btac757 |
| 15 | Liberzon, A. et al. (2015). The Molecular Signatures Database Hallmark gene set collection. *Cell Systems* 1(6):417–425 | Resource publication | Cite for the Hallmark gene sets used in Week 7 | DOI: 10.1016/j.cels.2015.12.004 |

*Citation details above were written from memory of the original papers; verify each against the publisher record before submitting the final report.*



## Weekly Entries

### Week 1 — Environment Setup, Dataset Selection & Raw QC ✅ COMPLETE
**Date range:** ~Sep 1 – Sep 6, 2026

**Actions:**
- Installed WSL2 + Ubuntu 22.04 LTS.
- Installed Miniforge (conda/mamba).
- Created and activated conda environment `rnaseq` with sra-tools, FastQC, STAR, SAMtools, Subread, and MultiQC — all versions verified (see Tool Versions table above).
- Set up standardized project folder structure at `~/rnaseq_project/` (`raw_data/`, `fastqc_raw/`, `trimmed/`, `fastqc_trimmed/`, `genome/`, `alignments/`, `counts/`, `results/`, `scripts/`) — verified with `ls -R`.
- Evaluated dataset options; selected GSE50760 over the originally planned GSE183947 for its paired tumor/normal design and strong tutorial support.
- Selected a 10-sample subset (5 patients, tumor + normal) for a "medium" scope balancing statistical power against download/compute time.
- Finalized the 10 SRR accessions via SRA Run Selector, matched by patient position and balanced file size (see Dataset section above).
- **All 20 FASTQ files (10 samples × paired-end) downloaded and gzip-integrity-verified** (`gzip -t` passed on all) — download completed via a mix of direct SRA `prefetch`/`fasterq-dump` and Google Drive transfer for samples affected by NCBI server-side timeouts.
- **FastQC v0.12.1 run on all 10 samples (20 files)**; aggregated with **MultiQC v1.35** into a single combined report.

**Deliverables produced:**
- `metadata/sample_metadata.csv`
- `fastqc_raw/` — individual FastQC reports for all 20 FASTQ files
- `fastqc_raw/multiqc_report.html` and `results/week1_multiqc_report.html` — combined QC report, pushed to GitHub

**Raw QC headline results (from MultiQC report, generated 2026-09-06):**
- Read depth: ~29–35 million reads per file across all 10 samples; read length uniform at 101 bp
- GC content: 51–53% across samples, consistent with expected human transcriptome GC range
- Per-base quality: strong (Phred >30) through most of the read, tapering toward the 3′ end — typical Illumina quality decay pattern
- Adapter content: low overall (<1% of sequences per FastQC's own flagging), though MultiQC's status-check grid flags several samples "abnormal" on a few individual metrics — **not yet interpreted in detail; full review scheduled before finalizing trimming parameters in Week 2**
- A few isolated N-content spikes at specific read positions in a subset of samples — noted for follow-up, not yet root-caused

**Infrastructure notes (environment troubleshooting during Week 1):**
- WSL became unstable due to the Windows C: drive running critically low on free space (down to ~1.4GB); root cause confirmed via Windows Event Viewer (Volsnap Event ID 36), not a RAM or software issue.
- Fixed by migrating the entire WSL Ubuntu-22.04 installation from C: to D: (`wsl --export` / `--unregister` / `--import`) and raising `.wslconfig` memory allocation to 14GB as an added safety margin.
- A subsequent WSL disk corruption event (`WSL_E_DISK_CORRUPTED`) required a full Ubuntu reinstall directly onto D:. Recovery was low-friction because all documentation had already been pushed to GitHub. Local Linux username changed from `sreevalli` to `valli` as part of this rebuild.
- The local git repository connection did not survive the reinstall (no `.git` folder remained locally), even though the remote GitHub repo was intact. Reconnected via `git init` + `git remote add origin` + `git fetch`/`git pull`, preserving all existing GitHub history without re-uploading raw data.
- Repository visibility changed from private to public.
- Git commit email configured to GitHub's private noreply address (repo-local `git config user.email`, not global) to keep the personal email off public commits.

**Week 1 status: ✅ COMPLETE.** Proceeding to Week 2 (quality trimming) next; detailed MultiQC interpretation to inform trimming parameter choices is queued as the first task of Week 2.

### Week 2 — Quality Trimming ✅ COMPLETE
**Date range:** ~Sep 6, 2026

**Tool decision:** chose **fastp** over Trimmomatic — single-command syntax, auto-adapter-detection, built-in HTML/JSON QC report per sample. Installed via `mamba install -c bioconda -c conda-forge fastp` (not `apt`, to keep the tool inside the versioned `rnaseq` conda environment). **fastp v1.3.6** verified.

**Pipeline decision (scope):** adopting a **hybrid pipeline** going forward — command-line (WSL/conda) through Week 4 (trimming, alignment, counting), switching to **Galaxy** (or R/RStudio) for Week 5–7 (DESeq2, clusterProfiler), since Bioconductor R package installation is the most fragile part of a local WSL setup and Galaxy provides these as ready-made tools. Command-line tools already installed (STAR, SAMtools, featureCounts) carry no switching cost, so there's no reason to move those steps off the command line.

**Raw QC interpretation (informing trimming parameters):**
- Reviewed Week 1 MultiQC report: adapter content was low (<1%) across all samples — adapter trimming was a low priority
- Main issue identified: steep 3′ per-base quality decay (typical Illumina pattern), dropping from Phred >30 to ~20–25 by read end
- Conclusion: prioritize quality-based trimming (`--cut_right`) over adapter trimming

**Parameter tuning (tested on SRR975554 before batch run):**
- **First attempt:** `--cut_right_mean_quality 20`, `--length_required 36` → only 72.8% of reads retained (50.4M / 69.2M), with 18.6M reads (27%) failing as "too short" after trimming
- **Investigated insert size** to rule out short-fragment library prep as the cause: fastp's own reported "insert size peak" of 46bp was misleading — it only reflects the subset of read pairs short enough for R1/R2 to overlap (~1.6M of 34.6M pairs); that subset's true distribution peaked at 140–159bp (34.7%), consistent with a normal RNA-seq fragment size. Confirmed insert size was **not** the cause of read loss.
- **Root cause:** aggressive Q20 tail-quality trimming was cutting deep enough into naturally-decaying reads to push many below the 36bp minimum length cutoff
- **Revised parameters:** `--cut_right_mean_quality 15` (Q15 ≈ 97% base-call accuracy — sufficient for RNA-seq read counting, vs. Q20's variant-calling-grade 99%), `--length_required 25` → retention improved to 83.8% (57.95M / 69.2M reads), "too short" failures dropped from 18.6M to 11.1M (−41%). Insert size peak recalculated to 149bp on the re-run, consistent with the true fragment size distribution found during investigation.

**Final fastp command used for all 10 samples:**
```
fastp -i raw_data/{sample}_1.fastq.gz -I raw_data/{sample}_2.fastq.gz \
  -o trimmed/{sample}_1.trimmed.fastq.gz -O trimmed/{sample}_2.trimmed.fastq.gz \
  --cut_right --cut_right_window_size 4 --cut_right_mean_quality 15 \
  --length_required 25 --thread 4 \
  --html trimmed/{sample}_fastp.html --json trimmed/{sample}_fastp.json
```

**Batch trimming results (all 10 samples):**

| Sample | Reads before | Reads after | % Retained |
|---|---|---|---|
| SRR975554 | 69,123,366 | 57,953,032 | 83.8% |
| SRR975556 | 61,802,386 | 52,102,678 | 84.3% |
| SRR975559 | 58,153,246 | 47,649,856 | 81.9% |
| SRR975564 | 65,054,980 | 53,096,586 | 81.6% |
| SRR975567 | 61,652,534 | 50,501,266 | 81.9% |
| SRR975572 | 63,282,332 | 52,189,876 | 82.5% |
| SRR975574 | 64,283,782 | 53,849,074 | 83.8% |
| SRR975577 | 66,679,458 | 54,521,890 | 81.8% |
| SRR975582 | 64,334,584 | 52,947,520 | 82.3% |
| SRR975585 | 67,739,046 | 55,139,100 | 81.4% |
| **TOTAL** | **642,105,714** | **529,950,878** | **82.5%** |

- Weighted average Q20 rate after trimming: **97.53%**
- Total bases retained after trimming: **48.83 billion bp**
- Consistent 81–84% retention across all samples indicates the tuned parameters generalized well, rather than being fit to a single sample

**Post-trim QC:** ran FastQC v0.12.1 on all 20 trimmed FASTQ files, aggregated with MultiQC v1.35 into `fastqc_trimmed/multiqc_trimmed_report.html`, copied to `results/week2_multiqc_trimmed_report.html` for GitHub.

**Deliverables produced:**
- `trimmed/` — 20 trimmed FASTQ files + per-sample fastp HTML/JSON reports
- `fastqc_trimmed/` — 20 post-trim FastQC reports + combined MultiQC report
- `results/week2_multiqc_trimmed_report.html` — pushed to GitHub

**Week 2 status: ✅ COMPLETE.** Proceeding to Week 3 (STAR alignment + SAMtools BAM processing) next.

### Week 3 — Reference Genome, STAR Index & Alignment ✅ COMPLETE
**Date range:** Sep – Oct 2026 (multi-week gap while indexing and alignment ran). Full detail: `docs/week3_alignment.md`

**Decisions:**
- Reference: **GRCh38 primary assembly + GENCODE release 50**. The Comprehensive annotation caused a STAR out-of-memory kill at junction insertion, so the **Basic** annotation was used with `--genomeSAsparseD 3 --limitGenomeGenerateRAM 14000000000 --sjdbOverhang 90`. WSL memory raised to 18GB.
- Long jobs run with `nohup ... & disown` after a foreground indexing attempt died silently when the terminal closed.

**Results:**
- STAR 2.7.10b index built (~13.5GB). All 10 samples aligned (`--outSAMtype BAM SortedByCoordinate`, ~1.7–2 hours per sample); all 10 BAMs pass `samtools quickcheck`.
- Mapping: uniquely mapped 89.5–92.6% (mean 90.9%), multi-mapped 4.9–7.8% (mean 6.4%), total mapped mean 97.3%; no outlier samples.
- Interruptions (Windows restart, laptop sleep, one batch stopping after 9 samples) were handled by re-running only affected samples; none affected the results.

### Week 4 — Quantification with featureCounts ✅ COMPLETE
**Date:** Oct 13, 2026. Full detail: `docs/week4_quantification.md`

- **Strandedness determined empirically** on SRR975554: `-s 0` assigned 70.5% of alignments vs ~41% for `-s 1` and `-s 2` (almost identical) → library is **unstranded**; `-s 0` used.
- featureCounts v2.1.1, `-p --countReadPairs -s 0`, same GENCODE v50 Basic GTF as the index; multi-mapping and multi-overlapping reads not counted (defaults). 78,941 genes quantified.
- Per-sample assignment 63.0–74.9% (mean 68.1%), 19–23M counted fragments per sample.
- Deliverables: `counts/gene_counts_matrix.tsv`, `counts/gene_id_to_name.tsv`, featureCounts summary.

### Week 5 — Differential Expression (DESeq2 on Galaxy) ✅ COMPLETE
**Date:** Oct 13, 2026. Full detail: `docs/week5_differential_expression.md`

- DESeq2 (Galaxy 2.11.40.8+galaxy4) with `condition` (Tumor first, so log2FC = Tumor vs. Normal) and `patient` as a second factor to model the pairing. Input: 10 per-sample count files (this tool version does not take a single matrix).
- Several runs were needed: unnamed factor levels (duplicate-level error), inverted comparison direction, labels swapped relative to files, and duplicated level names. Each was diagnosed from the output rather than accepted because the job turned green.
- **Validation:** BEST4 (−5.79) and CA7 (−5.52) down; COMP (+7.95), WNT2 (+7.77), ETV4 (+4.78) up — matches known colorectal cancer biology.
- **Results:** 23,047 genes tested; 4,661 with padj < 0.05; **3,313 DEGs** (padj < 0.05, |log2FC| ≥ 1): 1,368 up and 1,945 down in tumor.
- Open item: confirm the model formula (`~ patient + condition`) in the Galaxy job output.

### Week 6 — Annotation & Visualization ✅ COMPLETE
**Date:** Oct 13, 2026. Full detail: `docs/week6_visualization.md`

- `scripts/week6_analysis.py` annotates results with gene names and produces the summary tables, PCA, volcano plot and top-50 heatmap (size factors by median of ratios; log2(norm+1) for plotting).
- PCA: PC1 (61%) separates tumor from normal; normals cluster tightly, tumors are heterogeneous. **P2 tumor (SRR975556)** is the most normal-like tumor (probable lower tumor purity) and **P4 tumor (SRR975564)** is a PC2 outlier; both kept and reported as limitations.
- Heatmap: loss of normal colon-lining and immune genes, gain of stromal/ECM and stemness genes.

### Week 7 — Pathway Enrichment ✅ COMPLETE
**Date:** Oct 13, 2026. Full detail: `docs/week7_enrichment.md`

- **Method change:** the plan named clusterProfiler (R); enrichment was run instead as over-representation analysis with **Enrichr via gseapy (Python)**, because it is scripted and reproducible in the existing environment and avoids a fragile Bioconductor install. Limitation: Enrichr's default background gene set is used.
- Up and down DEGs tested separately (1,281 and 1,775 gene symbols) against GO Biological Process 2026, KEGG 2021 Human and MSigDB Hallmark 2020.
- **Up in tumor:** E2F targets, G2-M checkpoint, Myc targets, DNA replication, cell cycle (proliferation); epithelial-mesenchymal transition, ECM organisation (matrix remodelling). **Down in tumor:** mineral absorption, xenobiotic/bile-acid/fatty-acid metabolism (normal colon function); T-cell and B-cell receptor signalling (lymphocyte signal).

**Status: ✅ Weeks 1–7 complete.** Remaining: Week 8 — final write-up (methods, results, interpretation, limitations), README polish and final push.
