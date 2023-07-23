from dash import Dash, html
import dash_bootstrap_components as dbc
import dash

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
	dash.page_container
])


if __name__ == '__main__':
    app.run("192.168.1.189", 8080, debug=True)
