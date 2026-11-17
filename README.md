# Anthurium Atlas

A local Anthurium taxonomy and cross-evidence explorer. Dark, compact, buildless UI; Python standard-library HTTP server; real persisted SQLite database. No accounts, credentials, analytics, remote service dependency or journal UI.

## Run

Requires Python 3.10+. From this directory:

```sh
python3 app.py
```

Open **http://127.0.0.1:8000/**. The first run creates and seeds `data/anthurium-atlas.sqlite3`; subsequent runs preserve it. No install or build step is necessary. `npm run dev` is an optional convenience using port 3000. Loopback is the default; external access requires an explicit `--host 0.0.0.0`. This development server is for local research, not public deployment.

## What is included

- 1,460 accepted species in the WCVP v16 snapshot, 1,915 linked accepted/synonym name records in the species UI, and all 2,177 original names in the research schema/export.
- Twenty-four curated report/claim families (twenty-two registry/grower/seller reports, one vegetative-clone pedigree claim and one access-limited literature report), separately labeled from 43 historical hybrid-formula name records grouped into 22 nomenclatural groups. Counts are **not** counts of proven compatible crosses.
- Seven source-specific historical/traditional section assignments across two sections. Clarinervium and pallidiflorum conflicts remain unresolved; most species have no curated placement.
- Search by species, linked synonym or distribution, section filters, taxonomic record citations, single-parent partner discovery, searchable pair comparison and complete JSON export. Start with either a pollen or seed parent; reverse-only reports remain clearly separated. Freeform trade labels remain unresolved unless an exact cited label is present.
- Future-ready accession/clone, cultivar, source revision, cross plan, repeated attempt, stage outcome, genomic measurement and recursive pedigree schema. No personal events or genomic values are seeded. No account or recording UI is exposed; HTTP writes return 405.

## Evidence rules

Unknown ≠ incompatible. Shared section ≠ proven compatibility. Directional reports never imply reciprocal success. Formula order never proves seed/pollen roles. Registry acceptance and cultivar establishment are separate flags. Fruit set, harvested seed, germination, seedlings, flowering and fertility are distinct outcomes; none is automatically advanced into the next stage. Missing follow-up remains censored, not failure. Trade labels and cultivar names do not become accepted species automatically. Genetic parentage and fertility are unknown in the included reports.

Medusa keeps the registry's raw `forgetti` spelling alongside normalized WCVP `forgetii`. Giant Claire retains established=yes and the source misspelling. Amy's complex formula remains unparsed and direction-unknown. Mike's Goliath has alternative pollen identities, not two confirmed crosses. No compatibility probabilities are calculated.

## Reproduce and inspect data

```sh
python3 scripts/curate.py
python3 scripts/build_seed.py
python3 scripts/import_data.py data/seed.json
# After reviewing the printed diff; creates a preimport database backup:
python3 scripts/import_data.py data/seed.json --apply
```

The importer is local-only, transactional and merge-only. It rejects unexpected columns, invalid citation URLs and broken foreign keys. It does not delete previous records or silently resolve taxonomic disagreements. Full source snapshots remain in `research/`. `GET /api/export` includes all normalized research tables. Back up SQLite before any manual research edits.

## Scheduled WCVP refresh

`.github/workflows/wcvp-refresh.yml` defines a monthly run at **06:19 UTC on the first day of each month**, plus manual dispatch. It downloads only the official configured WCVP bulk ZIP, checks robots (404/410 means no published policy; explicit disallow and other errors fail closed), refuses redirects/unapproved sources, bounds download/decompression sizes, validates names and coverage, and publishes a checksum-addressed **candidate artifact** with an additions/changes/removals report. It does not commit, push, deploy or overwrite the reviewed database. The workflow is now published on the repository’s default branch with its schedule trigger defined. Execution depends on GitHub Actions being enabled; no completed scheduled run has been verified.

```sh
# Offline validation / staging, no network:
python3 scripts/refresh_wcvp.py --local-snapshot research/wcvp_anthurium_v16.json
# Explicit opt-in to the reviewed source configuration:
python3 scripts/refresh_wcvp.py --network-config config/wcvp-refresh.json
```

Immutable candidate files are written before `latest.json` is atomically replaced; `last-good.json` retains the previous valid pointer. Failed validation leaves last-good and the live SQLite database untouched. Source archive and snapshot hashes, retrieval date, source URL and license are retained. The downloaded release gets an honest download identifier; no unverified Kew version number is asserted. Review publisher release metadata, taxonomy changes and source terms before promoting a new release. Do not replace the v16 snapshot with an unreviewed newer release; use a new versioned snapshot and adapt the projection explicitly. Curated cross/section records are never overwritten by this refresh. This conservative review boundary intentionally prevents scheduled taxonomy changes from silently changing research conclusions.

