from pathlib import Path
import json,re,html
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.table import Table
from docx.text.paragraph import Paragraph
from reportlab.platypus import SimpleDocTemplate,Paragraph as PDFP,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors
blocks=json.loads(Path('cv-content.json').read_text(encoding='utf-8'));src='C:/Users/123/Desktop/Wei_Feng_Academic_CV_Draft.docx'
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
for lang in ['en','zh']:
 d=Document(src);i=0
 for el in list(d.element.body):
  if el.tag==qn('w:p'):
   p=Paragraph(el,d)
   if p.text:
    b=blocks[i];i+=1
    if lang=='zh':
     text=b[lang]
     if p.runs:
      p.runs[0].text=text
      for r in p.runs[1:]:r.text=''
     else:p.add_run(text)
  elif el.tag==qn('w:tbl'):
   t=Table(el,d);b=blocks[i];i+=1
   if lang=='zh':
    pair=b[lang].split(' | ')
    for c,txt in zip(t.rows[0].cells,pair):c.paragraphs[0].text=txt
 for b in blocks[i:]:
  d.add_paragraph(b[lang], 'Section Head' if b['kind']=='heading' else 'Normal')
 for st in d.styles:
  if st.type==1:
   st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),'Microsoft YaHei')
 d.save(f'files/Wei-Feng-CV-{lang.upper()}.docx')
 font='STSong-Light' if lang=='zh' else 'Helvetica'
 styles={k:ParagraphStyle(k,fontName=font,fontSize=size,leading=lead,textColor=colors.HexColor('#1f435b' if k=='heading' else '#1b2837'),spaceBefore=before,spaceAfter=after,keepWithNext=k in ['heading','entry','date']) for k,size,lead,before,after in [('text',9,12,0,4),('heading',10,13,12,6),('entry',9.5,13,5,2),('date',9.5,13,5,2),('blank',9,12,0,20),('name',19,23,0,5)]}
 story=[]
 for n,b in enumerate(blocks):
  t=html.escape(b[lang]).replace('\n','<br/>');style=styles['name' if n==0 else b['kind']]
  story.append(PDFP(t or '&#160;',style))
 SimpleDocTemplate(f'files/Wei-Feng-CV-{lang.upper()}.pdf',pagesize=(595.28,841.89),leftMargin=49,rightMargin=49,topMargin=40,bottomMargin=40,title='Wei Feng Academic CV').build(story)
# website content is shared with the downloadable documents
Path('cv-page.js').write_text('''let cvLanguage = new URLSearchParams(location.search).get('lang') === 'zh' ? 'zh' : 'en';
const cvContent = '''+json.dumps(blocks,ensure_ascii=False)+''';
const escapeCV = value => value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function setCVLanguage(lang) {
 cvLanguage = lang;
 document.querySelectorAll('[data-lang]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lang === lang)));
 document.getElementById('cv-profile').lang = lang === 'zh' ? 'zh-CN' : 'en';
 document.getElementById('cv-profile').innerHTML = cvContent.map((b,i) => i === 0 ? `<h1>${escapeCV(b[lang])}</h1>` : b.kind === 'heading' ? `<h2>${escapeCV(b[lang])}</h2>` : b.kind === 'blank' ? '<div class="cv-empty" aria-label="To be completed"></div>' : `<p class="cv-${b.kind}">${escapeCV(b[lang]).replaceAll('\\n','<br>')}</p>`).join('');
 for (const format of ['pdf','docx']) document.getElementById('cv-'+format).href = `files/Wei-Feng-CV-${lang.toUpperCase()}.${format}`;
 const url = new URL(location.href); url.searchParams.set('lang',lang); history.replaceState(null,'',url);
}
document.querySelectorAll('[data-lang]').forEach(button => button.addEventListener('click', () => setCVLanguage(button.dataset.lang)));
setCVLanguage(cvLanguage);
''',encoding='utf-8')
f=Path('cv.html');s=f.read_text(encoding='utf-8');a=s.index('    <div class="cv-controls"');b=s.index('\n  </main>',a)
s=s[:a]+'''    <div class="cv-controls" aria-label="CV controls"><div class="cv-toolbar" role="group" aria-label="Language"><button type="button" data-lang="en" aria-pressed="true">EN</button><button type="button" data-lang="zh" aria-pressed="false">中文</button></div><div class="cv-downloads"><a id="cv-pdf" href="files/Wei-Feng-CV-EN.pdf" download>PDF</a><a id="cv-docx" href="files/Wei-Feng-CV-EN.docx" download>DOCX</a></div></div>
    <article id="cv-profile" aria-live="polite"></article>
'''+s[b:];f.write_text(s,encoding='utf-8')
Path('cv-styles.css').write_text('''.cv-controls{display:flex;justify-content:space-between;align-items:center;margin:0 0 24px;gap:16px}.cv-toolbar{display:inline-flex;border:1px solid #d9dfe3;border-radius:5px;padding:3px}.cv-toolbar button{font:inherit;font-size:13px;border:0;border-radius:3px;background:transparent;color:var(--primary-color);padding:7px 16px;cursor:pointer}.cv-toolbar button[aria-pressed="true"]{background:#1f668a;color:white}.cv-downloads{display:flex;gap:8px}.cv-downloads a{border:1px solid #d9dfe3;border-radius:4px;padding:7px 16px;font-size:13px;color:var(--primary-color)}#cv-profile{background:var(--bg-color);padding:42px 48px;box-shadow:0 3px 24px #00000009;border:1px solid #e8ebee;font-size:13px;line-height:1.55}.about-page #cv-profile h1{font-size:28px;letter-spacing:1px;margin:0 0 5px}.about-page #cv-profile h2{font-size:14px;letter-spacing:.04em;color:#1f435b;border-bottom:1px solid #ccd5dd;padding-bottom:5px;margin:24px 0 9px}.about-page #cv-profile p{margin:0 0 7px!important;font-size:13px;line-height:1.6}.cv-entry,.cv-date{font-weight:600}.cv-date{color:#1f435b}.cv-empty{min-height:35px}[data-theme="dark"] #cv-profile h2,[data-theme="dark"] #cv-profile .cv-date{color:#a6c4d9}@media(max-width:600px){#cv-profile{padding:24px 20px}.cv-downloads a{padding:7px 12px}}@media print{.cv-controls,#site-nav,#site-footer{display:none}#cv-profile{box-shadow:none;border:0;padding:0}}''',encoding='utf-8')
print('Updated web CV and all four downloads')
