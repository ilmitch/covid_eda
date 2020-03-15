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
# pickle filepaths
df_filepath = "../../backend/working/_output/pckl/covid_df.pckl"
df_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/countries_lst.pckl"
w_df_filepath = "../../backend/working/_output/pckl/covid_per_capita_df.pckl"
w_df_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/covid_per_capita_df.pckl"
countries_filepath = "../../backend/working/_output/pckl/countries_lst.pckl"
countries_filepath = "/Users/Michele/Documents/Python/04_Projects/2020_03_Covid_EDA/backend/working/_output/pckl/countries_lst.pckl"

# loading list of countries
with open(countries_filepath, 'rb') as f:
     countries_lst = pickle.load(f)
#appending dicts, {'label':'value'}, {'user sees':'script sees'}
countries = [{'label':country, 'value':country} for country in countries_lst]


def post_country_dayone(df, thresh=1, countries=['Switzerland', 'Italy', 'France', 'Germany', 'United Kingdom', 'South Korea', 'China', 'Poland', 'Russia', 'United States Of America'], legend=True, lw=4, clmn_name='w_NewConfCases'):
    '''
    
    Params:
    -------
    df: pandas DataFrame, COVID dataframe
    thresh: int, min number of cumulative cases for plotting; if not met, the country is skipped
    countries: list, list of countries to plot
    
    Return: 
    -------
    '''

    df_dict = {}

    if thresh >= 1:
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
            
            df_dict.update({country : c_cumsum_df})

    return df_dict






app = dash.Dash()

app.layout = html.Div([
    html.H1('COVID-19 | Explorative Data Visualization'),

    html.Div([
        html.H3('Enter a country name:', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id='my_country_picker', 
            options = countries,
            value=['Switzerland', 'Italy', 'Germany', 'France'],
            multi=True
            )],
        style={'display':'inline-block', 'verticalAlign':'top', 'width':'30%'}),

    # html.Div([
    #     html.H3('Select a start and end date:'),
    #     dcc.DatePickerRange(
    #         id='my_date_picker',
    #         min_date_allowed=date(2019,12,31),
    #         max_date_allowed=date.today(),
    #         start_date=date(2020,1,1),
    #         end_date=date.today() 
    #         )], 
    #     style={'display':'inline-block'}),

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
    [Input('submit-button', 'n_clicks')],
    [State('my_country_picker', 'value')])
def update_graph(n_clicks, country_ticker):
    '''
    Update plot data for specified country and date range
    '''

    curves = []

    df = pd.read_pickle(w_df_filepath)
    df_dict = post_country_dayone(df, thresh=1e-6, countries=country_ticker)

    for key, value in df_dict.items():
        country = key
        x = value.index.values #date list
        y = value['w_NewConfCases'].values #pd.Series values
        #dates_lst = [item[1] for item in c_df.index]
        curves.append({'x':x, 'y':y, 'name':country})

    # Slicing data per input country
    fig = {
            #'data':[{'x':dates_lst, 'y':list(c_df.values)}],
            'data':curves,
            'layout': 
                go.Layout(
                    yaxis={
                        'title': 'Total Confirmed Cases',
                        'type': 'linear'
                        },
                    #margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                    hovermode='closest'
            )}
    return fig


if __name__ == '__main__':
    app.run_server()