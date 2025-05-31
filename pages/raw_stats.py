import dash
from dash import html, dcc, Input, Output, callback
from database_connection import DbConnection
import dash_bootstrap_components as dbc
from nav_bar import get_nav_bar

db = DbConnection()

dash.register_page(__name__, path='/raw-data')

seasons = db.get_seasons()
most_recent_season = seasons[len(seasons)-1]

layout = html.Div([
    get_nav_bar(most_recent_season),
    html.Div(id='raw-stats')
])


@callback(
    Output(component_id='raw-stats', component_property='children'),
    Input(component_id='season-select', component_property='value')
)
def update_raw_stats(season):
    if not season:
        return

    if season == "All":
        # this case isn't really important, just use the most recent season
        season = most_recent_season

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