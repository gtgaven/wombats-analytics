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
        team_header = "Wombats - All Time"
        player_header = "Player Stats - All Time"
    else:
        team_header = f'Wombats - {season} Season'
        player_header = f'Player Stats - {season} Season'

    stats = dict()
    for i in ['Cumulative', 'Median Wombat', 'Mean Wombat']:
        stats[i] = db.get_cumulative_stats(i, season)

    def stats_avg_row(player):
        return html.Tr([html.Td(player),
                        html.Td('%.3f'%(stats[player].avg())),
                        html.Td('%.3f'%(stats[player].obp())),
                        html.Td('%.3f'%(stats[player].slg()))])

    def stats_batting_row(player):
        return html.Tr([html.Td(player),
                        html.Td(round(stats[player].hits(), 2)),
                        html.Td(stats[player].runs),
                        html.Td(stats[player].singles),
                        html.Td(stats[player].doubles),
                        html.Td(stats[player].triples),
                        html.Td(stats[player].home_runs)])

    def stats_misc_row(player):
        return html.Tr([html.Td(player),
                        html.Td(stats[player].games_played),
                        html.Td(round(stats[player].at_bats(), 0)), # round to 0 needed for 'average wombat'
                        html.Td(stats[player].plate_appearances),
                        html.Td(stats[player].walks),
                        html.Td(stats[player].sac_flies),
                        html.Td(stats[player].strikeouts)])

    gp_home = db.get_num_games(season, True)
    gp_away = db.get_num_games(season, False)
    gp_any = db.get_num_games(season, "Any")

    rf_home = 0
    rf_away = 0
    rf_any = stats["Cumulative"].runs

    w_home = 0
    w_away = 0

    for game_id in db.get_game_ids_in_season(season):
        raw_stats = db.get_raw_stats_from_game_id(game_id)
        runs_for = sum([raw_stats["stats"][x][2] for x in range(0, len(raw_stats["stats"]))])
        win = runs_for > raw_stats["opponentscore"]
        if raw_stats["was_home"]:
            rf_home += runs_for
            if win:
                w_home += 1
        else:
            rf_away += runs_for
            if win:
                w_away += 1

    w_any = w_home + w_away

    if rf_any != rf_home + rf_away:
       raise RuntimeError("sanity validation failed for run calculation")

    ra_home = db.get_runs_against(season, True)
    ra_away = db.get_runs_against(season, False)
    ra_any = db.get_runs_against(season, "Any")

    team_stats_table = html.Table([
        html.Tr([html.Th(i) for i in ["", "GP", "W", "L", "%", "RF", "RA", "Diff"]]),
        html.Tr([
            html.Td("Home"),
            html.Td(gp_home),
            html.Td(w_home),
            html.Td(gp_home - w_home),
            html.Td('%.3f'%(w_home / gp_home)),
            html.Td(rf_home),
            html.Td(ra_home),
            html.Td(rf_home - ra_home),
        ]),
        html.Tr([
            html.Td("Away"),
            html.Td(gp_away),
            html.Td(w_away),
            html.Td(gp_away - w_away),
            html.Td('%.3f'%(w_away / gp_away)),
            html.Td(rf_away),
            html.Td(ra_away),
            html.Td(rf_away - ra_away),
        ]),
        html.Tr([
            html.Td("All"),
            html.Td(gp_any),
            html.Td(w_any),
            html.Td(gp_any - w_any),
            html.Td('%.3f'%(w_any / gp_any)),
            html.Td(rf_any),
            html.Td(ra_any),
            html.Td(rf_any - ra_any),
        ]),
    ])

    layout = [
        html.H3(team_header),
        team_stats_table,
        html.H3(player_header),
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'AVG', 'OBP', 'SLG']]),
            *[stats_avg_row(i) for i in stats.keys()]
        ]),
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'H', 'R', '1B', '2B', '3B', 'HR']]) ,
            *[stats_batting_row(i) for i in stats.keys()]
        ]),   
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'GP', 'AB', 'PA', 'BB', 'SF', 'K']]),
            *[stats_misc_row(i) for i in stats.keys()]
        ])
    ]

    return layout
