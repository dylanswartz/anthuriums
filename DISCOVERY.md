# Repeatable discovery, separate from authority

Grower pages can surface names worth researching. Their occurrence is not a popularity measurement, verified specimen identity or evidence of cross viability. This pipeline stages candidate names for human review, then performs an exact-name lookup against the local WCVP snapshot. It never writes the trusted taxonomy, cross, cultivar, accession or pedigree tables.

## Local curated input (default)

Create a JSON list with factual labels and provenance. This example is a synthetic illustration, not a report about a real supplier:

```json
[
  {"name":"Anthurium crystallinum","source_url":"https://example.org/curated-example","observed_on":"2026-11-17"},
  {"name":"Unresolved trade label","source_url":"https://example.org/curated-example","observed_on":"2026-11-17"}
]
```

Run `python3 scripts/discover_names.py --local-input /path/to/candidates.json`. Names, source URL/date, input checksum, WCVP version/status and resolution are stored in a checksum-addressed JSON file under `data/discovery/`. Every candidate remains `pending`; popularity is null. Only an exact canonical or synonym match can suggest a WCVP accepted name. It does not authenticate the plant. Misspellings, commercial abbreviations, clone codes, generational labels, compound formulas and trade labels remain unresolved; no fuzzy species substitution occurs.

## Explicit permitted-source configuration

`config/discovery-sources.json` ships disabled with an empty allowlist. Before enabling it, review each source's current terms and permission. Example source shape (placeholder only, not enabled):

```json
{
  "id":"reviewed-source",
  "url":"https://example.org/permitted-names.json",
  "terms_url":"https://example.org/terms",
  "terms_reviewed":true,
  "permission_note":"Document the actual permission and date reviewed here.",
  "format":"json_names"
}
```

`json_names` accepts `{"names":["Anthurium crystallinum"]}`. `html_names` extracts only narrow Anthurium binomial candidates from visible text. The HTML is not persisted, no descriptions/images are copied, and no arbitrary links are followed. Cultivar and complex labels should use local review or an explicitly permitted JSON names source rather than a guessing parser.

Use `python3 scripts/discover_names.py --source-config config/discovery-sources.json --network` only after configuring permission. The code validates every source before requesting any page, checks robots, blocks explicit disallow, treats 404/410 as absent policy, fails closed on other robots errors, refuses redirects, and limits source count and response size. Requests use exact configured URLs; no recursive crawling. Default limits are five pages and 500 kB/page; hard caps are ten and 1 MB. Source terms are not inferred from robots permission. An absent robots file does not establish reuse rights.

## Schedule and review

`.github/workflows/name-discovery.yml` defines Mondays at **07:43 UTC**, plus manual dispatch. The workflow and schedule trigger are now published on the repository default branch. Execution requires GitHub Actions enabled; no completed scheduled run has been verified. With the shipped configuration, it stages a disabled/no-requests receipt. It will not discover anything until an owner configures reviewed, permitted sources. The workflow is read-only and uploads pending artifacts; it never commits, pushes or promotes candidates.

Review candidate identity, source provenance, actual demand/popularity evidence (if any), and any scientific claims separately. A candidate can be rejected or researched further without modifying WCVP. Explicitly curated evidence updates use the separate local import process and source-specific rights review described in README.

## Pending research dossier

`research/breeder_skg_tezula.json` retains exact breeder/supplier labels and source rights limitations. The two explicitly reported Tezula Dreamweaver ↔ Tezula Necromancer directions are included in the live explorer as attributed grower reports, without taxon substitution. Their outcomes are pooled; no per-direction success rate or fertility is inferred. The other selfing/Carnivero/identity-note entries remain a **pending-review dossier**, not live trusted cross cards. Source-labeled `debilis` is not silently changed to `debile`. No images or article text are included. The live collection contains sixteen curated reports plus 22 historical formula groups.

## Enforced source policy and request pacing

Automated requests to `granthuriums.com`, `nsetropicals.com`, `carnivero.com` and every subdomain are prohibited by the reviewed terms, even if mistakenly placed in an enabled allowlist. Local factual citations remain permitted. This restriction is checked for every source before any network request.

`min_interval_seconds` defaults to five seconds globally and can be raised per source. The effective origin-wide interval is the maximum of the global/source minimum, robots `Crawl-delay` and the seconds-per-request implied by `Request-rate`. All requests, including the initial robots retrieval, count toward pacing; robots policies are cached per origin within a run, and each configured page is independently checked for path permission. Decimal crawl delays are supported. Malformed timing directives fail closed. The strictest timing directive in the file is conservatively honored even across agent groups. Concurrent discovery invocations are not coordinated; run one job at a time. Scheduled runs are weekly and bounded, not continuous crawlers.
