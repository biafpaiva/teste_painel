from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

from apps import brasil, municipios, home

app = Dash(__name__, suppress_callback_exceptions=True)

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Home      ", href="/home"),
        dbc.DropdownMenuItem("Brasil    ", href="/brasil"),
        dbc.DropdownMenuItem("Municipios      ", href="/municipios"),
    ],
    nav = True,
    in_navbar = True
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarToggler(id="navbar-toggler2"),
            dbc.Collapse(
                dbc.Nav(
                    [dropdown], className="ml-auto", navbar=True
                ),
                id="navbar-collapse2",
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

# embedding the navigation bar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/brasil':
        return brasil.layout
    elif pathname == '/municipios':
        return municipios.layout
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', debug=True)