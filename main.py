import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go

import pandas as pd


class Data():
    df = pd.DataFrame({})

    def __init__(self) -> None:
        pass


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
            html.Div([
                dbc.Button("Eliminar filas o columnas vacías",
                           color="primary", className="mb-2 mt-2"),
                dbc.DropdownMenu(
                    label="Remplazar usando",
                    children=[
                        dbc.DropdownMenuItem("Media"),
                        dbc.DropdownMenuItem("Moda"),
                        dbc.DropdownMenuItem("Mediana"),
                    ],
                ),
                dbc.InputGroup(
                    [

                        dbc.Input(id="input-group-button-input",
                                  placeholder="Remplazar usando"),
                        dbc.Button("Remplazar",
                                   id="input-group-button", n_clicks=0),
                    ], className="mb-2 mt-2"
                )
            ]),
            html.Span("Columnas para graficar"),
            dcc.Dropdown(id="multiple-dynamic-dropdown", multi=True),
            html.Div(id='df-info')
        ],
            style={'width': '20%', 'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px', 'margin': '10px'}, body=True,),

        html.Div([html.Div(id='table-container')], style={'width': '80%'})
    ], style={'display': 'flex'}),
    html.Div(id='graphics')
])


def update_figure(df, col):
    if len(df.columns) == 1:
        fig = px.histogram(df)
    elif len(df.columns) == 2:
        if (df.dtypes[0] == 'object' and df.dtypes[1] == 'object'):
            fig = px.count_cat(df, x=df.columns[0], y=df.columns[1])
        elif (df.dtypes[0] == 'object' or df.dtypes[1] == 'object'):
            if df.dtypes[0] == 'object':
                fig = px.histogram(
                    df, x=df.columns[0], y=df.columns[1], color=df.columns[0])
            else:
                fig = px.histogram(
                    df, x=df.columns[1], y=df.columns[0], color=df.columns[1])
        else:
            fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
    else:
        fig = px.scatter_matrix(df)
    return fig


@app.callback(
        Output('df-info','children'),
        Input('dynamic-dropdown','value')
)
def update_df_info(col_name):
    result = []
    result.append("Información de la columna '{}':\n".format(col_name))
    result.append("Tipo de datos: {}\n".format(Data.df[col_name].dtype))
    result.append("Porcentaje de datos nulos: {:.2f}%\n".format((Data.df[col_name].isnull().sum() / Data.df.shape[0]) * 100))
    result.append("Columna vacía: {}".format("Sí" if Data.df[col_name].isnull().sum() == Data.df.shape[0] else "No"))
    return [ html.Div(val) for val in result]


@app.callback(
    Output('graphics', 'children'),
    [Input('multiple-dynamic-dropdown', 'value')]
)
def uodate_col(col):
    if len(col) == 0:
        print(col)
        return go.Figure()
    columns_to_plot = col
    df_plot = Data.df[columns_to_plot]
    fig = update_figure(df_plot, col)
    return dcc.Graph(figure=fig)


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

    Data.df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),delimiter=";")
    return (html.Div([
        html.H4(
            f'Tabla con los datos del archivo CSV subido ({Data.df.shape[0]} filas)'),
        dash_table.DataTable(
            data=Data.df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in Data.df.columns],
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
    ]), list(Data.df.columns), list(Data.df.columns)
    )


if __name__ == '__main__':

    app.run_server(debug=True)
