from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import json
from urllib.request import urlopen

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # Marcação CSS externa para criação de estilos de layout.

app = Dash(__name__, external_stylesheets=external_stylesheets)

colors = { # Definindo variáveis de coloração do estilo do dashboard.
    'background': '#202c33',
    'text': '#e9edef'
}

###########
# Painel do Gráfico:

# 'df' é a base de dados que alimenta o dashboard:
df = pd.read_csv('https://raw.githubusercontent.com/arthurcito/app_dash_01/main/produtos_x_classes_fundiarias.csv')

# 'fig' é quem está criand o gráfico:
fig = px.bar(df, x="Classe Fundiária", y="Área em Km2", color="Produto", barmode="group")
opcoes = list(df['Produto'].unique()) # Lista de opções da coluna 'Produto'. Sem repetição dos nomes.
opcoes.append('Todos os Produtos de Área Queimada')

###########
# Painel do Mapa:

# Arquivo csv oriundo do mapa de interesse:
df_map = pd.read_csv('https://raw.githubusercontent.com/arthurcito/app_dash_01/main/municipios_x_coded_csv.csv')
df_map.rename(columns={'geocodigo':'id'}, inplace=True)
with urlopen('https://raw.githubusercontent.com/arthurcito/app_dash_01/main/mun_rr.json') as response:
    geo_json_rr = json.load(response)
geo_json_rr

# Criação da fig referente ao mapa:
fig_map = px.choropleth_mapbox(df_map,
                         geojson = geo_json_rr,
                         locations='id',
                         featureidkey = 'properties.id',
                         color = 'coded_km2',
                         hover_name = 'nome',
                         hover_data = ['coded_km2'],
                         color_continuous_scale='Viridis',
                         mapbox_style = 'carto-darkmatter', #defining a new map style
                         center = {'lat':0.4, 'lon': -61.0},
                         zoom = 5.5,
                         opacity = 0.8, )
fig.update_geos(fitbounds = 'locations', visible = False)
fig_map.update_layout(
    #plot_bgcolor=colors['background'], # Este update não teve resposta no plot do mapa.
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    #template='plotly_dark' # Um dos templates padrão do plotly. Aqui teve uma resposta positiva no background do plot mapa.
)
fig_map.layout.coloraxis.colorbar.title = 'Cicatrizes de Fogo (km²)' #Modifica o título da barra de legenda da coloração.


###########
# O dashboard terá componentes de html (partes fixas, textos e imagens) e de dcc (gráfico, interações):
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div([
        # Div do cabeçalho:
            html.H1(
                children='Cicatrizes de Fogo nas Florestas da Região Sul de Roraima',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
    ]),
    html.Div([
        # Div do Gráfico:
        html.Div([
            html.Div(
                children='Escolha um Produto de Área Queimada:',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
            # Componente que ativa o dropdown:
            dcc.Dropdown(opcoes, style={'background':colors['background'], 'font-size':20},
                         value='Todos os Produtos de Área Queimada', id='lista_produtos'),

            # 'dcc' é dash component core. Tudo que está relacionado aos gráficos é oriundo desta biblioteca:
            dcc.Graph(
                id='grafico_cicatrizes_x_classes',
                figure=fig
            ),
        ], className='six columns'), # O layout de uma tela tem 12 colunas. Aqui configuramos por CSS que metade será desta primeira Div.
        # Nova Div para o Mapa:
        html.Div([ # Criação da Div referente ao mapa coroplético.
            html.Div(
                children='Mapa da Região Sul de Roraima:',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
            dcc.Graph(
                id='mapa_coropletico',
                figure=fig_map),
        ],  className='six columns'), # Marcação CSS das outras 6 colunas da tela para a segunda fig = fig_map.
    ], className='row'),
])

##########
# Callback para escolher as opções de visualização do Gráfico:
@app.callback( # Decorator.
    Output('grafico_cicatrizes_x_classes', 'figure'),
    Input('lista_produtos', 'value')
)
def update_output(value):
    if value=='Todos os Produtos de Área Queimada':
        fig = px.bar(df, x="Classe Fundiária", y="Área em Km2", color="Produto", barmode="group") # É necessário a reconstrução da fig aqui.
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    else:
        tabela_filtrada = df.loc[df['Produto']==value, :] # Argumentos do dc.loc == [linhas, colunas]
        fig = px.bar(tabela_filtrada, x="Classe Fundiária", y="Área em Km2", color="Produto", barmode="group")
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    return fig

if __name__ == '__main__':
    app.run_server(debug=False) # Manter 'debug=False'.
