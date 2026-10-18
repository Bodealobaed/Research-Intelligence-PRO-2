# ATLAS Research Intelligence v2.0

An upgrade of the original Streamlit application, retaining `app.py`, `analyzer.py` and `report.py` and adding `science.py` and `medical.py`.

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

In Streamlit Community Cloud → App settings → Secrets, set:

```toml
OPENAI_API_KEY = "your-key-here"
```

**Never commit actual API keys** or patient data. There is intentionally no API key entry in the app UI. The server passes document excerpts to OpenAI only when the AI audit button is clicked.

## What's implemented

- Soft light teal/blue interface, enlarged colored ATLAS mark, Arabic/German/English navigation, language-selectable AI output and PDF.
- AI-generated scientific contribution, suggested project title, discussion, hypotheses and conclusions; explicit source coverage and quote validation.
- Extracted tables displayed alongside deterministic numeric summaries and downloadable CSVs. Numeric parser supports simple decimal commas and common unit suffixes; verify all extracted data.
- Extracted PDF/DOCX raster figures with descriptive pixel statistics (not chart-curve digitization).
- Research-only DICOM/NIfTI center-slice preview, metadata excluding names/IDs, adjustable pixel-threshold mask. **NOT anatomical segmentation or Parkinson diagnosis**.
- Explicitly hypothetical, user-parameterized linear what-if simulation with downloadable CSV. **NOT** trained simulation, COMSOL or a learned disease model.
- Two paginated PDF export modes: research audit and manuscript **draft**, with source quotes, warnings and references. Arabic text shaping is best-effort, and complex RTL/typography must be checked visually.
- API key read only from server-side Streamlit Secrets or environment.

## Important limitations and roadmap

1. **Medical models:** Clinically meaningful MRI/CT/SPECT/DaTSCAN segmentation requires modality-specific validated weights, appropriate preprocessing, ground truth and evaluation (e.g. MONAI / nnU-Net). The current threshold mask must not be used for diagnosis. MRI/CT do not directly reveal individual dying dopaminergic neurons.
2. **Chart digitization:** Extracted raster figures are shown, but axis calibration, curve tracing, error bars and scientific chart interpretation are not yet implemented. Image brightness is not an experimental measurement.
3. **True simulation:** Requires governing equations, boundary conditions, units, parameters and/or source simulation files. PDFs alone cannot reconstruct a valid finite-element model.
4. **References:** URLs and DOI text are detected. Full bibliography parsing, Crossref/OpenAlex matching and DOI verification are future work; an accessible link is not proof of a valid citation.
5. **Document coverage:** AI reads bounded excerpts (up to 145k characters, up to 6,500 per page). Not all pages of long documents may be analyzed; coverage is displayed.
6. **Privacy/security:** This application does not implement clinical-grade access controls, DICOM de-identification, GDPR compliance, patient record retention, or a data processing agreement. Avoid identifiable patient data on public hosting. Names and IDs are intentionally not displayed; their existence in uploaded files still makes them sensitive.
7. **Manuscript:** Drafts need real authors, accurate citations, figure permissions, ethics statements, review of statistical methods and journal-specific formatting. PDF alone does not imply publication readiness.
8. **OCR and vector charts:** Scanned PDFs, some vector graphics, image-based tables and DOCX diagrams may be missed.

## Safe deployment

Use a private repository if handling proprietary research code; keep `.streamlit/secrets.toml` out of Git. Use only licensed, non-identifiable example data on Streamlit Community Cloud. For identifiable medical data, a separately designed compliant infrastructure and legal review are necessary.

## Scientific book production (V2.1)

The **Book publishing studio** below the analysis tabs produces a **separate** book PDF, not a manuscript or audit. Select Arabic, German or English, click *Generate full book text*, review chapter text and title, then export A5 or A4. The workflow uses the server-side `OPENAI_API_KEY` and makes one paid model request per source chunk plus a conclusion request. It rejects documents exceeding 30 chunks rather than silently skipping material; split long theses into volumes. Figures and tables are appended in the book with source captions; their contents are **not automatically redrawn or translated**. Equations, image labels, bibliography entries, tables and references require editorial checking. Printed books may need a separate printer-specific full-bleed cover/spine PDF; this export supplies front/back pages but no calculated spine/bleed. All copyrights, author permissions, image permissions and attribution remain the user's responsibility. No scientific result is independently verified by this book-writing workflow.
