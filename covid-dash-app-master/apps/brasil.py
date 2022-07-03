from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

PROPORCAO_HABITANTES = 100000

#--------------- Carrega dados ---------
# Dados da Covid-19
df_municipios = pd.read_csv('../dados/df_municipios_semana.csv')
df_municipios =  df_municipios.rename(columns={'regiao': 'Região', 'data': 'Semana', 'estado': 'Estado'})
df_municipios.Semana = pd.to_datetime(df_municipios.Semana, infer_datetime_format=True)
df_covid_base = df_municipios.sort_values('Semana')

df_brasil = df_municipios.groupby(['Semana']).agg({'populacaoTCU2019': 'sum', 'obitosNovos': 'sum', 'obitosAcumulado': 'sum'}).reset_index()
df_brasil['Região'] = 'Brasil'
df_regioes = df_municipios.groupby(['Região', 'Semana']).agg({'populacaoTCU2019': 'sum', 'obitosNovos': 'sum', 'obitosAcumulado': 'sum'}).reset_index()

df_brasil['Taxa de óbitos novos'] = round(df_brasil.obitosNovos / df_brasil.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_regioes['Taxa de óbitos novos'] = round(df_regioes.obitosNovos / df_regioes.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_brasil['Taxa de óbitos acumulados'] = round(df_brasil.obitosAcumulado / df_brasil.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
df_regioes['Taxa de óbitos acumulados'] = round(df_regioes.obitosAcumulado / df_regioes.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)

df_brasil['Óbitos novos'] = df_brasil.obitosNovos
df_regioes['Óbitos novos'] = df_regioes.obitosNovos
df_brasil['Óbitos acumulados'] = df_brasil.obitosAcumulado
df_regioes['Óbitos acumulados'] = df_regioes.obitosAcumulado

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

#---------------Componentes de filtros ------------


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

@callback(Output('figura_novos_obitos', 'figure'),
          Output('figura_obitos_acumulados', 'figure'),
          Output('figura_dispersao_obitos', 'figure'),
          Output('figura_boxplot','figure'),
          Output('figura_tabela','figure'),
          [Input('seletor_periodo', 'value')])
def evento_filtragem(valor_seletor_periodo):
    periodo_selecionado_inicio, periodo_selecionado_fim = get_periodo_selecionado(valor_seletor_periodo)

    anotacoes_ondas, quadros_ondas = get_representacao_ondas_series_temporais(periodo_selecionado_fim, periodo_selecionado_inicio)

    df_brasil_regioes_filtrado = df_brasil_regioes[(df_brasil_regioes['Semana'] >= periodo_selecionado_inicio) & (
                df_brasil_regioes['Semana'] < periodo_selecionado_fim)]
    figura_novos_obitos = get_figura_novos_obitos(df_brasil_regioes_filtrado, anotacoes_ondas, quadros_ondas)

    df_semana_anterior_periodo_selecionado_inicio = df_brasil_regioes[df_brasil_regioes['Semana'] == periodo_selecionado_inicio]
    df_semana_anterior_periodo_selecionado_inicio['TAXA_OBITOS_ACUMULADOS_SEMANA_ANTERIOR'] = df_semana_anterior_periodo_selecionado_inicio['Taxa de óbitos acumulados'] - df_semana_anterior_periodo_selecionado_inicio['Taxa de óbitos novos']
    df_semana_anterior_periodo_selecionado_inicio = df_semana_anterior_periodo_selecionado_inicio[['Região', 'TAXA_OBITOS_ACUMULADOS_SEMANA_ANTERIOR']]
    df_brasil_regioes_filtrado = df_brasil_regioes_filtrado.merge(df_semana_anterior_periodo_selecionado_inicio, how='left', left_on='Região', right_on='Região')
    df_brasil_regioes_filtrado['Taxa de óbitos acumulados no período'] = df_brasil_regioes_filtrado['Taxa de óbitos acumulados'] - df_brasil_regioes_filtrado['TAXA_OBITOS_ACUMULADOS_SEMANA_ANTERIOR']
    figura_obitos_acumulados = get_figura_obitos_acumulados(df_brasil_regioes_filtrado, anotacoes_ondas, quadros_ondas)

    df_municipios_periodo_selecionado_fim = df_municipios[df_municipios.Semana == df_municipios[df_municipios.Semana < periodo_selecionado_fim].Semana.max()][
        ['codmun', 'municipio', 'Região', 'Estado', 'obitosAcumulado', 'populacaoTCU2019', 'Semana']]
    df_municipios_periodo_selecionado_inicio = df_municipios[df_municipios.Semana == periodo_selecionado_inicio]
    df_municipios_periodo_selecionado_inicio['OBITOS_ACUMULADOS_SEMANA_ANTERIOR'] = df_municipios_periodo_selecionado_inicio['obitosAcumulado'] - df_municipios_periodo_selecionado_inicio['obitosNovos']
    df_municipios_periodo_selecionado_inicio = df_municipios_periodo_selecionado_inicio[['codmun', 'OBITOS_ACUMULADOS_SEMANA_ANTERIOR']]
    df_municipios_periodo_selecionado = df_municipios_periodo_selecionado_fim.merge(df_municipios_periodo_selecionado_inicio, how='left', left_on='codmun', right_on='codmun')
    df_municipios_periodo_selecionado['Óbitos acumulados no período'] = df_municipios_periodo_selecionado['obitosAcumulado'] - df_municipios_periodo_selecionado['OBITOS_ACUMULADOS_SEMANA_ANTERIOR']
    df_municipios_periodo_selecionado['Taxa de óbitos acumulados no período'] = round(df_municipios_periodo_selecionado['Óbitos acumulados no período'] / df_municipios_periodo_selecionado.populacaoTCU2019 * PROPORCAO_HABITANTES, 2)
    df_municipios_periodo_selecionado = df_municipios_periodo_selecionado.sort_values('Região')
    df_municipios_periodo_selecionado = df_municipios_periodo_selecionado.merge(df_base, how='left', left_on='codmun', right_on='CODIGO_MUNICIPIO_6')

    figura_dispersao_obitos = get_figura_figura_dispersao_obitos(df_municipios_periodo_selecionado)

    figura_boxplot = get_figura_boxplot(df_municipios_periodo_selecionado)

    figura_tabela = get_figura_tabela(periodo_selecionado_inicio, periodo_selecionado_fim)

    return figura_novos_obitos, figura_obitos_acumulados, figura_dispersao_obitos, figura_boxplot, figura_tabela

def get_figura_novos_obitos(df, anotacoes_ondas, quadros_ondas):
    figura_novos_obitos = px.line(df,
                                   x='Semana',
                                   y='Taxa de óbitos novos',
                                   color='Região',
                                   width=864,
                                   height=432,
                                   hover_data=['Óbitos novos'],
                                   title='Novos óbitos por semana')
    figura_novos_obitos.update_layout(
        xaxis_title=None,
        yaxis_title='Taxa de mortalidade por 100 mil habitantes',
        legend_title=None
    )
    # figura_novos_obitos.update_xaxes(rangeslider_visible=True)

    figura_novos_obitos.update_layout(
        annotations=anotacoes_ondas,
        shapes=quadros_ondas
    )

    return figura_novos_obitos


def get_figura_obitos_acumulados(df, anotacoes_ondas, quadros_ondas):


    figura_obitos_acumulados = px.line(df,
                                       x='Semana',
                                       y='Taxa de óbitos acumulados no período',
                                       color='Região',
                                       width=864,
                                       height=432,
                                       hover_data=['Óbitos acumulados'],
                                       title='Óbitos acumulados no período')
    figura_obitos_acumulados.update_layout(
        xaxis_title=None,
        yaxis_title='Taxa de mortalidade por 100 mil habitantes',
        legend_title=None
    )
    # figura_obitos_acumulados.update_xaxes(rangeslider_visible=True)

    figura_obitos_acumulados.update_layout(
        annotations=anotacoes_ondas,
        shapes=quadros_ondas
    )

    return figura_obitos_acumulados

# Dispersão mortalidade x atributo socioeconomico
def get_figura_figura_dispersao_obitos(df):
    figura_dispersao_obitos = px.scatter(df,
                                         x='% ocupados na agropecuária',
                                         y='Taxa de óbitos acumulados no período',
                                         color='Região',
                                         hover_name='municipio',
                                         hover_data=['Estado', 'Região', 'Óbitos acumulados no período'],
                                         width=460,
                                         height=420,
                                         title='Análise da correlação')
    figura_dispersao_obitos.update_layout(
        xaxis_title='% ocupados na agropecuária',
        yaxis_title='Taxa de mortalidade por 100 mil hab.',
        legend_title=None
    )

    list_dict_botoes = []

    for coluna in df_base.columns.sort_values():
        if coluna != 'CODIGO_MUNICIPIO_6':
            dict_botao = dict(
                        args=[{"x": [df_municipios_acumulado[coluna]]},
                              {'xaxis.title':coluna}],
                        label=coluna,
                        method="update"
                    )
            list_dict_botoes.append(dict_botao)

    botoes = list(list_dict_botoes)

    figura_dispersao_obitos.update_layout(
        updatemenus=[
            dict(
                buttons=botoes,
                direction="down",
                pad={"r": 0, "t": 0},
                showactive=True,
                x=-0.25,
                xanchor="left",
                y=1.18,
                yanchor="top"
            )
        ])

    return figura_dispersao_obitos


# Boxplot por região
def get_figura_boxplot(df):
    figura_boxplot = px.box(df,
                            x='Região',
                            y='Taxa de óbitos acumulados no período',
                            color='Região',
                            hover_name='municipio',
                            hover_data=['Estado', 'Região', 'Óbitos acumulados no período'],
                            width=663,
                            height=420,
                            title='Análise da distribuição')
    figura_boxplot.update_layout(
        xaxis_title=None,
        yaxis_title='Taxa de mortalidade por 100 mil hab.',
        legend_title=None
    )
    return figura_boxplot

# Tabela com dados gerais
def get_figura_tabela(periodo_selecionado_inicio, periodo_selecionado_fim):
    total_obitos_periodo_selecionado_fim = df_brasil[df_brasil.Semana == df_brasil[df_brasil.Semana < periodo_selecionado_fim].Semana.max()].obitosAcumulado.values[0]
    total_obitos_periodo_selecionado_inicio = df_brasil[df_brasil.Semana == periodo_selecionado_inicio].obitosAcumulado.values[0]
    total_obitos_periodo_selecionado = total_obitos_periodo_selecionado_fim - total_obitos_periodo_selecionado_inicio
    taxa_mortalidade = round(total_obitos_periodo_selecionado / df_brasil.populacaoTCU2019.values[0] * PROPORCAO_HABITANTES, 2)

    tabela = go.Table(cells=dict(values=[
        ['Período:', 'Localidade(s):', 'Total de óbitos:', 'Taxa de mortalidade:'],
        [periodo_selecionado_inicio.strftime('%d/%m/%Y')+' até '+periodo_selecionado_fim.strftime('%d/%m/%Y'), 'Brasil', str(total_obitos_periodo_selecionado), str(taxa_mortalidade)+' por 100 mil habitantes']],
        fill=dict(color=['paleturquoise', 'white']),
        align=['right', 'left']
    ))
    figura_tabela = go.Figure(data=tabela)
    figura_tabela.layout['template']['data']['table'][0]['header']['fill']['color']='rgba(0,0,0,0)'
    figura_tabela.update_layout(width=640, height=420, title_text="Resumo da mortalidade no período")

    return figura_tabela

#----------------Exibir painel Covid-BR ------------------

layout = html.Div([
    html.H4("Painel da Mortalidade por Covid-19 no Brasil"),
    html.Label('Período: ', style={'display': 'inline-block'}),
    seletor_periodo,
    html.Div(children=[
        dcc.Graph(id='figura_novos_obitos', style={'display': 'inline-block'}),
        dcc.Graph(id='figura_obitos_acumulados', style={'display': 'inline-block'})
    ]),
    html.Div(children=[
        dcc.Graph(id='figura_dispersao_obitos', style={'display': 'inline-block'}),
        dcc.Graph(id='figura_boxplot', style={'display': 'inline-block'}),
        dcc.Graph(id='figura_tabela', style={'display': 'inline-block'})
    ])
])
