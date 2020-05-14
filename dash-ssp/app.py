# -*- coding: utf-8 -*-
"""
Created on Mon May  4 23:55:38 2020

@author: asus
"""

import pandas as pd
import os
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import webbrowser
from threading import Timer
import plotly.graph_objects as go

### Load data
fDir=os.getcwd()+os.sep+'data'
fName='data_cohv2.csv'
df = pd.read_csv(fDir+os.sep+fName, parse_dates=True)
df['SampleDate'] = pd.to_datetime(df['SampleDate'])
print(df.head())

### Initialise the app
app = dash.Dash(__name__)

### Create settings

well_list= [
    {"label": str(i), "value": str(i)}
    for i in df['WellName'].unique()
]

substance_list= [
    {"label": str(i), "value": str(i)}
    for i in df['Variable'].unique()
]
#print(substance_list)

date_list= [
    {"label": str(i), "value": str(i)}
    for i in df['SampleDate'].unique()
]
#print(date_list)


### Create global chart template
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

### Define the app
app.layout = html.Div()

### Create app layout
app.layout = html.Div(
    [
        html.Div(   ### logo, title, lear more
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("numineo_logo.png"),
                            id="app-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Groundwater monitoring data",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Visualisation & interpretation", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://numineo.fr",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(   ### choix utilisateur, 4 containers, 
            [
                html.Div(
                    [
                        html.H6(
                            "Settings",
                            className="panel_label",
                        ),
                        html.P("Well", className="control_label"),
                        dcc.Dropdown(
                            id="well_choice",
                            options=well_list,
                            multi=True,
                            value=list(df['WellName'].unique()[0]),
                            className="dcc_control",
                        ),
                        #html.P("Date", className="control_label"),
                        #dcc.Dropdown(
                            #id="date_choice",
                            #options=date_list,
                            #multi=True,
                            #value=list(df['SampleDate'].unique()[0]),
                            #className="dcc_control",
                        #),
                        html.P("Substance", className="control_label"),
                        dcc.Dropdown(
                            id="substance_choice",
                            options=substance_list,
                            multi=True,
                            value=list(df['Variable'].unique()[0]),
                            className="dcc_control",
                        ),
                        html.P("Solute conc. Unit", className="control_label"),
                        dcc.RadioItems(
                            id="unit_choise",
                            options=[
                                {"label": "ng/l ", "value": "ng"},
                                {"label": "ug/l ", "value": "ug"},
                                {"label": "mg/l ", "value": "mg"},
                            ],
                            value="ug",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="timeseries")],
                            className="pretty_container",
                        )
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        )
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
) 

### Helper functions
def filter_df(df, well_choice, substance_choice):
    dff = df[
        df["WellName"].isin(well_choice)
        & df["Variable"].isin(substance_choice)
        ]
    return dff

### Update Time Series

@app.callback(
    Output("timeseries", "figure"),
    [
        Input("well_choice", "value"),
        #Input("date_choice", "value"),
        Input("substance_choice", "value"),
    ],
)

def update_graph(well_choice, substance_choice):
    trace1 = []
    for well in well_choice:
        for sub in substance_choice:
            dff=filter_df(df,[well],[sub])
            trace1.append(go.Scatter(x=dff['SampleDate'],
                                     y=dff['Result'],
                                     #mode='lines+markers',
                                     mode='markers',
                                     opacity=0.7,
                                     name=well+' '+sub,
                                     textposition='bottom center',
                                     #line=dict(shape="spline", smoothing=0.5, width=1),
                                     marker=dict(symbol="diamond-open")
                                     ))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  autosize=True,
                  title={'text': 'TimeSeries', 'font': {'color': 'black'}, 'x': 0.5},
              ),

              }

    return figure

### Run the app
def open_browser():
    webbrowser.open_new('http://127.0.0.1:2000/')

if __name__ == '__main__':
    Timer(1, open_browser).start();
    app.run_server(debug=True, port=2000)