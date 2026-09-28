# Export and QA

Read this file when exporting a figure, running the QA gate, or handling a QA failure.

## Export

Two outputs, always:

- vector PDF for the publisher, because text and lines must stay resolution independent;
- 600 dpi PNG for preview, for journals that rasterise, and for slides.

With LibreOffice available:

```bash
python3 scripts/export_figures.py figure.pptx --outdir build --dpi 600 --target-width-mm 180
```

The script converts the deck to PDF, then renders each page to PNG at the requested dpi, and reports
the physical size of each exported page so you can confirm the print width matches the plan.

Without LibreOffice, export from PowerPoint directly: PDF at "best for printing", then PNG at 600
dpi for the figure area only. Keep the same file names so later runs overwrite cleanly.

## QA gate

```bash
python3 scripts/figure_qa.py figure.pptx --target-width-mm 180 --min-pt 5 --allow-mm2 0.5
```

The gate checks four things:

1. Overlap. Every pair of text boxes, and every text box against every picture, with intersection
   area in mm^2 at final print size. The allowance for border-level contact is 0.5 mm^2.
2. Minimum size. Every run's font size converted to final print size, against the floor.
3. Font names. Anything that is not Arial, SimSun, or Songti SC is reported, including runs that
   inherit their font from the theme and cannot be verified.
4. Canvas. Shapes that extend past the slide edge, which usually means an asset was placed at full
   size and never cropped.

It exits non-zero on a blocking finding so it can be used as a delivery gate.

## Reading a QA failure

An overlap is almost never fixed by nudging the text. Either the artwork extends into the label
band, in which case the asset needs its empty margin back, or two labels are fighting for one
anchor, in which case one of them belongs in the caption.

A font below the floor means the figure carries too much at that width. Options, in order of
preference: shorten the label, move the detail to the caption, split the panel, or enlarge the
figure's printed width.

An inherited font is not an error, but it is a risk. Set the font explicitly on every run before
delivery, because a theme change or a machine change will silently alter the figure otherwise.

## The visual pass the script cannot do

Open the exported PDF, set it to the final print size, and read it as a reviewer would:

- does every arrow point from the right ingredient to the right consequence;
- does the legend agree with the image, including colours and order;
- is the mechanism in the illustration the mechanism the text describes;
- is any panel empty, duplicated, or carrying a claim the data does not support;
- do the panel letters match the order they are cited in the manuscript;
- is every value, unit, and precision consistent with the text.

Run this pass on the export, not on the deck. Export introduces its own surprises: dropped
transparency, substituted fonts, and images that fall off the page edge.
