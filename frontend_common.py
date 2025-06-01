from dash import dcc, html
import dash_bootstrap_components as dbc
from database_connection import DbConnection

db = DbConnection()

all_seasons = db.get_seasons()
season_dropdown_list = all_seasons.copy()
season_dropdown_list.insert(0, "All")

nav_bar_element_style = {
    "margin": "auto",
    "text-align": "center",
    "padding": "10px",
    "color":"#fff"
}

def get_nav_bar(default_season="All"):
    return dbc.NavbarSimple(
        children=[
            dcc.Link('Players', href="/player", style=nav_bar_element_style),
            dcc.Link('Hall of Fame', href="/hall-of-fame", style=nav_bar_element_style),
            dcc.Link('Raw Data', href="/raw-data", style=nav_bar_element_style),
            html.Div([
                'Season:',
                dcc.Dropdown(
                    options=season_dropdown_list,
                    id='season-select',
                    value=default_season,
                    style={"color": "#000000"})
                ],
                style={
                    "margin": "auto",
                    "padding": "10px",
                    "color":"#fff",
                    "width": "200px"
                }
            )
        ],
        brand="West Building Wombats",
        brand_href="/",
        color="#696969",
        dark=True
    )
