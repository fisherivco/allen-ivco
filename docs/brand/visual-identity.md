# IVCO Visual Identity

Canonical visual identity for IVCO and the IVCO Fisher persona, derived from design direction B ("analyst workbench"). This document is the basis for all brand visual development from 2026-11-25 onward (owner ruling, §8).

Source of truth: `design-proposals/ivco-2026-11/b/` (`index.html`, `post.html`, `DESIGN.md`). Nothing here is invented; where this doc and the templates ever differ, the templates win and the doc is corrected in the same change.

## 1. Positioning and angle of expression

- **IVCO = Intrinsic Value Confidence Observatory.** An observatory, not a trading floor: it watches, measures, and publishes. It does not trade, predict, or advise.
- **Persona:** IVCO Fisher — named for Philip Fisher; archetype Li Lu (quiet, long-term, non-trader). Public voice of the system; American English. Fisher is the brand outward; the rigor behind it is internal.
- **Brand line** (exact, from the B home page h1): "I don't predict markets. I study businesses. Noise fades. Facts compound." The persona document extends it: "Intrinsic value is a starting point — not a prophecy."
- **Stance:** intrinsic value is a range backed by a confidence coefficient, never a single number. The first viewport shows the valuation range before a word of method. Only published numbers appear on the page; the instrument displays the published TSMC case and does not compute an IV.
- **Angle:** the reader is shown the instrument first — "the reader sees that value is a range before reading a word" (b/DESIGN.md). Analysis is presented *as published*, with the evidence that earned it.

## 2. Colour system

A dark, instrument-like palette: graphite surfaces in three tonal steps, one warm accent for value, one cool accent for links, and a four-step teal ramp reserved for the Confidence Coefficient tiers.

| Token | Hex | Role |
|---|---|---|
| Graphite | #0E1317 | Page background |
| Panel | #151C22 | Panels, top bar, table-row hover |
| Panel 2 | #1C252D | Inset wells: range track, readouts, selector labels, formula blocks |
| Line | #2B3740 | Borders and separators only |
| Text | #E4EAEE | Primary text |
| Muted | #9BA9B4 | Secondary text, metadata, navigation |
| Amber | #F0B34A | The range, value figures, focus, selection, checked state, link hover |
| Teal | #5CC8B6 | Links (resting state only) |
| On-amber ink | #14100A | Text on amber: `::selection`, focused skip link |
| Scrollbar | #3A4853 | Scrollbar thumb on Graphite |
| CC tier ramp | #3A4A57 / #2E6F73 / #3C9A94 / #8FD3C4 | Conservative / Steady / Aggressive / Extreme swatches |

### Text contrast pairs (WCAG 2.x ratios, recomputed)

Every text/background pair used in B. All pass WCAG AA (4.5:1) and AAA (7:1) for normal text except the two muted-on-dark pairs, which pass AA.

| Foreground | Background | Used for | Ratio |
|---|---|---|---|
| #E4EAEE | #0E1317 | Primary text on page | 15.39:1 |
| #E4EAEE | #151C22 | Text on panels and top bar | 14.17:1 |
| #E4EAEE | #1C252D | Text in inset wells (readout values, formula, selector options) | 12.80:1 |
| #9BA9B4 | #0E1317 | Secondary text and metadata on page | 7.76:1 |
| #9BA9B4 | #151C22 | Secondary text on panels; nav links on top bar | 7.15:1 |
| #9BA9B4 | #1C252D | Labels inside inset wells (readout terms) | 6.46:1 |
| #F0B34A | #151C22 | The IV range figure on the panel | 9.21:1 |
| #F0B34A | #0E1317 | Link hover; spec-table result row on page | 10.01:1 |
| #5CC8B6 | #0E1317 | Links on page | 9.24:1 |
| #14100A | #F0B34A | Selected text; focused skip link | 10.15:1 |

### Non-text surface pairs (reference; not text-bearing)

| Foreground | Background | Used for | Ratio |
|---|---|---|---|
| #F0B34A | #1C252D | Range band on its track | 8.32:1 |
| #2B3740 | #0E1317 | Hairline borders on page | 1.53:1 |
| #2B3740 | #151C22 | Hairline borders on panels | 1.41:1 |
| #3A4A57 | #151C22 | Conservative tier swatch on panel | 1.88:1 |
| #2E6F73 | #151C22 | Steady tier swatch on panel | 2.98:1 |
| #3C9A94 | #151C22 | Aggressive tier swatch on panel | 5.11:1 |
| #8FD3C4 | #151C22 | Extreme tier swatch on panel | 10.06:1 |
| #3A4853 | #0E1317 | Scrollbar thumb on page | 1.99:1 |

### Colour rules

