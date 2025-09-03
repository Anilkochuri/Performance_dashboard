from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome {session['username']} to the dashboard!"
    else:
        return redirect(url_for('login'))

# Add other routes like login, logout, upload, etc. here

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
