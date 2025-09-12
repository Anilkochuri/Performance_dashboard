from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import plotly.express as px
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from openpyxl import Workbook
from docx import Document

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy credentials for login
USERNAME = 'admin'
PASSWORD = 'password'

# Check allowed file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# Route for dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = None
    table_html = None
    chart_json = None
    chart_png = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                df = pd.read_csv(filepath)
                table_html = df.to_html(classes='table table-striped', index=False)

                # Generate bar chart for first numeric column
                numeric_cols = df.select_dtypes(include='number').columns
                if not numeric_cols.empty:
                    fig = px.bar(df, x=df.index, y=numeric_cols[0], title=f'Bar Chart of {numeric_cols[0]}')
                    chart_json = fig.to_json()
                    chart_png = f"{numeric_cols[0]}_chart.png"
                    fig.write_image(chart_png)

                data = df
            except Exception as e:
                flash(f"Error processing file: {e}")

    return render_template('dashboard.html', table_html=table_html, chart_json=chart_json, chart_png=chart_png)

# Route to export data to Excel
@app.route('/export/excel')
def export_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[0]))
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return send_file(output, download_name='data.xlsx', as_attachment=True)
    except Exception as e:
        flash(f"Error exporting to Excel: {e}")
        return redirect(url_for('dashboard'))

# Route to export data to CSV
@app.route('/export/csv')
def export_csv():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[0]))
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, download_name='data.csv', as_attachment=True)
    except Exception as e:
        flash(f"Error exporting to CSV: {e}")
        return redirect(url_for('dashboard'))

# Route to export data to Word
@app.route('/export/word')
def export_word():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(UPLOAD_FOLDER)[0]))
        doc = Document()
        doc.add_heading('Data Export', 0)

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
    except Exception as e:
        flash(f"Error exporting to Word: {e}")
        return redirect(url_for('dashboard'))

# Route to logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
