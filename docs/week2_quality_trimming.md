# Week 2: Quality Control & Trimming
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal) | **Supervisor:** Dr. Nilofer
**Platform:** Windows + WSL2 (Ubuntu 22.04) | **Time budget:** ~1 hr/day

---

## Goal

Trim adapters and low-quality bases from the raw reads before alignment, using the Week 1 MultiQC report to decide what actually needs fixing — rather than applying default parameters blindly.

## Step 1: Interpret the Week 1 MultiQC Report First

Before choosing trimming parameters, review `results/week1_multiqc_report.html` for:

| Metric | What was found |
|---|---|
| Adapter content | Low overall (<1%) — adapter trimming was a low priority |
| Per-base quality | Strong (Phred 30–36) through ~bp 50, steady decline to ~20–25 by bp 100 — typical Illumina 3′ decay |
| GC content | 51–53%, tight and unimodal — healthy, no contamination signal |
| Duplication | Present but expected for RNA-seq (highly expressed transcripts naturally duplicate) |

**Conclusion:** the main issue is 3′ quality decay, not adapters — so trimming parameters should prioritize a quality-based sliding-window trim over aggressive adapter removal.

## Step 2: Choose a Trimming Tool

**Decision: fastp** over Trimmomatic — single-command syntax, auto-adapter-detection, and a built-in HTML/JSON QC report per sample (useful for before/after comparison without needing a separate FastQC pass on each sample individually).

Install into the existing `rnaseq` conda environment (not `apt`, to keep everything inside one versioned environment):
```bash
mamba activate rnaseq
mamba install -c bioconda -c conda-forge fastp -y
fastp --version   # fastp 1.3.6
```

## Step 3: Test Parameters on One Sample First

Don't run a new tool across all 10 samples blind — test on one first.

**First attempt** (standard starting point — Q20, min length 36bp):
```bash
fastp \
  -i raw_data/SRR975554_1.fastq.gz \
  -I raw_data/SRR975554_2.fastq.gz \
  -o trimmed/SRR975554_1.trimmed.fastq.gz \
  -O trimmed/SRR975554_2.trimmed.fastq.gz \
  --cut_right --cut_right_window_size 4 --cut_right_mean_quality 20 \
  --length_required 36 \
  --thread 4 \
  --html trimmed/SRR975554_fastp.html \
  --json trimmed/SRR975554_fastp.json
```

**Result:** only 72.8% of reads retained (50.4M / 69.2M), with 18.6M reads (27%) failing as "too short" after trimming — high enough to investigate before committing to a full batch run.

## Step 4: Investigate Before Adjusting Blindly

fastp reported an "insert size peak" of 46bp, which looked alarmingly short. Rather than assume the library prep was the problem, the underlying JSON was inspected directly:

```bash
python3 -c "
import json
with open('trimmed/SRR975554_fastp.json') as f:
    data = json.load(f)
hist = data['insert_size']['histogram']
total = sum(hist)
print(f'Total reads in histogram: {total}')
print(f'Peak bin: {hist.index(max(hist))} bp, count: {max(hist)} ({100*max(hist)/total:.1f}%)')
for i in range(0, len(hist), 20):
    bucket = sum(hist[i:i+20])
    if bucket > 0:
        print(f'{i}-{i+19} bp: {bucket} ({100*bucket/total:.1f}%)')
"
```

**Finding:** the histogram only covers 1.6M of the 34.6M total read pairs — fastp can only estimate insert size when R1/R2 physically overlap (fragments shorter than ~2× read length). Within that subset, the real distribution peaked at 140–159bp (34.7%), a normal RNA-seq fragment size. **Insert size was ruled out as the cause of the read loss.**

**Actual cause:** the Q20 quality cutoff was trimming deep enough into the naturally-decaying 3′ tail that many reads dropped below the 36bp minimum length requirement.

## Step 5: Revised Parameters

```bash
fastp \
  -i raw_data/SRR975554_1.fastq.gz \
  -I raw_data/SRR975554_2.fastq.gz \
  -o trimmed/SRR975554_1.trimmed.fastq.gz \
  -O trimmed/SRR975554_2.trimmed.fastq.gz \
  --cut_right --cut_right_window_size 4 --cut_right_mean_quality 15 \
  --length_required 25 \
  --thread 4 \
  --html trimmed/SRR975554_fastp.html \
  --json trimmed/SRR975554_fastp.json
```

- **Q15** (~97% base-call accuracy) instead of Q20 (~99%, more of a variant-calling standard) — sufficient for RNA-seq read counting
- **25bp minimum length** instead of 36bp — close to the practical floor for unique alignment with STAR against the human genome

**Result:** retention improved to 83.8% (57.95M / 69.2M reads); "too short" failures dropped from 18.6M to 11.1M (−41%); re-calculated insert size peak of 149bp now matches the true fragment size distribution found during investigation.

## Step 6: Run on All 10 Samples

```bash
for s in SRR975572 SRR975556 SRR975574 SRR975559 SRR975577 SRR975564 SRR975582 SRR975567 SRR975585; do
  fastp -i raw_data/${s}_1.fastq.gz -I raw_data/${s}_2.fastq.gz \
    -o trimmed/${s}_1.trimmed.fastq.gz -O trimmed/${s}_2.trimmed.fastq.gz \
    --cut_right --cut_right_window_size 4 --cut_right_mean_quality 15 \
    --length_required 25 --thread 4 \
    --html trimmed/${s}_fastp.html --json trimmed/${s}_fastp.json
done
```

**Batch results (all 10 samples):**

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
- Total bases retained: **48.83 billion bp**
- Consistent 81–84% retention across all samples confirms the tuned parameters generalized well, rather than being fit to one sample

## Step 7: Post-Trim QC

```bash
fastqc trimmed/*.trimmed.fastq.gz -o fastqc_trimmed/ -t 4
multiqc fastqc_trimmed/ -o fastqc_trimmed/ -n multiqc_trimmed_report
cp fastqc_trimmed/multiqc_trimmed_report.html results/week2_multiqc_trimmed_report.html
```

---

## Week 2 Deliverables Checklist
- [x] fastp v1.3.6 installed in the `rnaseq` conda environment
- [x] Trimming parameters tuned and justified via investigation, not guessed
- [x] All 10 samples trimmed (20 files) — 82.5% overall read retention, 97.5% Q20 rate
- [x] Post-trim FastQC + combined MultiQC report (`results/week2_multiqc_trimmed_report.html`)
- [x] Pipeline scope decision: command-line through Week 4 (trimming/alignment/counting), Galaxy or R for Week 5–7 (DESeq2/clusterProfiler), since Bioconductor installs are the most fragile part of a local WSL setup
