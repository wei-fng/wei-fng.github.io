
from pathlib import Path
from collections import defaultdict
import json
import re
import html

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "cv-content.json"
OUTPUT_DIR = ROOT / "files"
OUTPUT_DIR.mkdir(exist_ok=True)

LANGUAGES = ("en", "zh")
KINDS = {"text", "heading", "date", "entry"}

NAVY = "#1f435b"
DARK = "#1b2837"
GRAY = "#596773"

blocks = json.loads(DATA_FILE.read_text(encoding="utf-8"))

if not isinstance(blocks, list) or not blocks:
    raise ValueError("cv-content.json must contain a non-empty array.")

for i, block in enumerate(blocks):
    if not isinstance(block, dict):
        raise ValueError(f"Block {i} must be an object.")

    if block.get("kind") not in KINDS:
        raise ValueError(f"Unsupported kind at block {i}: {block.get('kind')}")

    for lang in LANGUAGES:
        if not isinstance(block.get(lang), str) or not block[lang].strip():
            raise ValueError(f"Missing {lang} text at block {i}.")


def add_docx_text(doc, text, kind, index):
    if index == 0:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(5)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(19)
        run.font.color.rgb = RGBColor(31, 67, 91)
        return

    if kind == "heading":
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(31, 67, 91)
        return

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2 if kind == "date" else 0)
    p.paragraph_format.space_after = Pt(
        1 if kind == "date" else 3
    )

    if kind == "date":
        p.paragraph_format.keep_with_next = True

    for idx, line in enumerate(text.split("\n")):
        if idx:
            p.add_run().add_break()

        run = p.add_run(line)
        run.bold = kind in ("entry", "date")
        run.font.size = Pt(9.2)
        run.font.color.rgb = (
            RGBColor(31, 67, 91)
            if kind == "date"
            else RGBColor(27, 40, 55)
        )


def build_docx(lang):
    doc = Document()

    section = doc.sections[0]
    section.top_margin = Cm(1.7)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.2)
    normal.paragraph_format.line_spacing = 1.12

    normal.element.get_or_add_rPr().get_or_add_rFonts().set(
        qn("w:eastAsia"), "Microsoft YaHei"
    )

    for index, block in enumerate(blocks):
        add_docx_text(
            doc,
            block[lang],
            block["kind"],
            index,
        )

    output = OUTPUT_DIR / f"Wei-Feng-CV-{lang.upper()}.docx"
    doc.save(output)
    return output


pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))


def build_pdf(lang):
    font = "Helvetica" if lang == "en" else "STSong-Light"

    styles = {
        "name": ParagraphStyle(
            "name",
            fontName=font,
            fontSize=18,
            leading=23,
            textColor=colors.HexColor(NAVY),
            spaceAfter=7,
        ),
        "heading": ParagraphStyle(
            "heading",
            fontName=font,
            fontSize=10,
            leading=13,
            textColor=colors.HexColor(NAVY),
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "date": ParagraphStyle(
            "date",
            fontName=font,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(NAVY),
            spaceBefore=4,
            spaceAfter=1,
            keepWithNext=True,
        ),
        "entry": ParagraphStyle(
            "entry",
            fontName=font,
            fontSize=9.3,
            leading=13,
            textColor=colors.HexColor(DARK),
            spaceAfter=3,
        ),
        "text": ParagraphStyle(
            "text",
            fontName=font,
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor(DARK),
            spaceAfter=6,
        ),
    }

    story = []

    for index, block in enumerate(blocks):
        kind = "name" if index == 0 else block["kind"]
        value = html.escape(block[lang]).replace("\n", "<br/>")
        story.append(Paragraph(value, styles[kind]))

    output = OUTPUT_DIR / f"Wei-Feng-CV-{lang.upper()}.pdf"

    doc = SimpleDocTemplate(
        str(output),
        pagesize=(595.28, 841.89),
        leftMargin=49,
        rightMargin=49,
        topMargin=40,
        bottomMargin=40,
        title="Wei Feng Academic CV",
    )
    doc.build(story)
    return output


def build_web_js():
    data = json.dumps(blocks, ensure_ascii=False)

    script = r"""
let cvLanguage =
  new URLSearchParams(location.search).get('lang') === 'zh'
    ? 'zh'
    : 'en';

const cvContent = __CV_DATA__;

const escapeCV = value => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;');

function setCVLanguage(lang) {
  cvLanguage = lang;

  document.querySelectorAll('[data-lang]').forEach(button => {
    button.setAttribute(
      'aria-pressed',
      String(button.dataset.lang === lang)
    );
  });

  const profile = document.getElementById('cv-profile');
  if (!profile) return;

  profile.lang = lang === 'zh' ? 'zh-CN' : 'en';

  profile.innerHTML = cvContent.map((block, index) => {
    const value = escapeCV(block[lang]).replaceAll('\n', '<br>');

    if (index === 0) {
      return `<h1>${value}</h1>`;
    }

    if (block.kind === 'heading') {
      return `<h2>${value}</h2>`;
    }

    return `<p class="cv-${block.kind}">${value}</p>`;
  }).join('');

  for (const format of ['pdf', 'docx']) {
    const link = document.getElementById('cv-' + format);
    if (link) {
      link.href =
        `files/Wei-Feng-CV-${lang.toUpperCase()}.${format}`;
    }
  }

  const url = new URL(location.href);
  url.searchParams.set('lang', lang);
  history.replaceState(null, '', url);
}

document.querySelectorAll('[data-lang]').forEach(button => {
  button.addEventListener('click', () => {
    setCVLanguage(button.dataset.lang);
  });
});

setCVLanguage(cvLanguage);
"""

    script = script.replace("__CV_DATA__", data)
    output = ROOT / "cv-page.js"
    output.write_text(script, encoding="utf-8")
    return output


outputs = []

for language in LANGUAGES:
    outputs.append(build_docx(language))
    outputs.append(build_pdf(language))

outputs.append(build_web_js())

print("Build completed:")
for output in outputs:
    print(" -", output.relative_to(ROOT))
