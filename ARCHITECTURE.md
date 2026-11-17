# Architecture and scientific boundaries

The buildless browser client reads JSON from a loopback Python HTTP server. The server initializes a SQLite database from deterministic, cited JSON. SQLite foreign keys are enabled on every connection. Queries and writes use bound parameters. User/source text is HTML-escaped, source URLs are HTTPS-only at seed import, and a restrictive CSP disallows inline scripts. HTTP is read-only. The UI is a current WCVP v16 projection; the research schema retains broader name/status detail.

## Relational model

- `sources` → immutable checksum-addressed `source_revisions` → `taxon_names` (verbatim raw JSON, status, authors, accepted-name pointer). `taxa` represent accepted concepts in this imported release. UI `species` and `taxonomic_records` are projections, not a universal taxonomy authority. Unplaced names retain a null concept link. Accepted-name IDs in raw WCVP source are source identifiers, not invented internal FKs.
- `taxonomic_assertions` retain source-specific classification status and unresolved notes; no section is populated from WCVP. Section conflicts are not resolved automatically.
- `cultivars` keep registry acceptance, establishment and raw formula distinct from species. `accessions` are individual experimental units, with optional taxon/cultivar identity and explicit provenance.
- `cross_plans` contain maternal and paternal accession FKs. Repeated `pollination_attempts` carry date, inflorescence, protocol, controls, optional pollen lot and censored/follow-up fields. Pollen-lot identity is checked against the planned pollen parent by the operation layer.
- `outcomes` are one stage/result/date per record with optional counts and denominator units. Constraints prevent impossible counts. `record_outcome` validates chronology and inserts a separate unverified evidence claim transactionally. A fruit observation creates no seedling or fertility record.
- `evidence_claims` separate evidence type, source/revision, locator, uncertainty and an optional conflicting claim. This provides a foundation for competing claims, not an automated truth adjudicator. Polymorphic subject references are operation-layer conventions; they are not SQL foreign keys. No conflict claim pairs were fabricated merely to populate this table.
- `genomic_measurements` are accession-specific, optional, method-bearing and source-linked. No genomic/ploidy numbers are seeded. Equal chromosome counts would not establish compatibility.
- `pedigree_edges` carry maternal/paternal/unknown role and a cited claim. Recursive CTE lineage queries preserve role/path and stop at depth 64. SQL triggers reject cycles and in-place edge rewrites. Unknown formulas are never parsed into confirmed accession pedigrees.
- `nomenclatural_claims` retains all 43 raw historical hybrid-formula records. `crosses` contains 22 deduplicated display groups plus twenty-four curated report/claim families. Formula claims are contextual, not experimental proof.

## Migrations and updates

`schema.sql` is the idempotent initial explorer schema. `migrations/002_research.sql` and subsequent numbered migrations run transactionally, with checksums recorded in `schema_migrations`; changing an already-applied migration fails closed. Source snapshots are retained, and a complete export is accessible. Research ingestion is idempotent per source revision. Current UI projection tooling is deliberately pinned to v16; a new release needs an explicit reviewed projection migration rather than silently overwriting concepts referenced by experimental history.

The local importer validates a candidate in a separate in-memory database, reports additions/changes, then optionally applies within a transaction after creating a backup. Monthly refresh stages immutable source candidates with an atomic latest pointer and previous last-good pointer. It does not crawl IAS, POWO, IPNI or vendor sites. Network ingestion requires explicit allowlisted source configuration; explicit robots disallow, uncertain robots errors or format uncertainty stops the job.

## Inference policy

There is no numeric compatibility score, inferred probability, same-section success flag or negative inference from absence. Direct directional reports, unordered reports, historical formula assertions, classification context and personal observations remain different evidence categories. No outcome is upgraded to a later developmental stage. The included dataset cannot establish a universal viability or fertility matrix; its coverage limitations remain visible.

## Local limitations

Python's server is intentionally local and not production hosting infrastructure. This release has no authentication, account system, field-note UI or public write API. The developer operations are a tested foundation, not a complete laboratory information management system. Genome, pollen lot and conflict tables are currently empty. New taxonomy releases require curated review. Section coverage is sparse. Runtime databases and test fixtures are excluded from Git and distribution archives; first run deterministically creates the real database from included seeds.

Commercial specimen references inform future identity modeling only. Cultivar/clone/selection/generation labels must retain source provenance and must not be expanded into species or pedigrees by guesswork. No Hershey’s Houseplants imagery, descriptions, design or bulk records were imported.

## Inspectable related-report paths

The pair explorer can show a two-edge shared-partner path from identified species in curated registrar/grower reports, only as related literature context when no selected-direction report exists. Each edge retains its source, actual direction and outcome. Historical hybrid-formula records and unresolved/compound pedigrees cannot create edges. A shared mate is not transitive compatibility; no bridge pedigree is decomposed, no edge establishes fertility, and no probability or “strong” trial classification is assigned. Counterevidence coverage is explicitly incomplete. The tiny corpus cannot support a robust statistical predictor.

## Publication-grounded interpretation constraints

Marutani, Sheffer & Kamemoto (1993), *Cytological Analysis of Anthurium andraeanum (Araceae), Its Related Taxa and Their Hybrids*, DOI https://doi.org/10.1002/j.1537-2197.1993.tb13772.x, provides accession-specific reasons to avoid coarse compatibility rules. Researcher-verified table findings are retained here as interpretation rules, not redistributed tables or newly seeded cross outcomes:

