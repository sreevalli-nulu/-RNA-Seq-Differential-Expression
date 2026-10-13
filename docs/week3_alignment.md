# Week 3: Reference Genome Preparation & STAR Alignment
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal) | **Supervisor:** Dr. Nilofer
**Platform:** Windows + WSL2 (Ubuntu 22.04), conda environment `rnaseq`

---

## Goal

Align the trimmed reads from Week 2 to the human reference genome using STAR, producing coordinate-sorted BAM files ready for gene-level read counting in Week 4.

## Step 1: Resource Check Before Downloading Anything Large

Given the known history of WSL instability from low disk space (see Week 1 notes), and because STAR genome indexing is memory-intensive, resources were checked first:

```bash
df -h /
free -h
```

**Result:** 835GB free on D:, and WSL's memory cap confirmed at its existing setting.

**Decision:** raised the WSL memory allocation from 14GB → **18GB** (laptop has 20GB total RAM) via `.wslconfig` (edited from PowerShell with `notepad $env:USERPROFILE\.wslconfig`, then `wsl --shutdown` to apply), leaving ~2GB headroom for Windows itself.

## Step 2: Reference Genome & Annotation Choice

**Decision: GRCh38 + GENCODE** (over Ensembl) — current standard, most widely used and documented for human RNA-seq.

Latest available: **GENCODE Release 50 (GRCh38.p14)**.

