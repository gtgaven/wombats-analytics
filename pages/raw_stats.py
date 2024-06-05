import dash
from dash import html, dcc, Input, Output, callback
from database_connection import DbConnection
import dash_bootstrap_components as dbc

db = DbConnection('softball_readonly', 'softballrules!')

dash.register_page(__name__, path='/raw')

seasons = db.get_seasons()
most_recent_season = seasons[len(seasons)-1]


raw_stats_bar = dbc.NavbarSimple(
    children=[
        html.Div([
            'Season:',
            dcc.Dropdown(
                options=seasons,
                id='raw-stats-season-select',
                value=most_recent_season,
                style={"color": "#000000"}
            )],
            style={"width": "200px", "color":"#fff", "padding-right": "20px"}
        )
    ],
    brand="West Building Wombats",
    brand_href="/",
    color="#696969",
    dark=True
)


layout = html.Div([
    raw_stats_bar,
    html.Div(id='raw-stats')
])


@callback(
    Output(component_id='raw-stats', component_property='children'),
    Input(component_id='raw-stats-season-select', component_property='value')
)
def update_raw_stats(season):
    if not season:
        return

    layout = []

    for game_id in reversed(db.get_game_ids_in_season(season)):
        raw_stats = db.get_raw_stats_from_game_id(game_id)
        
        header = f' {season} Game#{raw_stats["game_num"]}'
        if (raw_stats["was_home"]):
            header += f' vs {raw_stats["opponent"]}'
        else:
            header += f' @ {raw_stats["opponent"]}'

        rows = []
        for stat in list(raw_stats["stats"]):
            rows.append(html.Tr([html.Td(i) for i in stat]))

        layout.append(
            html.Div([
            html.H3(header),
            html.Table(
                [html.Tr([html.Th(col) for col in ['Player', 'PA', 'R', 'SF', 'BB', 'K', '1B', '2B', '3B', 'HR']]) ] +
                rows
            )])
        )

    return layout