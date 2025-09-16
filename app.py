from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    chart = None
    if request.method            filename = secure_filename(file.filename)
            df = pd.read_csv(file)

            if 'Category' in df.columns and 'ElapsedTime' in df.columns:
                fig = px.bar(df, x='Category', y='ElapsedTime', title='Average Elapsed Time by Category')
                chart = fig.to_html(full_html=False)
                session['data'] = df.to_json()
            else:
                flash('CSV must contain Category and ElapsedTime columns')
        else:
            flash('Invalid file format. Please upload a CSV.')

    return render_template('dashboard.html', chart=chart)

@app.route('/export/csv')
def export_csv():
    if not session.get('logged_in') or 'data' not in session:
        return redirect(url_for('login'))

    df = pd.read_json(session['data'])
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name='export.csv')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)