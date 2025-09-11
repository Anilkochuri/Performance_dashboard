import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
import plotly.express as px
import plotly.io as pio

# Existing app setup...

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    table_html = None
    charts_html = None

    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)

            # Table
            table_html = df.to_html(classes='table table-striped', index=False)

            # Charts
            fig1 = px.bar(df, x=df.columns[0], y=df.columns[1], title='Bar Chart')
            fig2 = px.pie(df, names=df.columns[0], values=df.columns[1], title='Pie Chart')
            fig3 = px.line(df, x=df.columns[0], y=df.columns[1], title='Line Chart')

            charts_html = pio.to_html(fig1, full_html=False) + pio.to_html(fig2, full_html=False) + pio.to_html(fig3, full_html=False)

    return render_template('dashboard.html', table=table_html, charts=charts_html)
