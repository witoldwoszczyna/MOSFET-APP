# Import packages

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dash_table, dcc, callback, Input, Output, Patch
import pandas as pd
import plotly.express as px


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template(["minty", "morph", "slate"])
temp = "minty"

# Importing data
df = pd.read_csv('data.csv')

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

table = dag.AgGrid(
    id="data-selection-table",
    columnDefs=columnDefinition,
    rowData=df.to_dict("records"),
    defaultColDef={
        "flex": 0,
        "minWidth": 150,
        "width": 150,
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
    style={"margin": 10, "width": "fit"},
    columnSize="sizeToFit",
    className="ag-theme-balham",
)

graph = dcc.Graph(
    id='data-graph',
    figure=px.scatter(
        df,
        x='q_g',
        y='r_ds_on',
        size='c_oss',
        color='mpn',
        template=temp
    ),
)

default_x_param=df.columns[4]
print(df.columns[4])
default_y_param=df.columns[3]
print(df.columns[3])
default_z_param=df.columns[6]
print(df.columns[6])

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc_css])

# App layout
app.layout = dbc.Container([

    dbc.Label("dcc.Dropdown with Bootstrap theme"),
    dcc.Dropdown([i for i in df.select_dtypes(include='number')], id="dropdown-preview-graph-x-axis", value=default_x_param,
                 placeholder="X-axis"),
    dcc.Dropdown([i for i in df.select_dtypes(include='number')], id="dropdown-preview-graph-y-axis", value=default_y_param,
                 placeholder="Y-axis"),
    dcc.Dropdown([i for i in df.select_dtypes(include='number')], id="dropdown-preview-graph-z-axis", value=default_z_param,
                 placeholder="Size-axis"),

    html.Br(),
    graph,
    table,
    html.Div(id="selections-checkbox-output"),
],
    className="dbc",
)


@callback(
    Output('data-graph', 'figure'),
    Input('data-selection-table', 'selectedRows'),
    Input('dropdown-preview-graph-x-axis', 'value'),
    Input('dropdown-preview-graph-y-axis', 'value'),
    Input('dropdown-preview-graph-z-axis', 'value'))
def update_graph(selected, value_x, value_y, value_z):
    patched_fig = Patch()
    if selected:
        dff = pd.DataFrame(selected)
        fig = px.scatter(
            dff,
            x=value_x,
            y=value_y,
            size=value_z,
            color='mpn',
            template=temp,
        )
        return fig
    else:
        fig = px.scatter(
            df,
            x='q_g',
            y='r_ds_on',
            size='c_oss',
            color='mpn',
            template=temp,
        )
        return fig




# Run the app
if __name__ == '__main__':
    app.run(debug=True)
