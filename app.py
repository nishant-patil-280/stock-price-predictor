import dash
from dash.html.P import P
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime as dt
import yfinance as yf

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd

import plotly.graph_objs as go
import plotly.express as px

from model import prediction
from sklearn.svm import SVR


external_stylesheet = [
    {
        'href': 'assets/style.css',
        'rel': 'stylesheet'
    }
]

# create a dash instance
app = dash.Dash(__name__, external_stylesheets=external_stylesheet, meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
server = app.server


def get_stock_price_fig(df):
    fig = px.line(df, x="Date", y=["Close", "Open"],
                  title="Closing and Opening (Price vs Date)")
    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EWA_20",
                     title="Exponential Moving (Average vs Date)")
    fig.update_traces(mode='lines+markers')
    return fig

app.title = 'Stockino'
app.layout = html.Div([
    html.Div([
        html.P("Welcome to the Stockino!", className="start"),
        html.Div([
            html.P("Input stock code: "),
            html.Div([
                dcc.Input(id="dropdown_tickers", type="text", value="TSLA"),
                html.Button("Submit", id='submit', n_clicks=1)
            ],
                className="form")],
            className="input-place"),

        html.Div([
            html.P("Input date: "),
            dcc.DatePickerRange(id='my-date-picker-range', min_date_allowed=dt(1995, 8, 5),
                                max_date_allowed=dt.now(), initial_visible_month=dt.now(), end_date=dt.now().date()),
        ], className="date"),
        html.Button("Stock Price", className="stock-btn", id="stock"),

        html.Div([
            
            
            html.Br(),
            html.P("Stock Predictions:"),
            html.Br(),
            html.Button(
                "Indicator (EMA)", className="indicators-btn", id="indicators"),
            html.Br(),
            dcc.Input(id="n_days", type="text", placeholder=" Enter no. of days"),
            html.Button("Forecast", className="forecast-btn",
                        id="forecast")
        ], className="buttons"),
    ], className="nav"),

    html.Div([
        html.Div([
            html.Img(id="logo"),
            html.P(id="ticker")
        ], className="header"),
        html.Div(id="description", className="decription_ticker"),
        html.Div([], id="graphs-content"),
        html.Div([], id="main-content"),
        html.Div([], id="forecast-content")
    ], className="content"),
], className="container")


# callback for company info
@app.callback(
    [
        Output("description", "children"),
        Output("logo", "src"),
        Output("ticker", "children"),
        Output("stock", "n_clicks"),
        Output("indicators", "n_clicks"),
        Output("forecast", "n_clicks")
    ],
    [Input("submit", "n_clicks")],
    [State("dropdown_tickers", "value")])
def update_data(n, val):
    if n == None:
        raise PreventUpdate
    else:
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            inf = ticker.info
            df = pd.DataFrame().from_dict(inf, orient="index").T
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None


# callback for stocks graphs
@app.callback(
    [Output("graphs-content", "children"), ],
    [
        Input("stock", "n_clicks"),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    ],
    [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))
        else:
            df = yf.download(val)
    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]


# callback for indicators
@app.callback(
    [Output("main-content", "children")],
    [
        Input("indicators", "n_clicks"),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    ],
    [State("dropdown_tickers", "value")])
def indicators(n, start_date, end_date, val):
    if n == None:
        return [""]
    if val == None:
        return [""]
    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))
    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]


# callback for forecast
@app.callback(
    [Output("forecast-content", "children")],
    [Input("forecast", "n_clicks")],
    [
        State("n_days", "value"),
        State("dropdown_tickers", "value")
    ]
)
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
