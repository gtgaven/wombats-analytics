import dash
from dash import html, dcc, Input, Output, callback
from database_connection import DbConnection
import dash_bootstrap_components as dbc

db = DbConnection()

dash.register_page(__name__, path='/profile')

all_players = db.get_player_list()

def get_player_profile_bar(player):
    player_profile_bar = dbc.NavbarSimple(
        children=[
            html.Div([
                'Player:',
                dcc.Dropdown(
                    options=all_players,
                    id='player-profile-select',
                    multi=False,
                    value=player,
                    style={"color": "#000000"})
                ],
                style={"width": "250px", "color":"#fff", "padding-right": "20px"}
            ),
        ],
        brand="West Building Wombats",
        brand_href="/",
        color="#696969",
        dark=True
    )

    return player_profile_bar


def layout(**kwargs):
    player = kwargs.get("player", None)

    return html.Div([
        get_player_profile_bar(player),
        
        html.Div(id='player-profile-pane')
    ])


@callback(
    Output(component_id='player-profile-pane', component_property='children'),
    Input(component_id='player-profile-select', component_property='value')
)
def update_player_profile(player):
    if not player:
        return
    
    layout = []

    all_time_stats = db.get_cumulative_stats(player, "All")

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

    main_profile_pane = html.Div([
        html.H2(player),
        html.Table([
            html.Tr([
                html.Td(html.Img(src="../assets/pic.png", alt='image')),
                html.Td(main_player_stats_table)
            ])
        ])
    ])
    layout.append(main_profile_pane)

    layout.append("--season to season performance graphs coming soon--")

    # for game_id in reversed(db.get_game_ids_in_season(season)):
    #     raw_stats = db.get_raw_stats_from_game_id(game_id)
        
    #     header = f' {season} Game#{raw_stats["game_num"]}'
    #     if (raw_stats["was_home"]):
    #         header += f' vs {raw_stats["opponent"]}'
    #     else:
    #         header += f' @ {raw_stats["opponent"]}'

    #     rows = []
    #     for stat in list(raw_stats["stats"]):
    #         rows.append(html.Tr([html.Td(i) for i in stat]))

    #     layout.append(
    #         html.Div([
    #         html.H3(header),
    #         html.Table(
    #             [html.Tr([html.Th(col) for col in ['Player', 'PA', 'R', 'SF', 'BB', 'K', '1B', '2B', '3B', 'HR']]) ] +
    #             rows
    #         )])
    #     )

    return layout