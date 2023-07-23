import dash
from dash import html
from database_connection import DbConnection

db = DbConnection('softball-readonly', 'softballrules!')

dash.register_page(__name__, path='/raw')

layout = html.Div("heelo from raw")