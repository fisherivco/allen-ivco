# Direction A: research press

**Idea:** IVCO as a publication. The brand line is the masthead, set at 96px; everything else is quiet reading furniture.

## Palette
| Name | Hex | Use |
|---|---|---|
| Paper | #EEF0EC | page |
| Paper 2 | #E3E7E1 | scrollbar track |
| Ink | #15202B | text, heavy rules |
| Ink 2 | #3B4753 | secondary text (9.6:1 on paper) |
| Rule | #B7BEB8 | hairlines |
| Moss | #2F5A4A | last two brand sentences |
| Claret | #7E2530 | hover and focus only |

## Type
- Newsreader (serif): headings and body. Body 18px/1.62, article 19px/1.68, measure 38rem (about 65 characters).
- Hanken Grotesk (sans): dates, navigation, contents.
- Scale: 14, 18, 22, 28, 40, 68 px, plus 96px for the masthead statement.

## Layout and spacing
Left aligned. Home: statement, then a 7/5 grid (lead article, list of the other six). Article: deck, byline, then a 15rem contents column beside a 38rem text column. Spacing steps 8, 16, 32, 64px; more space above headings than below. Below 52rem everything stacks.

## Detector findings (npx impeccable@4.10.0 detect --json)
- `index.html` cramped-padding (warning): the detector flags the list column that has a 1px left divider. Its content has 2rem left padding. False positive; left as is.
- `post.html` em-dash-overuse (advisory) and aphoristic-cadence (warning): both come from the published article text, reproduced unchanged. Copy is the author's; not rewritten in a design proposal.
