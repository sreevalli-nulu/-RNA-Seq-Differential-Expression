# Week 1: Environment Setup, Dataset Retrieval & Initial QC
**Project:** RNA-Seq Differential Expression (Tumor vs Normal) | **Supervisor:** Dr. Nilofer
**Platform:** Windows + WSL2 (Ubuntu) | **Time budget:** ~1 hr/day

---

## Recommended Dataset: GSE50760

**Why this instead of GSE183947 (the example in your plan):**
- Human colorectal cancer study with **matched normal / primary tumor / liver metastasis** samples from the *same patients* — a clean, biologically clear two-condition comparison (tumor vs normal).
- Paired-end Illumina RNA-seq, well-annotated metadata, used in many published DE tutorials — so if you get stuck, there's prior art to sanity-check against.
- Full dataset has 54 samples, but you don't need all of them. **You'll use a subset of 6** (3 tumor + 3 normal) — this is standard practice for a learning project and keeps download + alignment time realistic for 1 hr/day.

> Note: your original 8-week plan mentioned HISAT2, but the plan in your screenshot uses STAR for alignment. STAR is a great choice too — slightly more resource-hungry (needs ~30GB RAM for human genome indexing by default, but you can build a smaller-memory index — see Week 3 notes later). We'll stick with STAR since that's your current plan.

### How to pick your 6 samples
1. Go to **GEO**: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE50760
2. Scroll to the bottom and click the **SRA Run Selector** link (or go directly to https://www.ncbi.nlm.nih.gov/Traces/study/ and search `GSE50760`).
3. In the Run Selector table, filter/sort by the sample source column — you're looking for samples labeled **"normal"** vs **"primary tumor"** (avoid "metastasis" for now — keep it a clean two-group comparison).
4. Pick **3 normal + 3 tumor samples, ideally from 3 different patients** (so each patient contributes one normal + one tumor sample — a paired design, which is statistically stronger and easier to justify in your writeup).
5. Note down the **SRR accession numbers** (e.g., SRR975551) for your 6 chosen samples — you'll need these for download.

---

## Step 1: Set Up WSL2 + Ubuntu (if not already done)

Open **PowerShell as Administrator** on Windows:
```powershell
wsl --install -d Ubuntu-22.04
```
Restart if prompted, then open the Ubuntu app and create your Linux username/password.

Update the system:
```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Miniconda/Mamba (environment manager)

```bash
cd ~
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
# accept defaults, then restart your shell or run: source ~/.bashrc
```

Add the bioinformatics channels:
```bash
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
```

## Step 3: Create Your Project Environment

```bash
mamba create -n rnaseq sra-tools fastqc star samtools subread multiqc -y
mamba activate rnaseq
```

Verify installs:
```bash
fastqc --version
prefetch --version
STAR --version
samtools --version
```

**Deliverable check:** ✅ working `rnaseq` conda environment (screenshot the version outputs for your project log — useful for your final writeup/README).

## Step 4: Set Up Your Project Folder Structure

```bash
mkdir -p ~/rnaseq_project/{raw_data,fastqc_raw,trimmed,fastqc_trimmed,genome,alignments,counts,results,scripts}
cd ~/rnaseq_project
```

Keeping this structure from Week 1 will save you real time in Weeks 2–7 — and it's exactly the kind of organization that looks good on GitHub later.

## Step 5: Download Raw FASTQ Files (your 6 chosen SRR accessions)

Create a text file with your 6 SRR IDs (replace with the ones you selected):
```bash
cd ~/rnaseq_project/raw_data
cat > srr_list.txt << 'EOF'
SRRxxxxxxx
SRRxxxxxxx
SRRxxxxxxx
SRRxxxxxxx
SRRxxxxxxx
SRRxxxxxxx
EOF
```

Download and convert to FASTQ (this will take a while — run it and step away, don't wait live):
```bash
while read srr; do
  prefetch $srr
  fasterq-dump $srr --split-files -O .
  gzip ${srr}*.fastq
done < srr_list.txt
```

> If your daily hour runs out mid-download, that's fine — `prefetch` resumes where it left off. Just don't delete the partial `.sra` cache folder.

**Deliverable check:** ✅ 6 (or 12, if paired-end — 2 files per sample) gzipped FASTQ files in `raw_data/`.

## Step 6: Run Initial FastQC on All Raw Reads

```bash
cd ~/rnaseq_project
fastqc raw_data/*.fastq.gz -o fastqc_raw/
```

Then aggregate all reports into one summary (much easier to read than 12 separate HTML files):
```bash
multiqc fastqc_raw/ -o fastqc_raw/
```

Open `fastqc_raw/multiqc_report.html` (from Windows: it's at
`\\wsl$\Ubuntu-22.04\home\<your-username>\rnaseq_project\fastqc_raw\multiqc_report.html`) to review per-base quality, adapter content, and GC distribution across all samples at once.

**Deliverable check:** ✅ Initial QC Report — save the MultiQC HTML as your "Initial QC Report" deliverable for Week 1.

## Step 7: Compile Sample Metadata File

Create `sample_metadata.csv` in your project root:

| SampleID | SRR_Accession | PatientID | Condition | Tissue |
|---|---|---|---|---|
| S1 | SRRxxxxxxx | P1 | Tumor | Primary tumor |
| S2 | SRRxxxxxxx | P1 | Normal | Adjacent normal |
| S3 | SRRxxxxxxx | P2 | Tumor | Primary tumor |
| S4 | SRRxxxxxxx | P2 | Normal | Adjacent normal |
| S5 | SRRxxxxxxx | P3 | Tumor | Primary tumor |
| S6 | SRRxxxxxxx | P3 | Normal | Adjacent normal |

This file is what DESeq2 will read in Week 5 to know which sample belongs to which condition — get the labels right now and it'll save you debugging time later. Fill in the real SRR numbers and patient IDs from Run Selector.

---

## Week 1 Deliverables Checklist
- [ ] Working WSL2 + conda `rnaseq` environment
- [ ] 6 raw FASTQ files downloaded (3 tumor + 3 normal, ideally paired by patient)
- [ ] Initial FastQC/MultiQC report (HTML)
- [ ] `sample_metadata.csv` completed
- [ ] (Optional but recommended) Push your `rnaseq_project/` folder structure + a short README to a GitHub repo now — starting the repo in Week 1 rather than at the end makes the resume-ready commit history happen naturally

## What to Watch For in Your FastQC Report
- **Per-base sequence quality**: should stay mostly in the green zone; a dip at the read tail is normal and gets fixed by trimming in Week 2.
- **Adapter content**: some adapter contamination is expected and is exactly what Week 2's trimming step addresses — don't worry about it now, just note it.
- **Per-sequence GC content**: should roughly follow a normal distribution; a second peak can indicate contamination and is worth flagging to Dr. Nilofer if you see it.
