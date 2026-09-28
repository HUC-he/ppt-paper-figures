# Asset Prompts

Read this file when writing a prompt for a figure asset, or when an asset came back with unwanted
writing on it.

## What an asset is

An asset is one visual element of one panel: a materials stack, a device cross-section, a landscape,
a workflow block, a cell or a molecule, a piece of apparatus. It is not the figure. Captions,
labels, values, arrows that carry meaning, scale bars, and panel letters are added later in
PowerPoint as vector text.

One prompt per asset. Two panels in one image means you lose independent control of each panel when
one of them is wrong.

## Prompt skeleton

Write the prompt in six parts, in this order:

1. Subject. The exact object and its parts, in the intended material and colour.
2. View. Cross-section, isometric, exploded, side elevation. Name the perspective explicitly.
3. Composition. Where the object sits in the frame, how much background it needs, and what must
   stay empty for the labels you will add later.
4. Style. Clean vector-like scientific illustration, flat or soft shading, thin consistent outlines,
   white or very light background, no texture noise.
5. Palette. The figure's own palette, so all assets from one figure look like siblings.
6. Output constraints. High resolution, generous margins, and the text ban stated twice, once
   positively and once as a negative list.

## The text ban

State it as both a requirement and a prohibition, because a single mention is routinely ignored:

> The image must contain no text of any kind. No letters, no words, no numerals, no units, no axis,
> no legend, no title, no caption, no watermark, no signature, no fake glyphs, no pseudo-writing.
> Leave clear empty space where labels will be placed later.

Negative list to append verbatim: watermark, signature, logo, brand mark, random letters, gibberish
characters, pseudo-text, caption strip, border with writing, ruler with numbers, colour bar with
numbers, unreadable symbols replacing labels.

## Check every asset before it enters the deck

Look at the returned image at full size, not as a thumbnail. Reject and regenerate when you see:

- any text, number, or letter-like glyph, including faint marks in the background;
- a signature, watermark, or logo;
- a colour bar, ruler, or scale with numerals;
- ambiguous pseudo-writing that only looks like text at a glance;
- an accidental second object that reads as a different material or mechanism;
- lighting or line style that does not match the other assets in the figure.

A frequent trap is a generated "micrograph" that is visually convincing but is not data. If the
panel is meant to show a real measurement, the asset route is wrong; use the author's own image.

## Space for the labels you will add

Ask for the space explicitly. Generated compositions tend to fill the frame, and a filled frame
leaves nowhere to put a 7 pt label without overlapping the artwork.

Include a line such as: leave a wide empty margin on the left and a clean band above the object for
labels; do not place any element in the outer 15 percent of the frame.

## Recording the prompt

Keep each prompt beside its asset in a small text file with the same stem as the image. When a
figure is revised six months later, the prompt is the only way to regenerate a matching asset. Also
record the model and size used, so a re-run is reproducible.

## Credentials

Prompts, prompt files, and the figure folder never contain an API key or a private endpoint.
Credentials come from the environment at the moment of generation, and are never written into the
project directory.
