from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        # Render dashboard.html with the uploaded data
        return render_template('dashboard.html', tables=[df.to_html(classes='data')], titles=df.columns.values)
    else:
        return "Invalid file format. Please upload a CSV.", 400

if __name__ == '__main__':
    app.run(debug=True)
