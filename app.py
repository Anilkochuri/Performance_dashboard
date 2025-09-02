from flask import Flask, request, redirect, url_for, session, render_template_string
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table, Input, Output, State
import io, base64

# Flask server setup
server = Flask(__name__)
server.secret_key = 'your_secret_key'  # Required for session management

# Dash app setup
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')
df = pd.DataFrame()

# Dash layout
app.layout = html.Div([
    html.H2("Performance Dashboard", style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Upload CSV'),
        multiple=False,
        style={'margin': '10px auto', 'display': 'block'}
    ),
    html.Div(id='file-upload-status'),
    html.Div([
        html.Label("Filter by Label"),
        dcc.Dropdown(id='label-filter', multi=True)
    ], style={'margin': '10px'}),
    html.Div([
        html.Label("Filter by Response Code"),
        dcc.Dropdown(id='response-filter', multi=True)
    ], style={'margin': '10px'}),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart'),
    dash_table.DataTable(
        id='data-table',
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        filter_action='native',
        sort_action='native'
    )
])

# Callback to update dashboard after CSV upload
@app.callback(
    Output('file-upload-status', 'children'),
    Output('label-filter', 'options'),
    Output('response-filter', 'options'),
    Output('label-filter', 'value'),
    Output('response-filter', 'value'),
    Output('data-table', 'columns'),
    Output('data-table', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_dashboard(contents, filename):
    if contents is None:
        return "", [], [], [], [], [], []

    content_type, content_string = contents.split(',')
    decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
    global df
    df = pd.read_csv(decoded)

    label_options = [{'label': lbl, 'value': lbl} for lbl in df['label'].dropna().unique()]
    response_options = [{'label': str(code), 'value': code} for code in df['responseCode'].dropna().unique()]
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    return f"Uploaded {filename}", label_options, response_options, [], [], columns, data

# Callback to update charts based on filters
@app.callback(
    Output('bar-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Input('label-filter', 'value'),
    Input('response-filter', 'value')
)
def update_charts(selected_labels, selected_codes):
    filtered_df = df.copy()
    if selected_labels:
        filtered_df = filtered_df[filtered_df['label'].isin(selected_labels)]
    if selected_codes:
        filtered_df = filtered_df[filtered_df['responseCode'].isin(selected_codes)]

    bar_fig = px.bar(filtered_df, x='label', y='elapsed', title='Elapsed Time per Label')
    pie_fig = px.pie(filtered_df, names='success', title='Success vs Failure')

    return bar_fig, pie_fig

# Flask route for login
@server.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect('/dashboard/')
        else:
            return render_template_string(login_template, error="Invalid credentials")
    return render_template_string(login_template)

# Flask route for dashboard access control
@server.route('/dashboard/')
def dashboard_redirect():
    if not session.get('logged_in'):
        return redirect('/')
    return app.index()

# Login page HTML template
login_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial; background-color: #f4f4f4; text-align: center; padding-top: 100px; }
        form { background: white; padding: 20px; display: inline-block; border-radius: 8px; box-shadow: 0 0 10px #ccc; }
        input { margin: 10px; padding: 10px; width: 200px; }
        .error { color: red; }
    </style>
</head>
<body>
    <form method="POST">
        <h2>Login to Dashboard</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <input type="text" name="username" placeholder="Username" required /><br/>
        <input type="password" name="password" placeholder="Password" required /><br/>
        <input type="submit" value="Login" />
    </form>
</body>
</html>
"""

# Run the Flask server
if __name__ == '__main__':
    server.run(debug=True)