- **Amber is spent, not sprinkled.** It marks the range band, the IV figure, focus rings, text selection, the checked selector option, and link hover — never body copy, headings, or decoration.
- **Teal is links only.** Resting state teal, hover amber. No other element uses teal.
- **The tier ramp never carries text.** Tier names and numeric ranges are printed in the legend next to each swatch, so colour is never the only code. Terminate has no swatch: it is stated as N/A beside the ramp, never drawn on it.
- **Depth is tonal, not shadowed.** Three surfaces only: Graphite < Panel < Panel 2. No drop shadows, no gradients.
- **Muted is the floor.** No text is set dimmer than Muted on its defined surfaces.

## 3. Typography

Two families, loaded at the used weights only (`IBM Plex Sans` 400/500/600, `IBM Plex Mono` 400/500, `display=swap`).

| Role | Stack | Weights | Used for |
|---|---|---|---|
| Sans | "IBM Plex Sans", system-ui, sans-serif | 400, 500, 600 | All headings, body, UI copy |
| Mono | "IBM Plex Mono", ui-monospace, Menlo, monospace | 400, 500 | Figures only: ranges, CAGR, CC values, dates, lengths, formulas, spec-table values |

- **Numeric style:** `.num` = mono + `font-variant-numeric: tabular-nums`. Every number on the page — IV range, percentages, dates, read lengths — is set in tabular mono so columns and digits align.
- **Scale (b/DESIGN.md):** 13, 15, 17, 22, 26, 52 px. Component truth from the CSS: hero h1 52px/1.08 at 600 with −0.025em (36px ≤56rem); article h1 44px (32px ≤56rem); articles-table head 22px; prose h2 24px; prose h3 19px; panel h2 17px; lede / title links / deck 17px; readout values 18px; nav, byline, sub, formula, spec values 15px; body 16px/1.6; article prose 17px/1.7; metadata (table head, terms, legend, notes, tags) 13px; row meta and footer 14px; range readout clamp(24–36px).
- **Measure:** article text column 44rem; title excerpts capped at 46rem; lede at 30rem.
- **Wrapping:** `text-wrap: balance` on h1–h3; `-0.025em` tracking on display sizes only.
- **Rule:** mono is for numbers. Never set prose in mono; never set a figure in sans.

## 4. Layout and components

- **Shell:** 80rem max-width, left-aligned, horizontal padding `clamp(1rem,3vw,2rem)`; a 12-column feel, not a centered marketing canvas.
- **Spacing scale:** 8 / 16 / 24 / 48 px steps.
- **Radius:** 10px panels, 6px wells and selector options, 4px track and tier bars, 999px tag pills. Hairline borders in Line on every panel and row.
- **Header bar:** Panel background, 1px Line bottom border. Brand mark = range-bar glyph (amber bar between two muted end ticks) + "IVCO Fisher". Nav: muted links, current/hover in text colour.
- **Home hero:** 5fr / 7fr grid — brand line plus one lede sentence on the left, the TSMC instrument panel on the right.
- **Valuation panel** (the signature component):
  - *Range readout:* amber mono figures "NT$4,565 - NT$5,639" with muted label "intrinsic value per share".
  - *Range bar:* 28px Panel 2 track; amber band spanning the full track; endpoints repeated in mono below.
  - *CC tier bar:* 34px segmented strip (9% / 23% / 45% / 23% = Conservative / Steady / Aggressive / Extreme) titled "Numeric Confidence Coefficient tiers", with a legend of 10px swatches plus tier names and mono ranges; Terminate noted as N/A in text.
  - *Two-position selector:* a fieldset of two radio wells on Panel 2; checked = amber border and amber accent. The positions are the published Steady pairs "1.2x / 21.19%" and "1.5x / 26.49%".
  - *Readout:* two-column definition list on Panel 2 wells — Historical CAGR (fixed at the published 17.66%) and Adjusted CAGR (updated by the selector).
- **Articles table:** columns Article / Type / Published / Length. Title links in text colour, amber on hover. Type as an outlined pill tag (Framework, Case Study, Opinion, Brand Story). Published and Length in muted mono. Row hover = Panel background. Muted hairline rules between rows.
- **Post layout:** 17rem sticky left rail (TSMC inputs definition list + "In this article" contents) beside a 44rem article column. Breadcrumb "Articles / Framework", deck block on Panel, prose at 17px/1.7, formula blocks in mono on Panel 2, spec tables with right-aligned mono values and an amber result row.
- **Mobile at 390px (≤56rem breakpoint):** all grids stack to one column; hero h1 36px, article h1 32px; the rail unsticks; the articles table collapses to stacked rows (header hidden, cells block, meta inline); panel padding 16px; readout values 16px. No sideways scrolling.
- **Accessibility furniture:** skip link (amber when focused), `:focus-visible` 2px amber outline with 3px offset, amber selection with dark ink, `role="img"` + `aria-label` on the range bar and tier strip, tinted scrollbar.

## 5. Presentation rules

