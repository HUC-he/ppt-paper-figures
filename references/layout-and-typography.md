# Layout and Typography

Read this file when choosing canvas size, panel grid, fonts, or palette.

## Final print width decides everything

Set the slide aspect to the aspect of the printed figure, so nothing is rescaled at export.

| Use | Typical width | Notes |
|---|---|---|
| Single column | 85 to 90 mm | small panels, one or two |
| Double column | 170 to 180 mm | the default for a multi-panel figure |
| Full page | 180 mm wide, up to 240 mm tall | only when the figure carries the paper |

Divide the final width by the slide width to get the print scale factor. A 180 mm figure built on a
13.33 in wide slide prints at about 0.53 scale, so a 10 pt label in the deck lands near 5.3 pt on
paper. This is the reason a figure that looks comfortable on screen fails the font gate.

Work backwards from the target: decide 7 pt final for labels, divide by the scale factor, and set
that size in the deck. If the arithmetic forces deck text above about 14 pt, the figure is carrying
too much at that width.

## Grid

Choose the grid before placing anything.

- Two by two and one by three are the workhorses. Beyond four panels, expect a reader to lose the
  order, and expect letters and arrows to collide.
- Gutters 3 to 5 mm at final size, at least twice the widest outline in the figure.
- One outer margin, the same on all sides, never less than 2 mm at final size.
- Panels that carry equal weight get equal size. Do not mix a dominant panel with three thumbnails
  unless the claim actually ranks them.
- Reading order left to right, top to bottom. Panel letters follow that order and sit in the same
  corner of every panel.

## Typography

| Element | Font | Size at final print |
|---|---|---|
| Panel letter | Arial bold | 8 to 10 pt |
| Axis label, ingredient name | Arial | 7 to 8 pt |
| Body or caption inside the figure | Arial | 7 pt |
| Footnote, scale value, citation tag | Arial | 5 to 6 pt |
| Chinese text | SimSun on Windows, Songti SC on macOS | match the Latin size |

Never mix two Latin families in one figure. Never render a label as part of an image. Never use
italic for emphasis in a technical label; italic is reserved for variables, genes, and species
names, and for nothing else.

Units follow the journal: SI, one space between value and unit, no period after the unit, and the
same precision everywhere. If a value appears twice in one figure at two precisions, that is a
defect, not a rounding detail.

## Palette and line work

- One palette, defined once, reused across every panel and every figure in the paper.
- Prefer colourblind-safe hues, and vary shape or position as well so greyscale printing survives.
- Reserve one accent colour for the element the figure is about. If everything is accented, nothing
  is.
- Outlines 0.5 to 1.5 pt, and identical for equivalent objects. A heavier outline reads as a
  different material.
- Arrows: one style, one head size, one thickness, and always pointing from cause to effect. A
  dashed arrow means a proposed relationship, and only then.
- Scale bars are vector lines with vector numerals, opaque, and never drawn by the image model.

## Common layout failures

A panel that is mostly empty background. A legend repeated in three panels. A sub-panel whose only
wording is inside an AI image. Two arrows crossing to reach their targets. A stacked bar whose
segments exceed the axis. A colour that means one thing in panel a and the opposite in panel c.
Every one of these is cheap to fix in the deck and expensive to fix after submission.
