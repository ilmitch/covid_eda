# conda activate base
# pip install dash
import datetime as dt
from datetime import date
import pickle
import numpy as np
import pandas as pd
idx = pd.IndexSlice

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

df_filepath = "../../backend/working/_output/pckl/covid_df.pckl"
with open("../../backend/working/_output/pckl/countries_lst.pckl", 'rb') as f:
     countries_lst = pickle.load(f)
#appending dicts, {'label':'value'}, {'user sees':'script sees'}
countries = [{'label':country, 'value':country} for country in countries_lst]


app = dash.Dash()

app.layout = html.Div([
    html.H1('COVID-19 | Explorative Data Visualization'),

    html.Div([
        html.H3('Enter a country name:', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id='my_country_picker', 
            options = countries,
            value=['Switzerland'],
            multi=True
            )],
        style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),

    html.Div([
        html.H3('Select a start and end date:'),
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=date(2019,12,31),
            max_date_allowed=date.today(),
            start_date=date(2020,1,1),
            end_date=date.today() 
            )], 
        style={'display':'inline-block'}),

    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':16, 'marginLeft':'30px'}
            )],
        style={'display':'inline-block'}),

    dcc.Graph(
        id='my_graph', 
        figure={
            'data':[{'x':[1,2], 'y':[1,1]}]
            }
        )
    ])


@app.callback(
    Output('my_graph', 'figure'),
    [
        Input('submit-button', 'n_clicks')
        ],
    [
        State('my_country_picker', 'value'),
        State('my_date_picker', 'start_date'),  
        State('my_date_picker', 'end_date')
    ])

def update_graph(n_clicks, country_ticker, start_date, end_date):
    '''
    Update plot data for specified country and date range
    '''
    start = dt.datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = dt.datetime.strptime(end_date[:10], '%Y-%m-%d')

    curves = []
    df = pd.read_pickle(df_filepath)
    for country in country_ticker:
        c_df = df.loc[idx[country,start:end],idx['cumsum','NewConfCases']]
        dates_lst = [item[1] for item in c_df.index]
        curves.append({'x':dates_lst, 'y':list(c_df.values), 'name':country})


    
    # Slicing data per input country
    ##c_df = df.loc[idx[country_ticker,start:end],idx['cumsum','NewConfCases']]
    ##dates_lst = [item[1] for item in c_df.index] #inelegant but effective way to extract the dates from the sliced df
    fig = {
            #'data':[{'x':dates_lst, 'y':list(c_df.values)}],
            'data':curves,
            'layout': 
                go.Layout(
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