- Table 2 reports A. formosum A287 × A. cerrocampanense A225-2 across the historical section boundary. Different sections must not automatically block a research hypothesis.
- The reported three-way cross (A. andraeanum cultivar Uniwai × A. kamemotoanum A288) × A. formosum A290 requires a hybrid-parent entity. It cannot be decomposed into successful component-species pairings.
- Uniwai's male-sterility report and use as a seed parent in the paper require accession- and role-specific fertility assertions; male fertility is not female fertility.
- Germination, flowering, pollen stainability and functional fertility are distinct observations. The cited paper's low-stainability hybrid results must not be rewritten as a binary functional-fertility conclusion.

The current graph renderer does not score confidence. Synonyms, reciprocal records, repeated rows and retellings of one source never increase a confidence value. Unresolved alternative-parent identities and unknown trade-line taxonomy cannot produce confirmed species-level edges. The structured publication corpus remains pending researcher delivery; these rules do not fabricate its experimental records.

## Explicit empirical eligibility and curated upgrades

`crosses.reported_result`, `reported_endpoint`, `identity_qualified` and `graph_eligible` are affirmatively curated. Missing values default to unknown/false. Registry propagation reports remain visible as registry outcomes but cannot supply observed-offspring graph edges merely because a registration was accepted. Historical formulas, fruit-only outcomes, alternatives, unresolved lines and inferred records are excluded. A 2026-11-17 source recheck affirmatively qualifies Medusa flowering and Smaug seedling growth as reported outcomes, without genetic identity or fertility verification. Medusa plus the reported forgetii/crystallinum seedlings support a real exploratory path between crystallinum and luxurians through forgetii, with one edge direction unknown. The requested forgetii/antolakii shared-luxurians path is not admitted: antolakii is absent from the bundled WCVP snapshot, so CAR-0280 retains an unresolved source-label parent rather than a fabricated taxon link. Giant Claire retains an unknown qualified endpoint. Registry acceptance alone never qualifies a record.

Startup compares the checksum of the bundled reviewed seed, transactionally merges changed curated records, and then synchronizes label assertions. Existing accessions and observations are not deleted. A legacy-seed upgrade regression runs initialization twice and verifies private synthetic research records and foreign keys remain intact. This mechanism updates the bundled curated release; scheduled network candidates still require review and are not automatically promoted.


Migration 008 adds nullable access-level and report-family metadata to the cross projection and the foreign-keyed `cross_report_sources` relation. The open-pollination literature family has one cross row and two linked publications; claims retain their particular source in `evidence_claims`. The broad `published-cross` claim category is not a controlled-experiment designation: the display type explicitly states open pollination and indexed-abstract access. Its uncertainty, `identity_qualified=0`, `graph_eligible=0`, nonfunctional endpoint and excluded display type prevent empirical inference promotion. Seed-parent identity is documented, while the father remains attributed; therefore the pair's direction is not marked confirmed. Initialization refreshes these source links idempotently, including on existing databases.


The two clarinervium grower additions use the existing source-family relation and idempotent claim ingestion. Lutz's disputed-hybridity display type is deliberately excluded from empirical inference eligibility, even though intended pollination roles and reported seedling growth are explicit. The Steve's Leaves compound parent has a null taxon FK, retained raw parent label, and unknown direction; it cannot supply either pure-species edge. Both records set identity qualification and graph eligibility to zero. Access notices render each record's own uncertainty rather than reusing the open-pollination family's role wording.


Public seller additions reuse the idempotent source/claim import and source-family relation. Each listing has one event-family ID and one source. Both parent taxon FKs remain null; exact labels appear in the existing parent search. The dossiers separately retain seller, parent-origin attribution, source-of-parent attribution and non-event inspiration mentions. Unknown event dates are null. Neither a trade label nor an affinity label authenticates an accession or matches a user's plant. These reports use an explicitly unresolved seller evidence type and zero graph/identity eligibility.


The vegetative-clone record is explicitly typed `Seller pedigree claim · vegetative clone` in the display projection, and `pedigree-claim` with verification category `unknown` in normalized claims. Its nested structure is retained in the curated dossier; display parent slots do not assign roles. It creates no accession pedigree edge or experimental outcome, has null parent taxon FKs and zero identity/graph qualification, and is excluded by the observed-report allowlist. Source-local RVDP expansion is not inserted into global label assertions. The existing idempotent import handles its source and claim without creating duplicate events.


The Happiest Plants nested seller event follows the existing source/claim ingestion path. Its outer directional claim is distinct from the pollen compound's unknown internal roles in the dossier. Both taxon FKs remain null, both identity and graph eligibility are zero, and the unresolved seller-attribution display type is excluded from empirical inference. No internal component event or global BVEP/Antolakii alias is generated.


Rochani uses the existing registrar-record claim category, with a page/registration locator and explicit maternal accession label. Its source-reported parent species map to accepted WCVP concepts for retrieval. The explicit inflorescence description qualifies its flowering endpoint and graph flag under the same rule as Medusa; identity qualification denotes an adequately specified source claim, not independent authentication. Graph outputs retain accession gaps, direction and citation, with no functional-fertility promotion or numeric estimate. No user accession or private specimen is created.
