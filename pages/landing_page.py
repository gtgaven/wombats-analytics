from dash import Dash, State, dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
from player import PlayerStats
import plotly.graph_objs as go
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
from database_connection import DbConnection

db = DbConnection()

dash.register_page(__name__, path='/')

all_players = db.get_player_list()
player_dropdown_list = all_players.copy()
player_dropdown_list.insert(0, "Mean Wombat")
player_dropdown_list.insert(0, "Median Wombat")
player_dropdown_list.insert(0, "Team Cumulative")

all_seasons = db.get_seasons()
season_dropdown_list = all_seasons.copy()
season_dropdown_list.insert(0, "All")


nav_bar = dbc.NavbarSimple(
    children=[
        html.Div([
            'Season:',
            dcc.Dropdown(
                options=season_dropdown_list,
                id='season-select',
                value='All',
                style={"color": "#000000"})
            ],
            style={"width": "200px", "color":"#fff", "padding-right": "20px"}
        ),
        html.Div([
            'Player(s):',
            dcc.Dropdown(
                options=player_dropdown_list,
                id='player-select',
                value=['Team Cumulative', 'Median Wombat', 'Mean Wombat'],
                multi=True,
                style={"color": "#000000"})
            ],
            style={"width": "250px", "color":"#fff", "padding-right": "20px"}
        )
    ],
    brand="West Building Wombats",
    brand_href="/",
    color="#696969",
    dark=True
)


layout = html.Div([
    nav_bar,
    html.Div(id='stats-summary'),
    html.Div(id='avg-graph')
])


@callback(
    Output(component_id='stats-summary', component_property='children'),
    Input(component_id='player-select', component_property='value'),
    Input(component_id='season-select', component_property='value')
)
def update_stats_summary(players, season):
    if not players or len(players) == 0:
        return

    if not season:
        return

    if season == "All":
        header = "All Time Stats"
    else:
        header = f'{season} Season'

    stats = dict()
    for i in players:
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
            [html.Tr([html.Th(col) for col in ['Player', 'AVG', 'OBP', 'SLG', 'GP', 'PA', 'AB', 'R', 'BB', 'SF', 'K', 'H', '1B', '2B', '3B', 'HR']]) ] +
            [stats_row(i) for i in stats.keys()]
        )
    ]

    return layout


@callback(
    Output(component_id='avg-graph', component_property='children'),
    Input(component_id='season-select', component_property='value')
)
def update_graph(season):
    if not season:
        return

    season_players = db.get_roster_for_season(season)

    stats = dict()
    for i in season_players:
        stats[i] = db.get_cumulative_stats(i, season)

    df = pd.DataFrame()
    df['Player'] = stats.keys()
    df['Batting Average'] = [stats[i].avg() for i in stats]
    df['On Base Percentage'] = [stats[i].obp() for i in stats]
    df['Slugging Percentage'] = [stats[i].slg() for i in stats]
    df['Games Played'] = [stats[i].games_played for i in stats]
    df['Plate Appearances'] = [stats[i].plate_appearances for i in stats]
    df['At Bats'] = [stats[i].at_bats() for i in stats]
    df['Runs'] = [stats[i].runs for i in stats]
    df['Walks']= [stats[i].walks for i in stats] 
    df['Sac Flies'] = [stats[i].sac_flies for i in stats]
    df['Strikeouts'] = [stats[i].strikeouts for i in stats]
    df['Hits']= [stats[i].hits() for i in stats]
    df['Singles']= [stats[i].singles for i in stats]
    df['Doubles'] = [stats[i].doubles for i in stats]
    df['Triples'] = [stats[i].triples for i in stats]
    df['Home Runs'] = [stats[i].home_runs for i in stats]
    layout = []

    for s in df.columns:
        if s == 'Player':
            continue

        if season == 'All':
            chart_title = f'{s} - Top 10 (All Time)'
        else:
            chart_title = f'{s} - Top 10 ({season})'
        df = df.sort_values([s], ascending=False)
        if s == 'Batting Average' or s == 'On Base Percentage' or s == 'Slugging Percentage':
            text_format = ['%.3f'%(i) for i in df[s][:10]]
        else:
            text_format = [i for i in df[s][:10]]
        bargraph = go.Figure(layout={'title':chart_title}, 
                             data=go.Bar(x=df['Player'][:10],
                                         y=df[s][:10],
                                         text=text_format))
        bargraph.update_layout(template="plotly_white", font={'size':16, 'family':"Calibri", 'color':"#000"})
        bargraph.update_traces(marker_color='#696969')
        layout.append(dcc.Graph(figure=bargraph))

    return layout