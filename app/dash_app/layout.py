from dash import dash_table, html, dcc


layout = html.Div([
    dcc.Dropdown(id='user-dropdown'),
    html.Div(id='missing-payments'),
    dash_table.DataTable(id='payments-table'),
    dcc.Graph(id='monthly-balance-graph'),
])
