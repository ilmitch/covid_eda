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

w_df_filepath = "../../backend/working/_output/pckl/covid_df.pckl"

app = dash.Dash()

app.layout = html.Div([
                    html.H1('COVID-19 | Explorative Data Visualization'),
                    html.H3('Enter a country name:'),

                    dcc.Input(id='my_data_picker', value='Switzerland'),

                    dcc.Graph(id='my_graph', 
                              figure={
                                  'data':[{'x':[1,2], 'y':[3,1]}],
                                  'layout' : {'title':'Default Title'}
                                  }
                              )
                    ])


@app.callback(Output('my_graph', 'figure'),[Input('my_data_picker','value')])
def update_graph(country_ticker):
    start = date(2020,1,1)
    end = date.today()
    df = pd.read_pickle(w_df_filepath)
    c_df = df.loc[idx['Switzerland',:],idx['cumsum','NewConfCases']]
    fig = {'data':[{'x':list(df.index.levels[1]), 'y':list(c_df.values)}],
           'layout' : {'title':country_ticker}
           }
    return fig


if __name__ == '__main__':
    app.run_server()