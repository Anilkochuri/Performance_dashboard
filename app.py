from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy credentials
USERNAME = 'admin'
PASSWORD = 'password'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            session['data'] = df.to_json()
            return redirect(url_for('dashboard'))
        return render_template('upload.html', error='Please upload a CSV file')
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    df = pd.read_json(session['data'])
    table_html = df.to_html(classes='table table-striped', index=False)
    pie_data = df.iloc[:, -1].value_counts()

    # Pie chart
    fig, ax = plt.subplots()
    pie_data.plot.pie(autopct='%1.1f%%', ax=ax)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    pie_chart_data = img.getvalue().decode('latin1')

    return render_template('dashboard.html', table=table_html, pie_chart=pie_chart_data)

@app.route('/export/<format>')
def export(format):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    df = pd.read_json(session['data'])
    buffer = io.BytesIO()

    if format == 'csv':
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='data.csv', mimetype='text/csv')
    elif format == 'excel':
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='data.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return "Invalid format"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
