from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import geopandas as gpd

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
fig = px.bar(df, x="Classe Fundiaria", y="Area em Km2", color="Produto", barmode="group")
opcoes = list(df['Produto'].unique()) # Lista de opções da coluna 'Produto'. Sem repetição dos nomes.
opcoes.append('Todos os Produtos de Área Queimada')

###########
# Painel do Mapa:

# Arquivo csv oriundo do mapa de interesse:
df_map = pd.read_csv('https://raw.githubusercontent.com/arthurcito/app_dash_01/main/municipios_x_coded_csv.csv')
# Criação do GeoDataFrame. O arquivo geojson deve estar em WGS84:
gdf = gpd.read_file('https://github.com/arthurcito/app_dash_01/blob/7ff8884d51e7c21fb833c784c0ffc05e4102a63e/municipios_x_coded_wgs84.geojson').merge(df_map, on="nome").set_index("nome") # Mescla do gdf com o df_map.
# Criação da fig referente ao mapa:
fig_map = px.choropleth(gdf,
                   geojson=gdf.geometry,
                   locations=gdf.index,
                   color="coded_km2_x", # A variável 'color' não deve ser o nome da coluna original do dado, e sim o novo nome dado ao mesclar (merge) os dois dados.
                   color_continuous_scale="viridis",
                   labels = 'Teste',
                   projection="mercator")
fig_map.update_geos(fitbounds='locations', visible=False)
fig_map.update_layout(
    #plot_bgcolor=colors['background'], # Este update não teve resposta no plot do mapa.
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    template='plotly_dark' # Um dos templates padrão do plotly. Aqui teve uma resposta positiva no background do plot mapa.
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
        fig = px.bar(df, x="Classe Fundiaria", y="Area em Km2", color="Produto", barmode="group") # É necessário a reconstrução da fig aqui.
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    else:
        tabela_filtrada = df.loc[df['Produto']==value, :] # Argumentos do dc.loc == [linhas, colunas]
        fig = px.bar(tabela_filtrada, x="Classe Fundiaria", y="Area em Km2", color="Produto", barmode="group")
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
    return fig

if __name__ == '__main__':
    app.run_server(debug=False) # Manter 'debug=False'.
