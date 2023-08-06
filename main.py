# Import packages

import dash_ag_grid as dag
from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px

# Importing data
df = pd.read_excel('data.xlsx', sheet_name='MOSFETS')
print(df)

# Setting header names and options
columnDefinition = [{"field": i} for i in df.columns]
for d in columnDefinition:
    if d['field'] == "mpn":
        d.update({
            'headerName': 'Part Number',
            'pinned': True,
            'checkboxSelection': True,
            'headerCheckboxSelection': True,
        })
    elif d['field'] == "manufacturer":
        d.update({
            "filter": "agStringColumnFilter",
            "filterParams": {
                "filterPlaceholder": d.get('field') + '...',
                "alwaysShowBothConditions": False,
            }
        })
    else:
        d.update({
            "filter": "agNumberColumnFilter",
            "filterParams": {
                "filterPlaceholder": d.get('field') + '...',
                "alwaysShowBothConditions": True,
                "defaultJoinOperator": "AND",
            }
        })

print(columnDefinition)
print(df)

table = dag.AgGrid(
    id="data-selection-table",
    columnDefs=columnDefinition,
    rowData=df.to_dict("records"),
    defaultColDef={
        "flex": 0,
        "minWidth": 150,
        "width":150,
        "sortable": True,
        "resizable": True,
        "filter": True,
    },
    dashGridOptions={
        "rowSelection": "multiple",
        "pagination": True,
        "paginationPageSize": 10
    },
    selectedRows=df.head(4).to_dict("records"),
    style={"margin": 20},
    columnSize="sizeToFit",
    className='ag-theme-balham'
)

graph = dcc.Graph(
    id='data-graph',
    figure=px.scatter(
        df,
        x='q_g',
        y='r_ds_on',
        size='c_oss',
        color='mpn',
    ),
    className="border",
)

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1(children='MOSFETs', style={'textAlign': 'center', 'color': '#7FDBFF'}),
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Part Selection', children=[
            graph,
            table,
            html.Div(id="selections-checkbox-output"),

        ]),
        dcc.Tab(label='Output', children=[
            # graph
        ]),
    ]),

])

@callback(
    Output('data-graph', 'figure'),
    Input('data-selection-table', 'selectedRows'))
def update_graph(selected):
    if selected:
        dff = pd.DataFrame(selected)
        fig = px.scatter(
            dff,
            x='q_g',
            y='r_ds_on',
            size='c_oss',
            color='mpn',
        )
        return fig
    else:
        return df


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
