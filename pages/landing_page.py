from dash import Dash, State, dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
from player import PlayerStats
import plotly.graph_objs as go
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
from database_connection import DbConnection
from nav_bar import get_nav_bar

db = DbConnection()

dash.register_page(__name__, path='/')

layout = html.Div([
    get_nav_bar(),
    html.Div(id='stats-summary')
])


@callback(
    Output(component_id='stats-summary', component_property='children'),
    Input(component_id='season-select', component_property='value')
)
def update_stats_summary(season):
    if not season:
        return

    if season == "All":
        header = "Player Stats - All Time"
    else:
        header = f'Player Stats - {season} Season'

    stats = dict()
    for i in ['Cumulative', 'Median Wombat', 'Mean Wombat']:
        stats[i] = db.get_cumulative_stats(i, season)

    def stats_row(player):
        return html.Tr([html.Td(player),
                        html.Td('%.3f'%(stats[player].avg())),
                        html.Td('%.3f'%(stats[player].obp())),
                        html.Td('%.3f'%(stats[player].slg())),
                        html.Td(stats[player].games_played),
                        html.Td(stats[player].plate_appearances),
                        html.Td(round(stats[player].at_bats(), 0)), # round to 0 needed for 'average wombat'
                        html.Td(stats[player].runs),
                        html.Td(stats[player].walks),
                        html.Td(stats[player].sac_flies),
                        html.Td(stats[player].strikeouts),
                        html.Td(round(stats[player].hits(), 2)),
                        html.Td(stats[player].singles),
                        html.Td(stats[player].doubles),
                        html.Td(stats[player].triples),
                        html.Td(stats[player].home_runs)])

    layout = [
        html.H3(header),
        html.Table(
            [html.Tr([html.Th(col) for col in ['-', 'AVG', 'OBP', 'SLG', 'GP', 'PA', 'AB', 'R', 'BB', 'SF', 'K', 'H', '1B', '2B', '3B', 'HR']]) ] +
            [stats_row(i) for i in stats.keys()]
        )
    ]

    return layout
