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

#
# INPUT DATA ---------------
#
# pickle filepaths; relative for deployement and absolute for debugging
df_filepath = "../../backend/working/_output/pckl/covid_df.pckl"
#df_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/covid_df.pckl"
w_df_filepath = "../../backend/working/_output/pckl/covid_per_capita_df.pckl"
#w_df_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/covid_per_capita_df.pckl"
countries_filepath = "../../backend/working/_output/pckl/countries_lst.pckl"
#countries_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/countries_lst.pckl"

# loading list of countries
with open(countries_filepath, 'rb') as f:
     countries_lst = pickle.load(f)
# for html.Button, appending dicts, {'label':'value'}, {'user sees':'script sees'}
countries = [{'label':country, 'value':country} for country in countries_lst]


def post_country_dayone(df, thresh=1, countries=['Switzerland', 'Italy', 'France', 'Germany', 'United Kingdom', 'South Korea', 'China', 'Poland', 'Russia', 'United States Of America'], legend=True, lw=4, clmn_name='w_NewConfCases'):
    '''
    Prepare DataFrame for visualization for the specified country

    Params:
    -------
    df: pandas DataFrame, COVID dataframe
    thresh: int, min number of cumulative cases for plotting; if not met, the country is skipped
    countries: list, list of countries to plot
    
    Return: 
    -------
    '''

    df_dict = {}

    if thresh > 1:
        thresh = thresh-1

    else:
        pass
    
    for country in countries:
    
        c_df = df.loc[country, idx[:,clmn_name]]
        
        #checking if the specific country has reached thresh
        if (c_df['cumsum'].sum(axis=1)>thresh).sum()>0:
            date_first_case = (c_df['cumsum'].sum(axis=1)>thresh).idxmax() #identifying first date with 1 case
            
            days = c_df.loc[date_first_case:,'cumsum'].size
            c_cumsum_df = c_df.loc[date_first_case:,'cumsum']
            c_cumsum_df['day'] = np.arange(1,days+1,1)
            c_cumsum_df = c_cumsum_df.reset_index().set_index(['day'])[[clmn_name]].rename({clmn_name:country})
            if thresh<1.:
                # in case it is a per capita value, then scale it for visulization, else keep as it is
                c_cumsum_df = c_cumsum_df / thresh # e.g. thresh = 1.e-6 -> case per million inhabitants
            df_dict.update({country : c_cumsum_df})

    return df_dict




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('COVID-19 | Explorative Data Visualization'),
    
    dcc.Markdown(
        'Explorative data analysis and visualizations based on a COVID-19 dataset provided by the [European Centre for Disease Prevention and Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide).'
        ),
    
    html.Div([
        html.H3('Enter a country name:', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id='my_country_picker', 
            options = countries,
            value=['Switzerland', 'Italy', 'Germany', 'France'],
            multi=True
            )],
        style={'display':'inline-block', 'verticalAlign':'top', 'width':'50%'}),

    html.Div([
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Submit',
            style={'fontSize':16, 'marginTop' : '30px', 'margin':'30px'}
            )],
        #style={'display':'inline-block'}
        ),

    dcc.Graph(
        id='my_graph_capita', 
        figure={
            'data':[{'x':[1,2], 'y':[1,1]}]
            }
        ),
    dcc.Graph(
        id='my_graph_total', 
        figure={
            'data':[{'x':[1,2], 'y':[1,2]}]
            }
        ),

    dcc.Markdown(
        '`All information on this page is of unofficial nature and may contain error.\nNo liability for the correctness of the data is provided.\nOfficial data and information can be found on official sources websites.`'
        ),

    dcc.Markdown(
        'March 2020, [https://github.com/ilmitch/](https://github.com/ilmitch/)'
        ),
    dcc.Markdown(""),
    ])

#
# PER CAPITA 
#
@app.callback(
    Output('my_graph_capita', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_country_picker', 'value')])
def update_graph_capita(n_clicks, country_ticker):
    '''
    Update data for per capita cumulative plot for specified country
    '''

    curves = []

    df = pd.read_pickle(w_df_filepath)
    df_dict = post_country_dayone(df, thresh=1e-6, countries=country_ticker, clmn_name='w_NewConfCases')

    for key, value in df_dict.items():
        country = key
        x = value.index.values #date array
        y = value['w_NewConfCases'].values #pd.Series values array
        curves.append({'x':x, 'y':y, 'name':country})

    # Slicing data per input country
    fig = {
            'data':curves,
            'layout': 
                go.Layout(
                    title="Per Capita Total Confirmed Cases (per million inhabitants)",
                    yaxis={
                        'title': 'Total Confirmed Cases',
                        'type': 'log'
                        },
                    xaxis={'title': 'Days From First Confirmed Case'},
                    hovermode='closest'
            )}
    return fig

#
# CUMULATIVE 
#
@app.callback(
    Output('my_graph_total', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_country_picker', 'value')])
def update_graph_total(n_clicks, country_ticker):
    '''
    Update data for cumulative plot for specified country
    '''

    curves = []

    df = pd.read_pickle(df_filepath)
    df_dict = post_country_dayone(df, thresh=100., countries=country_ticker, clmn_name='NewConfCases')

    for key, value in df_dict.items():
        country = key
        x = value.index.values #date array
        y = value['NewConfCases'].values #pd.Series values array
        curves.append({'x':x, 'y':y, 'name':country})

    # Slicing data per input country
    fig = {
            'data':curves,
            'layout': 
                go.Layout(
                    title="Total Confirmed Cases (from 100 cases)",
                    yaxis={
                        'title': 'Total Confirmed Cases',
                        'type': 'log'
                        },
                    xaxis={'title': 'Days From First Confirmed Case'},
                    hovermode='closest'
            )}
    return fig

if __name__ == '__main__':
    app.run_server()