Local cron alternative (after reviewing current source terms): `19 6 1 * * cd /absolute/path/anthurium-atlas && python3 scripts/refresh_wcvp.py --network-config config/wcvp-refresh.json`. No cron entry was installed.

## Grower-source name discovery

See `DISCOVERY.md` for the separate staged discovery workflow. It accepts local factual name candidates or explicitly configured permitted HTTPS pages, performs exact WCVP name resolution, and retains every result as pending. It does not invent popularity rankings or automatically promote taxonomy or crossing claims. The shipped source allowlist is empty and disabled. `.github/workflows/name-discovery.yml` defines a Monday 07:43 UTC run, and is now published on the default branch. No completed scheduled run has been verified; execution depends on GitHub Actions being enabled.

## Research model operations (developer foundation)

`research_db.py` contains tested operations; `scripts/research.py` is a developer CLI, not a user-facing recording feature. Use a separate `ANTHURIUM_ATLAS_DB` for experiments. Example synthetic fixtures:

```sh
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py accession '{"id":"demo-a","label":"Synthetic accession A","taxon_id":"10999"}'
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py accession '{"id":"demo-b","label":"Synthetic unresolved label"}'
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py plan '{"id":"demo-plan","maternal":"demo-a","paternal":"demo-b"}'
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py attempt '{"id":"demo-attempt","plan":"demo-plan","when":"2026-01-01"}'
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py outcome '{"id":"demo-fruit","attempt":"demo-attempt","stage":"fruit set","when":"2026-02-01","result":"observed","notes":"Synthetic fixture, no hybridity established","numerator":1,"denominator":2,"unit":"inflorescences"}'
ANTHURIUM_ATLAS_DB=data/sandbox.sqlite3 python3 scripts/research.py pedigree demo-a
```

Use explicit SQLite records for pollen lots, cited pedigree edges and nullable genomic measurements. These developer-level entities are not a complete end-user editing system. No field data is sent anywhere.

## Tests

```sh
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.js
```

Node 18+ is required only for the frontend unit tests. See `QA.md` for browser coverage and limitations; `ARCHITECTURE.md` for schema and inference rules. Code: MIT. Data: source-specific terms in `DATA_LICENSES.md`.

## Collector-focused coverage and inference

The planner highlights curated collector topics: papillilaminum, Blue Pap, FS/RL/FSRL/RLFS, NSE Red Crystallinum and Tezula lines. These are navigational topics, not a measured popularity ranking. Ten source-specific label assertions preserve separate labels and provenance; they never authenticate an accession or become taxonomic synonyms. The current corpus contains 24 report/claim families plus 22 historical formula groups. Blue Pap remains an unresolved trade identity, but the attributed Happiest Plants report records Blue Pap as seed parent and the intact BVEP × Dorito Portillae hybrid as pollen parent. That seller-reported nested event does not authenticate identity or establish a direct Blue Pap × BVEP cross; it remains excluded from the inference graph.

Pair assessment follows the researcher-authored cited rules in `research/inference_rules.md`. It returns a structured tier, evidence motifs, selected endpoint, gaps, source origins and next check. This release uses documented direct outcome, exploratory inferred trial, or insufficient basis; it does not award “promising” or calculate probabilities. Negative/role constraints can coexist with a tier. Source rows are not independent trials. Separate future hypothesis/fertility tables keep predictions apart from observations. Published numerical crossing tables were not imported from OCR; accession-level page verification remains necessary.

### Access-limited open-pollination literature

