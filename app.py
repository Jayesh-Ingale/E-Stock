import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import plotly.express as px
import pandas as pd
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import plotly.express as px
from model import prediction
from sklearn.svm import SVR



from dash_html_components.Br import Br

def get_stock_price_fig(df):

    fig = px.line(df,
                  x="Date",
                  y=["Close", "Open"],
                  title="Closing and Opening Price vs Date")

    return fig


def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,
                     x="Date",
                     y="EWA_20",
                     title="Exponential Moving Average vs Date")
    fig.update_traces(mode='lines+markers')
    return fig

app = dash.Dash(__name__,external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
    ])
server = app.server

app.layout = html.Div(
    [
        html.Div(
            [
                # Navigation
                html.H1("Welcome!", className="start"),
                html.Div([
                    html.P("Input stock code: "),
                    html.Div([
                        dcc.Input(id="dropdown_tickers", type="text"),
                        html.Button("Submit", id='submit'),
                    ],
                             className="form")
                ],
                         className="input-place"),
                html.Div([
                    dcc.DatePickerRange(id='my-date-picker-range',
                                        min_date_allowed=dt(1995, 8, 5),
                                        max_date_allowed=dt.now(),
                                        initial_visible_month=dt.now(),
                                        end_date=dt.now().date()),
                ],
                         className="date"),
                html.Div([
                    html.Button(
                        "Stock Price", className="stock-btn", id="stock"),
                    html.Button("Indicators",
                                className="indicators-btn",
                                id="indicators"),
                    dcc.Input(id="n_days",
                              type="text",
                              placeholder="number of days"),
                    html.Button(
                        "Forecast", className="forecast-btn", id="forecast")
                ],
                         className="buttons"),
                # here
                html.Footer([
                    html.P("Project developed by Atharvraj Patil and Jayesh Ingale: Electrical Engineering, COEP")
                ],className="Foo")
            ],
            className="nav"),

        # content
        html.Div(
            [
                html.Div(
                    [  # header
                        html.Img(id="logo"),
                        html.P(id="ticker")
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
                html.Div([], id="graphs-content"),
                html.Div([], id="main-content"),
                html.Div([], id="forecast-content"),
                
            ],
            className="content"),
        
        
    ],
    className="container")

@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("stock", "n_clicks"),
    Output("indicators", "n_clicks"),
    Output("forecast", "n_clicks")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val):  # inpur parameter(s)
    if n == None:
        # c = nse_quote_ltp(v)
        # print(c)
        return "Hey there! Please enter a legitimate stock code to get details.","data:image/png;base64,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", "E-Stock", None, None, None
        # raise PreventUpdate
    else:
        print(val)
        if val == None:
            raise PreventUpdate
        else:
            ticker = yf.Ticker(val)
            print(ticker)
            inf = ticker.info
            # print(inf)
            df = pd.DataFrame().from_dict(inf, orient="index").T
            print(df)
            df[['logo_url', 'shortName', 'longBusinessSummary']]
            print(df[['logo_url', 'shortName', 'longBusinessSummary']])
    
            return df['longBusinessSummary'].values[0], df['logo_url'].values[
                0], df['shortName'].values[0], None, None, None



@app.callback([
    Output("graphs-content", "children"),
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
def stock_price(n, start_date, end_date, val):
    if n == None:
        return [""]
        #raise PreventUpdate
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

@app.callback([Output("main-content", "children")], [
    Input("indicators", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])
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



@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


if __name__ == '__main__':
    app.run_server(debug=True)
