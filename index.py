import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from google.oauth2 import service_account
import pandas_gbq as pd1
import plotly.graph_objs as go
import dash_daq as daq
import pandas as pd
import csv
import dash_bootstrap_components as dbc

meta_tags = [{"name": "viewport", "content": "width=device-width"}]
external_stylesheets = [meta_tags]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([

    dcc.Interval(id='update_value',
                 interval=1 * 11000,
                 n_intervals=0),

    dcc.Interval(id='update_value1',
                 interval=1 * 5000,
                 n_intervals=0),

    html.Div([

        html.Div([
            html.Div([
                html.Img(src=app.get_asset_url('sensor.png'),
                         style={'height': '30px'},
                         className='title_image'
                         ),
                html.Div('ARDUINO WEATHER SENSORS',
                         className='title_text')
            ], className='title_row'),

            html.Div('Sensors Location: Walsall, England',
                     className='location'),

            dbc.Spinner(html.Div(id='date',
                                 className='date_id'))
        ], className='title_location_row')

    ], className='bg_title'),

    html.Div([
        html.Div([
            html.Div([
                daq.Gauge(id='daq_gauge1',
                          showCurrentValue=True,
                          units='°C',
                          value=0,
                          label='Temperature',
                          style={'color': 'white',
                                 'fontFamily': 'sans-serif',
                                 'fontWeight': 'bold'},
                          max=20,
                          min=0,
                          color='#1EEC11')
            ], className='chart_value1 twelve columns'),

            html.Div([
                daq.Gauge(id='daq_gauge2',
                          showCurrentValue=True,
                          units='%',
                          value=0,
                          label='Humidity',
                          style={'color': 'white',
                                 'fontFamily': 'sans-serif',
                                 'fontWeight': 'bold'},
                          max=100,
                          min=0,
                          color='#DFFF00')
            ], className='chart_value2 twelve columns')
        ], className='gauge_chart four columns'),

        html.Div([
            dcc.Graph(id='line_chart1',
                      config={'displayModeBar': False},
                      className='line_chart_layout twelve columns'),
            dcc.Graph(id='line_chart2',
                      config={'displayModeBar': False},
                      className='line_chart_layout twelve columns'),
        ], className='line_chart four columns')
    ], className='row chart_row')
], id='mainContainer', style={'display': 'flex', 'flex-direction': 'column'})


@app.callback(Output('date', 'children'),
              [Input('update_value', 'n_intervals')])
def update_confirmed(n_intervals):
    credentials = service_account.Credentials.from_service_account_file('weatherdata1.json')
    project_id = 'weatherdata1'
    df_sql = f"""SELECT *
                             FROM
                             `weatherdata1.WeatherSensorsData1.SensorsData1`
                             ORDER BY
                             DateTime DESC LIMIT 1
                             """
    df = pd1.read_gbq(df_sql, project_id=project_id, dialect='standard', credentials=credentials)
    df1 = df.tail(1)
    df2 = df1.values.tolist()[0]
    with open('data1.csv', 'a', newline='\n') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(df2)

    header = ['DateTime', 'InsideHumidity', 'InsideTemperature', 'InsideCO2',
              'OutsideHumidity', 'OutsideTemperature', 'OutsideCO2']
    df3 = pd.read_csv('data1.csv', names=header)
    df3.drop_duplicates(keep=False, inplace=True)
    get_date = df3['DateTime'].tail(1).iloc[0]

    return [
        html.Div('Last Date Update Time: ' + get_date,
                 className='date_format')
    ]


@app.callback(Output('daq_gauge1', 'value'),
              [Input('update_value1', 'n_intervals')])
def update_confirmed(n_intervals):
    header = ['DateTime', 'InsideHumidity', 'InsideTemperature', 'InsideCO2',
              'OutsideHumidity', 'OutsideTemperature', 'OutsideCO2']
    df3 = pd.read_csv('data1.csv', names=header)
    df3.drop_duplicates(keep=False, inplace=True)
    get_temp = df3['OutsideTemperature'].tail(1).iloc[0]
    return get_temp


@app.callback(Output('daq_gauge2', 'value'),
              [Input('update_value1', 'n_intervals')])
def update_confirmed(n_intervals):
    header = ['DateTime', 'InsideHumidity', 'InsideTemperature', 'InsideCO2',
              'OutsideHumidity', 'OutsideTemperature', 'OutsideCO2']
    df3 = pd.read_csv('data1.csv', names=header)
    df3.drop_duplicates(keep=False, inplace=True)
    get_hum = df3['OutsideHumidity'].tail(1).iloc[0]
    return get_hum


