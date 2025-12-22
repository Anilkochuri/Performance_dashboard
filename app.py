#!/usr/bin/env python3
import os, io, uuid
from types import SimpleNamespace
from typing import Dict, Any, List

from flask import (
    Flask, request, redirect, url_for, session, flash,
    render_template, send_file
)
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {"xlsx", "xls"}
CACHE: Dict[str, Dict[str, Any]] = {}

# -------------------- Utilities --------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_excel_sheets(file_bytes: bytes, ext: str) -> Dict[str, pd.DataFrame]:
    bio = io.BytesIO(file_bytes)
    engine = "openpyxl" if ext == "xlsx" else "xlrd"
    xls = pd.ExcelFile(bio, engine=engine)
    sheets_available = set(xls.sheet_names)

    def safe_read(name: str) -> pd.DataFrame:
        return xls.parse(name) if name in sheets_available else pd.DataFrame()

    return {
        "Observations": safe_read("Observations"),
        "Transaction Summary": safe_read("Transaction Summary"),
        "DB_HITS": safe_read("DB_HITS"),
        "Response Codes": safe_read("Response Codes") if "Response Codes" in sheets_available else pd.DataFrame(),
    }

DEF_COLS = {
    'txn': ['transaction name', 'transaction', 'txn', 'sampler', 'label'],
    'avg': ['average', 'avg', 'mean'],
    'p90': ['90 percent', '90%', 'p90', '90th percentile'],
    'pass': ['pass', 'passed'],
    'fail': ['fail', 'failed'],
}


def _pick_column(df: pd.DataFrame, keys) -> str:
    cols = [str(c).strip() for c in df.columns]
    lowered = [c.lower() for c in cols]
    # exact match
    for key in keys:
        kl = key.lower()
        for c, lc in zip(cols, lowered):
            if lc == kl:
                return c
    # substring match
    for key in keys:
        kl = key.lower()
        for c, lc in zip(cols, lowered):
            if kl in lc:
                return c
    return ''


def compute_observations_from_ts(ts_df: pd.DataFrame) -> Dict[str, Any]:
    obs = {"lt_5s":0, "between_5_10s":0, "gt_10s":0, "total_pass":0, "total_fail":0}
    if ts_df.empty:
        return obs
    df = ts_df.copy(); df.columns = [str(c).strip() for c in df.columns]
    avg_col = _pick_column(df, DEF_COLS['avg'])
    pass_col = _pick_column(df, DEF_COLS['pass'])
    fail_col = _pick_column(df, DEF_COLS['fail'])
    if avg_col:
        avg_vals = pd.to_numeric(df[avg_col], errors='coerce')
        obs['lt_5s'] = int((avg_vals < 5).sum())
        obs['between_5_10s'] = int(((avg_vals >= 5) & (avg_vals <= 10)).sum())
        obs['gt_10s'] = int((avg_vals > 10).sum())
    if pass_col:
        obs['total_pass'] = int(pd.to_numeric(df[pass_col], errors='coerce').fillna(0).sum())
    if fail_col:
        obs['total_fail'] = int(pd.to_numeric(df[fail_col], errors='coerce').fillna(0).sum())
    return obs


# -------------------- Routes --------------------
@app.route('/')
def home():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        if username == os.environ.get('DASH_USERNAME','admin') and password == os.environ.get('DASH_PASSWORD','password'):
            session['user'] = username
            session['sid'] = session.get('sid') or str(uuid.uuid4())
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Try admin / password (default).')
    return render_template('login.html')


