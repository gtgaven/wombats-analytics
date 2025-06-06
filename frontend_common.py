from dash import dcc, html
import dash_bootstrap_components as dbc
from database_connection import DbConnection

db = DbConnection()

all_seasons = db.get_seasons()
season_dropdown_list = all_seasons.copy()
season_dropdown_list.insert(0, "All")

def get_nav_bar(default_season="All"): 
    return dbc.NavbarSimple(
        children=[
            dbc.Row([
                dbc.Col([
                    dcc.Link('Player Profiles', href="/player", className="nav-bar-element"),
                    dcc.Link('Hall of Fame', href="/hall-of-fame", className="nav-bar-element"),
                    dcc.Link('Raw Data', href="/raw-data", className="nav-bar-element"), 
            dbc.Row([
                    html.Div([
                        'Season',
                        dcc.Dropdown(
                            options=season_dropdown_list,
                            id='season-select',
                            value=default_season,
                            style={"color": "#000000"}) # Items in menu
                    ],
                    style={
                        "padding-top": "30px",
                        "color":"#D3D3D3",
                        "width": "250px",
                        "margin-left": "auto"
                    }
                    )
                ])])
            ])
        ],
        style={
            "color":"#D3D3D3",
            "background-color": "#000000"
        },
        brand="West Building Wombats",
        brand_href="/",
        color = "#000000", # Color of nav bar
        dark=True
    )
