import dash
from dash import html, dcc, Input, Output, State, callback
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
        html.Div(id='player-progression-graphs'), 
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
    ], 
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
    Output(component_id='player-progression-graphs', component_property='children'),
    Input(component_id='player-profile-select', component_property='value')
)
def update_player_progression_graphs(player):
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


    rolling_cumulative = db.get_all_rolling_cumulative_stats_for_player(player)
    
    game_stats = []
    season_stats = []
    for season, playerstats in rolling_cumulative.items():
        game_stats.extend([[season, p.games_played, p.avg(), p.slg(), p.hits()] for p in playerstats])
        # last PlayerStats of each season are the season-cumulative
        season_stats.append([season,
                             playerstats[len(playerstats) - 1].avg(),
                             playerstats[len(playerstats) - 1].slg()])
    
    df_games = pd.DataFrame(game_stats, columns=["Season", "Games Played", "AVG", "SLG", "Hits"])
    df_seasons = pd.DataFrame(season_stats, columns=["Season", "AVG", "SLG"])
    
    linefig_seasonal_avgs = px.line(df_seasons, x ="Season", y =["AVG", "SLG"], title=f'AVG & SLG by Season', markers=True)
    linefig_seasonal_avgs.update_layout(
        template="plotly_dark", 
        paper_bgcolor="#000000", 
        plot_bgcolor="#000000",
        yaxis_title="AVG & SLG",
        legend=dict(
            x=0.008, y=1.05, xanchor='left', yanchor='bottom', orientation='h', 
            bgcolor='#000000', bordercolor='#000000', title=None),
        margin=dict(t=120)
    )
    linefig_seasonal_avgs.update_xaxes(type='category')

    # Make progression figures - all seasons
    linefig_moving_avg = px.line(
        df_games,
        x="Games Played", y="AVG", color="Season",
        title=f'Cumulative Batting Average by Game',
        markers=True
    ) 
    linefig_moving_avg.update_xaxes(type='category')
    linefig_moving_avg.update_layout(
        yaxis_range=[0,1],
        legend=dict(
            x=0.008, y=1.05, xanchor='left', yanchor='bottom', orientation='h', 
            bgcolor='#000000', bordercolor='#000000'),
        margin=dict(t=120),
        template="plotly_dark", 
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
    )

    linefig_moving_slg = px.line(
        df_games,
        x="Games Played", y="SLG", color="Season",
        title=f'Cumulative Slugging Percentage by Game',
        markers=True
    ) 
    linefig_moving_slg.update_xaxes(type='category')
    linefig_moving_slg.update_layout(
        legend=dict(x=0.008, y=1.05, xanchor='left', yanchor='bottom', orientation='h', bgcolor='#000000', bordercolor='rgba(0,0,0,0)'),
        margin=dict(t=120),
        template="plotly_dark", 
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
    )

    linefig_moving_hits = px.line(
        df_games,
        x="Games Played", y="Hits", color="Season",
        title=f'Cumulative Hits by Game',
        markers=True
    ) 
    linefig_moving_hits.update_xaxes(type='category')
    linefig_moving_hits.update_layout(
        legend=dict(x=0.008, y=1.05, xanchor='left', yanchor='bottom', orientation='h', bgcolor='#000000', bordercolor='rgba(0,0,0,0)'),
        margin=dict(t=120),
        template="plotly_dark", 
        paper_bgcolor="#000000",
        plot_bgcolor="#000000"
    )

    layout.append(career_graphs_pane)
    layout.append(html.Div([
    dcc.Graph(figure=linefig_seasonal_avgs), 
    dcc.Graph(figure=linefig_moving_avg),
    dcc.Graph(figure=linefig_moving_slg),
    dcc.Graph(figure=linefig_moving_hits)
    ]))

    return html.Div(layout)
