import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

import pandas as pd

df: pd.DataFrame
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arrastra y suelta o ',
            html.A('selecciona un archivo CSV', className="")
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
        multiple=False
    ),
    html.Div([
        dbc.Card([
            html.Span("Columna a limpiar", style={
                "margin-top": "10vh"
            }),
            dcc.Dropdown(id="dynamic-dropdown"),
            html.Span("Columnas para graficar"),
            dcc.Dropdown(id="multiple-dynamic-dropdown", multi=True)

        ],
            style={'width': '20%', 'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px', 'margin': '10px'}, body=True,),
        html.Div([html.Div(id='table-container')], style={'width': '80%'})
    ], style={'display': 'flex'})
])


@app.callback(
    (Output('table-container', 'children'),
     Output('dynamic-dropdown', 'options'),
     Output('multiple-dynamic-dropdown', 'options')),
    [Input('upload-data', 'contents')]
)
def update_output(contents):
    if contents is None:
        return (html.Div([]), [], [])

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return (html.Div([
        html.H4(
            f'Tabla con los datos del archivo CSV subido ({df.shape[0]} filas)'),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            fixed_rows={'headers': True},
            sort_action="native",
            sort_mode='multi',
            row_selectable='multi',
            row_deletable=True,
            selected_rows=[],
            filter_action="native",
            export_format='csv',
            export_headers='display',
            style_table={}
        )
    ]), list(df.columns), list(df.columns)
    )


if __name__ == '__main__':

    app.run_server(debug=True)
