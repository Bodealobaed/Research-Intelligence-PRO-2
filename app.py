"""ATLAS Research Intelligence 2.0 — multilingual research workstation."""
import os, io, hashlib
import streamlit as st
import pandas as pd
from analyzer import extract_document, extract_links, verify_links, analyze_with_ai, basic_analysis
from report import build_pdf
from science import table_insights, simulate_linear, image_measurements, threshold_mask
from medical import read_medical_image
from book import create_book_content, build_book_pdf

st.set_page_config(page_title='ATLAS | Research Intelligence',page_icon='🧬',layout='wide')
I18N={
'English':{'settings':'Workspace settings','language':'Interface language','output':'Analysis / export language','model':'AI model','upload':'Upload a research project (PDF or DOCX)','run':'✦ Run scientific AI audit','inspect':'Inspect without AI','summary':'Research overview','methods':'Methods & quality','results':'Scientific value','tables':'Tables & calculations','figures':'Figures & image analysis','medical':'Medical imaging lab','simulation':'Simulation studio','refs':'References','export':'Evidence & export','missing':'Run an audit to populate this section','project':'Project title','download':'Download research PDF','manuscript':'Research manuscript draft','audit':'Scientific audit report','book':'Scientific book'},
'Deutsch':{'settings':'Arbeitsbereich','language':'Sprache der Oberfläche','output':'Analyse- / Berichtssprache','model':'KI-Modell','upload':'Forschungsprojekt hochladen (PDF oder DOCX)','run':'✦ Wissenschaftliche KI-Analyse starten','inspect':'Ohne KI prüfen','summary':'Forschungsüberblick','methods':'Methoden & Qualität','results':'Wissenschaftlicher Mehrwert','tables':'Tabellen & Berechnungen','figures':'Abbildungen & Bildanalyse','medical':'Medizinische Bildgebung','simulation':'Simulationsstudio','refs':'Literatur','export':'Belege & Export','missing':'Starten Sie eine Analyse','project':'Projekttitel','download':'Wissenschaftlichen PDF-Bericht herunterladen','manuscript':'Manuskriptentwurf','audit':'Wissenschaftlicher Analysebericht','book':'Wissenschaftliches Buch'},
'العربية':{'settings':'إعدادات مساحة العمل','language':'لغة الواجهة','output':'لغة التحليل والتقرير','model':'نموذج الذكاء الاصطناعي','upload':'حمّل مشروعًا بحثيًا PDF أو DOCX','run':'✦ ابدأ التدقيق العلمي بالذكاء الاصطناعي','inspect':'استعراض دون ذكاء اصطناعي','summary':'نظرة علمية عامة','methods':'المنهجية والجودة','results':'القيمة العلمية','tables':'الجداول والحسابات','figures':'الصور وتحليلها','medical':'مختبر الصور الطبية','simulation':'مختبر المحاكاة','refs':'المراجع','export':'الأدلة والتصدير','missing':'ابدأ التحليل لعرض النتائج','project':'عنوان المشروع','download':'تحميل التقرير العلمي PDF','manuscript':'مسودة ورقة علمية','audit':'تقرير تدقيق علمي','book':'كتاب علمي'}}
with st.sidebar:
    lang=st.selectbox('🌐 Interface / Oberfläche / الواجهة',list(I18N),index=0)
