from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import numpy as np
import pandas as pd

from datetime import datetime, timedelta

PROPORCAO_HABITANTES = 100000

#--------------- Carrega dados ---------
# Dados da Covid-19
df_municipios = pd.read_csv('../dados/df_municipios_semana.csv')
df_municipios =  df_municipios.rename(columns={'regiao': 'Região', 'data': 'Semana', 'estado': 'Estado'})
df_municipios.Semana = pd.to_datetime(df_municipios.Semana, infer_datetime_format=True)
df_municipios['Taxa de óbitos novos'] = round(df_municipios.obitosNovos / df_municipios.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_covid_base = df_municipios.sort_values('Semana')

df_brasil = df_municipios.groupby(['Semana']).agg({'populacaoTCU2019': 'sum', 'obitosNovos': 'sum', 'obitosAcumulado': 'sum'}).reset_index()
df_brasil['Região'] = 'Brasil'
df_regioes = df_municipios.groupby(['Região', 'Semana']).agg({'populacaoTCU2019': 'sum', 'obitosNovos': 'sum', 'obitosAcumulado': 'sum'}).reset_index()

df_brasil['Taxa de óbitos novos'] = round(df_brasil.obitosNovos / df_brasil.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_regioes['Taxa de óbitos novos'] = round(df_regioes.obitosNovos / df_regioes.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_brasil['Taxa de óbitos acumulados'] = round(df_brasil.obitosAcumulado / df_brasil.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_regioes['Taxa de óbitos acumulados'] = round(df_regioes.obitosAcumulado / df_regioes.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_brasil_regioes = pd.concat([df_regioes, df_brasil])

df_municipios_acumulado = df_municipios[df_municipios.Semana == df_municipios.Semana.max()][['codmun', 'municipio', 'Região', 'Estado', 'obitosAcumulado', 'populacaoTCU2019']]
df_municipios_acumulado['Taxa de óbitos acumulados'] = round(df_municipios_acumulado.obitosAcumulado / df_municipios_acumulado.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_municipios_acumulado = df_municipios_acumulado.sort_values('Região')

# Dados socioeconomicos
df_base =  pd.read_csv('../dados/df_base_selecionada.csv')
df_base = df_base.dropna()
df_base = df_base.rename(columns={'IDHM_EDUCACAO': 'IDHM - Educação', 'IDHM_LONGEVIDADE': 'IDHM - Longevidade',
                                  'IDHM_RENDA': 'IDHM - Renda', 'GINI': 'Gini',
                                  'TRANSFERENCIA_PERCAPTA_BOLSA_FAMILIA': 'Trans. per capita Bolsa Família',
                                  'TAXA_ATIVIDADE': 'Taxa de atividade',
                                  'PERCENTUAL_TRABALHADORES_INFORMAIS': '% trabalhadores informais',
                                  'PERCENTUAL_OCUPADOS_AGROPECUARIA': '% ocupados na agropecuária',
                                  'PERCENTUAL_OCUPADOS_COMERCIO': '% ocupados no comércio',
                                  'PERCENTUAL_OCUPADOS_SERVICO': '% ocupados no sertor de serviço',
                                  'PERCENTUAL_OCUPADOS_INDUSTRIA': '% ocupados na indústria',
                                  'PERCENTUAL_POPULACAO_URBANA': '% população urbana'})
df_municipios_acumulado = df_municipios_acumulado.merge(df_base, how='left', left_on='codmun', right_on='CODIGO_MUNICIPIO_6')

semanas = df_brasil['Semana'].values
data_inicio = df_brasil.Semana.min()
data_fim = df_brasil.Semana.max()

inicio_primeira_onda = datetime.strptime('2020-03-29', '%Y-%m-%d')
fim_primeira_onda = datetime.strptime('2020-11-01', '%Y-%m-%d')
inicio_segunda_onda = datetime.strptime('2020-11-08', '%Y-%m-%d')
fim_segunda_onda = datetime.strptime('2021-12-26', '%Y-%m-%d')
inicio_terceira_onda = datetime.strptime('2022-01-02', '%Y-%m-%d')
fim_terceira_onda = datetime.strptime('2022-04-23', '%Y-%m-%d')

#--------------- Testes ---------

marcadores = {}
for i in range(0, len(semanas), 8):
    data_timestamp = (semanas[i] - np.datetime64('1970-01-01')) / np.timedelta64(1, 's')
    data = datetime.utcfromtimestamp(data_timestamp)
    marcadores[i] = data.strftime('%d/%m/%y')

data_fim_slider = pd.to_datetime(data_fim) + pd.DateOffset(days=7)
marcadores[len(semanas)] = data_fim_slider.strftime('%d/%m/%y')

seletor_periodo = dcc.RangeSlider(0, len(semanas), 1, marks=marcadores, value=[0, len(semanas)], allowCross=False, id='seletor_periodo')

#----------------Cria gráficos ----------------
def get_periodo_selecionado(seletor_periodo_valor):
    seletor_periodo_inicio = seletor_periodo_valor[0]
    if seletor_periodo_inicio < len(semanas):
        periodo_selecionado_inicio = semanas[seletor_periodo_inicio]
    else:
        periodo_selecionado_inicio = data_fim_slider

    seletor_periodo_fim = seletor_periodo_valor[1]
    if seletor_periodo_fim < len(semanas):
        periodo_selecionado_fim = semanas[seletor_periodo_fim]
    else:
        periodo_selecionado_fim = data_fim_slider

    timestamp_periodo_selecionado_inicio = (periodo_selecionado_inicio - np.datetime64(
        '1970-01-01')) / np.timedelta64(1, 's')
    datetime_periodo_selecionado_inicio = datetime.utcfromtimestamp(timestamp_periodo_selecionado_inicio)
    timestamp_periodo_selecionado_fim = (periodo_selecionado_fim - np.datetime64(
        '1970-01-01')) / np.timedelta64(1, 's')
    datetime_periodo_selecionado_fim = datetime.utcfromtimestamp(timestamp_periodo_selecionado_fim)

    return datetime_periodo_selecionado_inicio, datetime_periodo_selecionado_fim

def get_representacao_ondas_series_temporais(periodo_selecionado_fim, periodo_selecionado_inicio):
    anotacoes_ondas = []
    quadros_ondas = []
    if (((inicio_primeira_onda >= periodo_selecionado_inicio) & (inicio_primeira_onda <= periodo_selecionado_fim)) |
            ((fim_primeira_onda >= periodo_selecionado_inicio) & (fim_primeira_onda <= periodo_selecionado_fim)) |
            ((periodo_selecionado_inicio >= inicio_primeira_onda) & (periodo_selecionado_fim <= fim_primeira_onda))):
        maximo_inicio = max(inicio_primeira_onda, periodo_selecionado_inicio)
        minimo_fim = min(fim_primeira_onda, periodo_selecionado_fim)

        delta = minimo_fim - maximo_inicio
        x = maximo_inicio + timedelta(days=delta.days / 2)

        anotacoes_ondas.append(dict(
            x=x,
            y=0,
            arrowcolor="rgba(63, 81, 181, 0)",
            ax=0,
            ay=30,
            text="Primeira onda",
            xref="x",
            yanchor="bottom",
            yref="y"
        ))

        quadros_ondas.append(
            dict(
                fillcolor="rgba(63, 81, 181, 0.2)",
                line={"width": 0},
                type="rect",
                x0=maximo_inicio,
                x1=minimo_fim,
                xref="x",
                y0=0,
                y1=0.95,
                yref="paper"
            ))
    if (((inicio_segunda_onda >= periodo_selecionado_inicio) & (inicio_segunda_onda <= periodo_selecionado_fim)) |
            ((fim_segunda_onda >= periodo_selecionado_inicio) & (fim_segunda_onda <= periodo_selecionado_fim)) |
            ((periodo_selecionado_inicio >= inicio_segunda_onda) & (periodo_selecionado_fim <= fim_segunda_onda))):
        maximo_inicio = max(inicio_segunda_onda, periodo_selecionado_inicio)
        minimo_fim = min(fim_segunda_onda, periodo_selecionado_fim)

        delta = minimo_fim - maximo_inicio
        x = maximo_inicio + timedelta(days=delta.days / 2)

        anotacoes_ondas.append(dict(
            x=x,
            y=0,
            arrowcolor="rgba(63, 81, 181, 0)",
            ax=0,
            ay=30,
            text="Segunda onda",
            xref="x",
            yanchor="bottom",
            yref="y"
        ))

        quadros_ondas.append(
            dict(
                fillcolor="rgba(76, 175, 80, 0.1)",
                line={"width": 0},
                type="rect",
                x0=maximo_inicio,
                x1=minimo_fim,
                xref="x",
                y0=0,
                y1=0.95,
                yref="paper"
            ))
    if (((inicio_terceira_onda >= periodo_selecionado_inicio) & (inicio_terceira_onda <= periodo_selecionado_fim)) |
            ((fim_terceira_onda >= periodo_selecionado_inicio) & (fim_terceira_onda <= periodo_selecionado_fim)) |
            ((periodo_selecionado_inicio >= inicio_terceira_onda) & (periodo_selecionado_fim <= fim_terceira_onda))):
        maximo_inicio = max(inicio_terceira_onda, periodo_selecionado_inicio)
        minimo_fim = min(fim_terceira_onda, periodo_selecionado_fim)

        delta = minimo_fim - maximo_inicio
        x = maximo_inicio + timedelta(days=delta.days / 2)

        anotacoes_ondas.append(dict(
            x=x,
            y=0,
            arrowcolor="rgba(63, 81, 181, 0)",
            ax=0,
            ay=30,
            text="Terceira onda",
            xref="x",
            yanchor="bottom",
            yref="y"
        ))

        quadros_ondas.append(
            dict(
                fillcolor="rgba(63, 81, 181, 0.2)",
                line={"width": 0},
                type="rect",
                x0=maximo_inicio,
                x1=minimo_fim,
                xref="x",
                y0=0,
                y1=0.95,
                yref="paper"
            ))
    return anotacoes_ondas, quadros_ondas

dropdowns = html.Div([

    #dropdown 1
    html.Div([
    dcc.Dropdown(
    df_municipios['municipio'].unique(),
    id='filter-y1')],
        style={'width': '49%', 'display': 'inline-block'}),

    #dropdown 2
    html.Div([
    dcc.Dropdown(
    df_municipios['municipio'].unique(),
    id='filter-y2')],
        style={'width': '49%', 'display': 'inline-block'})

])

@callback(Output('figura_1', 'figure'),
          Output('figura_2', 'figure'),
          Input('seletor_periodo', 'value'),
          Input('filter-y1', 'value'),
          Input('filter-y2', 'value'),
        )

def evento_filtragem(valor_seletor_periodo, value1, value2):
    periodo_selecionado_inicio, periodo_selecionado_fim = get_periodo_selecionado(valor_seletor_periodo)

    anotacoes_ondas, quadros_ondas = get_representacao_ondas_series_temporais(periodo_selecionado_fim, periodo_selecionado_inicio)

    df_municipios_periodo_selecionado_fim = df_municipios[df_municipios.Semana == df_municipios[df_municipios.Semana < periodo_selecionado_fim].Semana.max()][
        ['codmun', 'municipio', 'Região', 'Estado', 'Taxa de óbitos novos', 'Semana']]
    df_municipios_periodo_selecionado_inicio = df_municipios[df_municipios.Semana == periodo_selecionado_inicio][
        ['codmun', 'municipio', 'Região', 'Estado', 'Taxa de óbitos novos', 'Semana']]
    df_municipios_periodo_selecionado = df_municipios_periodo_selecionado_fim.merge(df_municipios_periodo_selecionado_inicio, how='left', left_on='codmun', right_on='codmun')

    figura_1 = get_figura_1(df_municipios_periodo_selecionado, anotacoes_ondas, quadros_ondas, value1)
    figura_2 = get_figura_2(df_municipios_periodo_selecionado, anotacoes_ondas, quadros_ondas, value2)

    return figura_1, figura_2

def get_figura_1(df, anotacoes_ondas, quadros_ondas, value):
    df_filtered = df[df['municipio'] == value]
    figura_1 = px.line(df_filtered,
                    x='Semana',
                    y='Taxa de óbitos novos',
                    width=664,
                    height=432,
                    title='Novos óbitos por semana')

    figura_1.update_traces(line_color='#0000ff')


    figura_1.update_layout(
        annotations=anotacoes_ondas,
        shapes=quadros_ondas
    )

    return figura_1


def get_figura_2(df, anotacoes_ondas, quadros_ondas, value):
    df_filtered = df[df['municipio'] == value]
    figura_2 = px.line(df_filtered,
                    x='Semana',
                    y='Taxa de óbitos novos',
                    width=664,
                    height=432,
                    title='Novos óbitos por semana')

    figura_2.update_traces(line_color='#0000ff')


    figura_2.update_layout(
        annotations=anotacoes_ondas,
        shapes=quadros_ondas
    )

    return figura_2

# ----------------Exibir painel Covid-BR ------------------

layout = html.Div([

    html.Label('Período: ', style={'display': 'inline-block'}),
    seletor_periodo,
    dropdowns,

    ##### #gráfico1
    html.Div([
        dcc.Graph(id='figura_1'), ],
        style={'display': 'inline-block', 'width': '49%'}),

    # gráfico2
    html.Div([
        dcc.Graph(id='figura_2'), ],
        style={'display': 'inline-block', 'width': '49%'}),
    ])
