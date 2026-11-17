# Botanist-style inference: implementable, cited rules

Research update 17 November 2026. **Provide useful inference, not just “unknown.”** The implementable MVP is a transparent hypothesis-ranking engine. These tier thresholds are proposed product rules, not empirically validated probability estimates.

## Minimum honest tiers

- **Documented direct outcome**: a cited or logged cross of the requested directional parents, with its actual endpoint. Clearly distinguish same accession vs same species; label reported identity and verification separately. This is not a universal compatibility guarantee.
- **Promising inferred trial**: no qualifying direct record, but two or more distinct, role-consistent observed cross analogues in a biologically coherent local neighborhood, supported by a resolved phylogenetic relationship or curator rationale, without unresolved identity or compelling exact-pair counterevidence. This proposed threshold is a conservative UI rule, not a scientific law. Display the actual analogues, shared partners, unsupported leap and endpoint sought.
- **Exploratory inferred trial**: one observed analogue, documented reciprocal only, or supported phylogenetic neighborhood without direct crossing evidence. Explain which kind. Section/morphology alone stays here at most; it cannot earn “promising.”
- **Constrained / conflicting trial**: relevant failures or measured parent-role limitations conflict with positive analogy. Keep both visible rather than averaging into a reassuring score. The flag can coexist with any evidence tier.
- **Insufficient inference basis**: identity cannot be resolved or no relevant observed/phylogenetic evidence exists. Suggest a concrete observation or identity check, not a fabricated relationship.

“Promising” is about experimental prioritization. Never show “80% compatible” without a calibrated model and suitable data.

## Graph semantics and rules for Codex

### R01 Observations and predictions occupy separate tables
`ObservedCrossEvidence` stores actual reported experiments/offspring, direction, endpoint, identity confidence, protocol and provenance. `CrossHypothesis` stores requested parents, rule version, tier, evidence IDs, counterevidence IDs, argument, gaps and curator review. Inferred edges never enter the observed-cross graph or recursively count as empirical support.
**Test:** adding an inferred A×B edge does not raise another candidate's observed evidence count.

### R02 Directed bipartite mate profiles, not transitive closure
Represent seed-parent and pollen-parent roles separately. A→C and B→C means A and B share a successful pollen donor; it supports a reproductive-neighborhood analogy, not proof of A→B. A→C and C→B is a sequential two-edge pattern, not a demonstrated bridge. Construct local similarity from multiple independently reported partners where available; cap prolific hubs and duplicated reports so popularity is not biological certainty.
**Test:** with only A→C and C→B, A→B cannot be marked documented or become a direct edge. Its explanation calls the path exploratory.

### R03 Both endpoint roles require examination
For A(seed)×B(pollen), retrieve A's observed seed-parent performance and B's observed pollen-parent performance. If all observations for B are as seed parent, say its pollen-role performance is missing. Reverse-direction evidence is a separate analogue, not a copied outcome. General plant crossing research demonstrates reciprocal asymmetries at seed, viability and fertility stages [S4].
**Test:** B→A never satisfies exact-direction A→B; measured inability to produce pollen constrains pollen-role advice but does not block use as seed parent.

### R04 Hybrid parentage is a hyperedge, not a clique
Represent (A×B)×C with a specific hybrid offspring H of A×B and a second cross H×C. It documents H×C, not A×C or B×C. A practical bridge recommendation requires evidence H exists, the appropriate sexual function of H, and the next cross or a clearly marked next-step hypothesis. Alternative parent identities, ambiguous mixtures and sellers' formula strings are not verified offspring records.
**Tests:** no inferred component A×C/B×C edges; maternal/paternal alternatives never form two simultaneous observed relationships; a pedigree label alone cannot create an observed-cross success.

### R05 Evidence clusters motivate trials; they do not define equivalence classes
Display a cluster of observed successful crosses as a local breeding neighborhood. Do not give it a universal “compatible group” label or allow connected-component membership to imply all pairs cross. Use endpoint-specific graphs: viable offspring graph and offspring-fertility graph must remain distinct.
**Test:** a connected path of ten taxa never produces a complete compatibility matrix.

### R06 Taxonomy is supportive context, not gate
Maintain source-versioned section and molecular-clade assignments. A supported clade can strengthen an analogy, but low support, unsampled taxa and uncertain labels cannot be patched by silently assigning the nearest-looking species. Do not reject a cross solely because sections differ [S1,S2].
**Test:** documented historical intersectional crosses survive a taxonomy filter; ambiguous tree placement reduces inference specificity, not observed evidence.

### R07 Cytology is sample-scoped and stage-specific
Use measured specimen cytology preferentially; distinguish somatic count, ploidy, B chromosomes, genome size and meiotic pairing. Equal counts support no guaranteed fertility; a cytotype mismatch is an explicit caution, not an automatic impossibility verdict [S3].
**Test:** a species with 30 and 60 chromosome records does not receive a single asserted accession count; 30+1B does not automatically become a new ploidy.

### R08 Independent evidence and negative evidence
Deduplicate publications derived from the same crossing program. Count experimental units, not table rows, seeds or citations. Evaluate failed attempts only with endpoint, protocol, follow-up and usable parent material known. No record is not a failed cross. Store adverse exact-pair evidence beside related success. Search ranking may prioritize exact verified parents over many distant analogues.
**Test:** a syndicated breeder report has one independent origin; one unsuccessful event does not assign “incompatible.”

