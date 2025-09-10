from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

# Dummy login credentials
USERNAME = 'admin'
PASSWORD = 'password'

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    return "Invalid credentials", 401

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        return render_template('dashboard.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
    return "Invalid file format. Please upload a CSV.", 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
