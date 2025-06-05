import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from frontend_common import get_nav_bar, db
from player import PlayerStats


dash.register_page(__name__, path='/player')

all_players = db.get_player_list()
current_player = None

def layout(**kwargs):
    player = kwargs.get("name", None)
    return html.Div([
        get_nav_bar(),
        html.Div([
            'Player',
            dcc.Dropdown(
                placeholder="Select a player",
                options=all_players,
                id='player-profile-select',
                multi=False,
                value=player,
                style={"color": "#000000"})
            ],
            style={"width": "250px", "margin-left": "auto"}
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
    style={"font-size": "medium"}
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
    ],
    style={"font-size": "medium"}
    )

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
    ],
    style={"font-size": "medium"}
    )

    main_player_stats_table = html.Table([
        html.Tr(avg_table),
        html.Tr(batting_table),
        html.Tr(misc_table)
    ]    ,
    style={"font-size": "medium"})

    if season == "All":
        header = f"{player} – Career"
    else:
        header = f"{player} – {season} Season"

    main_profile_pane = html.Div([
        html.Table([
            html.Tr(html.Th(header)),
            html.Tr(html.Td(html.Img(src="../assets/pic.png", alt='image'))),
            html.Tr(html.Td(main_player_stats_table))
        ])
    ],
    style={"font-size": "x-large"})
    layout.append(main_profile_pane)
    return layout


@callback(
    Output(component_id='player-progression-graph', component_property='children'),
    Input(component_id='player-profile-select', component_property='value')
)
def update_player_progression_graph(player):
    if not player:
        return 
    layout = []
    header = f"{player} – Career"
    career_graphs_pane = html.Div([
        html.Table([
            html.Tr(html.Th(header))
        ])
    ],
    style={"font-size": "x-large"}
    )

    # Game progression, overall season
    seasons = sorted(db.get_player_seasons(player)) 
    avgs = []

    for season in seasons:
        stats = db.get_cumulative_stats(player, season)
        avgs.append(stats.avg())

    average_by_season = {'Season': seasons, 'AVG': avgs}
    df = pd.DataFrame(data=average_by_season)
    
    linefig_batting_avg = px.line(df, x = "Season", y = "AVG", title=f'Batting Average by Season', markers=True)
    linefig_batting_avg.update_layout(yaxis_range=[0, 1], template="plotly_dark", paper_bgcolor="#000000", plot_bgcolor="#000000")
    linefig_batting_avg.update_xaxes(type='category')
    
    # Game progression, all games
    columns, stats = db.get_all_player_stats_for_player(player)
    df_games = pd.DataFrame(stats, columns=columns)
    #df_games = df_games.sort_values(['Season', 'game_num']) TODO put in sql query ?

    # Batting average = hits / at bats
    df_games['hits'] = df_games['singles'] + df_games['doubles'] + df_games['triples'] + df_games['home_runs']
    df_games['at_bats'] = df_games['plate_appearances'] - df_games['walks'] - df_games['sac_flies']
    df_games['batting_avg'] = df_games['hits'] / df_games['at_bats'].replace(0, pd.NA)
    df_games['hits_expanded'] = df_games.groupby('Season')['hits'].transform(lambda x: x.expanding().sum())
    df_games['at_bats_expanded'] = df_games.groupby('Season')['at_bats'].transform(lambda x: x.expanding().sum())

    # Rolling average and rolling game count
    df_games['AVG'] = df_games['hits_expanded'] /df_games['at_bats_expanded']
    df_games['Games Played'] = df_games.groupby(['Season']).cumcount() + 1

    # Make progression figure - all seasons
    linefig_moving_avg = px.line(
        df_games,
        x="Games Played", y="AVG", color="Season",
        title=f'Cumulative Batting Average by Game',
        markers=True
    ) 
    linefig_moving_avg.update_xaxes(type='category')
    linefig_moving_avg.update_layout(
        yaxis_range=[0, 1],
        legend=dict(x=0.008, y=1.05, xanchor='left', yanchor='bottom', orientation='h', bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
        margin=dict(t=120),
        template="plotly_dark", 
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
    )

    layout.append(career_graphs_pane)
    layout.append(html.Div([
    dcc.Graph(figure=linefig_batting_avg), 
    dcc.Graph(figure=linefig_moving_avg)
    ]))

    return html.Div(layout)
