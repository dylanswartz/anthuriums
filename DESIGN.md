# Anthurium Atlas — botanical observatory

## Product and scope

Anthurium Atlas is a botanical editorial publication that behaves like a precise late-1970s research instrument. The experience should feel expensive through proportion, typography, restraint and reliable evidence—not decoration or a false sense of scientific certainty.

The landing task is **Find a pollen parent**: search a name, accession or alias, inspect the identity resolution, then read reported pairings. Seed-parent discovery and pair comparison remain available. This release has no accounts, inventory, journal, personal notes or pollen-log interface. Those future models remain internal.

## Visual principles

- **One calm question at a time.** Search is immediately useful. A concise heading and one paragraph orient the reader; a large ornamental hero never delays the first interaction.
- **Botanical editorial, not a trading dashboard.** Serif botanical names and headings provide character; open space, fine rules and quiet index numbers provide structure. No KPI clutter, glass walls, gold gradients or likelihood meters.
- **Evidence, not color, establishes meaning.** Every status has a text label. Sage indicates navigation and emphasis, never crossing success. A hypothesis cannot look like a documented outcome.
- **No simulated specimens.** No stock or generated photograph is presented as a real plant or hybrid phenotype. The atlas's abstract line motif is decorative botanical illustration, not scientific specimen evidence.
- **Offline and respectful.** System fonts, local assets and no analytics or remote font calls. Source photographs and prose are not borrowed to create polish.

## Color tokens

| Purpose | Token | Value |
|---|---|---|
| Canvas | `--bg` | near-black olive `#101411` |
| Surface | `--panel` | deep botanical green `#161D18` |
| Rules | `--edge` | muted slate-green `#354039` |
| Primary type | `--text` | warm paper `#ECE9DD` |
| Secondary type | `--muted` | soft green-gray `#AAB7AC` |
| Active controls | `--green` | sage `#A6B6A4` |
| Context and uncertainty | `--amber` | pollen ochre `#D8B56D` |
| Adverse evidence | caution border | terracotta `#D99C89` |

Use one-pixel borders and 16px card/surface radii. Input corners are 10px; topic chips may be pill-shaped. Avoid large shadows; a subtle shadow may separate sticky mobile controls from scrolling content.

## Typography

Georgia with serif fallbacks carries page titles and botanical names. Regular-weight desktop titles are approximately 50px, reduced to 39–42px on small screens; use restrained negative tracking. Botanical names in evidence cards are approximately 22–23px italic with generous line height.

System sans carries body text and controls at **16px or larger**. Secondary readable copy, labels, source links and evidence statuses are **14px or larger**. Line height is 1.6–1.75. Small monospace is reserved for nonessential field-index metadata, quiet dates/accession identifiers and instrument-like navigation numbering; it is not the main reading voice. Large formulas and long names wrap naturally.

## Layout

Design from a 390px-wide screen with 20px gutters and an 8px spacing rhythm. Primary touch targets are at least 44px tall. Navigation becomes a horizontally scrollable labeled row. Parent controls stack and remain available while evidence scrolls; no fixed-height cards truncate scientific text. Tables scroll within their own containers rather than widening the page.

At desktop widths, a compact left rail and thin contextual masthead frame a maximum 1200px reading column. Parent and role controls sit alongside one another. Use 24–48px spacing between major sections. A low-contrast coverage strip belongs to the atlas view, not the task-focused landing page. Empty states receive useful explanation, not decorative filler.

## Information and evidence hierarchy

1. **Chosen parent and identity.** Accepted WCVP species, source-specific label assertion, or unresolved identity. An alias assertion does not silently replace an input or authenticate a clone.
2. **Recorded relationships.** Exact parent labels, seed/pollen role when recorded, narrow reported endpoint, evidence type, citation and source date. Unknown direction explicitly says **not established**.
3. **Related collector-line context.** FS/RL, FSRL/RLFS, RC and complex-line reports remain separate from exact-species and exact-role matches. Collector shortcuts are curated navigation, not a measured popularity ranking.
4. **Historical formulas.** Nomenclature-only records remain visibly separate and cannot support the observed-outcome graph.
5. **Structured assessment and exploratory hypotheses.** Expose target endpoint, direct-match scope, edge IDs/sources, parent-role and identity gaps, cytology gaps, counterevidence and next checks. Connectedness is not compatibility. No calibrated probability or “promising” tier is claimed.

## Evidence-card interaction

Keep evidence type, direction, parentage, endpoint, source and the identity/fertility qualifier visible. Use a native inline `details`/`summary` disclosure for full provenance, raw source spelling/formula and longer limitations. No drawer or modal is needed. Disclosure labels must be keyboard-operable and at least 44px tall on touch layouts.

Positive and adverse evidence coexist. Display a visible constrained/conflicting notice and the relevant negative reports or accession-role limitations; do not average them into a reassuring score. If no role constraints were applied, explicitly state that the plants' sexual function has not been verified. Source URL counts are not independent-study counts.

## Accessibility

Use semantic landmarks and table headings; real input labels; visible keyboard focus; skip navigation; native controls; text labels beyond color; and natural document reading order. Search updates do not steal focus. Essential uncertainty is never hover-only. Respect reduced motion and avoid unnecessary animation. Escape imported content and keep external links attached to a specific citation.

## Acceptance and verification

Review the actual running application in the supported browser: pollen-parent landing, species search/detail, unresolved Blue Pap, FS/Fort Sherman, distinct FSRL/RLFS reports, reciprocal separation, structured assessment, and collapsed/expanded evidence cards. Confirm the visual refinement does not hide a source or scientific qualifier. Test a narrow viewport where supported and document any coverage limit honestly.

The current desktop observatory design and interactions have been visually checked in the supported browser. Mobile CSS implements the 390px-first rules; device-sized visual QA is not claimed unless separately recorded in `QA.md`.