@app.callback(Output('line_chart1', 'figure'),
              [Input('update_value1', 'n_intervals')])
def line_chart_values(n_intervals):
    header = ['DateTime', 'InsideHumidity', 'InsideTemperature', 'InsideCO2',
              'OutsideHumidity', 'OutsideTemperature', 'OutsideCO2']
    df = pd.read_csv('data1.csv', names=header)
    df.drop_duplicates(keep=False, inplace=True)

    return {
        'data': [go.Scatter(
            x=df['DateTime'].tail(15),
            y=df['OutsideTemperature'].tail(15),
            mode='markers+lines',
            line=dict(width=3, color='#1EEC11'),
            marker=dict(size=7, symbol='circle', color='#1EEC11',
                        line=dict(color='#1EEC11', width=2)
                        ),
            hoverinfo='text',
            hovertext=
            '<b>Date Time</b>: ' + df['DateTime'].tail(15).astype(str) + '<br>' +
            '<b>Temperature (°C)</b>: ' + [f'{x:,.2f} °C' for x in df['OutsideTemperature'].tail(15)] + '<br>'
        )],

        'layout': go.Layout(
            plot_bgcolor='rgba(255, 255, 255, 0)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            title={
                'text': '<b>Temperature (°C)</b>',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont={
                'color': '#ffbf00',
                'size': 17},
            margin=dict(t=50, r=10),
            xaxis=dict(
                title='<b>Hours</b>',
                color='#ffffff',
                showline=True,
                showgrid=True,
                linecolor='#ffffff',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='#ffffff')

            ),

            yaxis=dict(
                range=[min(df['OutsideTemperature'].tail(15)) - 0.05, max(df['OutsideTemperature'].tail(15)) + 0.05],
                title='<b>Temperature (°C)</b>',
                color='#ffffff',
                zeroline=False,
                showline=True,
                showgrid=True,
                linecolor='#ffffff',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='#ffffff')

            ),
            font=dict(
                family="sans-serif",
                size=12,
                color='#ffffff')

        )

    }


@app.callback(Output('line_chart2', 'figure'),
              [Input('update_value1', 'n_intervals')])
def line_chart_values(n_intervals):
    header = ['DateTime', 'InsideHumidity', 'InsideTemperature', 'InsideCO2',
              'OutsideHumidity', 'OutsideTemperature', 'OutsideCO2']
    df = pd.read_csv('data1.csv', names=header)
    df.drop_duplicates(keep=False, inplace=True)

    return {
        'data': [go.Scatter(
            x=df['DateTime'].tail(15),
            y=df['OutsideHumidity'].tail(15),
            mode='markers+lines',
            line=dict(width=3, color='#DFFF00'),
            marker=dict(size=7, symbol='circle', color='#DFFF00',
                        line=dict(color='#DFFF00', width=2)
                        ),
            hoverinfo='text',
            hovertext=
            '<b>Date Time</b>: ' + df['DateTime'].tail(15).astype(str) + '<br>' +
            '<b>Temperature (°C)</b>: ' + [f'{x:,.2f} °C' for x in df['OutsideHumidity'].tail(15)] + '<br>'
        )],

        'layout': go.Layout(
            plot_bgcolor='rgba(255, 255, 255, 0)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            title={
                'text': '<b>Humidity (%)</b>',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            titlefont={
                'color': '#ffbf00',
                'size': 17},
            margin=dict(t=50, r=10),
            xaxis=dict(
                title='<b>Hours</b>',
                color='#ffffff',
                showline=True,
                showgrid=True,
                linecolor='#ffffff',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='#ffffff')

            ),

            yaxis=dict(range=[min(df['OutsideHumidity'].tail(15)) - 0.05, max(df['OutsideHumidity'].tail(15)) + 0.05],
                       title='<b>Humidity (%)</b>',
                       color='#ffffff',
                       zeroline=False,
                       showline=True,
                       showgrid=True,
                       linecolor='#ffffff',
                       linewidth=1,
                       ticks='outside',
                       tickfont=dict(
                           family='Arial',
                           size=12,
                           color='#ffffff')

                       ),
            font=dict(
                family="sans-serif",
                size=12,
                color='#ffffff')

        )

    }


if __name__ == '__main__':
    app.run_server(debug=True)
