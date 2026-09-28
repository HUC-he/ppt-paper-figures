#!/usr/bin/env python3
"""Export a PowerPoint figure to vector PDF and 600 dpi PNG.

Usage:
    python3 export_figures.py figure.pptx --outdir build --dpi 600 --target-width-mm 180

LibreOffice does the pptx to PDF step, PyMuPDF renders the PNGs. If LibreOffice is missing the
script says so and exits, rather than silently producing a low quality raster.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SOFFICE_CANDIDATES = (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
    "/usr/bin/libreoffice",
    "soffice",
)
POINTS_PER_INCH = 72.0
MM_PER_POINT = 25.4 / POINTS_PER_INCH


class ExportError(Exception):
    """User-facing failure."""


def find_soffice(explicit: str | None) -> str:
    if explicit:
        if not Path(explicit).exists() and shutil.which(explicit) is None:
            raise ExportError(f"soffice not found at {explicit}")
        return explicit
    for candidate in SOFFICE_CANDIDATES:
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    raise ExportError(
        "LibreOffice/soffice not found. Install it, pass --soffice, or export PDF and PNG from "
        "PowerPoint directly and keep the same file names."
    )


def pptx_to_pdf(pptx: Path, outdir: Path, soffice: str) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [soffice, "--headless", "--norestore", "--convert-to", "pdf",
         "--outdir", str(outdir), str(pptx)],
        capture_output=True,
        text=True,
        check=False,
    )
    pdf = outdir / (pptx.stem + ".pdf")
    if result.returncode != 0 or not pdf.exists():
        raise ExportError(
            "conversion failed: " + (result.stderr or result.stdout or "no output").strip()[:400]
        )
    return pdf


def pdf_to_png(pdf: Path, outdir: Path, dpi: int) -> list[Path]:
    try:
        import pymupdf as fitz  # PyMuPDF 1.24+
    except ImportError:
        try:
            import fitz  # older PyMuPDF
        except ImportError as exc:  # pragma: no cover - environment guard
            raise ExportError(
                "PyMuPDF is required for PNG export: pip install pymupdf"
            ) from exc

    zoom = dpi / POINTS_PER_INCH
    written: list[Path] = []
    with fitz.open(pdf) as doc:
        for index, page in enumerate(doc, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            name = pdf.stem if len(doc) == 1 else f"{pdf.stem}-p{index}"
            target = outdir / f"{name}.png"
            pixmap.save(target)
            written.append(target)
            size = page.rect
            print(
                f"page {index}: {size.width * MM_PER_POINT:.1f} x "
                f"{size.height * MM_PER_POINT:.1f} mm -> {target.name} at {dpi} dpi"
            )
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export a .pptx figure to PDF and PNG.")
    parser.add_argument("pptx")
    parser.add_argument("--outdir", default="build")
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--target-width-mm", type=float, default=None,
                        help="warn when the exported page width is far from this value")
    parser.add_argument("--soffice", default=None)
    args = parser.parse_args(argv)

    pptx = Path(args.pptx)
    if not pptx.exists():
        print(f"error: {pptx} does not exist", file=sys.stderr)
        return 2
    outdir = Path(args.outdir)
    try:
        soffice = find_soffice(args.soffice)
        pdf = pptx_to_pdf(pptx, outdir, soffice)
        print(f"vector PDF: {pdf}")
        pages = pdf_to_png(pdf, outdir, args.dpi)
        if args.target_width_mm:
            try:
                import pymupdf as fitz
            except ImportError:
                import fitz

            with fitz.open(pdf) as doc:
                width_mm = doc[0].rect.width * MM_PER_POINT
            delta = abs(width_mm - args.target_width_mm)
            if delta > 2.0:
                print(
                    f"warning: exported width is {width_mm:.1f} mm, target was "
                    f"{args.target_width_mm:.1f} mm; rescale before submission",
                    file=sys.stderr,
                )
        print(f"PNG pages: {len(pages)}")
        return 0
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
