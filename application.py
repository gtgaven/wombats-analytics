from dash import Dash, html
import dash_bootstrap_components as dbc
import dash
import flask

server = flask.Flask(__name__) # define flask app.server

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CYBORG], server=server)
app.layout = html.Div(
    [dash.page_container],
    style={
        "max-width": "1000px",
        "margin": "0 auto",
    }
)

def get_app():
    return app.server

if __name__ == '__main__':
    app.run("localhost", 8080, debug=True, use_reloader=False)
