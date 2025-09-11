from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Hardcoded credentials
USERNAME = 'admin'
PASSWORD = 'password'

@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@app.route('/signin', methods=['GET', 'POST'])  # Alias route
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            return render_template('dashboard.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
        else:
            flash('Please upload a valid CSV file.', 'error')
            return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
