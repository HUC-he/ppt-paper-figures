# Demo QA report

Real output from `scripts/figure_qa.py` on the demo deck built by
[build_demo_figure.py](build_demo_figure.py). The deck is deliberately plain: two stand-in assets,
four labels, one panel letter per panel. What matters is the gate, not the artwork.

## Run 1: the defective deck

Injected faults: one label placed on the artwork, one label at 3.5 pt, and one label duplicating an
existing anchor.

```bash
python3 examples/build_demo_figure.py --outdir build --defect
python3 scripts/figure_qa.py build/figure-defective.pptx \
  --target-width-mm 180 --min-pt 5 --allow-mm2 0.5
```

```text
figure QA: build/figure-defective.pptx
slide 338.66 x 132.08 mm, target 180.0 mm, print scale 0.5315
shapes: 10 (text 8, pictures 2)

FAIL overlap: 2
  - text-text overlap 716.128 mm2: "1.2 kg m-2 h-1 at 1 sun" x "1.2 kg m-2 h-1 at 1 sun"
  - text-image overlap 812.902 mm2: "Photothermal layer" x "(picture)"

FAIL text below the print floor: 1
  - 1.86 pt on paper (3.5 pt in deck): "1.2 kg m-2 h-1 at 1 sun"

FAIL outside the canvas: 0

WARN font not verified: 0

WARN estimated text overflow: 0

BLOCKING
```

Exit code 1, so the gate blocks delivery. Three points worth noticing.

The 3.5 pt label is 1.86 pt on paper. On a 13.33 in slide at 180 mm print width the scale is 0.53,
which is why a size that looks readable on screen is illegible in print.

The duplicated anchor shows up as text-text overlap rather than as a judgement call. Two labels
competing for one position is exactly the mistake that survives a casual look at the deck.

The picture overlap is measured as a box intersection, so it is conservative: a label in the corner
of an asset with transparent surroundings is still flagged. Treat a flag as a prompt to look, not
as proof of a visual collision.

The duplicated label also produces the largest number in the report, 716 mm^2 of pure text on text.
A figure at 180 mm width has no room for that, and on a 13.33 in slide the two boxes are far enough
apart to look harmless at a glance in PowerPoint.

## Run 2: the clean deck

Fix: move the label out of the artwork into the band the asset reserved, delete the duplicate,
and raise the 3.5 pt run to 13 pt so it lands near 7 pt on paper.

```bash
python3 examples/build_demo_figure.py --outdir build
python3 scripts/figure_qa.py build/figure-clean.pptx \
  --target-width-mm 180 --min-pt 5 --allow-mm2 0.5
```

```text
figure QA: build/figure-clean.pptx
slide 338.66 x 132.08 mm, target 180.0 mm, print scale 0.5315
shapes: 8 (text 6, pictures 2)

FAIL overlap: 0

FAIL text below the print floor: 0

FAIL outside the canvas: 0

WARN font not verified: 0

WARN estimated text overflow: 0

PASS: no blocking finding
```

Exit code 0. The section headings say FAIL even when the count is zero, because they name the gate,
not the result. Read the count and the final verdict.

## Export

```bash
python3 scripts/export_figures.py build/figure-clean.pptx --outdir build --dpi 600
```

```text
vector PDF: build/figure-clean.pdf
page 1: 338.7 x 132.1 mm -> figure-clean.png at 600 dpi
PNG pages: 1
```

The exported page is 338.7 mm wide, the slide width. If your target is 180 mm, rescale at export
time in PowerPoint or set the slide width to the print width before building, and `--target-width-mm`
will tell you when the two disagree.

## What the script still cannot check

Whether the arrow points at the right layer. Whether the legend matches the artwork. Whether the
illustration shows the mechanism the text describes. Open the exported PDF at final print size and
read it as a reviewer before you send it anywhere.
