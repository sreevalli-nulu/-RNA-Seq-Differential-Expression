# Week 2 QC Interpretation: Raw vs. Trimmed Comparison

This section supplements the Week 2 trimming log with a per-sample before/after comparison and a discussion of two QC findings from the raw MultiQC report: adapter read-through and overrepresented sequences.

---

## 1. Raw vs. Trimmed Read Quality — Per-Sample Comparison

Values extracted directly from fastp's JSON summary for each sample (`before_filtering` vs. `after_filtering`).

| Sample | Reads (raw) | Reads (trimmed) | GC% (raw) | GC% (trimmed) | Q20% (raw) | Q20% (trimmed) | Mean length (raw) | Mean length (trimmed) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SRR975554 | 69,123,366 | 57,953,032 | 51.6% | 50.8% | 82.6% | 97.5% | 101 | 90 |
| SRR975556 | 61,802,386 | 52,102,678 | 51.2% | 50.5% | 83.2% | 97.5% | 101 | 90 |
| SRR975559 | 58,153,246 | 47,649,856 | 53.0% | 52.3% | 81.4% | 97.5% | 101 | 90 |
| SRR975564 | 65,054,980 | 53,096,586 | 52.4% | 51.8% | 82.7% | 97.6% | 101 | 93 |
| SRR975567 | 61,652,534 | 50,501,266 | 52.0% | 51.4% | 82.9% | 97.7% | 101 | 93 |
| SRR975572 | 63,282,332 | 52,189,876 | 51.4% | 50.6% | 81.7% | 97.4% | 101 | 91 |
| SRR975574 | 64,283,782 | 53,849,074 | 51.9% | 51.2% | 82.8% | 97.5% | 101 | 90 |
| SRR975577 | 66,679,458 | 54,521,890 | 52.3% | 51.6% | 81.3% | 97.4% | 101 | 90 |
| SRR975582 | 64,334,584 | 52,947,520 | 52.2% | 51.6% | 83.2% | 97.6% | 101 | 93 |
| SRR975585 | 67,739,046 | 55,139,100 | 52.8% | 52.1% | 82.3% | 97.6% | 101 | 92 |
| **Average** | **64,210,571** | **52,995,088** | **52.3%** | **51.5%** | **82.4%** | **97.5%** | **101** | **91.2** |

**Overall totals:** 642,105,714 raw reads → 529,950,878 trimmed reads (**82.5% retention**).

### What changed, and why

- **Read count** dropped by ~17.5% on average, consistent with removing low-quality 3′ tails and any reads that fell below the 25bp minimum length after trimming (see the Week 2 log for the parameter-tuning investigation behind this threshold).
- **Q20 rate rose sharply** (82.4% → 97.5%) — this is the direct, expected effect of quality-based trimming: removing the low-confidence tail bases raises the average confidence of what remains.
- **Mean read length dropped** from a uniform 101bp to a variable 90–93bp — this variability itself is expected, since `--cut_right` trims a different number of bases per read depending on where quality first drops below the threshold, rather than removing a fixed number of bases from every read.
- **GC% shifted down slightly** (~52.3% → ~51.5%) — a small, consistent shift across all samples, most likely because adapter-contaminated 3′ ends (which have a different composition than genomic sequence) were removed; the shift is minor and doesn't indicate any new bias introduced by trimming.

---

## 2. Adapter Read-Through — Origin and Handling

Adapters are not added by the sequencer itself; they're ligated onto every cDNA fragment during **library preparation**, before sequencing begins, since they're required for the fragment to bind the flow cell and be read at all.

Adapter contamination appears in the data specifically when a fragment's insert is **shorter than the 101bp read length** — the sequencer reads through the entire real insert and then continues into the adapter sequence ligated on the other end, which shows up as adapter sequence at the 3′ end of the read.

The raw MultiQC report's overrepresented sequences table confirms this directly — two of the top hits were exact matches to the standard Illumina TruSeq adapter (`AGATCGGAAGAGC...`), together making up under 0.02% of all reads. This is consistent with the low (<1%) adapter content flagged across all 20 samples in the "Adapter Content" panel.

**Handling:** fastp performs paired-end adapter detection automatically (via R1/R2 overlap analysis, without needing the adapter sequence specified manually) as part of the same trimming pass used for quality trimming. In the SRR975554 test run, this removed 555,918 adapter-containing reads and trimmed 15,570,896 adapter bases — already resolved as part of the Week 2 trimming step.

---

## 3. Overrepresented Sequences — Interpretation

FastQC flags any exact sequence exceeding 0.1% of total reads. In RNA-seq, this is frequently expected rather than concerning — a small number of highly expressed transcripts (ribosomal RNA, mitochondrial genes, dominant housekeeping genes) naturally dominate a library, since sequencing depth reflects transcript abundance.

MultiQC's own summary for this section reported: *"20 samples had less than 1% of reads made up of overrepresented sequences"* — below any threshold indicating contamination or a technical problem.

The specific sequences identified:

| Sequence type | Occurrences | % of all reads | Interpretation |
|---|---:|---:|---|
| Poly-N (`NNNNN...`) | 10,928,072 | 0.14% | Consistent with the isolated N-content spikes seen at specific read positions in a subset of samples — most likely a sequencer imaging-cycle artifact from the original HiSeq 2000 run, not a sample or library issue |
| Illumina TruSeq adapter (×2 variants) | 48,642 / 34,033 | 0.0076% / 0.0053% | Adapter read-through, as discussed above — negligible and already resolved by trimming |


## 4. Duplication Rate — Why It's Expected in RNA-seq

| Sample | Duplication Rate |
|---|---:|
| SRR975554 | 4.92% |
| SRR975556 | 8.36% |
| SRR975559 | 2.78% |
| SRR975564 | 4.44% |
| SRR975567 | 4.06% |
| SRR975572 | 6.72% |
| SRR975574 | 6.00% |
| SRR975577 | 4.87% |
| SRR975582 | 5.75% |
| SRR975585 | 4.16% |
| **Average** | **5.21%** |

In DNA sequencing (e.g., whole-genome or exome sequencing), a high duplication rate is generally treated as a red flag — it usually signals PCR over-amplification during library prep, and duplicate reads are typically removed before variant calling since they can inflate confidence in false-positive variant calls.

RNA-seq is different, and duplication needs to be read in that context: since sequencing depth at any given position directly reflects **transcript abundance**, highly expressed genes will naturally and legitimately produce many reads that look identical, simply because so much of that transcript was present in the sample to begin with. This is a real biological signal, not a technical artifact — removing "duplicates" in RNA-seq (as you might in DNA-seq) would actually discard genuine expression-level information and bias the results.

The duplication rates seen here — averaging 5.21%, ranging from 2.78% to 8.36% across the 10 samples — are well within the range considered normal for RNA-seq libraries of this depth (typically single-digit to low double-digit percentages). No deduplication step is applied in this pipeline, consistent with standard RNA-seq DE analysis practice (deduplication is reserved for DNA-based variant-calling workflows, not gene-level expression counting).

**Handling:** fastp's default N-base filtering (`--n_base_limit`, default 5) already addresses the poly-N reads — in practice, only 4 reads were dropped for excess N content across the SRR975554 test run, confirming this was a negligible, self-resolving issue once trimming was applied. No further action was required for either category.

