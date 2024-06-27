#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Statistics Dashboard"

# List of years
year_list = [i for i in range(1980, 2014)]

# Create the layout of the app
app.layout = html.Div([
    # Add title to the dashboard
    html.H1("Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([  # Add two dropdown menus
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            style={'width': '80%', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center'}),
    html.Div(dcc.Dropdown(
        id='select-year',
        options=[{'label': i, 'value': i} for i in year_list],
        placeholder='Select a year',
        style={'width': '80%', 'margin': 'auto'}
    ), style={'textAlign': 'center'}),
    html.Div([  # Add a division for output display
        html.Div(id='output-container', className='chart-grid', style={
            'display': 'grid',
            'gridTemplateColumns': '1fr 1fr',
            'gap': '20px',
            'padding': '20px'
        })
    ])
])

# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value'))
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

# Callback for plotting
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='select-year', component_property='value'), Input(component_id='dropdown-statistics', component_property='value')])
def update_output_container(input_year, selected_statistics):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]

        # Plot 1: Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec,
                           x='Year',
                           y='Automobile_Sales',
                           title="Average Automobile Sales fluctuation over Recession Period"))

        # Plot 2: Calculate the average number of vehicles sold by vehicle type
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(
            average_sales,
            x='Vehicle_Type',
            y='Automobile_Sales',
            title='Average Number of Vehicles Sold by Vehicle Type During Recession Period'))

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(
            exp_rec,
            values='Advertising_Expenditure',
            names='Vehicle_Type',
            title='Total Advertisement Expenditure by Vehicle Type during Recession'
        ))

        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unemployment_effect = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().unstack().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(unemployment_effect,
                                           x='unemployment_rate',
                                           y=unemployment_effect.columns[1:],
                                           title='Effect of Unemployment Rate on Vehicle Type and Sales'))

        return [
            html.Div(children=R_chart1, style={'width': '100%'}),
            html.Div(children=R_chart2, style={'width': '100%'}),
            html.Div(children=R_chart3, style={'width': '100%'}),
            html.Div(children=R_chart4, style={'width': '100%'})
        ]

    elif (input_year and selected_statistics == 'Yearly Statistics'):
        yearly_data = data[data['Year'] == input_year]

        # Plot 1: Yearly Automobile sales using line chart for the whole period.
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales', title='Yearly Average Automobile Sales'))

        # Plot 2: Total Monthly Automobile sales using line chart.
        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(monthly_sales, x='Month', y='Automobile_Sales', title='Total Monthly Automobile Sales'))

        # Plot 3: Bar chart for average number of vehicles sold during the given year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata,
                                           x='Vehicle_Type',
                                           y='Automobile_Sales',
                                           title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year)))

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(exp_data,
                                           values='Advertising_Expenditure',
                                           names='Vehicle_Type',
                                           title='Total Advertisement Expenditure for Each Vehicle'))

        return [
            html.Div(children=Y_chart1, style={'width': '100%'}),
            html.Div(children=Y_chart2, style={'width': '100%'}),
            html.Div(children=Y_chart3, style={'width': '100%'}),
            html.Div(children=Y_chart4, style={'width': '100%'})
        ]

    else:
        return None

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