- **Data honesty:** every figure on a page is a published figure. The panel shows the published TSMC case only — historical OE CAGR 17.66% (2013–2022), the two published Steady pairs 1.2x / 21.19% and 1.5x / 26.49%, and the published IV range NT$4,565 - NT$5,639. 17.66% is the historical baseline; there is no 1.0x adjusted scenario. The instrument displays published results; it does not compute.
- **Case study presentation:** titled "TSMC case study, as published" with the method line "Owner Earnings CAGR 2013 to 2022, three-stage DCF"; the articles table marks it Type = Case Study.
- **CC display:** numeric tiers drawn as a ramp titled "Numeric Confidence Coefficient tiers"; Terminate is stated separately as N/A — never drawn as a tier.
- **Motion:** one moment only — the range band draws in on load (1.1s, `cubic-bezier(.16,1,.3,1)`). Nothing else animates. Disabled under `prefers-reduced-motion`.
- **What B deliberately avoids:** single point estimates; sliders or any control implying an arbitrary continuous CC; unpublished scenarios; blanket claims about "each IVCO valuation" (replaced by the published example during review); decorative colour, shadows, gradients, card chrome, and hero imagery.

## 6. Voice and copy

- **Tone:** first person, quiet, plain, evidence-first; conviction stated with its evidence, never as a claim. Confession-then-method rhythm: "Here's a confession: I used to love spreadsheets that spit out one number."
- **Register:** short declarative sentences; questions answered immediately. Example: "The forward-looking question: what CC do we assign?"
- **Words used:** range, evidence, published, conviction, integrity, historical, track record, adjustment, case study, "as published". Framework vocabulary is always capitalized as named concepts: Owner Earnings, Reality Coefficient, Confidence Coefficient, Three-Stage DCF.
- **Words and frames avoided:** predictions, targets, advice, disclaimers ("Not investment advice" was removed in review), hype superlatives, trading-floor language (calls, signals to act, buy/sell), and generalized claims about "each IVCO valuation".
- **Numbers are ranges or labelled points:** "NT$4,565 - NT$5,639", "1.2x - 1.5x" — a bare point estimate appears only as the anti-example inside an article ("TSMC is worth $487.32 per share." — quoted as what IVCO does not do).
- **Labels are nouns:** Workbench, Articles, Framework, Case Study, Opinion, Brand Story.
- **Footer:** "© 2026 IVCO Fisher" — nothing else. No tagline, no disclaimer, no link farm.

## 7. Do / don't

| Do | Don't |
|---|---|
| Show intrinsic value as a range: "NT$4,565 - NT$5,639" | Show a single point estimate ("worth $487.32 per share") |
| Spend Amber on value figures, focus, selection, checked state | Use Amber on body copy, large fills, or decoration |
| Set every number in Mono with tabular figures | Set figures in Sans, or prose in Mono |
| Teal links, Amber hover | Any other link treatment |
| Title the tier chart and name each tier in the legend | Let ramp colour alone carry tier meaning |
| State Terminate as N/A beside the ramp | Draw Terminate on the numeric ramp |
| Offer only published CC pairs in the selector | Offer a free slider or an unpublished scenario |
| Ship the footer as "© 2026 IVCO Fisher" alone | Add disclaimers, taglines, or link lists to the footer |
| Animate the range band once on load | Scatter fades, slides, or scroll effects |
| Layer Graphite / Panel / Panel 2 with hairline borders | Add shadows, gradients, or card-in-card chrome |

## 8. Provenance

- **Source files:** `design-proposals/ivco-2026-11/b/` — `DESIGN.md`, `index.html`, `post.html`, `detect-index.json`, `detect-post.json` — merged via PR #5 (head `79bed2b458084550fc12595e0ccf63bda107b6c0`, merge commit `f2fcf8fbdb08bd6f738fc29453255859f0b9df4e`, merged 2026-11-25).
- **Decision:** owner ruling 2026-11-25 (issue #4, verbatim): 「B, 並寫入 IVCO 相關文件中，接下來依這個為基礎進行品牌視覺發展，品牌色碼、風格、呈現方式、表達角度都要詳細記錄，同時這兩個範本也要保留下來在 repo 中，未來可回頭審視」. Direction A is kept in `design-proposals/ivco-2026-11/a/` for later review and is not normative.
- **Review history (issue #4 / PR #5):** T3 round 1 verdict REVISE at head `1ef0b5a`. The oracle required, and the builder applied: the "Numeric Confidence Coefficient tiers" label; the two-position selector of published pairs replacing a continuous slider; removal of the unshown 1.0x scenario with 17.66% kept as the historical baseline only; the published footer; restored inline source links; repo-relative detector file paths. Round 2 was an oracle correction only (number and link verification widened to the live ivco.ai site; the investor.tsmc.com link passes on destination identity, not HTTP status). Closed PASS at `79bed2b` on independent verifier evidence and merged.
- **Detector findings** (`npx impeccable@4.10.0 detect --json`): `b/index.html` none; `b/post.html` em-dash-overuse (advisory) and aphoristic-cadence (warning) — both originate in the published article text reproduced unchanged; copy is the author's and is not rewritten in a design proposal. Reasons recorded in `b/DESIGN.md` and `b/detect-post.json`.
