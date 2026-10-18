"""Paginated research audit and clearly marked manuscript DRAFT PDFs."""
import io,os,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_RIGHT,TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from analyzer import SECTIONS

FONT_PATHS=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf']
font='Helvetica'
for path in FONT_PATHS:
    if os.path.exists(path):
        pdfmetrics.registerFont(TTFont('AtlasBodyFont',path));font='AtlasBodyFont';break

def shape(text):
    s=str(text or '')
    if re.search('[\u0600-\u06ff]',s):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return '\n'.join(get_display(arabic_reshaper.reshape(line)) for line in s.split('\n'))
        except ImportError:pass
    return s

def build_pdf(doc,analysis,links,title=None,manuscript=False,language='English'):
    out=io.BytesIO()
    project_title=title or analysis.get('proposed_title') or os.path.splitext(doc['name'])[0]
    pdf=SimpleDocTemplate(out,pagesize=(210*mm,297*mm),leftMargin=19*mm,rightMargin=19*mm,topMargin=23*mm,bottomMargin=21*mm,title=project_title)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='AtlasCover',fontName=font,fontSize=21,leading=30,textColor=colors.HexColor('#143a4b'),spaceAfter=14,alignment=TA_CENTER,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasSection',fontName=font,fontSize=12,leading=18,textColor=colors.HexColor('#0e7e88'),spaceBefore=12,spaceAfter=6,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasText',fontName=font,fontSize=9,leading=15,textColor=colors.HexColor('#273a4a'),spaceAfter=8,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='AtlasNote',fontName=font,fontSize=8,leading=12,textColor=colors.HexColor('#52677a'),spaceAfter=8,wordWrap='CJK'))
    def para(s,style='AtlasText'):
        return Paragraph(escape(shape(str(s))[:30000]).replace('\n','<br/>'),styles[style])
    story=[Spacer(1,25*mm),para('◈ ATLAS  |  RESEARCH INTELLIGENCE','AtlasCover'),para(project_title,'AtlasCover'),Spacer(1,8*mm),para('SCIENTIFIC MANUSCRIPT — UNREVIEWED DRAFT' if manuscript else 'EVIDENCE-BASED RESEARCH AUDIT','AtlasSection'),para('Document: '+doc['name'],'AtlasNote'),para('Language: '+language+'  |  AI-assisted; author verification required','AtlasNote'),para('This is not a peer-reviewed publication or a clinical certification. Authorship, ethics, permissions, numerical results and references must be checked before submission.','AtlasNote'),PageBreak()]
    if manuscript:
        sections=[('Abstract','abstract'),('1. Introduction / Research question','research_question'),('2. Materials and methods','methods'),('2.1 Samples and materials','sample_and_materials'),('2.2 Statistical methods','statistics'),('3. Results','key_findings'),('3.1 Scientific contribution','scientific_contribution'),('4. Discussion','discussion'),('4.1 Limitations','limitations'),('5. Conclusion','conclusion')]
    else: sections=[(key.replace('_',' ').title(),key) for key in SECTIONS]
    for heading,key in sections:
        story.extend([para(heading,'AtlasSection'),para(analysis.get(key,'Not reported'))])
    story.append(para('Page-anchored evidence','AtlasSection'))
    for item in analysis.get('evidence',[])[:45]:
        if isinstance(item,dict):
            story.append(para(f"Page {item.get('page','?')} · {'Exact quote located' if item.get('verified_quote') else 'UNVERIFIED QUOTE'} · {item.get('claim','')}",'AtlasNote'))
            story.append(para(item.get('excerpt','')))
    story.append(para('References — extracted, not necessarily verified','AtlasSection'))
    for url in links[:90]:story.append(para(url,'AtlasNote'))
    story.append(para('Methodological transparency','AtlasSection'))
    story.append(para(analysis.get('_coverage','Not specified')))
    for warning in analysis.get('warnings',[]):story.append(para('Warning: '+str(warning),'AtlasNote'))
    def footer(canvas,doc_):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#bdd3d9'));canvas.line(19*mm,17*mm,191*mm,17*mm)
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#57717e'))
        canvas.drawString(19*mm,12*mm,'ATLAS | Research draft · verify before publication')
        canvas.drawRightString(191*mm,12*mm,str(doc_.page))
        canvas.restoreState()
    pdf.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()
