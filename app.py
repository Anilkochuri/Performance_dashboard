from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import plotly.express as px
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global variable to store uploaded data
data = pd.DataFrame()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Simple authentication (replace with real logic)
        if username == 'admin' and password == 'admin':
           ('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    global data
    chart_html = ''
    if not data.empty:
        fig = px.bar(data, x=data.columns[0], y=data.columns[1])
        chart_html = fig.to_html(full_html=False)
    return render_template('dashboard.html', chart=chart_html)

@app.route('/upload', methods=['POST'])
def upload():
    global data
    if 'file' not in request.files:
        return redirect(url_for('dashboard'))
    file = request.files['file']
    if file.filename.endswith('.csv'):
        data = pd.read_csv(file)
    return redirect(url_for('dashboard'))

@app.route('/export/<format>')
def export(format):
    global data
    if data.empty:
        return redirect(url_for('dashboard'))
    buffer = io.BytesIO()
    if format == 'csv':
        buffer.write(data.to_csv(index=False).encode())
        buffer.seek(0)
        return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name='data.csv')
    elif format == 'excel':
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='data.xlsx')
    elif format == 'word':
        # Placeholder for Word export logic
        buffer.write(b'Word export not implemented yet.')
        buffer.seek(0)
        return send_file(buffer, mimetype='application/msword', as_attachment=True, download_name='data.doc')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
