"""Reproducible, explicitly bounded research calculations; no autonomous clinical inference."""
import io, re
import numpy as np
import pandas as pd
from PIL import Image

def parse_numeric(value):
    s=str(value).strip().replace('−','-').replace(' ','')
    s=re.sub(r'(?i)(µm|μm|mm|cm|nm|pf/n|pf|nf|hz|khz|ms|mv|v|%|kg|mg|g|°c)$','',s).strip()
    if re.fullmatch(r'[-+]?\d{1,3}(?:\.\d{3})+,\d+',s): s=s.replace('.','').replace(',','.')
    elif re.fullmatch(r'[-+]?\d+,\d+',s): s=s.replace(',','.')
    try: return float(s) if re.fullmatch(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',s) else np.nan
    except (ValueError,TypeError): return np.nan

def table_insights(rows):
    """Only arithmetic summaries, not claims of significance or causal relationships."""
    if not rows: return [],pd.DataFrame()
    frame=pd.DataFrame(rows[1:],columns=[str(x or f'Column {i+1}') for i,x in enumerate(rows[0])]) if len(rows)>1 else pd.DataFrame(rows)
    out=[]
    for col in frame.columns:
        series=frame[col].map(parse_numeric).dropna()
        if len(series)<2: continue
        vals=series.to_numpy(dtype=float)
        out.append({'column':str(col),'n':len(vals),'min':float(np.min(vals)),'max':float(np.max(vals)),'mean':float(np.mean(vals)),'median':float(np.median(vals)),'std_sample':float(np.std(vals,ddof=1)),'unit':'as in source (verify)','status':'Descriptive arithmetic only; verify extracted cells, units, and independence.'})
    return out,frame

def simulate_linear(x0, rate, steps, step_size):
    """User-defined hypothetical sensitivity scenario, never fitted from PDF or clinical data."""
    xs=np.arange(int(steps)+1,dtype=float)*float(step_size)
    return pd.DataFrame({'input_delta':xs,'hypothetical_output':float(x0)+float(rate)*xs})

def image_measurements(blob):
    """Pixel-only diagnostics; not chart digitization or disease segmentation."""
    im=Image.open(io.BytesIO(blob)).convert('L')
    a=np.asarray(im,dtype=np.float32)
    return {'width_px':int(a.shape[1]),'height_px':int(a.shape[0]),'mean_gray_0_255':round(float(a.mean()),2),'std_gray':round(float(a.std()),2),'min_gray':int(a.min()),'max_gray':int(a.max())}

def threshold_mask(blob, threshold=128, invert=False):
    """Exploratory threshold-based pixel selection; never anatomical segmentation."""
    im=Image.open(io.BytesIO(blob)).convert('L')
    a=np.asarray(im,dtype=np.uint8)
    mask=a<int(threshold) if invert else a>=int(threshold)
    output=Image.fromarray((mask*255).astype('uint8'))
    b=io.BytesIO();output.save(b,format='PNG')
    return b.getvalue(),{'selected_pixels':int(mask.sum()),'fraction_selected':round(float(mask.mean()),5)}
