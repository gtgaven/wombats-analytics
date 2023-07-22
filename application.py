from dash import Dash, State, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
from database_connection import DbConnection
from player import PlayerStats
from metadata import ALL_TIME_PLAYERS

db = DbConnection('softball-readonly', 'softballrules!')
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def get_cumulative_stats(player):
    cumulative_stats = PlayerStats()
    if player == 'Team Cumulative':
        for p in ALL_TIME_PLAYERS:
            cumulative_stats += db.get_career_stats_for_player(p)
    elif player == 'The Average Wombat':
        #TODO need to account for season selected instead of ALL_TIME_PLAYERS
        for p in ALL_TIME_PLAYERS:
            cumulative_stats += db.get_career_stats_for_player(p)
        average_wombat = PlayerStats(round(cumulative_stats.games_played/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.plate_appearances/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.runs/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.sac_flies/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.walks/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.strikeouts/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.singles/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.doubles/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.triples/len(ALL_TIME_PLAYERS), 2),
                                     round(cumulative_stats.home_runs/len(ALL_TIME_PLAYERS), 2))
        return average_wombat
    else:
        cumulative_stats += db.get_career_stats_for_player(player)

    return cumulative_stats

player_dropdown_list = ALL_TIME_PLAYERS.copy()
player_dropdown_list.insert(0, "The Average Wombat")
player_dropdown_list.insert(0, "Team Cumulative")

nav_bar = dbc.NavbarSimple(
    children=[
        html.Div([
            'Season',
            dcc.Dropdown(
                options=['All', '2021', '2022', '2023'],
                id='season-select',
                value=['All'],
                multi=True)
            ],
            style={"width": "200px"}
        ),
        html.Div([
            'Player:',
            dcc.Dropdown(
                options=player_dropdown_list,
                id='player-select',
                value=['Team Cumulative', 'The Average Wombat'],
                multi=True)
            ],
            style={"width": "250px"}
        ),
    ],
    brand="Staaaaats",
    brand_href="/",
    color="primary",
    dark=True
)

app.layout = html.Div([
	nav_bar,
	html.Div(id='stats-summary')
])

#TODO add additional input for season-select
@callback(
    Output(component_id='stats-summary', component_property='children'),
    Input(component_id='player-select', component_property='value')
)
def update_stats_summary(input_value):
    if not input_value or len(input_value) == 0:
        return

    df = pd.DataFrame()
    stats = dict()
    for i in input_value:
        stats[i] = get_cumulative_stats(i)

    def stats_row(player):
        return html.Tr([html.Td(player),
                        html.Td('%.3f'%(stats[player].avg())),
                        html.Td('%.3f'%(stats[player].obp())),
                        html.Td('%.3f'%(stats[player].slg())),
                        html.Td(stats[player].plate_appearances),
                        html.Td(round(stats[player].at_bats(), 0)), # round to 0 needed for 'average wombat'
                        html.Td(stats[player].runs),
                        html.Td(stats[player].walks),
                        html.Td(stats[player].sac_flies),
                        html.Td(stats[player].strikeouts),
                        html.Td(stats[player].hits()),
                        html.Td(stats[player].singles),
                        html.Td(stats[player].doubles),
                        html.Td(stats[player].triples),
                        html.Td(stats[player].home_runs)])

    layout = [
        html.Br(),
        html.Table(
            [html.Tr([html.Th(col) for col in ['Player', 'AVG', 'OBP', 'SLG', 'PA', 'AB', 'R', 'BB', 'SF', 'K', 'H', '1B', '2B', '3B', 'HR']]) ] +
            [stats_row(i) for i in stats.keys()]
        ),
    ]

    return layout


if __name__ == '__main__':
    app.run("192.168.1.189", 8080, debug=True)