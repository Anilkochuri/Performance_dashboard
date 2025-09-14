from flask import Flask, render_template, request, send_file
import pandas as pd
import plotly.express as px
import plotly.io as pio
from io import BytesIO
from docx import Document

app = Flask(__name__)
dataframe = None

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    global dataframe
    error_message = None
    plot_div = None
    table_html = None

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            try:
                dataframe = pd.read_csv(file)

                # Group by 'label' and sum 'elapsed'
                grouped = dataframe.groupby('label')['elapsed'].sum().reset_index()

                # Bar chart
                bar_fig = px.bar(grouped, x='label', y='elapsed', title='Total Elapsed Time by Label')
                bar_div = pio.to_html(bar_fig, full_html=False)

                # Pie chart
                pie_fig = px.pie(grouped, names='label', values='elapsed', title='Elapsed Time Distribution by Label')
                pie_div = pio.to_html(pie_fig, full_html=False)

                plot_div = bar_div + pie_div
                table_html = dataframe.to_html(classes='table table-striped', index=False)
            except Exception as e:
                error_message = f"Error processing file: {str(e)}"
        else:
            error_message = "Please upload a valid CSV file."

    return render_template('dashboard.html', plot_div=plot_div, table_html=table_html, error_message=error_message)

@app.route('/export/<format>')
def export_data(format):
    global dataframe
    if dataframe is None:
        return "No data to export", 400

    buffer = BytesIO()

    if format == 'csv':
        dataframe.to_csv(buffer, index=False)
        buffer.seek(0)
        return send_file(buffer, mimetype='text/csv', as_attachment=True, download_name='dashboard_data.csv')

    elif format == 'excel':
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Dashboard')
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='dashboard_data.xlsx')

    elif format == 'word':
        doc = Document()
        doc.add_heading('Dashboard Data', level=1)
        table = doc.add_table(rows=1, cols=len(dataframe.columns))
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(dataframe.columns):
            hdr_cells[i].text = col
        for _, row in dataframe.iterrows():
            row_cells = table.add_row().cells
            for i, cell in enumerate(row):
                row_cells[i].text = str(cell)
        doc.save(buffer)
        buffer.seek(0)
        return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         as_attachment=True, download_name='dashboard_data.docx')

    else:
        return "Unsupported format", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
