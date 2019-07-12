import base64
import datetime
import io
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc 
import pandas as pd


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'TATA STEEL CUSTOMIZED REPORTS'

navbar = dbc.NavbarSimple(id="navBar",color="#256caa",dark=True,
    brand="TATA STEEL",
    brand_href="#",
    sticky="top",
)
jumbotron1 = dbc.Jumbotron(
    [
        html.H1("WELCOME TO CUSTOMIZED REPORTS", className="display-3"),
        html.P(
            "Users can customize the report that "
            "features content or information.",
            className="lead",
        ),
        html.Hr(className="my-2"),
        html.P(
            "Upload your .csv or .xlsx files to "
            "experience customized reports"
        ),
        html.P(dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '97.8%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
        },
        # Allow multiple files to be uploaded
        multiple=True
    ), className="lead"),
    ]
)

jumbotron2 = dbc.Jumbotron(
    [
        html.H1("", className="display-3"),
        html.P(
            "select your attributes "
            "for generation of reports: ",
            className="lead",
        ),
        html.Hr(className="my-2"),
        html.P(
            ""
        ),
        html.P(dcc.Dropdown(id='drop',placeholder="SELECT ATTRIBUTES IN THIS FILE:",multi=True,style={'width':'60%','Align': 'center'}), className="lead"),
    ]
)

jumbotron3 = dbc.Jumbotron(
    [
        html.H1("Your customized graph", className="display-3"),
        html.P(
            "pie graph",
            className="lead",
        ),
        html.Hr(className="my-2"),
        html.P(
            ""
        ),
        html.P(dcc.Graph(id='pie',figure={}), className="lead"),
    ]
)
app.layout = html.Div([
    navbar,jumbotron1,html.Div(id='output-data-upload'),html.Hr(),
    jumbotron2,
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.Hr(),
    jumbotron3
])

@app.callback([Output('output-data-upload', 'children'),
            Output('drop','options'),
            Output('intermediate-value', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        for content, filename, date in zip(list_of_contents, list_of_names, list_of_dates):
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            try:
                if 'csv' in filename:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    dc=df.copy()
                    smp=df.sample(5)
                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
                    dc=df.copy()
                    smp=df.sample(5)
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])
        children=[
                html.Div([
                html.H5(filename +'\'s sample data:'),
                html.H6(datetime.datetime.fromtimestamp(date)),
                dash_table.DataTable(
                data=smp.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in smp.columns] ),
                ])]
        attr=[{'label': i, 'value': i}for i in dc.columns]
        cleaned_df = dc

    return [children,attr,cleaned_df.to_json(date_format='iso', orient='split')]

global dc
dc = pd.DataFrame()

@app.callback(Output('pie','figure'),
                [Input('drop','value'),
                Input('intermediate-value', 'children')])
def graph(value,jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')
    readers=dff[value]
    #dataframe for readers count ie....how many times used.
    readcount=pd.DataFrame({'count' : readers.groupby( value ).size()}).reset_index()
    return {'data': [go.Pie(labels=readcount[value], values=readcount['count'],marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='label')],
                                'layout':go.Layout(title=" ",legend={"x": 1, "y": 1}),
                            }


if __name__ == '__main__':
    app.run_server(debug=False)