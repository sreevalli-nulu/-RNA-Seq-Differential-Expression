# Week 7: Pathway & Gene Ontology Enrichment
**Project:** RNA-Seq Differential Expression (Colorectal Tumor vs. Matched Normal)
**Platform:** WSL2, conda environment `rnaseq` | **Script:** `scripts/week7_enrichment.py` | **Method:** over-representation analysis with Enrichr (via the `gseapy` Python package)

---

## Goal

Find the biological processes and pathways that the 3,313 differentially expressed genes point to, separately for genes up and down in tumor.

## Step 1: Method

```bash
pip install gseapy adjustText     # inside the rnaseq environment
cd ~/rnaseq_project && python scripts/week7_enrichment.py
```

- **Input:** `results/deseq2_significant_genes.tsv` (padj < 0.05, |log2FC| ≥ 1). Up- and down-regulated genes were tested **separately**, because mixing directions hides opposite biology.
- **Gene lists:** genes with an official symbol only — **1,281 up** and **1,775 down** (the remaining Ensembl-only IDs, mostly novel or non-coding genes, were dropped).
- **Libraries:** GO Biological Process 2026, KEGG 2021 Human, MSigDB Hallmark 2020. The script selects the newest GO/KEGG library available from Enrichr rather than hard-coding a year.
- **Statistics:** Enrichr's Fisher exact test; adjusted p-values (Benjamini–Hochberg) reported.
- **Background:** Enrichr's web service uses its **own default background gene set**, not the genes expressed in this experiment. This is a known limitation of the web-service approach and is stated in the methods; a local analysis with a custom background could refine it.

## Step 2: Results

Terms with adjusted p < 0.05 per library:

| Library | Up in tumor | Down in tumor |
|---|---:|---:|
| GO Biological Process 2026 | 157 | 88 |
| KEGG 2021 Human | 16 | 40 |
| MSigDB Hallmark 2020 | 26 | 10 |

### Up in tumor (1,281 genes)

| Library | Top terms (overlap, adjusted p) |
|---|---|
| Hallmark | E2F Targets (85/200, 1e-46); Epithelial-Mesenchymal Transition (81/200, 7.6e-43); G2-M Checkpoint (73/200, 4e-35); mTORC1 Signaling (45/200, 1e-12); Myc Targets V2 (22/58, 2.8e-11) |
| KEGG | Cell cycle (37/124, 2.7e-13); DNA replication (15/36, 2.5e-7); ECM-receptor interaction (20/88, 5.1e-5); IL-17 signaling (20/94, 1.2e-4); Protein digestion and absorption (20/103, 4.1e-4) |
| GO BP | Extracellular Matrix Organization (49/192, 1e-13); DNA Replication (31/108, 8e-10); Mitotic Sister Chromatid Segregation (34/128, 8e-10); External Encapsulating Structure Organization (29/111, 2.8e-8) |

### Down in tumor (1,775 genes)

| Library | Top terms (overlap, adjusted p) |
|---|---|
| Hallmark | Allograft Rejection (48/200, 5.8e-9); KRAS Signaling Up (38/200, 1.3e-4); Xenobiotic Metabolism (33/200, 0.0044); Bile Acid Metabolism (22/112, 0.0044); Fatty Acid Metabolism (25/158, 0.03) |
| KEGG | Neuroactive ligand-receptor interaction (67/341, 1.2e-7); Cell adhesion molecules (38/148, 2e-7); Hematopoietic cell lineage (29/99, 4.7e-7); Mineral absorption (21/60, 1.5e-6); cAMP signaling (43/216, 2.2e-5) |
| GO BP | Antigen Receptor-Mediated Signaling Pathway (36/120, 1.3e-7); Regulation of T Cell Activation (28/83, 4.8e-7); B Cell Receptor Signaling Pathway (17/33, 4.9e-7); T Cell Activation (33/124, 6.3e-6) |

Full tables: `results/enrichment_up_in_tumor.tsv`, `results/enrichment_down_in_tumor.tsv`; summary: `results/enrichment_summary.txt`; figure: `results/fig_enrichment.png`.

## Step 3: Biological Interpretation

Three themes emerge, consistent with the gene-level results from Weeks 5–6:
1. **Proliferation is up.** E2F targets, G2-M checkpoint, Myc targets, DNA replication, mitotic chromosome segregation and the KEGG cell-cycle pathway are all strongly enriched in tumor — the textbook proliferative signature of cancer.
2. **Matrix remodelling and a mesenchymal programme are up.** Epithelial-mesenchymal transition, extracellular-matrix organisation and ECM-receptor interaction reflect the stromal reaction and invasive features of tumor tissue (COMP, COL11A1, COL8A1, MMP3 among the genes).
3. **Normal colon function and immune-signalling genes are down.** Mineral absorption and xenobiotic, bile-acid and fatty-acid metabolism are the absorptive and metabolic roles of the colon lining and fall in tumors, consistent with loss of differentiation. Lymphocyte pathways (T-cell and B-cell receptor signalling, hematopoietic lineage, allograft rejection) are lower in tumor than in adjacent normal mucosa.

**Cautions for the write-up:**
- The lower lymphocyte signal is an observation from five pairs. Plausible explanations include lymphoid-rich normal mucosa or immune exclusion in tumors, but neither was tested here; it is reported as an observation, not a mechanism.
- Bulk RNA-seq mixes cell types, so some enrichment reflects tissue composition.
- "KRAS Signaling Up" in the down-in-tumor list is not interpreted: that gene set contains many immune genes, which probably drive the match.
- Results use Enrichr's default background (see Step 1).

## Week 7 Progress Checklist
- [x] Up- and down-regulated DEG lists tested separately against GO BP, KEGG and MSigDB Hallmark
- [x] Results tables, summary and figure generated and committed
- [x] Themes interpreted against the Week 5–6 gene-level findings
- [x] gseapy 1.3.1 (see environment.yml)
