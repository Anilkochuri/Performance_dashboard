from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERNAME = 'admin'
PASSWORD = 'password'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = None
    table_html = ''
    graph_json = ''
    pie_json = ''

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_csv(filepath)
            table_html = df.to_html(classes='table table-striped', index=False)

            fig_bar = px.bar(df, x=df.columns[0], y=df.columns[1], title='Bar Chart')
            graph_json = pio.to_json(fig_bar)

            fig_pie = px.pie(df, names=df.columns[0], values=df.columns[1], title='Pie Chart')
            pie_json = pio.to_json(fig_pie)

            data = df

    return render_template('dashboard.html', data=data, table_html=table_html, graph_json=graph_json, pie_json=pie_json)

@app.route('/export/excel')
def export_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[-1])
    df = pd.read_csv(filepath)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='data.xlsx', as_attachment=True)

@app.route('/export/csv')
def export_csv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[-1])
    return send_file(filepath, download_name='data.csv', as_attachment=True)

@app.route('/export/word')
def export_word():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[-1])
    df = pd.read_csv(filepath)

    doc = Document()
    doc.add_heading('CSV Data Export', 0)

    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col

    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return send_file(output, download_name='data.docx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
