---
name: ppt-paper-figures
description: >-
  Assemble publication-quality scientific figures with PowerPoint as the editable vector master:
  AI generates text-free visual assets, every label, number, arrow, and citation is set as real
  vector text in the deck, then the figure is exported to PDF plus 600 dpi PNG and checked for
  overlap, font, and minimum size before delivery. Use for 论文配图, 科研绘图, 综述配图, 示意图,
  机制图, 图形摘要, PPT 拼图, 拼版, 配图质检, graphical abstract, mechanism schematic, figure
  assembly, journal figure export, PowerPoint figure workflow. For figures driven by numeric data
  use nature-figure; for prompt-only mechanism artwork with no layout control use
  biorender-mechanism-figures.
---

# PPT Paper Figures

Build a figure the way a careful author would: think about what the figure must prove, assemble it
in PowerPoint with real vector text, export it at submission resolution, then prove it is clean
before sending it anywhere.

The division of labour is the whole point. The AI makes pictures. PowerPoint makes the figure.

## Core rule

PowerPoint is the editable master. Text, numbers, units, panel letters, arrows, scale bars, and
citation tags are vector text in the deck, never pixels baked into an AI image.

Consequences worth stating out loud, because they are the usual failure:

- No AI-generated text, numerals, axis labels, or legends. Every asset is requested text-free.
- Assets are illustrations, never data. A generated image may suggest a mechanism; it may not
  depict a measured result, a real micrograph, or a value.
- Every number in the figure is traceable to the author's own data or cited source.
- Final export is vector PDF for the publisher plus 600 dpi PNG for preview and for journals that
  demand raster.

## Workflow

1. Fix the claim before the layout. Write the one sentence the figure must prove, the panel count,
   the reading order, and the evidence each panel carries. A figure that cannot state its claim in
   one sentence is two figures.
2. Set the canvas. Choose final print width and the panel grid first, and set the slide size to
   match that aspect. Read [references/layout-and-typography.md](references/layout-and-typography.md)
   for the width table, grid, gutter, and font floors.
3. Generate assets, text-free. Write one prompt per panel and keep assets separate so a bad asset
   costs one regeneration, not a rebuild. Read
   [references/asset-prompts.md](references/asset-prompts.md) for the prompt skeleton, the negative
   list, and the fake-text check.
4. Inspect every asset before it enters the deck. Regenerate or crop anything with invented
   lettering, watermark-like glyphs, mismatched lighting, or a wrong material colour.
5. Assemble and label. Place assets, then add vector text, arrows, scale bars, and panel letters
   directly in PowerPoint. Keep one text box per label so overlap QA can see it.
6. Export vector PDF and 600 dpi PNG with `scripts/export_figures.py` when LibreOffice is
   available, or through PowerPoint's own export when it is not.
7. Run the QA gate with `scripts/figure_qa.py`, fix everything it flags, then do one visual pass at
   final print size. Read [references/export-and-qa.md](references/export-and-qa.md).

## Typography and palette

- English text and numerals use Arial. Chinese uses SimSun on Windows and Songti SC on macOS;
  write the font name your target machine will resolve, and never mix two Latin families in one
  figure.
- Body text and labels: 7 pt at final print size is the target, 5 pt is the absolute floor.
  Numbers below 5 pt will be illegible in print and will be rejected in review.
- One palette per figure, colourblind-safe, and use position or shape as well as colour so the
  figure survives greyscale printing.
- Line weights 0.5 to 1.5 pt, arrows consistent in head shape and thickness, panel letters in one
  size and one position.

## QA gate

Run before delivery, every time:

```bash
python3 scripts/figure_qa.py figure.pptx --target-width-mm 180 --min-pt 5 --allow-mm2 0.5
```

It reports text-text and text-image overlaps in mm^2, font sizes measured at the final print size,
font names that are not Arial, SimSun, or Songti SC, and shapes that run outside the canvas. It
exits non-zero when a blocking problem is found, so it can gate the deliverable.

Then look at the exported PDF and PNG at final size. The script cannot see a leader line that
points at the wrong ingredient, a legend that contradicts the image, or an asset that shows the
wrong mechanism. A human pass over the export is not optional.

## Red lines

- Never let an AI asset carry text, numbers, units, or a citation.
- Never present a generated illustration as experimental data, a micrograph, or a measurement.
- Never stretch, mirror, splice, or retouch a real image in a way that changes its meaning.
- Never ship a figure whose numbers cannot be traced to the author's data or a cited source.
- Never publish a figure that failed the overlap or minimum-font gate, however good it looks on
  screen.
- Never write an API key, endpoint credential, or personal token into a prompt file, a script, or
  the deck.

## Related files

| File | Open when |
|---|---|
| [references/asset-prompts.md](references/asset-prompts.md) | Writing or repairing text-free asset prompts |
| [references/layout-and-typography.md](references/layout-and-typography.md) | Choosing canvas, grid, fonts, or palette |
| [references/export-and-qa.md](references/export-and-qa.md) | Exporting, running QA, or handling a failure |
| [scripts/figure_qa.py](scripts/figure_qa.py) | Running the overlap, font, and size gate |
| [scripts/export_figures.py](scripts/export_figures.py) | Exporting PDF and 600 dpi PNG |
| [examples/demo-qc-report.md](examples/demo-qc-report.md) | Showing what a QA report looks like |

## Handoff

`nature-figure` covers data plots from numeric data with matplotlib or R. `biorender-mechanism-figures`
covers prompt engineering for mechanism artwork alone. This skill covers the assembly, labelling,
export, and QA stages that turn a set of assets into a submission-ready figure.
