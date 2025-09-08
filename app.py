
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import plotly.express as px
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy credentials
USERNAME = 'admin'
PASSWORD = 'password'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid credentials')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('index'))

    data = None
    table_html = None
    graph_html = None
    pie_html = None

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            data = pd.read_csv(filepath)

            # Generate table
            table_html = data.to_html(classes='table table-striped', index=False)

            # Generate bar chart
            if not data.empty:
                numeric_cols = data.select_dtypes(include='number').columns
                if len(numeric_cols) >= 2:
                    fig = px.bar(data, x=numeric_cols[0], y=numeric_cols[1])
                    graph_html = fig.to_html(full_html=False)

                # Generate pie chart
                if len(numeric_cols) >= 1:
                    fig_pie = px.pie(data, names=numeric_cols[0])
                    pie_html = fig_pie.to_html(full_html=False)

    return render_template('dashboard.html', table=table_html, graph=graph_html, pie=pie_html)

@app.route('/export/<format>')
def export(format):
    if 'logged_in' not in session:
        return redirect(url_for('index'))

    # Load the latest uploaded file
    files = os.listdir(UPLOAD_FOLDER)
    if not files:
        return 'No file uploaded yet.'

    latest_file = max([os.path.join(UPLOAD_FOLDER, f) for f in files], key=os.path.getctime)
    data = pd.read_csv(latest_file)

    if format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, download_name='data.xlsx', as_attachment=True)

    elif format == 'csv':
        output = io.StringIO()
        data.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), download_name='data.csv', as_attachment=True)

    elif format == 'word':
        from docx import Document
        doc = Document()
        doc.add_heading('Data Export', 0)
        table = doc.add_table(rows=1, cols=len(data.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(data.columns):
            hdr_cells[i].text = col
        for _, row in data.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        return send_file(output, download_name='data.docx', as_attachment=True)

    return 'Unsupported format.'

if __name__ == '__main__':
    app.run(debug=True)
