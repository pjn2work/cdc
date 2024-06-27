import pandas as pd
from dash import dcc, html, Input, Output
from sqlalchemy import text

from ..db import get_db


def get_payments_data():
    session = next(get_db())
    query = session.execute(text("SELECT * FROM member_dues_payments"))
    df = pd.DataFrame(query.fetchall(), columns=query.keys())
    print(df)
    return df


def register_callbacks(app):
    @app.callback(
        Output('payments-table', 'data'),
        Input('user-dropdown', 'value')
    )
    def update_table(member_id):
        df = get_payments_data()
        return df[df['member_id'] == member_id].to_dict('records')

    @app.callback(
        Output('monthly-balance-graph', 'figure'),
        Input('user-dropdown', 'value')
    )
    def update_graph(user_id):
        df = get_payments_data()
        balance = df.groupby('id_year_month')['amount'].sum()
        return {
            'data': [{'x': balance.index.astype(str), 'y': balance.values, 'type': 'bar'}],
            'layout': {'title': 'Monthly Balance'}
        }
