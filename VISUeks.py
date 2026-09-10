import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)


data = pd.read_csv('house_info-geocoded.csv', encoding='utf-8')


#'cleaning' the data, hvorfor igen???
data['Price_(DKK)'] = (
    data['Price_(DKK)'].astype(str)
    .str.replace(',', '').str.replace('.', '').str.replace(' ', '')
)
data['Price_(DKK)'] = pd.to_numeric(data['Price_(DKK)'], errors='coerce')

data['Last_price_(DKK)'] = (
    data['Last_price_(DKK)'].astype(str)
    .str.replace(',', '').str.replace('.', '')
    .str.replace(' ', '').str.replace('kr', '')
)
data['Last_price_(DKK)'] = pd.to_numeric(data['Last_price_(DKK)'], errors='coerce')


data['Sqm'] = pd.to_numeric(data['Sqm'], errors='coerce')


data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')


data = data.dropna(subset=['latitude', 'longitude', 'Price_(DKK)', 'Sqm'])


#vores variabler
data['Decades'] = (data['Built_year'] // 10) * 10

heatingtypes = data['Heating_type'].dropna().unique().tolist()
heatingtypes.append('all')

decades_list = sorted(data['Decades'].dropna().unique().tolist())
decades_list.append('all')




app.layout = html.Div([
    html.H1("Plotting houses"),

    dcc.Dropdown(
        id='heating_types',
        options=[{'label': i, 'value': i} for i in heatingtypes],
        value='all'
    ),

    dcc.Dropdown(
        id='decade_types',
        options=[{'label': i, 'value': i} for i in decades_list],
        value='all'
    ),

    dcc.Graph(id='house_map'),
    dcc.Graph(id='house_chart'),
    dcc.Graph(id='house_table')
])



def filter_data(htype, dtype):
    mydata = data.copy()
    if htype != 'all':
        mydata = mydata[mydata['Heating_type'] == htype]
    if dtype != 'all':
        mydata = mydata[mydata['Decades'] == dtype]
    return mydata



@app.callback(
    Output('house_map', 'figure'),
    [
        Input('heating_types', 'value'),
        Input('decade_types', 'value'),
        Input('house_chart', 'clickData')
    ]
)
def update_map(htype, dtype, clickData):

    mydata = filter_data(htype, dtype).copy()


    clicked_decade = None
    if clickData and 'points' in clickData:
        clicked_decade = clickData['points'][0]['x']


    if clicked_decade is not None:
        mydata = mydata[mydata['Decades'] == clicked_decade]


    if mydata.empty:
        fig = px.scatter_geo(lat=[], lon=[])
        fig.update_geos(
            scope='europe',
            center=dict(lat=56, lon=10),
            projection_scale=5
        )
        return fig



    mydata['color'] = 'no_change'
    mydata.loc[mydata['Price_(DKK)'] > mydata['Last_price_(DKK)'], 'color'] = 'expensive'
    mydata.loc[mydata['Price_(DKK)'] < mydata['Last_price_(DKK)'], 'color'] = 'cheaper'


    fig = px.scatter_geo(
        mydata,
        lat='latitude',
        lon='longitude',
        scope='europe',
        size='Sqm',
        color='color',
        hover_name='Address',
        color_discrete_map={
            'expensive': 'red',
            'cheaper': 'blue',
            'no_change': 'gray'
        }
    )

    fig.update_geos(
        center=dict(lat=55.2, lon=10),
        projection_scale=60,
        showcountries=True
    )

    return fig



@app.callback(
    Output('house_chart', 'figure'),
    [
        Input('heating_types', 'value'),
        Input('decade_types', 'value')
    ]
)
def display_chart(htype, dtype):
    mydata = filter_data(htype, dtype)
    chart_data = mydata.groupby('Decades').size().reset_index(name='Number of houses')
    fig = px.bar(chart_data, x='Decades', y='Number of houses')
    fig.update_layout(clickmode='event+select')
    return fig



@app.callback(
    Output('house_table', 'figure'),
    [
        Input('heating_types', 'value'),
        Input('decade_types', 'value'),
        Input('house_chart', 'clickData')
    ]
)
def update_table(htype, dtype, clickData):
    mydata = filter_data(htype, dtype).copy()


    clicked_decade = None
    if clickData and 'points' in clickData:
        clicked_decade = clickData['points'][0]['x']


    if clicked_decade is not None:
        mydata = mydata[mydata['Decades'] == clicked_decade]


    if mydata.empty:
        fig = go.Figure(data=[go.Table(
            header=dict(values=["No data"]),
            cells=dict(values=[[""]])
        )])
        return fig

    fig = go.Figure(data=[go.Table(
        header=dict(values=[
            "Address", "Price (DKK)", "Last price (DKK)",
            "Built year", "Heating type"
        ]),
        cells=dict(values=[
            mydata['Address'],
            mydata['Price_(DKK)'],
            mydata['Last_price_(DKK)'],
            mydata['Built_year'],
            mydata['Heating_type']
        ])
    )])
    return fig


if __name__ == '__main__':
    app.run(debug=True, port=8080)
    #http://localhost:8080
    
    
    
    