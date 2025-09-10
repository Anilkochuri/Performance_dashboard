from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import plotly.express as px
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Login credentials
USERNAME = 'admin'
PASSWORD = 'admin123'

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        if user == USERNAME and pwd == PASSWORD:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    chart = None
    table = None
    filename = None
    error = None

    if request.method == 'POST':
        try:
            file = request.files.get('file')
            if not file or not file.filename.endswith('.csv'):
                error = "Please upload a valid CSV file."
            else:
                df = pd.read_csv(file)
                filename = file.filename
                table = df.to_html(classes='table table-striped', index=False)

                # Chart rendering
                if df.shape[1] >= 2:
                    try:
                        chart = px.bar(df, x=df.columns[0], y=df.columns[1])
                        chart = chart.to_html(full_html=False)
                    except Exception as chart_error:
                        error = f"Chart rendering failed: {chart_error}"

                session['data'] = df.to_json()
        except Exception as e:
            error = f"Error processing file: {e}"

    return render_template('dashboard.html', chart=chart, table=table, filename=filename, error=error)

@app.route('/export/<format>')
def export(format):
    if 'data' not in session:
        return redirect(url_for('dashboard'))

    df = pd.read_json(session['data'])

    buffer = io.BytesIO()
    if format == 'csv':
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name='export.csv')
    elif format == 'excel':
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='export.xlsx')
    elif format == 'word':
        return "Word export not implemented yet."

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('data', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)