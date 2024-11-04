import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

app = dash.Dash(__name__)
app.layout = html.Div(
    style={'backgroundColor': '#f0f2f5', 'padding': '20px'},
    children=[
        html.H1(
            "Indian Stock Data",
            style={'textAlign': 'center', 'color': '#4CAF50'}
        ),
        html.Div(
            style={'textAlign': 'center', 'marginBottom': '20px'},
            children=[
                html.Label('STOCK NAME   :'),
                dcc.Input(
                    id='stock-input',
                    type='text',
                    placeholder="Type the stock symbol (e.g., INFY.NS)",
                    value='',
                    style={
                        'width': '300px',
                        'padding': '10px',
                        'borderRadius': '5px',
                        'border': '1px solid #ccc'
                    }
                ),
                html.Button(
                    'Search',
                    id='search-button',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'padding': '10px 20px',
                        'cursor': 'pointer',
                        'fontSize': '16px'
                    }
                ),
            ]
        ),
        dcc.ConfirmDialog(
            id='confirm-dialog',
            message='Stock not found. Please enter a valid ticker.',
            displayed=False
        ),
        html.Div(
            style={'textAlign': 'center', 'marginBottom': '20px'},
            children=[
                html.Label('Select Date Range:'),
                dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=datetime(2000, 1, 1),
                    max_date_allowed=datetime.today(),
                    start_date=(datetime.today() - timedelta(days=365)).date(),
                    end_date=datetime.today().date(),
                ),
            ]
        ),
        html.Div(
            id='company-description',
            style={
                'margin': '20px',
                'padding': '15px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.2)',
                'display': 'none'  
            }
        ),
        html.Div(
            id='fundamentals',
            style={
                'margin': '20px',
                'padding': '15px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.2)',
                'display': 'none'  
            }
        ),
        html.Div(
            id='stock-graph-container',
            style={
                'margin': '20px',
                'padding': '15px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.2)',
                'display': 'none'  
            },
            children=[
                dcc.Graph(id='stock-graph', style={'margin': '20px'})
            ]
        ),
        html.Div(
            id='forecasting',
            style={
                'margin': '20px',
                'padding': '15px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 5px rgba(0, 0, 0, 0.2)',
                'display': 'none' 
            },
            children=[
                dcc.Graph(id='forecast-graph', style={'margin': '20px'})
            ]
        )
    ]
)

@app.callback(
    [Output('stock-graph', 'figure'),
     Output('fundamentals', 'children'),
     Output('company-description', 'children'),
     Output('forecast-graph', 'figure'),
     Output('confirm-dialog', 'displayed'),
     Output('stock-graph-container', 'style'),
     Output('forecasting', 'style'),
     Output('company-description', 'style'),
     Output('fundamentals', 'style')],
    [Input('search-button', 'n_clicks')],
    [State('stock-input', 'value'),
     State('date-picker', 'start_date'),
     State('date-picker', 'end_date')]
)
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    if n_clicks == 0 or not stock_ticker:
        return go.Figure(), html.Div(""), "", go.Figure(), False, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

    stock_data = yf.Ticker(stock_ticker)


    try:
        df = stock_data.history(start=start_date, end=end_date)
        if df.empty:
            return go.Figure(), html.Div(), "", go.Figure(), True, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}
    except Exception:
        return go.Figure(), html.Div(), "", go.Figure(), True, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

    fig = go.Figure([go.Scatter(x=df.index, y=df['Close'], mode='lines', name=f'{stock_ticker} Close Price')])
    fig.update_layout(title=f'{stock_ticker} Stock Price', xaxis_title='Date', yaxis_title='Price (INR)', template='plotly_dark')



    # Fetch fundamentals
    try:
        market_cap = stock_data.info['marketCap']
        pe_ratio = stock_data.info.get('trailingPE', 'N/A')
        dividend_yield = stock_data.info.get('dividendYield', 'N/A')
    except KeyError:
        market_cap = pe_ratio = dividend_yield = 'N/A'

    fundamentals = html.Div([
        html.H4(f"Key Fundamentals for {stock_ticker}"),
        html.P(f"Market Cap: {market_cap:,} INR"),
        html.P(f"P/E Ratio: {pe_ratio}"),
        html.P(f"Dividend Yield: {dividend_yield}")
    ])



    # Fetch company description
    
    try:
        company_description = stock_data.info['longBusinessSummary']
    except KeyError:
        company_description = "No description available."

    description = html.Div([html.H4(f"About {stock_ticker}:"), html.P(company_description)])



    # Simple forecasting using moving average

    df['Forecast'] = df['Close'].rolling(window=5).mean().shift(-5)
    forecast_data = df[['Close', 'Forecast']].dropna()

    forecast_fig = go.Figure()
    if not forecast_data.empty:
        forecast_fig.add_trace(go.Scatter(x=forecast_data.index, y=forecast_data['Close'], mode='lines', name='Actual Close Price'))
        forecast_fig.add_trace(go.Scatter(x=forecast_data.index, y=forecast_data['Forecast'], mode='lines', name='5-Day Moving Average Forecast'))
        forecast_fig.update_layout(title=f'{stock_ticker} Price Forecast', xaxis_title='Date', yaxis_title='Price (INR)', template='plotly_dark')
        forecast_style = {'display': 'block'}
    else:
        forecast_style = {'display': 'none'}

    return fig, fundamentals, description, forecast_fig, False, {'display': 'block'}, forecast_style, {'display': 'block'}, {'display': 'block'}

if __name__ == '__main__':
    app.run_server(debug=True)
