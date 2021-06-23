import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from Calculadora_TL import Calculadora_TL

app = dash.Dash(__name__)
calculadora_tl = Calculadora_TL('/content/TABLA MATERIALES TP1.xlsx')
data = calculadora_tl.data
available_indicators = data.material.unique()

app.layout = html.Div([
html.H1("Calculadora de TL"),
    html.Div([

        html.Div([
            html.P(id = 'text-material',children = 'Material'),
            dcc.Dropdown(
                id='material',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Acero'
            ),
            html.Div([
                html.P(id = 'text-dimensiones',children = 'Dimensiones'),
                dcc.Input(
                    id='largo',
                    placeholder='Largo',
                    type='number',
                    value='Largo'
                    ),
                dcc.Input(
                    id='alto',
                    placeholder='Alto',
                    type='number',
                    value='Alto'),
                dcc.Input(
                    id='espesor',
                    placeholder='Ancho',
                    type='number',
                    value='Ancho')
            ]),      
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
             html.Button('Exportar', id='boton_exportar'), dcc.Download(id="exportar"),
             dcc.Checklist(    
                 id='metodos',          
                options=[
                    {'label': 'Primera ley de masa', 'value': 'ley1'},
                    {'label': 'Sharp', 'value': 'sharp'},
                    {'label': 'ISO', 'value': 'ISO'},
                    {'label': 'Davy', 'value': 'davy'}
                ],
                labelStyle={'display': 'block'},
                style={'marginBottom': 50, 'marginTop': 25})
        ],style={'width': '30%', 'float': 'right', 'display': 'inline-block'}),
    ]),

    dcc.Graph(id='indicator-graphic')

])

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('material', 'value'),
    Input('alto', 'value'),
    Input('largo', 'value'),
    Input('espesor', 'value'),
    Input('metodos', 'value'))
def update_graph(material,alto,largo,espesor,metodos):

    calculadora_tl = Calculadora_TL(data_path='/content/TABLA MATERIALES TP1.xlsx',
                                    t=espesor,
                                    l1=largo, l2=alto)
    resultados = calculadora_tl.calcular_r(material, metodos)
    resultados['frecuencia'] = calculadora_tl.f
    colors = px.colors.qualitative.Plotly
    resultados_df = pd.DataFrame(resultados)
    fig = go.Figure()
    # Edit the layout
    fig.update_layout(title='R calculados para diferentes metodos',
                   xaxis_title='Frecuencias (Hz)',
                   yaxis_title='Nivel (dB)')
    for i, x in enumerate(metodos):
        fig.add_traces(go.Scatter(x=resultados['frecuencia'], y = resultados[x],
                                  mode = 'lines+markers', line=dict(color=colors[i]),
                                  name=x))
    fig.show()
    return fig

@app.callback(
    Output("exportar", "data"),
    Input('boton_exportar', 'n_clicks'),
    Input('material', 'value'),
    Input('alto', 'value'),
    Input('largo', 'value'),
    Input('espesor', 'value'),
    Input('metodos', 'value'),
    prevent_initial_call=True,)
def download_func(boton_exportar, material, alto, largo, espesor, metodos):
    calculadora_tl = Calculadora_TL(data_path='/content/TABLA MATERIALES TP1.xlsx',
                                    t=espesor,
                                    l1=largo, l2=alto)
    resultados = calculadora_tl.calcular_r(material, metodos)
    resultados['frecuencia'] = calculadora_tl.f
    colors = px.colors.qualitative.Plotly
    resultados_df = pd.DataFrame(resultados)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'boton_exportar' in changed_id:
        return dcc.send_data_frame(resultados_df.to_csv, "resultados.csv")

if __name__ == '__main__':
    app.run_server(debug=True)