import dash
from dash import Dash, dcc, html, Input, Output, callback

from database_connection import DbConnection

dash.register_page(__name__)
db = DbConnection('softball-service-account', 'softballrules!')

layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Dropdown(db.get_player_list(), id='player-profile-select', value='Greg')
    ]),
    html.Br(),
    html.Div(id='player-profile-display'),

])

@callback(
    Output(component_id='player-profile-display', component_property='children'),
    Input(component_id='player-profile-select', component_property='value')
)
def update_player_profile(input_value):
    s = db.get_career_stats_for_player(input_value)
    #f'{input_value},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{s.avg()},{s.obp()},{s.slg()}'

    profile_div = html.Div([
        
        html.Li(s.avg()),
        html.Li(s.obp()),
        html.Li(s.slg())    


    ])
    return profile_div