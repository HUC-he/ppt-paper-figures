#!/usr/bin/env python3
"""Behavioral tests for the figure QA gate. Run: python3 tests/test_figure_qa.py"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_DIR / "scripts"


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


qa = load("figure_qa", "figure_qa.py")
exporter = load("export_figures", "export_figures.py")

from pptx import Presentation  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402
from PIL import Image  # noqa: E402


def add_text(slide, text, left_in, top_in, width_in, height_in, size_pt, font="Arial"):
    box = slide.shapes.add_textbox(
        Inches(left_in), Inches(top_in), Inches(width_in), Inches(height_in)
    )
    run = box.text_frame.paragraphs[0].add_run()
    run.text = text
    run.font.size = Pt(size_pt)
    run.font.name = font
    return box


class FigureQATest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.png = self.dir / "asset.png"
        Image.new("RGB", (400, 300), "white").save(self.png)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def build(self, name: str = "figure.pptx") -> Path:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_text(slide, "Cathode current collector", 1.0, 1.0, 3.0, 0.4, 10)
        add_text(slide, "Anode current collector", 1.2, 1.15, 3.0, 0.4, 10)
        add_text(slide, "tiny footnote 12 mg cm-2", 6.0, 6.5, 2.0, 0.3, 4)
        slide.shapes.add_picture(
            str(self.png), Inches(1.0), Inches(3.0), Inches(3.0), Inches(2.0)
        )
        add_text(slide, "Electrolyte reservoir", 1.1, 3.2, 2.0, 0.4, 9)
        off = slide.shapes.add_textbox(Emu(-400000), Inches(1.0), Inches(1.0), Inches(0.4))
        off_run = off.text_frame.paragraphs[0].add_run()
        off_run.text = "offscreen label"
        off_run.font.size = Pt(9)
        off_run.font.name = "Arial"
        path = self.dir / name
        prs.save(str(path))
        return path

    def report(self, path: Path, **overrides):
        args = Namespace(
            pptx=str(path),
            target_width_mm=180.0,
            min_pt=5.0,
            allow_mm2=0.5,
            fonts="Arial,SimSun,Songti SC,Times New Roman",
            json=None,
            dump=False,
        )
        for key, value in overrides.items():
            setattr(args, key, value)
        return qa.build_report(args)

    def test_clean_figure_passes(self) -> None:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_text(slide, "Cathode", 1.0, 1.0, 2.0, 0.4, 14)
        add_text(slide, "Anode", 6.0, 1.0, 2.0, 0.4, 14)
        path = self.dir / "clean.pptx"
        prs.save(str(path))
        report, blocking = self.report(path)
        self.assertFalse(blocking, report)
        self.assertEqual(report["overlaps"], [])
        self.assertEqual(report["too_small"], [])

    def test_detects_text_on_text(self) -> None:
        report, blocking = self.report(self.build())
        kinds = {item["kind"] for item in report["overlaps"]}
        self.assertIn("text-text overlap", kinds)
        self.assertTrue(blocking)

    def test_detects_text_on_picture(self) -> None:
        report, _ = self.report(self.build())
        kinds = {item["kind"] for item in report["overlaps"]}
        self.assertIn("text-image overlap", kinds)

    def test_detects_font_below_print_floor(self) -> None:
        report, blocking = self.report(self.build())
        self.assertTrue(any("tiny footnote" in item["text"] for item in report["too_small"]))
        self.assertTrue(blocking)
        self.assertLess(report["too_small"][0]["print_pt"], 5.0)

    def test_detects_shape_outside_canvas(self) -> None:
        report, _ = self.report(self.build())
        self.assertTrue(report["outside_canvas"])

    def test_print_scale_reflects_target_width(self) -> None:
        report, _ = self.report(self.build(), target_width_mm=90.0)
        # a 90 mm target halves the effective size, so a 10 pt label lands near 2.6 pt
        self.assertLess(report["print_scale"], 0.3)

    def test_flags_unexpected_font(self) -> None:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_text(slide, "Cathode", 1.0, 1.0, 2.0, 0.4, 14, font="Comic Sans MS")
        path = self.dir / "font.pptx"
        prs.save(str(path))
        report, _ = self.report(path)
        self.assertTrue(
            any(item.get("font") == "Comic Sans MS" for item in report["font_notes"])
        )

    def test_reports_inherited_font_as_unverified(self) -> None:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(2), Inches(0.4))
        box.text_frame.paragraphs[0].text = "no explicit font"
        path = self.dir / "inherited.pptx"
        prs.save(str(path))
        report, _ = self.report(path)
        self.assertTrue(report["font_notes"])

    def test_missing_file_is_an_error(self) -> None:
        with self.assertRaises(qa.QAError):
            self.report(self.dir / "nope.pptx")


class ExporterTest(unittest.TestCase):
    def test_finds_libreoffice_on_this_machine(self) -> None:
        try:
            found = exporter.find_soffice(None)
        except exporter.ExportError:
            self.skipTest("LibreOffice is not installed here")
        self.assertTrue(found)

    def test_missing_soffice_reports_clearly(self) -> None:
        with self.assertRaises(exporter.ExportError):
            exporter.find_soffice("/definitely/not/soffice")


if __name__ == "__main__":
    unittest.main(verbosity=2)
