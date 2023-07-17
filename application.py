from dash import Dash, State, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from dash_bootstrap_components._components.Container import Container
import pandas as pd
import plotly.express as px

from database_connection import DbConnection

db = DbConnection('softball-service-account', 'softballrules!')
app = Dash(__name__, use_pages=True)


#TODO nav bar doesnt work

nav_bar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="NavbarSimple",
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div([
	nav_bar,

    html.Div(
        [
            html.Div('hello'
            )
        ]
    ),

	dash.page_container
])





if __name__ == '__main__':
    app.run("192.168.1.189", 8080, debug=True)