Downloaded the **primary assembly** genome FASTA (excludes alternate haplotype contigs/scaffolds — appropriate for RNA-seq gene counting, and reduces STAR's memory footprint) and the matching annotation GTF:

```bash
cd ~/rnaseq_project/genome
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/GRCh38.primary_assembly.genome.fa.gz
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.primary_assembly.annotation.gtf.gz
gunzip GRCh38.primary_assembly.genome.fa.gz
gunzip gencode.v50.primary_assembly.annotation.gtf.gz
```

Genome FASTA: 3.0GB uncompressed. Initial GTF (Comprehensive annotation): 4.4GB / 11.25M lines — later found to be the root cause of the indexing failure below.

**Integrity note:** after an interrupted `gunzip` (accidental Ctrl+C) raised concern about file corruption, validity was confirmed directly rather than assumed, by checking every line had the correct 9-column tab-separated GTF structure:
```bash
awk -F'\t' 'NF != 9 && !/^#/ {print "Bad line " NR ": " NF " fields"; count++} END {print "Total malformed lines: " count+0}' gencode.v50.primary_assembly.annotation.gtf
```
Result: 0 malformed lines — file was structurally valid despite its unexpectedly large size (GENCODE annotation has grown substantially in recent releases vs. older documentation/tutorials).

## Step 3: First STAR Indexing Attempt — Failed (Out of Memory)

```bash
STAR --runMode genomeGenerate \
  --genomeDir genome/star_index \
  --genomeFastaFiles genome/GRCh38.primary_assembly.genome.fa \
  --sjdbGTFfile genome/gencode.v50.primary_assembly.annotation.gtf \
  --sjdbOverhang 90 \
  --genomeSAsparseD 2 \
  --runThreadN 4 \
  --limitGenomeGenerateRAM 16000000000
```

Progressed through suffix array generation (~1.5 hrs) but was **killed by the Linux OOM killer** at the "inserting junctions into the genome indices" step — the Comprehensive GTF's large transcript/junction count exceeded available memory even with the sparse suffix array setting.

## Step 4: Switch to GENCODE Basic Annotation

GENCODE documents the **Basic** annotation set (transcripts tagged 'basic' in every gene — a curated subset of Comprehensive) as "the main annotation file for most users," and it is standard for gene-level RNA-seq quantification rather than exhaustive isoform cataloguing.

```bash
wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.primary_assembly.basic.annotation.gtf.gz
gunzip gencode.v50.primary_assembly.basic.annotation.gtf.gz
```

Result: 3.0GB / 7.4M lines — roughly 34% fewer lines than Comprehensive.

## Step 5: Second Attempt — Silently Failed to Launch (Session/Terminal Closure)

Re-ran indexing with the Basic GTF and a more conservative `--genomeSAsparseD 3`, plus a background memory logger to diagnose any future OOM kill:
```bash
(while true; do date; free -h; sleep 60; done > genome/memory_log.txt 2>&1 &)
STAR --runMode genomeGenerate ... --genomeSAsparseD 3 --limitGenomeGenerateRAM 14000000000
```

After a multi-day gap between sessions, the `star_index/` output folder was found empty, and the memory log showed only ~300MB used at every logged interval — confirming **STAR never actually ran for any sustained period**. Root cause: the command was launched directly in the foreground of a terminal session, which closed (window closed, or WSL session ended) before STAR could make real progress — it was never actually killed by low memory this time, it just never got the chance to run.

## Step 6: Third Attempt — Correctly Backgrounded with `nohup`

**Key fix:** long-running steps must survive terminal/WSL session closures between work sessions. Launched with `nohup` (ignores hangup signal) and `disown` (detaches from the shell's job table) together:

```bash
cd ~/rnaseq_project
nohup STAR --runMode genomeGenerate \
  --genomeDir genome/star_index \
  --genomeFastaFiles genome/GRCh38.primary_assembly.genome.fa \
  --sjdbGTFfile genome/gencode.v50.primary_assembly.basic.annotation.gtf \
  --sjdbOverhang 90 \
  --genomeSAsparseD 3 \
  --runThreadN 4 \
  --limitGenomeGenerateRAM 14000000000 \
  > genome/star_index_log.txt 2>&1 &
disown
```

Confirmed running via `ps aux | grep STAR`; the index completed successfully (~13.5GB in `genome/star_index/`). Progress and completion can be checked anytime via:
```bash
tail -30 genome/star_index_log.txt
ls -la genome/star_index/
```

**Parameter summary for the log:**
- `--sjdbOverhang 90`: read length − 1, matching the ~91bp average trimmed read length from Week 2
- `--genomeSAsparseD 3`: trades alignment speed for lower indexing memory (increased from the initially-attempted value of 2 after the first OOM failure)
- `--limitGenomeGenerateRAM 14000000000`: caps STAR at 14GB, leaving headroom under the 18GB WSL memory limit

## Step 7: Alignment of All 10 Samples

All 10 trimmed pairs were aligned to the index sequentially in one backgrounded batch, producing coordinate-sorted BAM files:

```bash
nohup bash -c 'for s in SRR975554 SRR975572 SRR975556 SRR975574 SRR975559 SRR975577 SRR975564 SRR975582 SRR975567 SRR975585; do
  STAR --runMode alignReads \
    --genomeDir genome/star_index \
    --readFilesIn trimmed/${s}_1.trimmed.fastq.gz trimmed/${s}_2.trimmed.fastq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix alignments/${s}_ \
    --runThreadN 4 \
    --limitBAMsortRAM 10000000000
done' > alignments/star_align_log.txt 2>&1 &
disown
```

- Each sample takes roughly **1.7–2 hours** with 4 threads, because the sparse suffix array (`--genomeSAsparseD 3`) trades speed for memory and the index (~13.5GB) must be held in RAM. This is far longer than the initial estimate of 10–20 minutes per sample.
- `--limitBAMsortRAM 10000000000` caps the BAM-sorting memory at 10GB so that index + sorting stay inside the 18GB WSL allocation.

**Interruptions and how they were handled** (none affected the final results):
- A full Windows restart killed the running batch. A leftover temporary directory (`SRR975554__STARtmp`) had to be deleted with `rm -rf` before STAR would re-run that sample.
- Laptop sleep froze the STAR job for hours at a time; the job resumed once the laptop was kept awake, so the remaining samples were run with the machine kept awake.
- One later batch stopped after 9 of 10 samples; only the missing sample (SRR975585) was re-run.
- A sample counts as finished only when it has a `*_Log.final.out` file **and** passes `samtools quickcheck`.

## Step 8: Post-Alignment Verification

```bash
ls alignments/*Log.final.out | wc -l        # 10
for s in SRR975554 SRR975556 SRR975559 SRR975564 SRR975567 SRR975572 SRR975574 SRR975577 SRR975582 SRR975585; do
  samtools quickcheck -v alignments/${s}_Aligned.sortedByCoord.out.bam && echo "$s BAM OK"
done
grep -H -E "Uniquely mapped reads %|% of reads mapped to multiple loci|% of reads unmapped: too short" alignments/*_Log.final.out
```

**Result:** 10/10 `Log.final.out` files; all 10 BAMs intact (`samtools quickcheck` passed).

### Mapping statistics (from STAR `Log.final.out`)

| Sample | Condition | Uniquely mapped | Multi-mapped | Total mapped | Unmapped (too short) |
|---|---|---:|---:|---:|---:|
| SRR975554 | Tumor (P1) | 92.61% | 5.63% | 98.24% | 1.66% |
| SRR975556 | Tumor (P2) | 90.15% | 7.75% | 97.90% | 1.81% |
| SRR975559 | Tumor (P3) | 91.19% | 6.41% | 97.60% | 2.32% |
| SRR975564 | Tumor (P4) | 92.30% | 4.85% | 97.15% | 2.74% |
| SRR975567 | Tumor (P5) | 91.50% | 5.64% | 97.14% | 2.73% |
| SRR975572 | Normal (P1) | 91.21% | 6.59% | 97.80% | 2.02% |
| SRR975574 | Normal (P2) | 90.47% | 6.87% | 97.34% | 2.45% |
| SRR975577 | Normal (P3) | 89.53% | 6.95% | 96.48% | 3.33% |
| SRR975582 | Normal (P4) | 89.98% | 6.15% | 96.13% | 3.68% |
| SRR975585 | Normal (P5) | 89.73% | 7.04% | 96.77% | 3.07% |
| **Average** | | **90.9%** | **6.4%** | **97.3%** | **2.6%** |

**Interpretation:**
- Alignment quality is excellent and consistent: uniquely mapped reads range 89.5–92.6% (well above the ~70–80% often used as a minimum for human RNA-seq), and no sample is an outlier.
- Multi-mapped reads (4.9–7.8%) come mainly from paralogous genes and repeats. featureCounts does not count them by default (Week 4), which is the conservative choice for gene-level counting.
- The only unmapped category extracted here is "too short" (1.7–3.7%): reads whose alignable portion was below STAR's minimum length. Normal samples average slightly lower unique mapping than tumors (90.2% vs 91.6%) with slightly more too-short reads; the difference is small and was not interpreted further.

---

## Lessons Learned (added to project working notes)

1. Any long-running command (genome indexing, batch alignment) must be launched with `nohup ... & disown` rather than in the terminal foreground, since the terminal or WSL session can close and a foreground process dies silently with no error message.
2. Memory is the binding constraint for STAR on a 20GB laptop: the Comprehensive GTF caused an OOM kill at junction insertion; the Basic GTF with `--genomeSAsparseD 3` and an explicit RAM cap worked.
3. Verify completion by files, not by assumption: a sample is done only when `Log.final.out` exists and the BAM passes `samtools quickcheck`.
4. Time estimates for STAR should be taken from the first completed sample, not guessed — the real figure was about 1.7–2 hours per sample.

---

## Week 3 Progress Checklist
- [x] WSL memory limit raised to 18GB
- [x] GRCh38 primary assembly genome + GENCODE Release 50 downloaded, integrity-verified
- [x] Annotation choice revised: Comprehensive → Basic, after OOM failure
- [x] STAR genome index built (backgrounded with `nohup`)
- [x] All 10 trimmed samples aligned (sorted BAMs)
- [x] Post-alignment verification: 10/10 BAMs valid; mapping rates tabulated (avg 90.9% unique, 97.3% total mapped)
- [ ] (Optional) MultiQC report aggregating the 10 STAR `Log.final.out` files
