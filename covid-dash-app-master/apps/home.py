from dash import html
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Bem vindo ao dashboard da COVID-19", className="text-center")
                    , className="mb-5 mt-5")
        ]),

        dbc.Row([
            dbc.Col(html.H5(children='Ele consiste em duas páginas principais: Brasil, que mostra uma visão geral da COVID-19 no pais, '
                                     'e Municipios, que possibilita a seleção de municipios para comparar.')
                    , className="mb-5")
        ]),

        dbc.Row([
            dbc.Col(html.H5(children='Alunos: Abner, Beatriz, Cybele, Helder, Selene')
                    , className="mb-5")
        ])
    ])

])