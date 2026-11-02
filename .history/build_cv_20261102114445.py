"""Build matching, compact EN/ZH academic CV documents from cv-content.json.

Run from the directory containing this script and cv-content.json:
    python build_cv_compact.py
Outputs: files/Wei-Feng-CV-EN.docx, .pdf, -ZH.docx, .pdf

Does not change your cv-content.json or cv-page.js.
"""
from pathlib import Path
import json
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
DATA_FILE=ROOT/'cv-content.json'
OUT=ROOT/'files'
OUT.mkdir(parents=True,exist_ok=True)
RAW=json.loads(DATA_FILE.read_text(encoding='utf-8'))
assert isinstance(RAW,list) and all(x.get('kind') in ('heading','date','entry','text') for x in RAW)

NAVY='#1f435b'; INK='#1b2837'; GRAY='#64717b'
COLOR_NAVY=RGBColor(31,67,91);COLOR_INK=RGBColor(27,40,55);COLOR_GRAY=RGBColor(100,113,123)

# One source of content, one semantic layout for DOCX and PDF.
def records(lang):
    result=[];i=0
    while i<len(RAW):
        current=RAW[i]; kind=current['kind'];value=current[lang].strip()
        if kind=='date' and i+1<len(RAW) and RAW[i+1]['kind']=='entry':
            entry=RAW[i+1][lang].strip(); sub='';i+=2
            if i<len(RAW) and RAW[i]['kind']=='text':
                sub=RAW[i][lang].strip();i+=1
            result.append(('item',value,entry,sub))
            continue
        if kind=='entry':
            raise ValueError('Unexpected entry without date, block '+str(i))
        result.append((kind,value));i+=1
    return result

def style_run(run, size, bold=False, color=COLOR_INK, lang='en'):
    run.bold=bold;run.font.size=Pt(size);run.font.color.rgb=color
    run.font.name='Arial' if lang=='en' else 'Microsoft YaHei'
    rPr=run._element.get_or_add_rPr(); fonts=rPr.get_or_add_rFonts();fonts.set(qn('w:eastAsia'),'Microsoft YaHei')

def p_format(p,before=0,after=0,line=1.07,keep_next=False):
    pf=p.paragraph_format;pf.space_before=Pt(before);pf.space_after=Pt(after)
    pf.line_spacing=line;pf.keep_with_next=keep_next

def insert_rule(p):
    pbdr=OxmlElement('w:pBdr'); bottom=OxmlElement('w:bottom')
    for k,v in {'val':'single','sz':'4','color':'D9E2E9','space':'4'}.items():bottom.set(qn('w:'+k),v)
    pbdr.append(bottom);p._p.get_or_add_pPr().append(pbdr)

def no_split_row(row):
    trPr=row._tr.get_or_add_trPr();e=OxmlElement('w:cantSplit');trPr.append(e)

def set_cell_margin(cell,top=0,start=0,bottom=0,end=0):
    tcPr=cell._tc.get_or_add_tcPr(); tcMar=tcPr.first_child_found_in('w:tcMar')
    if tcMar is None:
        tcMar=OxmlElement('w:tcMar');tcPr.append(tcMar)
    for m,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        tag=qn('w:'+m);el=tcMar.find(tag)
        if el is None:el=OxmlElement('w:'+m);tcMar.append(el)
        el.set(qn('w:w'),str(val));el.set(qn('w:type'),'dxa')

