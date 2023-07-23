from dash import Dash, html
import dash_bootstrap_components as dbc
import dash
import flask

server = flask.Flask(__name__) # define flask app.server

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.layout = html.Div([
	dash.page_container
])

def get_app():
    return app.server


if __name__ == '__main__':
    app.run("192.168.1.189", 8080, debug=True)
