from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import plotly.express as px
import plotly
import json
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(minutes=10)

# Global variable to store uploaded data
uploaded_data = pd.DataFrame()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session.permanent = True
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global uploaded_data
    table_html = None
    bar_chart = None
    pie_chart = None

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            uploaded_data = pd.read_csv(file)
            table_html = uploaded_data.to_html(classes='table table-striped', index=False)

            # Bar Chart
            if uploaded_data.shape[1] >= 2:
                bar_fig = px.bar(uploaded_data, x=uploaded_data.columns[0], y=uploaded_data.columns[1], title='Bar Chart')
                bar_chart = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)

            # Pie Chart
            if uploaded_data[uploaded_data.columns[0]].dtype == 'object':
                pie_data = uploaded_data[uploaded_data.columns[0]].value_counts().reset_index()
                pie_data.columns = ['Category', 'Count']
                pie_fig = px.pie(pie_data, names='Category', values='Count', title='Pie Chart')
                pie_chart = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)

    elif not uploaded_data.empty:
        table_html = uploaded_data.to_html(classes='table table-striped', index=False)

        # Bar Chart
        if uploaded_data.shape[1] >= 2:
            bar_fig = px.bar(uploaded_data, x=uploaded_data.columns[0], y=uploaded_data.columns[1], title='Bar Chart')
            bar_chart = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Pie Chart
        if uploaded_data[uploaded_data.columns[0]].dtype == 'object':
            pie_data = uploaded_data[uploaded_data.columns[0]].value_counts().reset_index()
            pie_data.columns = ['Category', 'Count']
            pie_fig = px.pie(pie_data, names='Category', values='Count', title='Pie Chart')
            pie_chart = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', table_html=table_html, bar_chart=bar_chart, pie_chart=pie_chart)

if __name__ == '__main__':
    app.run(debug=True)
