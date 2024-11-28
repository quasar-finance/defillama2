import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import requests
import pandas as pd
import plotly.graph_objs as go

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Historical APY Dashboard"), className="text-center")
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Input(id='pool-id-input', type='text', placeholder='Enter Pool ID', style={'width': '100%'}),
            dbc.Button('Fetch Data', id='fetch-button', color='primary', className='mt-2', n_clicks=0)
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='column-dropdown',
                options=[
                    {'label': 'APY', 'value': 'apy'},
                    {'label': 'APY Base', 'value': 'apyBase'},
                    {'label': 'TVL USD', 'value': 'tvlUsd'}
                ],
                value='apy',  # Default value
                clearable=False
            ),
            dcc.Graph(id='data-graph')
        ], width=12)
    ])
], fluid=True)

# Callback to fetch data and update the graph
@app.callback(
    Output('data-graph', 'figure'),
    Input('fetch-button', 'n_clicks'),
    Input('pool-id-input', 'value'),
    Input('column-dropdown', 'value')
)
def update_graph(n_clicks, pool_id, selected_column):
    if n_clicks > 0 and pool_id:
        try:
            # Fetch data from the API
            response = requests.get(f'http://localhost:5001/historical_apy/{pool_id}')
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            # Convert the data to a DataFrame
            df = pd.DataFrame(data)

            # Create the graph
            figure = {
                'data': [
                    go.Scatter(
                        x=list(range(len(df))),  # X-axis as index
                        y=df[selected_column],
                        mode='lines+markers',
                        name=selected_column
                    )
                ],
                'layout': go.Layout(
                    title=f'{selected_column} Over Time',
                    xaxis={'title': 'Time'},
                    yaxis={'title': selected_column},
                    hovermode='closest'
                )
            }

            return figure

        except Exception as e:
            return go.Figure()  # Return an empty figure on error

    return go.Figure()  # Return an empty figure initially

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 