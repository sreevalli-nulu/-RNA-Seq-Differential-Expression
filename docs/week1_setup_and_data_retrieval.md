# Week 1: Environment Setup, Dataset Retrieval & Initial QC
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal) | **Supervisor:** Dr. Nilofer
**Platform:** Windows + WSL2 (Ubuntu 22.04) | **Time budget:** ~1 hr/day

---

## Dataset: GSE50760

- **Source:** [GSE50760](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE50760) (Gene Expression Omnibus)
- **Original publication:** Kim, S.K. et al. (2014), *PLoS ONE*. PMID: [25049118](https://pubmed.ncbi.nlm.nih.gov/25049118/)
- **Why this dataset:** paired-end Illumina RNA-seq with matched normal / primary tumor / liver metastasis samples from the *same patients* — a clean, biologically clear tumor-vs-normal comparison with strong tutorial support (used in the Griffith Lab GenViz course, among others).
- **Subset used:** 10 samples (5 patients × 1 tumor + 1 matched normal), chosen from the full 54-sample study for computational feasibility on a WSL-based laptop workflow.

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

Samples selected via the [NCBI SRA Run Selector](https://www.ncbi.nlm.nih.gov/Traces/study/?acc=GSE50760), matched by patient position across the tumor/normal blocks (standard GEO submission convention for this series) and balanced for similar file size per pair.

---

## Step 1: Set Up WSL2 + Ubuntu 22.04

In **PowerShell as Administrator**:
```powershell
wsl --install -d Ubuntu-22.04
```
Restart if prompted, then open Ubuntu and create a Linux username/password.

```bash
sudo apt update && sudo apt upgrade -y
```

> **Lesson learned:** if you have limited space on your C: drive, consider installing WSL directly to a secondary drive (D:/E:) from the start — see the Infrastructure Notes section below for why this matters.

## Step 2: Install Miniforge (conda/mamba)

```bash
cd ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
source ~/.bashrc
```
```bash
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

## Step 3: Create the `rnaseq` Conda Environment

```bash
mamba create -n rnaseq sra-tools fastqc star samtools subread multiqc -y
mamba activate rnaseq
```

Verify installs (versions used in this project):
```bash
prefetch --version      # sra-tools 3.4.1
fastqc --version         # FastQC v0.12.1
STAR --version           # STAR 2.7.10b
samtools --version       # SAMtools 1.24
featureCounts -v         # Subread v2.1.1
multiqc --version        # MultiQC 1.35
```

## Step 4: Project Folder Structure

```bash
mkdir -p ~/rnaseq_project/{raw_data,fastqc_raw,trimmed,fastqc_trimmed,genome,alignments,counts,results,scripts,docs,metadata}
cd ~/rnaseq_project
```

## Step 5: Download the 10 Samples

```bash
cd ~/rnaseq_project/raw_data
cat > srr_list.txt << 'EOF'
SRR975554
SRR975572
SRR975556
SRR975574
SRR975559
SRR975577
SRR975564
SRR975582
SRR975567
SRR975585
EOF
```

```bash
while read srr; do
  prefetch $srr
  fasterq-dump $srr --split-files -O .
  gzip ${srr}*.fastq
done < srr_list.txt
```

> **Note:** NCBI SRA server-side timeouts are common with large downloads and are not a local network/WSL issue — retry rather than troubleshoot the connection. A hybrid approach (direct SRA download + Google Drive transfer for problem samples) was used in this project when downloads repeatedly stalled.

**Always verify integrity after downloading:**
```bash
for f in *.fastq.gz; do gzip -t "$f" && echo "$f: OK"; done
```

## Step 6: Initial FastQC + MultiQC

```bash
cd ~/rnaseq_project
fastqc raw_data/*.fastq.gz -o fastqc_raw/ -t 4
multiqc fastqc_raw/ -o fastqc_raw/
```

Open the report from Windows at:
`\\wsl.localhost\Ubuntu-22.04\home\<username>\rnaseq_project\fastqc_raw\multiqc_report.html`

**Raw QC headline results (10 samples, 20 files):**
- ~29–35M reads per file, 101bp read length
- GC content 51–53% — consistent with expected human transcriptome range
- Strong per-base quality (Phred >30) through most of the read, tapering toward the 3′ end — typical Illumina decay pattern, addressed in Week 2 trimming
- Adapter content low overall (<1%)

## Step 7: Sample Metadata File

`metadata/sample_metadata.csv`:
```csv
SampleID,SRR_Accession,PatientID,Condition,Tissue
S1,SRR975554,P1,Tumor,Primary tumor
S2,SRR975572,P1,Normal,Adjacent normal
S3,SRR975556,P2,Tumor,Primary tumor
S4,SRR975574,P2,Normal,Adjacent normal
S5,SRR975559,P3,Tumor,Primary tumor
S6,SRR975577,P3,Normal,Adjacent normal
S7,SRR975564,P4,Tumor,Primary tumor
S8,SRR975582,P4,Normal,Adjacent normal
S9,SRR975567,P5,Tumor,Primary tumor
S10,SRR975585,P5,Normal,Adjacent normal
```

This file is what DESeq2 reads in Week 5 to know which sample belongs to which condition.

---

## Infrastructure Notes (Troubleshooting Encountered)

- **WSL instability was caused by low C: drive space** (down to ~1.4GB free), not RAM or battery — diagnosed via Windows Event Viewer (Volsnap Event ID 36). Fixed by migrating the entire WSL installation from C: to D: (`wsl --export` / `--unregister` / `--import`) and raising `.wslconfig` memory to 14GB as an added safety margin.
- A subsequent WSL disk corruption (`WSL_E_DISK_CORRUPTED`) required a full Ubuntu reinstall directly to D:. Recovery was low-friction because documentation was already pushed to GitHub.
- PowerShell prompts end in `>`; WSL/Linux prompts end in `$` — easy to confuse, worth double-checking before running Linux-only commands like `mamba` or `gzip`.
- Multi-line pasted commands (loops, `mkdir -p {...}`) can get corrupted in Windows Terminal, appearing as garbled escape codes — retype manually or paste with Ctrl+Shift+V if this happens.
- Files transferred via Google Drive sometimes get renamed with suffixes (e.g. `_1.fastq-001.gz`) — check with `ls` and `mv` back to the expected filename before use.

---

## Week 1 Deliverables Checklist
- [x] Working WSL2 + conda `rnaseq` environment (sra-tools 3.4.1, FastQC v0.12.1, STAR 2.7.10b, SAMtools 1.24, Subread v2.1.1, MultiQC 1.35)
- [x] All 20 FASTQ files (10 samples, paired-end) downloaded and gzip-integrity-verified
- [x] Initial FastQC/MultiQC report (`results/week1_multiqc_report.html`)
- [x] `sample_metadata.csv` completed
- [x] GitHub repository set up and pushed

