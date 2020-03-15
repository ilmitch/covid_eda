# conda activate base
# pip install dash
import datetime as dt
from datetime import date

import numpy as np
import pandas as pd
idx = pd.IndexSlice

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

w_df_filepath = "../../backend/working/_output/pckl/covid_df.pckl"

app = dash.Dash()

app.layout = html.Div([
    html.H1('COVID-19 | Explorative Data Visualization'),
    html.Div([
        html.H3('Enter a country name:', style={'paddingRight':'30px'}),
        dcc.Input(
            id='my_data_picker', 
            value='Switzerland',
            style={'fontSize':16,'width':75})
            ],
        style={'display':'inline-block', 'verticalAlign':'top'}),
    html.Div([
        html.H3('Select a start and end date:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=date(2020,1,1),
            max_date_allowed=date.today(),
            )
        ]),
    dcc.Graph(
        id='my_graph', 
        figure={
            'title':'Total Confirmed Cases',
            'data':[{'x':[1,2], 'y':[3,1]}],
            'layout' : [{'title':'Total Confirmed Cases (daily cumulative sum)'}]
            }
        )
    ])


@app.callback(Output('my_graph', 'figure'),[Input('my_data_picker','value')])
def update_graph(country_ticker):
    start = date(2020,1,1)
    end = date.today()
    df = pd.read_pickle(w_df_filepath)
    #c_df = df.loc[idx['Switzerland',:],idx['cumsum','NewConfCases']]
    # Slicing data per input country
    c_df = df.loc[idx[country_ticker,:],idx['cumsum','NewConfCases']]
    
    fig = {'data':[{'x':list(c_df.index.levels[1]), 'y':list(c_df.values)}],
           'layout': go.Layout(
                yaxis={
                    'title': 'Total Confirmed Cases',
                    'type': 'log'
                      },
            #margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )}
    return fig


if __name__ == '__main__':
    app.run_server()