@app.route('/logout')
def logout():
    sid = session.get('sid')
    if sid and sid in CACHE:
        CACHE.pop(sid, None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('user'):
        return redirect(url_for('login'))
    sid = session.get('sid')
    cache = CACHE.get(sid, {}) if sid else {}
    observations = cache.get('observations', {"lt_5s":0,"between_5_10s":0,"gt_10s":0,"total_pass":0,"total_fail":0})
    ts_rows = cache.get('ts_rows', [])
    ts_columns = cache.get('ts_columns', [])
    db_rows = cache.get('db_rows', [])
    db_columns = cache.get('db_columns', [])
    data_loaded = bool(ts_rows)
    return render_template(
        'dashboard.html',
        observations=SimpleNamespace(**observations),
        ts_rows=ts_rows,
        ts_columns=ts_columns,
        db_rows=db_rows,
        db_columns=db_columns,
        data_loaded=data_loaded,
    )


@app.route('/upload_xlsx', methods=['POST'])
def upload_xlsx():
    if not session.get('user'):
        return redirect(url_for('login'))
    if 'file' not in request.files:
        flash('No file part'); return redirect(url_for('dashboard'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file'); return redirect(url_for('dashboard'))
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload .xlsx or .xls'); return redirect(url_for('dashboard'))

    ext = file.filename.rsplit('.',1)[1].lower()
    file_bytes = file.read()
    try:
        sheets = read_excel_sheets(file_bytes, ext)
        ts_df = sheets.get('Transaction Summary', pd.DataFrame())
        db_df = sheets.get('DB_HITS', pd.DataFrame())
        # Observations computed from TS
        observations = compute_observations_from_ts(ts_df)

        ts_cols = [str(c).strip() for c in ts_df.columns]
        ts_rows = ts_df.fillna('').to_dict(orient='records') if not ts_df.empty else []
        db_cols = [str(c).strip() for c in db_df.columns]
        db_rows = db_df.fillna('').to_dict(orient='records') if not db_df.empty else []

        sid = session.get('sid') or str(uuid.uuid4()); session['sid'] = sid
        CACHE[sid] = {
            'observations': observations,
            'ts_rows': ts_rows,
            'ts_columns': ts_cols,
            'db_rows': db_rows,
            'db_columns': db_cols,
            'ts_df': ts_df,
            'db_df': db_df,
        }
        flash('Excel processed successfully.')
    except Exception as e:
        print('Upload XLSX error:', e)
        flash(f'Failed to process Excel: {e}')
    return redirect(url_for('dashboard'))


@app.route('/export_xlsx', methods=['GET'])
def export_xlsx():
    if not session.get('user'):
        return redirect(url_for('login'))
    sid = session.get('sid'); cache = CACHE.get(sid)
    if not cache:
        flash('No data to export. Upload Excel first.'); return redirect(url_for('dashboard'))

    from openpyxl import Workbook

    wb = Workbook()
    # Observations sheet
    ws_obs = wb.active; ws_obs.title = 'Observations'
    obs = cache.get('observations', {})
    ws_obs.append(['Metric', 'Count'])
    ws_obs.append(['< 5s', obs.get('lt_5s', 0)])
    ws_obs.append(['5–10s', obs.get('between_5_10s', 0)])
    ws_obs.append(['> 10s', obs.get('gt_10s', 0)])
    ws_obs.append(['Total Pass', obs.get('total_pass', 0)])
    ws_obs.append(['Total Fail', obs.get('total_fail', 0)])

    # Transaction Summary sheet
    ws_ts = wb.create_sheet('Transaction Summary')
    ts_df: pd.DataFrame = cache.get('ts_df', pd.DataFrame())
    if not ts_df.empty:
        ws_ts.append(list(ts_df.columns))
        for row in ts_df.fillna('').itertuples(index=False):
            ws_ts.append(list(row))

    # DB_HITS sheet
    ws_db = wb.create_sheet('DB_HITS')
    db_df: pd.DataFrame = cache.get('db_df', pd.DataFrame())
    if not db_df.empty:
        ws_db.append(list(db_df.columns))
        for row in db_df.fillna('').itertuples(index=False):
            ws_db.append(list(row))

    # Various Graphs placeholder
    ws_vg = wb.create_sheet('Various Graphs')
    ws_vg.append(['Info', 'Value'])
    ws_vg.append(['Charts will be embedded in next iteration', 1])

    bio = io.BytesIO(); wb.save(bio); bio.seek(0)
    return send_file(bio, as_attachment=True,
                     download_name='Performance_Dashboard_Export.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    if not session.get('user'):
        return redirect(url_for('login'))
    sid = session.get('sid'); cache = CACHE.get(sid)
    if not cache:
        flash('No data to export. Upload Excel first.'); return redirect(url_for('dashboard'))

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    styles = getSampleStyleSheet()
    bio = io.BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=A4)
    elements: List[Any] = []

    def add_title(t):
        elements.append(Paragraph(f"<b>{t}</b>", styles['Heading2']))
        elements.append(Spacer(1, 8))

    # Header
    elements.append(Paragraph('<b>Performance Dashboard</b>', styles['Title']))
    elements.append(Spacer(1, 12))

    # Observations
    add_title('Observations')
    obs = cache.get('observations', {})
    elements.append(Paragraph(
        f"<b>&lt; 5s:</b> {obs.get('lt_5s',0)} &nbsp;&nbsp; "
        f"<b>5–10s:</b> {obs.get('between_5_10s',0)} &nbsp;&nbsp; "
        f"<b>&gt; 10s:</b> {obs.get('gt_10s',0)} &nbsp;&nbsp; "
        f"<b>Total Pass/Fail:</b> {obs.get('total_pass',0)} / {obs.get('total_fail',0)}",
        styles['BodyText']
    ))
    elements.append(PageBreak())

    # Transaction Summary table (all rows)
    ts_df: pd.DataFrame = cache.get('ts_df', pd.DataFrame())
    if not ts_df.empty:
        add_title('Transaction Summary (all rows)')
        header = [str(c) for c in ts_df.columns]
        data_rows = ts_df.fillna('').astype(str).values.tolist()
        table_data = [header] + data_rows
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(table)
        elements.append(PageBreak())

    # DB_HITS table
    db_df: pd.DataFrame = cache.get('db_df', pd.DataFrame())
    if not db_df.empty:
        add_title('DB_HITS')
        header = [str(c) for c in db_df.columns]
        data_rows = db_df.fillna('').astype(str).values.tolist()
        table_data = [header] + data_rows
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(table)

    doc.build(elements)
    bio.seek(0)
    return send_file(bio, as_attachment=True,
                     download_name='Performance_Dashboard_Export.pdf',
                     mimetype='application/pdf')


@app.route('/version')
def version():
    return {'app': 'Performance Dashboard', 'version': 'v2.1-fixed'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT','5000')), debug=True)