The scherzerianum/wendlingeri report links Kamemoto & Sheffer (1978, [HortScience DOI](https://doi.org/10.21273/HORTSCI.13.2.177)) and their 1982 Aroideana account ([IAS index](https://www.aroidsociety.org/aroideana/search/scripts/flex_index.php?genus=Anthurium)) as one report family, not two independent experiments. Access was limited to primary-source search indexes/abstracts; full methods and numerical tables were not inspected. The indexed 1982 abstract identifies scherzerianum as the seed mother in open pollination, with wendlingeri an attributed, unconfirmed pollen parent. The reversed title order does not establish a reciprocal cross. The 1978 qualitative F1-fertility statement remains an unverified-method claim, not verified functional fertility. This report is searchable but excluded from inference-graph support. Publication spelling `wendlingerii` is preserved alongside WCVP's `wendlingeri` without creating a new taxonomic synonym. See `research/published_open_pollination.json` for access notes and factual provenance.


### Clarinervium grower reports

Two primary grower pages are retained as factual paraphrases in `research/clarinervium_grower_reports.json`, reviewed 2026-11-17. [Lutz Botanicals (11 October 2024)](https://lutzbotanicals.com/2024/10/11/anthurium-clarinervium-x-forgetii-pollination/) narrates forgetii seed × clarinervium applied pollen, despite the title's reversed order. Seeds and seedlings are reported, but the author questions their hybrid identity; this is excluded from successful-cross inference. [Steve's Leaves](https://stevesleaves.com/collections/aroids/products/anthurium-crystallinum-magnificum-x-clarinervum) reports seedlings hybridized in-house by Ryan Wilhelm from a crystallinum × magnificum hybrid and clarinervium. The hybrid remains one compound parent and roles remain unknown. Neither report establishes genetic parentage, reciprocal success or fertility; no photos or descriptive prose are reproduced. The URL's `clarinervum` spelling is preserved, while the stated species component aligns with accepted `clarinervium` without assigning parental direction.


### Public seller reports

`research/palmstreet_seller_reports.json` preserves two public DannyGardner listings, reviewed 2026-11-17, with unknown event dates: [Besseae aff. × FSRL × BVEP 'Felix' sprout](https://palmstreet.app/product/9Dqkhuap4sf8OKEzFtSts/anthurium-besseae-aff-x-fsrl-bvep-sprout) and [Mr.Worldwide × Ralph Lynam self germinated seed](https://palmstreet.app/product/neTixnDTjXUOHsdoErJkA/anthurium-mrworldwide-x-rl-self-papillilaminum-wide-sinus-germinated-seed). Exact source-qualified parent labels are searchable; affinity, compound and trade identities remain unresolved. Seller, parent-origin and sourcing attributions are distinct. The second listing's mention of Seth Schweers is inspiration only, not a separately observed event. Germination and a newly sprouted seedling remain different endpoints; neither establishes adult phenotype or fertility. No personal plant identification, taxon-level inference edges, photos, reviews, shipping data or automated Palmstreet crawling are included.


### Vegetative-clone pedigree claim

The [Plant.ess listing](https://plantsbytess.com/products/anthurium-clarinervium-papillilaminum-rvdp-clarinervium-variegated-clone), reviewed 2026-11-17, offers one rooted, one-leaf vegetatively propagated clone under `(Clarinervium × Papillilaminum) × (RVDP × Clarinervium)`, explicitly not seed-grown. `research/vegetative_clone_claims.json` preserves the nested seller formula, unknown crossing dates and unknown roles at every level. RVDP's expansion to Red Vein Dark Phoenix is source-specific, not an authenticated lineage or global alias. The claim establishes no observed sexual cross, intermediate hybrid success, pure-species edge, personal-specimen identity, phenotype causation, variegation inheritance or fertility. No images or marketing prose are reproduced.


### Source-attributed Blue Pap report

The [Happiest Plants description](https://happiestplants.com/products/anthurium-papillilaminum-blue-x-bvep-x-dorito-portillae), reviewed 2026-11-17, reports small seedlings from seeds acquired from Eddy Pranoto at a Bangkok show. It names Blue Pap as mother and the entire BVEP × Dorito Portillae hybrid as pollen donor. `research/happiestplants_seller_report.json` retains this as seller-attributed breeder information, not breeder-direct confirmation. Only the outer roles are stated; internal roles and crossing dates remain unknown. BVEP/Antolakii wording does not establish synonymy, and Blue Pap remains an unresolved trade identity. Exact-label search now finds this report without assigning a species or connecting it to a user's plant. There is no direct Blue Pap × BVEP edge, authenticated lineage, adult outcome or fertility claim; graph eligibility remains zero.


### Rochani registration

`research/rochani_registration.json` cites the official Indonesian Agriculture 2023 bulletin, printed pages 25–26 (PDF zero-index 28–29): registration **1028/PVHP/2023**, dated **31 May 2023**, publication **140/BR/PVHP/05/2023**. Rochani's origin is reported as **veitchii GCI 002 female × forgetii male**. Plant and inflorescence descriptions support a reported grown/flowering endpoint. Species resolve to WCVP for retrieval, while the maternal accession and source-qualified identity remain explicit. Consistent with other explicit flowering reports, it may support traceable exploratory analogies; it does not authenticate other accessions, demonstrate independent controlled replication, establish DNA parentage, or imply germination rates, functional fertility or reciprocal success. Only factual paraphrases and the source link are included, not the PDF or its images.


### Repository publication status

The source repository is published at [dylanswartz/anthuriums](https://github.com/dylanswartz/anthuriums). The initial published `main` commit `e61cf7b745a92be0e0992b2490dd4469003ae117` has the same tree (`3b6dea08d259e95a39e01e9ca18164c6588fe946`) as local release `5beb8ee3dabe6926b2d4ba11cf324c6f36743c33`. Publishing source code does not deploy or host the application. The documented local run command remains the way to run it. Both scheduled workflow definitions are on the default branch; no completed run has been verified, and candidate artifacts still require review before promotion.
