#!/usr/bin/env python3
"""Build the demo two-panel figure used in the README and the QA report.

The stand-in assets are drawn locally so the demo needs no image model and no network. In a real
figure these would be AI assets requested text-free, per references/asset-prompts.md.

    python3 examples/build_demo_figure.py --outdir /tmp/demo
    python3 examples/build_demo_figure.py --outdir /tmp/demo --defect

--defect injects the three classic failures: a label sitting on the artwork, a label at 3.5 pt, and
two labels fighting for the same anchor.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt

ASSETS = {
    "asset-wood.png": ((232, 240, 254), (90, 110, 140)),
    "asset-device.png": ((255, 241, 230), (150, 100, 70)),
}


def draw_assets(outdir: Path) -> dict[str, Path]:
    paths = {}
    for name, (fill, line) in ASSETS.items():
        image = Image.new("RGB", (900, 620), "white")
        pen = ImageDraw.Draw(image)
        pen.rounded_rectangle([24, 24, 876, 596], radius=44, fill=fill, outline=line, width=6)
        if "wood" in name:
            for x in (210, 330, 450, 570, 690):
                pen.rounded_rectangle([x, 140, x + 54, 500], radius=26, fill="white",
                                      outline=line, width=5)
            for y in (250, 350, 450):
                pen.line([70, y, 830, y], fill=line, width=3)
        else:
            for index, y in enumerate((150, 270, 390, 510)):
                pen.rounded_rectangle([120, y - 45, 780, y + 45], radius=18,
                                      fill="white", outline=line, width=5)
                pen.text((140, y - 12), "", fill=line)
            pen.ellipse([360, 200, 540, 460], fill=fill, outline=line, width=5)
        image.save(outdir / name)
        paths[name] = outdir / name
    return paths


def build(outdir: Path, defect: bool) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    assets = draw_assets(outdir)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(5.2)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    def label(
        text: str, left: float, top: float, size: float, bold: bool = False,
        width: float = 3.0,
    ) -> None:
        box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(0.42))
        run = box.text_frame.paragraphs[0].add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.name = "Arial"
        run.font.bold = bold

    # both assets keep a clean top band and bottom band for vector labels
    slide.shapes.add_picture(str(assets["asset-wood.png"]), Inches(0.5), Inches(1.05),
                             Inches(6.0), Inches(3.0))
    slide.shapes.add_picture(str(assets["asset-device.png"]), Inches(7.0), Inches(1.05),
                             Inches(6.0), Inches(3.0))
    label("a", 0.5, 0.28, 14, bold=True, width=0.4)
    label("b", 7.0, 0.28, 14, bold=True, width=0.4)
    label("Photothermal layer", 1.05, 0.30, 13)
    label("Wood-derived channel", 7.55, 0.30, 13)
    label("Evaporation-driven ion transport", 0.5, 4.20, 13, width=5.2)
    label("1.2 kg m-2 h-1 at 1 sun", 7.0, 4.20, 13, width=5.2)

    if defect:
        label("Photothermal layer", 0.75, 1.15, 11, width=3.0)       # sits on the artwork
        label("1.2 kg m-2 h-1 at 1 sun", 7.6, 4.25, 3.5, width=3.0)  # below the print floor

    path = outdir / ("figure-defective.pptx" if defect else "figure-clean.pptx")
    prs.save(str(path))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the demo figure deck.")
    parser.add_argument("--outdir", default="build")
    parser.add_argument("--defect", action="store_true")
    args = parser.parse_args()
    path = build(Path(args.outdir), args.defect)
    print(path)


if __name__ == "__main__":
    main()
