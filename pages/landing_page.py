from dash import Dash, State, dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
from player import PlayerStats
import plotly.graph_objs as go
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
from frontend_common import get_nav_bar, db

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
        team_header = "Team – All Time"
        player_header = "Players – All Time"
    else:
        team_header = f'Team – {season} Season'
        player_header = f'Players – {season} Season'

    stats = dict()
    for i in ['Cumulative', 'Median Wombat', 'Mean Wombat']:
        stats[i] = db.get_cumulative_stats(i, season)

    def stats_avg_row(player):
        return html.Tr([html.Td(player, style={"text-align": "left"}),
                        html.Td('%.3f'%(stats[player].avg())),
                        html.Td('%.3f'%(stats[player].obp())),
                        html.Td('%.3f'%(stats[player].slg()))])

    def stats_batting_row(player):
        return html.Tr([html.Td(player, style={"text-align": "left"}),
                        html.Td(round(stats[player].hits(), 2)),
                        html.Td(stats[player].runs),
                        html.Td(stats[player].singles),
                        html.Td(stats[player].doubles),
                        html.Td(stats[player].triples),
                        html.Td(stats[player].home_runs)])

    def stats_misc_row(player):
        return html.Tr([html.Td(player, style={"text-align": "left"}),
                        html.Td(stats[player].games_played),
                        html.Td(round(stats[player].at_bats(), 0)), # round to 0 needed for 'average wombat'
                        html.Td(stats[player].plate_appearances),
                        html.Td(stats[player].walks),
                        html.Td(stats[player].sac_flies),
                        html.Td(stats[player].strikeouts)])

    gp_home = db.get_num_games(season, True)
    gp_away = db.get_num_games(season, False)
    gp_any = gp_home + gp_away

    rf_home = db.get_runs_in_year(True, season, True)
    rf_away = db.get_runs_in_year(True, season, False)
    rf_any = rf_home + rf_away

    ra_home = db.get_runs_in_year(False, season, True)
    ra_away = db.get_runs_in_year(False, season, False)
    ra_any = ra_home + ra_away

    w_home = db.get_wins_in_year(season, True)
    w_away = db.get_wins_in_year(season, False)
    w_any = w_home + w_away

    ties_home = db.get_ties_in_year(season, True)
    ties_away = db.get_ties_in_year(season, False)
    ties_any = ties_home + ties_away

    losses_home = gp_home - w_home - ties_home
    losses_away = gp_away - w_away - ties_away
    losses_any = gp_any - w_any - ties_any

    if rf_any != stats["Cumulative"].runs:
       raise RuntimeError("sanity validation failed for runs-for calculation")

    team_stats_table = html.Table([
        html.Tr([html.Th(i) for i in ["", "GP", "W", "L", "T", "%", "RF", "RA", "Diff"]]),
        html.Tr([
            html.Td("Home"),
            html.Td(gp_home),
            html.Td(w_home),
            html.Td(losses_home),
            html.Td(ties_home),
            html.Td('%.3f'%(w_home / (w_home + losses_home))),
            html.Td(rf_home),
            html.Td(ra_home),
            html.Td(rf_home - ra_home),
        ]
        ),
        html.Tr([
            html.Td("Away"),
            html.Td(gp_away),
            html.Td(w_away),
            html.Td(losses_away),
            html.Td(ties_away),
            html.Td('%.3f'%(w_away / (w_away + losses_away))),
            html.Td(rf_away),
            html.Td(ra_away),
            html.Td(rf_away - ra_away),
        ]
        ),
        html.Tr([
            html.Td("All"),
            html.Td(gp_any),
            html.Td(w_any),
            html.Td(losses_any),
            html.Td(ties_any),
            html.Td('%.3f'%(w_any / (w_any + losses_any))),
            html.Td(rf_any),
            html.Td(ra_any),
            html.Td(rf_any - ra_any),
        ]
        ),
    ], className="landingtable")

    layout = [
        html.H3(team_header),
        team_stats_table,
        html.H3(player_header),
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'AVG', 'OBP', 'SLG']]),
            *[stats_avg_row(i) for i in stats.keys()]
        ], className="landingtable"),
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'H', 'R', '1B', '2B', '3B', 'HR']]),
            *[stats_batting_row(i) for i in stats.keys()]
        ], className="landingtable"),
        html.Table([
            html.Tr([html.Th(col) for col in ['', 'GP', 'AB', 'PA', 'BB', 'SF', 'K']]),
            *[stats_misc_row(i) for i in stats.keys()]
        ], className="landingtable")
    ]

    return layout
