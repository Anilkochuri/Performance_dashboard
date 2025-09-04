from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import io
from werkzeug.utils import secure_filename
from docx import Document

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USER_CREDENTIALS = {
    'admin': 'password123'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USER_CREDENTIALS.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    data = None
    table_html = None
    graph_json = None
    pie_json = None

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            data = pd.read_csv(filepath)
            table_html = data.to_html(classes='table table-striped', index=False)

            numeric_cols = data.select_dtypes(include='number').columns
            if len(numeric_cols) >= 2:
                fig = px.bar(data, x=numeric_cols[0], y=numeric_cols[1], title='Bar Chart')
                graph_json = pio.to_json(fig)

            if len(numeric_cols) >= 1:
                fig_pie = px.pie(data, names=numeric_cols[0], title='Pie Chart')
                pie_json = pio.to_json(fig_pie)

            session['data'] = data.to_json()

    return render_template('dashboard.html', table=table_html, graph_json=graph_json, pie_json=pie_json)

@app.route('/export/<format>')
def export(format):
    if 'username' not in session or 'data' not in session:
        return redirect(url_for('login'))

    data = pd.read_json(session['data'])

    if format == 'csv':
        output = io.StringIO()
        data.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='data.csv')

    elif format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='data.xlsx')

    elif format == 'word':
        doc = Document()
        doc.add_heading('Exported Data', 0)
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
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document', as_attachment=True, download_name='data.docx')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
