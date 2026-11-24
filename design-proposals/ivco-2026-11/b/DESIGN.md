# Direction B: analyst workbench

**Idea:** IVCO as an instrument. The first screen shows the valuation range and a Confidence Coefficient slider, so the reader sees that value is a range before reading a word.

## Palette
| Name | Hex | Use |
|---|---|---|
| Graphite | #0E1317 | page |
| Panel | #151C22 | panels |
| Panel 2 | #1C252D | inset wells, slider readouts |
| Line | #2B3740 | borders |
| Text | #E4EAEE | text |
| Muted | #9BA9B4 | secondary text |
| Amber | #F0B34A | the range, focus, selection |
| Teal | #5CC8B6 | links |
Tier ramp on the CC scale: #3A4A57, #2E6F73, #3C9A94, #8FD3C4 (each tier is also named in the legend).

## Type
- IBM Plex Sans: headings and body (body 16px/1.6, article 17px/1.7, measure 44rem).
- IBM Plex Mono: figures only (ranges, CAGR, dates), tabular numerals.
- Scale: 13, 15, 17, 22, 26, 52 px.

## Layout and spacing
Left aligned, 12-column feel on an 80rem shell. Home: brand line and one sentence on the left, TSMC instrument panel on the right, then the seven articles as a table (type, date, length). Article: sticky left rail with the TSMC inputs and contents, 44rem text. Spacing steps 8, 16, 24, 48px. Below 56rem the grid stacks and the table becomes stacked rows.

## Data
All numbers come from the published TSMC article: CAGR 17.66%, CC 1.2x to 1.5x, adjusted CAGR 21.19% to 26.49%, IV NT$4,565 to NT$5,639. The slider only computes adjusted CAGR = 17.66% x CC, the formula in the article. It does not compute an IV.

## Motion
One moment: the range bar draws in on load. Disabled under prefers-reduced-motion.

## Detector findings (npx impeccable@4.10.0 detect --json)
- `index.html`: none (exit 0).
- `post.html` em-dash-overuse (advisory) and aphoristic-cadence (warning): both come from the published article text, reproduced unchanged. Copy is the author's; not rewritten in a design proposal.
