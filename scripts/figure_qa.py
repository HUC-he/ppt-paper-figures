#!/usr/bin/env python3
"""QA gate for PowerPoint figures.

Checks a .pptx figure for the four defects that survive to print: overlapping text, text sitting on
top of artwork, text smaller than the legibility floor at final print size, and shapes running off
the canvas.

Usage:
    python3 figure_qa.py figure.pptx --target-width-mm 180 --min-pt 5 --allow-mm2 0.5
    python3 figure_qa.py figure.pptx --dump
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EMU_PER_MM = 36000.0
DEFAULT_FONTS = ("Arial", "SimSun", "Songti SC", "Times New Roman")
SHAPE_GROUP = 6
SHAPE_PICTURE = 13


class QAError(Exception):
    """User-facing failure."""


# ------------------------------------------------------------------ geometry


class Box:
    """An absolutely positioned shape, in EMU."""

    __slots__ = ("left", "top", "width", "height", "name", "kind", "text", "runs")

    def __init__(self, left, top, width, height, name, kind, text="", runs=None):
        self.left = float(left or 0)
        self.top = float(top or 0)
        self.width = float(width or 0)
        self.height = float(height or 0)
        self.name = name
        self.kind = kind
        self.text = text
        self.runs = runs or []

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def bottom(self) -> float:
        return self.top + self.height

    def mm(self, key: str) -> float:
        return getattr(self, key) / EMU_PER_MM

    def intersection_mm2(self, other: "Box") -> float:
        dx = min(self.right, other.right) - max(self.left, other.left)
        dy = min(self.bottom, other.bottom) - max(self.top, other.top)
        if dx <= 0 or dy <= 0:
            return 0.0
        return (dx * dy) / (EMU_PER_MM * EMU_PER_MM)


def iter_shapes(shapes, dx: float = 0.0, dy: float = 0.0):
    """Yield (shape, absolute_left, absolute_top) with group offsets applied."""
    for shape in shapes:
        try:
            shape_type = shape.shape_type
        except (ValueError, AttributeError):
            shape_type = None
        if shape_type == SHAPE_GROUP:
            for item in iter_shapes(
                shape.shapes,
                dx + float(shape.left or 0),
                dy + float(shape.top or 0),
            ):
                yield item
        else:
            yield shape, dx + float(getattr(shape, "left", 0) or 0), dy + float(
                getattr(shape, "top", 0) or 0
            )


def collect_runs(shape) -> list[dict]:
    runs: list[dict] = []
    text_frame = getattr(shape, "text_frame", None)
    if text_frame is None:
        return runs
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if not run.text.strip():
                continue
            size = None
            if run.font.size is not None:
                size = float(run.font.size.pt)
            elif paragraph.font.size is not None:
                size = float(paragraph.font.size.pt)
            name = run.font.name or paragraph.font.name
            runs.append(
                {
                    "text": run.text.strip(),
                    "font": name,
                    "size_pt": size,
                    "bold": bool(run.font.bold),
                }
            )
    return runs


def collect_boxes(path: Path) -> tuple[list[Box], float]:
    try:
        from pptx import Presentation
    except ImportError as exc:  # pragma: no cover - environment guard
        raise QAError("python-pptx is required: pip install python-pptx") from exc

    try:
        prs = Presentation(str(path))
    except Exception as exc:
        raise QAError(f"cannot open {path}: {exc}") from exc

    slide_w = float(prs.slide_width or 0)
    slide_h = float(prs.slide_height or 0)
    boxes: list[Box] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            for item, left, top in iter_shapes([shape]):
                try:
                    kind = item.shape_type
                except (ValueError, AttributeError):
                    kind = None
                runs = collect_runs(item)
                text = "\n".join(run["text"] for run in runs)
                if kind == SHAPE_PICTURE:
                    label = "picture"
                elif text.strip():
                    label = "text"
                else:
                    label = "shape"
                boxes.append(
                    Box(
                        left,
                        top,
                        getattr(item, "width", 0),
                        getattr(item, "height", 0),
                        getattr(item, "name", "shape"),
                        label,
                        text,
                        runs,
                    )
                )
    return boxes, slide_w


# ------------------------------------------------------------------ checks


def check_overlaps(boxes: list[Box], allow_mm2: float) -> list[dict]:
    findings: list[dict] = []
    text_boxes = [b for b in boxes if b.kind == "text"]
    pictures = [b for b in boxes if b.kind == "picture"]
    for index, first in enumerate(text_boxes):
        for second in text_boxes[index + 1:]:
            area = first.intersection_mm2(second)
            if area > allow_mm2:
                findings.append(
                    {
                        "kind": "text-text overlap",
                        "area_mm2": round(area, 3),
                        "a": first.name,
                        "a_text": first.text[:40],
                        "b": second.name,
                        "b_text": second.text[:40],
                    }
                )
    for text_box in text_boxes:
        for picture in pictures:
            area = text_box.intersection_mm2(picture)
            if area > allow_mm2:
                findings.append(
                    {
                        "kind": "text-image overlap",
                        "area_mm2": round(area, 3),
                        "a": text_box.name,
                        "a_text": text_box.text[:40],
                        "b": picture.name,
                        "b_text": "(picture)",
                    }
                )
    return findings


def check_fonts(
    boxes: list[Box],
    scale: float,
    min_pt: float,
    allowed_fonts: tuple[str, ...],
) -> tuple[list[dict], list[dict]]:
    too_small: list[dict] = []
    inherited: list[dict] = []
    for box in boxes:
        for run in box.runs:
            size = run["size_pt"]
            if size is None:
                inherited.append({"shape": box.name, "text": run["text"][:40]})
                continue
            printed = size * scale
            if printed < min_pt:
                too_small.append(
                    {
                        "shape": box.name,
                        "text": run["text"][:40],
                        "deck_pt": round(size, 1),
                        "print_pt": round(printed, 2),
                    }
                )
            font = run["font"]
            if font and font not in allowed_fonts:
                inherited.append(
                    {
                        "shape": box.name,
                        "text": run["text"][:40],
                        "font": font,
                        "note": "font outside the allowed set",
                    }
                )
    return too_small, inherited


def check_canvas(boxes: list[Box], slide_w: float, slide_h: float) -> list[dict]:
    findings: list[dict] = []
    for box in boxes:
        out = []
        if box.left < -1:
            out.append(f"left {box.mm('left'):.1f} mm")
        if box.top < -1:
            out.append(f"top {box.mm('top'):.1f} mm")
        if box.right > slide_w + 1:
            out.append(f"right {box.mm('right'):.1f} mm")
        if box.bottom > slide_h + 1:
            out.append(f"bottom {box.mm('bottom'):.1f} mm")
        if out:
            findings.append({"shape": box.name, "kind": box.kind, "outside": ", ".join(out)})
    return findings


def check_text_fit(boxes: list[Box]) -> list[dict]:
    """Heuristic: the longest run may not fit its box at the stated size."""
    findings: list[dict] = []
    for box in boxes:
        if box.kind != "text" or not box.runs or box.width <= 0:
            continue
        widest = 0.0
        for run in box.runs:
            size = run["size_pt"]
            if not size:
                continue
            # rough advance width: 0.55 em for mixed Latin text, 1.0 em for CJK
            latin = sum(1 for ch in run["text"] if ord(ch) < 0x2E80)
            cjk = len(run["text"]) - latin
            est_pt = size * (0.55 * latin + 1.0 * cjk)
            widest = max(widest, est_pt)
        box_pt = box.width / EMU_PER_MM / 25.4 * 72.0
        if widest > box_pt * 1.05:
            findings.append(
                {
                    "shape": box.name,
                    "text": box.text[:40],
                    "estimated_width_pt": round(widest, 1),
                    "box_width_pt": round(box_pt, 1),
                }
            )
    return findings


# ------------------------------------------------------------------ report


def build_report(args: argparse.Namespace) -> tuple[dict, bool]:
    boxes, slide_w = collect_boxes(Path(args.pptx))
    if not boxes:
        raise QAError("no shapes found in the deck")
    slide_h = max(b.bottom for b in boxes) if boxes else 0.0
    try:
        from pptx import Presentation

        prs = Presentation(str(args.pptx))
        slide_h = float(prs.slide_height or slide_h)
    except Exception:  # pragma: no cover - height is only informational
        pass

    slide_w_mm = slide_w / EMU_PER_MM
    if slide_w_mm <= 0:
        raise QAError("slide width is zero; the deck may be corrupt")
    scale = args.target_width_mm / slide_w_mm

    overlaps = check_overlaps(boxes, args.allow_mm2)
    too_small, inherited = check_fonts(
        boxes, scale, args.min_pt, tuple(args.fonts.split(","))
    )
    outside = check_canvas(boxes, slide_w, slide_h)
    tight = check_text_fit(boxes)

    report = {
        "file": str(args.pptx),
        "slide_width_mm": round(slide_w_mm, 2),
        "slide_height_mm": round(slide_h / EMU_PER_MM, 2),
        "target_width_mm": args.target_width_mm,
        "print_scale": round(scale, 4),
        "counts": {
            "shapes": len(boxes),
            "text": sum(1 for b in boxes if b.kind == "text"),
            "pictures": sum(1 for b in boxes if b.kind == "picture"),
        },
        "overlaps": overlaps,
        "too_small": too_small,
        "font_notes": inherited,
        "outside_canvas": outside,
        "text_fit_warnings": tight,
    }
    blocking = bool(overlaps or too_small or outside)
    return report, blocking


def render_text(report: dict) -> str:
    lines = [
        f"figure QA: {report['file']}",
        f"slide {report['slide_width_mm']} x {report['slide_height_mm']} mm, "
        f"target {report['target_width_mm']} mm, print scale {report['print_scale']}",
        f"shapes: {report['counts']['shapes']} "
        f"(text {report['counts']['text']}, pictures {report['counts']['pictures']})",
    ]

    def section(title: str, items: list[dict], formatter) -> None:
        lines.append("")
        lines.append(f"{title}: {len(items)}")
        for item in items:
            lines.append("  - " + formatter(item))

    section(
        "FAIL overlap",
        report["overlaps"],
        lambda i: f'{i["kind"]} {i["area_mm2"]} mm2: "{i["a_text"]}" x "{i["b_text"]}"',
    )
    section(
        "FAIL text below the print floor",
        report["too_small"],
        lambda i: f'{i["print_pt"]} pt on paper ({i["deck_pt"]} pt in deck): "{i["text"]}"',
    )
    section(
        "FAIL outside the canvas",
        report["outside_canvas"],
        lambda i: f'{i["shape"]} ({i["kind"]}): {i["outside"]}',
    )
    section(
        "WARN font not verified",
        report["font_notes"],
        lambda i: f'{i["shape"]}: {i.get("note", "no explicit font")} "{i["text"]}"',
    )
    section(
        "WARN estimated text overflow",
        report["text_fit_warnings"],
        lambda i: f'{i["shape"]}: needs about {i["estimated_width_pt"]} pt, box is '
        f'{i["box_width_pt"]} pt',
    )
    lines.append("")
    lines.append("BLOCKING" if report.get("blocking") else "PASS: no blocking finding")
    lines.append(
        "note: overlap uses shape boxes, which is slightly conservative for text that does not fill "
        "its frame. Confirm visually on the exported PDF."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QA gate for PowerPoint figures.")
    parser.add_argument("pptx", help="the .pptx figure")
    parser.add_argument("--target-width-mm", type=float, default=180.0,
                        help="printed width of the figure (default 180)")
    parser.add_argument("--min-pt", type=float, default=5.0,
                        help="minimum font size on paper (default 5)")
    parser.add_argument("--allow-mm2", type=float, default=0.5,
                        help="overlap allowance for border contact (default 0.5)")
    parser.add_argument("--fonts", default=",".join(DEFAULT_FONTS),
                        help="comma separated allowed font names")
    parser.add_argument("--json", help="also write the report as JSON here")
    parser.add_argument("--dump", action="store_true",
                        help="list every shape with its position in mm and exit")
    args = parser.parse_args(argv)

    try:
        if args.dump:
            boxes, slide_w = collect_boxes(Path(args.pptx))
            for box in boxes:
                print(
                    f"{box.name[:34]:34s} {box.kind:7s} "
                    f"L{box.mm('left'):7.1f} T{box.mm('top'):7.1f} "
                    f"W{box.mm('width'):7.1f} H{box.mm('height'):7.1f} "
                    f"{box.text[:30]}"
                )
            return 0

        report, blocking = build_report(args)
        report["blocking"] = blocking
        print(render_text(report))
        if args.json:
            Path(args.json).write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        return 1 if blocking else 0
    except QAError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
