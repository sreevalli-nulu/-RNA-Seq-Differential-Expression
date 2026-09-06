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
| 5 | Andrews, S. (2010). FastQC: A Quality Control Tool for High Throughput Sequence Data | Tool documentation | QC reference for interpreting raw-read FastQC/MultiQC output | https://www.bioinformatics.babraham.ac.uk/projects/fastqc/ |
| 6 | Ewels, P. et al. (2016). MultiQC: summarize analysis results for multiple tools and samples in a single report. *Bioinformatics* | Tool publication | Cite when describing the aggregate QC step in the final write-up | DOI: 10.1093/bioinformatics/btw354 |



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