T=I18N[lang]
st.markdown('''<style>
.stApp{background:radial-gradient(ellipse at 92% 2%,#e3f1f2 0%,transparent 40%),linear-gradient(155deg,#edf2f7,#dce7ed);color:#203449}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#132b42,#1b3c51);border-right:2px solid #3d7380}
[data-testid="stSidebar"] *{color:#edf8fb!important}
[data-testid="stSidebar"] input,[data-testid="stSidebar"] [data-baseweb="select"] *{color:#182b3a!important}
[data-testid="stHeader"]{background:#edf2f7c9}
[data-testid="stMetric"]{background:#ffffffd9;padding:15px;border-radius:15px;border:1px solid #c6d8df}
h1,h2,h3{color:#17374d!important}
.hero{background:linear-gradient(112deg,#17384f,#1d6670);border-radius:22px;padding:25px 30px;color:#fff;margin:0 0 20px;box-shadow:0 12px 25px #234b5c30}
.hero h1,.hero p{color:#fff!important}.hero h1{font-size:36px;margin:6px 0}.hero p{opacity:.9}
.brand{font-size:39px;color:#70e2d4;vertical-align:middle;margin-right:12px}
.stButton>button[kind="primary"],.stDownloadButton>button{background:#187f89;color:#fff;border-radius:12px;border:0}
[data-testid="stTabs"] button{font-weight:650}
</style>''',unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<div style="font-size:30px;font-weight:800;color:#fff"><span style="font-size:42px;color:#72e6d3">◈</span> ATLAS</div><div style="letter-spacing:2px;font-size:11px">RESEARCH INTELLIGENCE · V2.0</div>',unsafe_allow_html=True)
    st.divider()
    target=st.selectbox(T['output'],['English','German','Arabic'],index={'English':0,'Deutsch':1,'العربية':2}[lang])
    model=st.selectbox(T['model'],['gpt-4.1-mini','gpt-4o-mini','gpt-4.1'])
    try: api_key=st.secrets.get('OPENAI_API_KEY','')
    except Exception: api_key=''
    api_key=api_key or os.environ.get('OPENAI_API_KEY','')
    st.caption('🔐 API credentials are configured server-side only (Streamlit Secrets).')
    check=st.checkbox('Verify reference URLs / روابط المراجع',False)
    st.warning('Research use only. Do not upload identifiable patient data to public hosting or external AI without required safeguards and permissions.')
st.markdown('<div class="hero"><h1><span class="brand">◈</span> ATLAS Research Intelligence</h1><p>Scientific evidence · Quantitative analysis · Multilingual manuscripts · Exploratory medical imaging</p><div style="color:#b8f5ee">العربية  ·  Deutsch  ·  English</div></div>',unsafe_allow_html=True)
upload=st.file_uploader(T['upload'],type=['pdf','docx'])
if upload:
    signature=hashlib.sha256(upload.getvalue()).hexdigest()
    if st.session_state.get('document_signature')!=signature:
        st.session_state['document_signature']=signature
        for k in ['analysis','doc','checks','book_content','book_signature']: st.session_state.pop(k,None)
        try: st.session_state['doc']=extract_document(upload)
        except Exception as exc: st.error(str(exc));st.stop()
    doc=st.session_state['doc'];links=extract_links(doc['text'])
    metrics=st.columns(4)
    for col,title,value in zip(metrics,['Pages','Tables','Figures','DOI / URLs'],[len(doc['pages']),len(doc['tables']),len(doc['images']),len(links)]): col.metric(title,value)
    st.caption(f'{doc["name"]} · {len(doc["text"]):,} characters extracted')
    c1,c2=st.columns(2)
    with c1:
        if st.button(T['run'],type='primary',use_container_width=True,disabled=not bool(api_key)):
            try:
                with st.spinner('Auditing source text…'):
                    st.session_state['analysis']=analyze_with_ai(doc,api_key,model,target)
                    st.session_state['analysis_language']=target
            except Exception as exc: st.error(f'AI analysis failed: {type(exc).__name__}: {exc}')
    with c2:
        if st.button(T['inspect'],use_container_width=True): st.session_state['analysis']=basic_analysis(doc)
    if not api_key: st.info('Configure OPENAI_API_KEY in Streamlit Cloud → App settings → Secrets to enable AI. No key is entered in the interface.')
    analysis=st.session_state.get('analysis')
else:
    doc=None;analysis=None;links=[]
    st.info('Upload a PDF/DOCX to explore its scientific evidence, or use the independent medical-image lab and simulation studio below.')

tab_names=[T[k] for k in ['summary','methods','results','tables','figures','medical','simulation','refs','export']]
tabs=st.tabs(tab_names)
with tabs[0]:
    if analysis:
        st.subheader(analysis.get('proposed_title') or T['summary'])
        st.write(analysis.get('executive_summary',''))
        for key in ['research_question','discipline','study_design','translation_notes']:
            with st.expander(key.replace('_',' ').title()):st.write(analysis.get(key,''))
    else: st.info(T['missing'])
with tabs[1]:
    if analysis:
        for key in ['methods','sample_and_materials','statistics','limitations','risk_of_bias','reproducibility']:
            st.markdown('#### '+key.replace('_',' ').title());st.write(analysis.get(key,''))
    else:st.info(T['missing'])
with tabs[2]:
    if analysis:
        for key in ['scientific_contribution','key_findings','clinical_findings','engineering_findings','pharmaceutical_findings','new_hypotheses','discussion','conclusion']:
            st.markdown('#### '+key.replace('_',' ').title());st.write(analysis.get(key,''))
        st.caption('AI-generated interpretations and hypotheses require verification. They are not measured experimental results.')
    else:st.info(T['missing'])
with tabs[3]:
    if doc and doc['tables']:
        for i,table in enumerate(doc['tables']):
            with st.expander(table['title'],expanded=i==0):
                insights,frame=table_insights(table['rows']);st.dataframe(frame,use_container_width=True)
                if insights:
                    st.write('Reproducible descriptive calculations (not inferential statistics)')
                    st.dataframe(pd.DataFrame(insights),use_container_width=True)
                    st.download_button('Download extracted table (CSV)',frame.to_csv(index=False).encode('utf-8-sig'),file_name=f'atlas_table_{i+1}.csv',key=f'table_{i}')
                else:st.caption('No numeric column with at least two reliably parsed values. Do not infer significance.')
    else:st.info('No extractable tables. Scanned or complex tables may require manual verification / OCR.')
with tabs[4]:
    if doc and doc['images']:
        for i,img in enumerate(doc['images']):
            with st.expander(img['label'],expanded=i==0):
                st.image(img['bytes'],caption=img['label'],width=650)
                st.json(image_measurements(img['bytes']))
                st.caption('Pixel statistics are not graph digitization. Axes, units, data points and plot curves require verified chart digitization.')
    else:st.info('No embedded raster images detected. Vector-only PDF graphics may need page rendering.')
with tabs[5]:
    st.markdown('### Research-only medical image preview')
    st.caption('DICOM and NIfTI supported. Patient names and IDs are intentionally suppressed. Age and modality may be displayed when available. No clinical diagnosis or validated disease segmentation.')
    medical_file=st.file_uploader('Upload DICOM / NIfTI',type=['dcm','dicom','nii','gz'],key='medical_upload')
    if medical_file:
        try:
            preview,metadata=read_medical_image(medical_file.name,medical_file.getvalue())
            st.image(preview,caption='Normalized central-slice preview',width=500)
            st.json(metadata)
            cutoff=st.slider('Exploratory pixel threshold',0,255,128,key='medical_threshold')
            mask,stats=threshold_mask(preview,cutoff)
            st.image(mask,caption='Threshold mask — NOT anatomical or Parkinson segmentation',width=500)
            st.json(stats)
            st.download_button('Download exploratory mask PNG',mask,'atlas_exploratory_mask.png','image/png')
        except Exception as exc:st.error(f'Image could not be processed: {exc}')
    st.warning('MRI/CT cannot directly identify individual dying dopaminergic neurons. Parkinson-related imaging requires modality-specific protocols, validated models, expert review and appropriate clinical context.')
with tabs[6]:
    st.markdown('### Transparent what-if model')
    st.caption('This is a user-parameterized linear scenario, NOT a fitted model or a COMSOL/finite-element simulation. No model is learned automatically from a thesis PDF.')
    p1,p2,p3,p4=st.columns(4)
    base=p1.number_input('Initial output',value=1.0)
    slope=p2.number_input('Output change per input unit',value=0.15)
    n=p3.number_input('Steps',min_value=2,max_value=1000,value=20)
    step=p4.number_input('Input step',min_value=0.00001,value=1.0)
    curve=simulate_linear(base,slope,n,step)
    st.line_chart(curve.set_index('input_delta'))
    st.download_button('Download simulated scenario CSV',curve.to_csv(index=False).encode('utf-8-sig'),'atlas_hypothetical_simulation.csv')
with tabs[7]:
    if links:
        st.dataframe(pd.DataFrame({'Reference URL / DOI':links}),use_container_width=True)
        if check and st.button('Check URLs',key='check_urls'):
            with st.spinner('Checking reference endpoints…'):st.session_state['checks']=verify_links(links)
        if st.session_state.get('checks'):st.dataframe(pd.DataFrame(st.session_state['checks']))
    else:st.info('No machine-readable URLs / DOIs detected. Print-only references may require a bibliography parser.')
    st.caption('URL accessibility does not establish bibliographic accuracy or scientific credibility.')
with tabs[8]:
    if analysis and doc:
        proposed=analysis.get('proposed_title') or os.path.splitext(doc['name'])[0]
        project_title=st.text_input(T['project'],value=proposed)
        report_type=st.radio('Export format',[T['audit'],T['manuscript']],horizontal=True)
        manuscript=report_type==T['manuscript']
        st.info('Manuscript export is an editable scientific DRAFT in content, not publication approval. Verify authorship, data rights, ethics, figures, statistics and references.')
        st.markdown('#### Page-anchored evidence')
        for i,item in enumerate(analysis.get('evidence',[])):
            if not isinstance(item,dict):continue
            mark='✓' if item.get('verified_quote') else '⚠'
            with st.expander(f'{mark} Page {item.get("page","?")} — {str(item.get("claim",""))[:90]}'):
                st.write(item.get('claim',''))
                st.code(item.get('excerpt',''))
                st.caption('Verbatim quote located in source page' if item.get('verified_quote') else 'Quote not verified verbatim — check original')
        for warning in analysis.get('warnings',[]):st.warning(str(warning))
        st.caption(analysis.get('_coverage',''))
        try:
            pdf=build_pdf(doc,analysis,links,title=project_title,manuscript=manuscript,language=target)
            st.download_button(T['download'],pdf,file_name='ATLAS_Research_Manuscript_DRAFT.pdf' if manuscript else 'ATLAS_Scientific_Audit.pdf',mime='application/pdf',type='primary',use_container_width=True)
        except Exception as exc:st.error(f'PDF export error: {exc}')
    else:st.info(T['missing'])

# Independent book-production workflow: no dependency on the audit/manuscript export.
st.divider()
st.header('📚 '+T['book']+' · Book publishing studio')
st.caption('Transforms a source document into book-style prose in a chosen language. This is a separate, paid API process; generation may require many calls. Source coverage and licensing must be checked.')
if doc:
    bc1,bc2=st.columns(2)
    with bc1:
        book_lang=st.selectbox('Book language / Buchsprache / لغة الكتاب',['Arabic','German','English'],index=1,key='book_language')
        trim=st.selectbox('Print page size / مقاس الطباعة',['A5','A4'],key='book_trim')
    with bc2:
        book_author=st.text_input('Author / Editor credit (verify rights)',value='Research adaptation',key='book_author')
        st.caption('Use the actual rights holder and accurate editorial attribution; do not replace the thesis author without permission.')
    if st.button('✦ Generate full book text / إنشاء نص الكتاب',type='primary',disabled=not bool(api_key),key='book_generate'):
        try:
            with st.spinner('Rewriting and translating all source chunks. API usage is billed per chunk…'):
                st.session_state['book_content']=create_book_content(doc,api_key,model,book_lang,analysis)
                st.session_state['book_signature']=(signature,book_lang)
        except Exception as exc:
            st.error(f'Book generation stopped: {type(exc).__name__}: {exc}')
    book=st.session_state.get('book_content')
    if book and st.session_state.get('book_signature')==(signature,book_lang):
        st.success('Book text prepared · '+book['coverage'])
        title=st.text_input('Editable book title / عنوان الكتاب',value=book['title'],key='book_title')
        book['title']=title
        st.write('Chapters:',len(book['chapters']))
        for i,ch in enumerate(book['chapters']):
            with st.expander(f'{i+1}. {ch["heading"]} · source page {ch["page"]}'):
                for paragraph in ch['paragraphs']:st.write(paragraph)
        show_tables=st.checkbox('Include extracted source tables',value=True,key='book_tables')
        show_figures=st.checkbox('Include extracted source figures',value=True,key='book_figures')
        try:
            book_pdf=build_book_pdf(doc,book,links,book_author,show_figures,show_tables,trim)
            st.download_button('📖 Download print-ready book PDF',book_pdf,'ATLAS_Scientific_Book_'+book_lang+'.pdf','application/pdf',type='primary',key='download_book')
            st.caption('Includes front cover, internal title page, page-numbered contents, book chapters, original tables/figures appendix, references, and back cover. For commercial printing, confirm bleed, spine width and printer specifications.')
        except Exception as exc:st.error(f'Book PDF error: {exc}')
    elif book:
        st.info('Language or source changed; generate a new book for this selection.')
else:
    st.info('Upload a source document to create a book.')
