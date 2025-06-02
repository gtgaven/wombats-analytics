import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from frontend_common import get_nav_bar, db


dash.register_page(__name__, path='/player')

all_players = db.get_player_list()
current_player = None

def layout(**kwargs):
    player = kwargs.get("name", None)
    return html.Div([
        get_nav_bar(),
        html.Div([
            'Player:',
            dcc.Dropdown(
                placeholder="Select a player",
                options=all_players,
                id='player-profile-select',
                multi=False,
                value=player,
                style={"color": "#000000"})
            ],
            style={"width": "250px", "color":"#fff", "padding-left": "20px"}
        ),
        html.Div(id='player-profile-pane'),
        html.Div(id='player-progression-graph')
    ])


@callback(
    Output(component_id='player-profile-pane', component_property='children'),
    Input(component_id='player-profile-select', component_property='value'),
    Input(component_id='season-select', component_property='value')
)
def update_player_profile(player, season):
    if not player:
        return

    layout = []

    all_time_stats = db.get_cumulative_stats(player, season)

    avg_table = html.Table([
        html.Tr([html.Th(col) for col in ['AVG', 'OBP', 'SLG']]),
        html.Tr([
            html.Td('%.3f'%(all_time_stats.avg())),
            html.Td('%.3f'%(all_time_stats.obp())),
            html.Td('%.3f'%(all_time_stats.slg()))
        ])
    ],
    style={"font-size": "x-large"}
    )

    batting_table = html.Table([
        html.Tr([html.Th(col) for col in ['H', 'R', '1B', '2B', '3B', 'HR']]),
        html.Tr([
            html.Td(round(all_time_stats.hits(), 2)),
            html.Td(all_time_stats.runs),
            html.Td(all_time_stats.singles),
            html.Td(all_time_stats.doubles),
            html.Td(all_time_stats.triples),
            html.Td(all_time_stats.home_runs)
        ])
    ])

    misc_table = html.Table([
        html.Tr([html.Th(col) for col in ['GP', 'AB', 'PA', 'BB', 'SF', 'K']]),
        html.Tr([
            html.Td(all_time_stats.games_played),
            html.Td(round(all_time_stats.at_bats(), 0)),
            html.Td(all_time_stats.plate_appearances),
            html.Td(all_time_stats.walks),
            html.Td(all_time_stats.sac_flies),
            html.Td(all_time_stats.strikeouts)
        ])
    ])

    main_player_stats_table = html.Table([
        html.Tr(avg_table),
        html.Tr(batting_table),
        html.Tr(misc_table)
    ])

    if season == "All":
        header = f"{player} - Career"
    else:
        header = f"{player} - {season} Season"

    main_profile_pane = html.Div([
        html.Table([
            html.Tr(html.Th(header)),
            html.Tr(html.Td(html.Img(src="../assets/pic.png", alt='image'))),
            html.Tr(html.Td(main_player_stats_table))
        ])
    ])
    layout.append(main_profile_pane)
    return layout


@callback(
    Output(component_id='player-progression-graph', component_property='children'),
    Input(component_id='player-profile-select', component_property='value')
)
def update_player_progression_graph(player):
    if not player:
        return

    # TODO new function 'get_player_seasons' needs to return something like [2021, 2022, 2024]
    
    seasons = sorted(db.get_player_seasons(player)) 
    avgs = []

    for season in seasons:
        stats = db.get_cumulative_stats(player, season)
        avgs.append(stats.avg())

    average_by_season = {'seasons': seasons, 'avgs': avgs}
    df = pd.DataFrame(data=average_by_season)
    
    linefig = px.line(df, x = "seasons", y = "avgs", title=f'{player} - Batting Average by Season', markers=True)
    linefig.update_layout(yaxis_range=[0, 1])
    linefig.update_xaxes(type='category')
    return dcc.Graph(figure=linefig)





