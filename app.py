from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Hardcoded credentials
USERNAME = 'admin'
PASSWORD = 'password'

@app.route('/')
def home():
    if 'username' in session:
        return render_template('dashboard.html')  # Replace with your actual dashboard template
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
            return render_template('login.html')  # Replace with your actual login template
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # Replace with your actual 404 template

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500  # Replace with your actual 500 template

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
