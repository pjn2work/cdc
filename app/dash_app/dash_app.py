from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from .layout import layout
from .callbacks import register_callbacks


app = Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                requests_pathname_prefix='/dashboard1/')
app.layout = layout


register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
