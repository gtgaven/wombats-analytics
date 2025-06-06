from dash import Dash, State, dcc, html, Input, Output, callback
import dash
import dash_bootstrap_components as dbc
from player import PlayerStats
import plotly.graph_objs as go
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px
from frontend_common import get_nav_bar, db

dash.register_page(__name__, path='/hall-of-fame')

layout = html.Div([
    get_nav_bar(),
    html.Div(id='hof-graphs')
])

@callback(
    Output(component_id='hof-graphs', component_property='children'),
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
            chart_title = f'{s} – Top 10 (All Time)'
        else:
            chart_title = f'{s} – Top 10 ({season})'
        df = df.sort_values([s], ascending=False)
        if s == 'Batting Average' or s == 'On Base Percentage' or s == 'Slugging Percentage':
            text_format = ['%.3f'%(i) for i in df[s][:10]]
        else:
            text_format = [i for i in df[s][:10]]
        bargraph = go.Figure(layout={'title':chart_title}, 
                             data=go.Bar(x=df['Player'][:10],
                                         y=df[s][:10],
                                         text=text_format))
        bargraph.update_layout(template="plotly_dark", 
            paper_bgcolor="#000000",
            plot_bgcolor="#000000", 
            font={'size':16, 'family':"sans-serif"}
        )
        bargraph.update_traces(marker_color='#3f4952')
        layout.append(dcc.Graph(figure=bargraph))

    return layout