def build_docx(lang):
    doc=Document();s=doc.sections[0]
    s.page_width=Cm(21);s.page_height=Cm(29.7)
    s.top_margin=Cm(1.10);s.bottom_margin=Cm(1.10)
    s.left_margin=Cm(1.55);s.right_margin=Cm(1.55)
    s.header_distance=Cm(.4);s.footer_distance=Cm(.4)
    normal=doc.styles['Normal'];normal.font.name='Arial' if lang=='en' else 'Microsoft YaHei'
    normal.font.size=Pt(8.7);normal.paragraph_format.space_after=Pt(0)
    normal.paragraph_format.line_spacing=1.07
    rfonts=normal.element.get_or_add_rPr().get_or_add_rFonts();rfonts.set(qn('w:eastAsia'),'Microsoft YaHei')

    first=True
    for rec in records(lang):
        kind=rec[0]
        if kind=='text':
            p=doc.add_paragraph();p_format(p,after=2.5 if not first else 4)
            for j,line in enumerate(rec[1].splitlines()):
                if j:p.add_run().add_break()
                style_run(p.add_run(line), 8.5 if not first else 17, first, COLOR_NAVY if first else COLOR_INK,lang)
            first=False
        elif kind=='heading':
            p=doc.add_paragraph();p_format(p,before=5.2,after=3.6,line=1.0,keep_next=True)
            style_run(p.add_run(rec[1]),9.4,True,COLOR_NAVY,lang)
            insert_rule(p)
        elif kind=='item':
            date,title,sub=rec[1:]
            t=doc.add_table(rows=1,cols=2)
            t.autofit=False; t.alignment=WD_TABLE_ALIGNMENT.CENTER
            t.columns[0].width=Cm(3.55);t.columns[1].width=Cm(14.25)
            cells=t.rows[0].cells
            cells[0].width=Cm(3.55);cells[1].width=Cm(14.25)
            no_split_row(t.rows[0])
            for c in cells:
                c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
                set_cell_margin(c,top=2,start=0,bottom=8,end=60 if c==cells[0] else 0)
            lp=cells[0].paragraphs[0];p_format(lp,line=1.08)
            style_run(lp.add_run(date),7.9,False,COLOR_GRAY,lang)
            rp=cells[1].paragraphs[0];p_format(rp,after=1 if sub else 0,line=1.08,keep_next=bool(sub))
            style_run(rp.add_run(title),8.6,True,COLOR_INK,lang)
            if sub:
                sp=cells[1].add_paragraph();p_format(sp,after=0,line=1.08)
                style_run(sp.add_run(sub),8.1,False,COLOR_GRAY,lang)
    out=OUT/f'Wei-Feng-CV-{lang.upper()}.docx'
    doc.save(out);return out

# Register PDF fonts, with Chinese CID fallback (doesn't depend on the user's local fonts).
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
try:
    pdfmetrics.registerFont(TTFont('CVLatin','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('CVLatinBold','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'))
except Exception:
    pass

def build_pdf(lang):
    main_font='STSong-Light' if lang=='zh' else ('CVLatin' if 'CVLatin' in pdfmetrics.getRegisteredFontNames() else 'Helvetica')
    bold_font='STSong-Light' if lang=='zh' else ('CVLatinBold' if 'CVLatinBold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold')
    def S(name,size,leading,color,spaceBefore=0,spaceAfter=0,keepWithNext=False,font=None):
        return ParagraphStyle(name,fontName=font or main_font,fontSize=size,leading=leading,
                              textColor=colors.HexColor(color),spaceBefore=spaceBefore,spaceAfter=spaceAfter,
                              keepWithNext=keepWithNext,allowWidows=0,allowOrphans=0)
    styles={
        'name':S('name'+lang,17,21,NAVY,spaceAfter=4,font=bold_font),
        'header':S('header'+lang,8.5,11,INK,spaceAfter=2.5),
        'heading':S('heading'+lang,9.4,12,NAVY,spaceBefore=5.0,spaceAfter=2.8,keepWithNext=True,font=bold_font),
        'date':S('date'+lang,7.9,10.1,GRAY),
        'entry':S('entry'+lang,8.6,11.2,INK,spaceAfter=1,font=bold_font),
        'sub':S('sub'+lang,8.1,10.7,GRAY),
    }
    body=[];first=True
    for rec in records(lang):
        kind=rec[0]
        if kind=='text':
            value='<br/>'.join(xml_escape(x) for x in rec[1].splitlines())
            body.append(Paragraph(value,styles['name' if first else 'header']))
            first=False
        elif kind=='heading':
            body.append(Paragraph(xml_escape(rec[1]),styles['heading']))
        else:
            date,title,sub=rec[1:]
            right=[Paragraph(xml_escape(title),styles['entry'])]
            if sub:right.append(Paragraph(xml_escape(sub),styles['sub']))
            table=Table([[Paragraph(xml_escape(date),styles['date']),right]],colWidths=[105,410],hAlign='LEFT')
            table.setStyle(TableStyle([
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
                ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),1),
                ('LEFTPADDING',(1,0),(1,-1),4)
            ]))
            body.append(table)
    out=OUT/f'Wei-Feng-CV-{lang.upper()}.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=40,rightMargin=40,
         topMargin=35,bottomMargin=35,title='Wei Feng Academic CV',
         author='Wei Feng',pageCompression=1)
    doc.build(body);return out

if __name__=='__main__':
    for lang in ('en','zh'):
        for make in (build_docx,build_pdf):
            print(make(lang))