### R09 Explain every promotion
Return `tier`, `target_endpoint`, `direct_match_scope`, `supporting_motifs[]`, `counterevidence[]`, `identity_gaps[]`, `cytology_gaps[]`, `rule_version`, `source_ids[]`, and `next_experiment`. Each motif names its edge IDs and whether it is same-direction role analogy, reciprocal evidence, clade neighborhood or actual hybrid bridge. Do not let an LLM invent edges; it may narrate structured facts and flag errors.
**Test:** every recommendation exposes a traceable argument; absent evidence results in a weaker tier, not made-up references.

## Read primary publications: concrete curated examples

**S1 Marutani, Sheffer & Kamemoto (1993), American Journal of Botany 80:93–103.** Read full-text transcription including Tables 2–6. Table 2 records A. formosum A287 × A. cerrocampanense A225-2 across the historical sections Calomystrium/Cardiolonchium. It also records (A. andraeanum cv. Uniwai × A. kamemotoanum A288) × A. formosum, a genuine hybrid-parent structure. Table 4 labels Uniwai male sterile; other tables use it as seed parent. Therefore sexual function is role-specific. Tables 5–6 report pollen staining separately from germination and meiotic observations. Do not promote germinated/flowering offspring to fertile offspring. These are reported historical identities, not independently DNA-verified pedigrees. OCR contains table inconsistencies; check original page images before bulk numerical import.
DOI: https://doi.org/10.1002/j.1537-2197.1993.tb13772.x
Accessible full text: https://www.academia.edu/107719161/Cytological_Analysis_of_Anthurium_Andraeanum_Araceae_Its_Related_Taxa_and_Their_Hybrids

**S2 Camelo et al. (2026), Plants 15:866.** Read full Methods/Results/Data Availability. Target capture sampling covers 35 Anthurium species; traditional Pachyneurium is not monophyletic. The study recovers a close relationship between Atlantic Forest Pachyneurium taxa and A. coriaceum of historical Urospadix. Some placements remain unstable, including A. paraguayense, A. ernestii and A. salvinii. One accession per species was used, not population sampling. Thus this phylogeny can support specific evolutionary-neighborhood explanations but cannot resolve every collector accession or supply crossing outcomes. The paper points to raw reads and voucher data; those are not a ready-made compatibility dataset.
https://www.mdpi.com/2223-7747/15/6/866

**S3 Nascimento et al. (2019).** Read full accessible Methods/Results. A. pentaphyllum populations include 2n=30 and 60; B chromosome variation occurs in other studied samples. A species label alone cannot assign a user's accession cytotype. Preserve vouchers and population context.
https://www.scielo.br/j/gmb/a/bQVywrCJGLW3CnszHYFJhmK/?lang=en

**S4 Tiffin, Olson & Moyle (2001).** Read accessible primary comparative paper. Their analysis of reciprocal experiments in 14 angiosperm genera finds asymmetry at seed production, F1 viability and F1 fertility. It justifies direction/stage preservation, not numerical Anthurium-specific success estimates.
https://cbs.umn.edu/sites/cbs.umn.edu/files/migrated-files/downloads/Tiffinetal_ProcB_2001.pdf

**S5 Carlsen & Croat (2013; 2019).** Molecular study of 102 species reports low divergence and unresolved deep nodes. Later sectional analysis supports only a subset of traditional groups. Neither is a crossability model.
https://doi.org/10.1600/036364413X670287
https://annals.mobot.org/index.php/annals/article/view/215

## Real data acquisition, ordered by usefulness

1. **Curated experimental cross rows:** S1 Tables 2/5/6 and Sheffer & Kamemoto (1976) Tables 1/2. These are actual observations, not a machine-ready comprehensive matrix. 1976 publisher PDF remains access-blocked in this pass, so no fabricated row import: https://journals.ashs.org/downloadpdf/journals/jashs/101/6/article-p705.pdf . Use double-reviewed page extraction. Keep historical names, vouchers and overlapping experimental provenance.
2. **CCDB cytology API:** documented at https://ccdb.tau.ac.il/services/ . It supports `countsFull/?genus=Anthurium&format=json` and XML/CSV. Documentation verified; actual Anthurium endpoint retrieval was not supported by the web tool. Retrieve raw records, not taxon medians, and preserve original n/2n and citation. Programmatic availability is not proof of blanket commercial licensing; check terms before redistribution.
3. **NCBI PRJNA812606:** directly verified BioProject, Missouri Botanical Garden Anthurium phylogenomics, 42 linked SRA experiments/BioSamples. Raw sequences, not breeding outcomes. https://www.ncbi.nlm.nih.gov/bioproject/812606
4. **2026 phylogeny resources:** S2 declares SRA PRJNA1413566 and Figshare https://doi.org/10.6084/m9.figshare.31456999 (voucher Table S1/supporting data). Declaration read; Figshare content retrieval failed, so do not claim a Newick tree or license was inspected. Start by inspecting actual supplement file manifest before promising import.
5. **Names and concepts:** Kew WCVP release + GBIF Species API. They support identity alignment, not compatibility. Keep ambiguous nomenclature in review, especially historical lindenianum/nymphaeifolium name usages.
6. **First-party breeder reports:** useful observational layer when parent identity, direction, offspring stage and provenance are stated. Label reported identity; ask for failures too. Marketplace formula strings alone are weak pedigree claims, not controlled cross evidence. No comprehensive open Anthurium compatibility API was verified in this research pass.

## Validation before any “likelihood” product claim

Backtest by withholding whole directional species pairs and whole studies, not random table rows. Mask a direct edge, rank candidate trials from remaining evidence, and evaluate whether the observed endpoint is recovered. Include recorded negatives and abstention; avoid treating missing edges as negatives. Compare with section-only, phylogeny-only and popularity-only baselines. Then prospectively record new trials, control protocol variation and calibration. A useful exploratory ranking can ship now; proven probability accuracy cannot.
