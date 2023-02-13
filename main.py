import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arrastra o ',
            html.A('Selecciona un archivo')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),

])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'No se puede procesar el archivo.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.Div([
            html.Div([
                dcc.Input(
                    id="input",
                    type="text",
                    placeholder="input type text",
                ),
                 dcc.Input(
                    id="input",
                    type="number",
                    placeholder="input type number",
                )

            ], style={'width': '30%', 'borderWidth': '1px',
                      'borderStyle': 'dashed',
                      'borderRadius': '5px', }),
            dash_table.DataTable(
                df.to_dict('records'),
                [{'name': i, 'id': i} for i in df.columns],
                style_table={'height': '100%',
                             'overflowY': 'auto', 'with': '100%'},
                fixed_rows={'headers': True},
                sort_action="native",
                sort_mode='multi',
                row_selectable='multi',
                row_deletable=True,
                selected_rows=[],
                filter_action="native",
            ),

        ], style={'display': 'flex', 'width': '100%'}),


        html.Hr(),  # horizontal line

    ], style={'width': '100%'})


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)
