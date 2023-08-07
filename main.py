# Import packages

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dash_table, dcc, callback, Input, Output, Patch
import pandas as pd
import plotly.express as px

from bench import workbench, transistor

scatter_width = None
scatter_height = 600

# Importing and defining styles
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template(["minty", "morph", "slate"])
temp = "minty"

# Importing data
df = pd.read_csv('data.csv')

q1 = transistor(df, 4)
wb1 = workbench(100, 2, 0.5, 100e3)
wb1.solder_transistor(q1)
lst = [10**i for i in range(7)]
wb1.set_sweep_list(lst)

sweep1 = wb1.frequency_sweep()
print(sweep1)
print(q1.mpn)
print(q1.r_ds_on)

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

# defining table
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

# defining preview graph
graph = dcc.Graph(
    id='data-graph',
    figure=px.scatter(
        df,
        x='q_g',
        y='r_ds_on',
        size='c_oss',
        color='mpn',
        template=temp,
        width=scatter_width,
        height=scatter_height,
    ),

)

parameter_list = ["None"] + [i for i in df.select_dtypes(include='number')]
default_x_param = parameter_list[2]
default_y_param = parameter_list[3]
default_z_param = parameter_list[0]

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc_css])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "max-width": "1800px",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("MOSFET APP", className="display-4"),
        html.Hr(),
        html.P(
            "N-MOS power loss estimation tool", className="lead"
        ),
        dbc.Nav(
            [
                dbc.Progress(),
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Setup", href="/setup", active="exact"),
                dbc.NavLink("Result", href="/result", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content_home = dbc.Container([
    dbc.Label("Home"),
],
    className="dbc",
    id="content-home",
    style={'display': 'inline'}
)

content_setup = dbc.Container([
    dbc.Row([graph]),
    dbc.Row([
        dbc.Col([
            dbc.Label("X-Axis:"),
            dcc.Dropdown(parameter_list, id="dropdown-preview-graph-x-axis", value=default_x_param,
                         placeholder="X-axis"),
        ],
            width=1
        ),
        dbc.Col([
            dbc.Label("Y-Axis:"),
            dcc.Dropdown(parameter_list, id="dropdown-preview-graph-y-axis", value=default_y_param,
                         placeholder="Y-axis"),
        ],
            width=1
        ),
        dbc.Col([
            dbc.Label("Size:"),
            dcc.Dropdown(parameter_list, id="dropdown-preview-graph-z-axis", value=default_z_param,
                         placeholder="Size-axis"),
        ],
            width=1
        ),
    ],
        justify="center"
    ),
    html.Br(),
    table,
    html.Div(id="selections-checkbox-output"),
],
    className="dbc",
    id="content-setup",
    style={'display': 'inline'}
)

content_result = dbc.Container([
    dbc.Label("Result"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Row1 Col1"),
            dcc.Graph(id="result_graph_1_1",
                      figure=px.line(sweep1, x="frequency", y = sweep1.columns)
                      )
        ]),
        dbc.Col([
            dbc.Label("Row1 Col2"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Row2 Col1"),
        ]),
        dbc.Col([
            dbc.Label("Row2 Col2"),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Row3 Col1"),
        ]),
        dbc.Col([
            dbc.Label("Row3 Col2"),
        ]),
    ]),
],
    className="dbc",
    id="content-result",
    style={'display': 'inline'}
)

content = html.Div(children=[content_home, content_setup, content_result], id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@callback(
    Output('data-graph', 'figure'),
    Input('data-selection-table', 'selectedRows'),
    Input('dropdown-preview-graph-x-axis', 'value'),
    Input('dropdown-preview-graph-y-axis', 'value'),
    Input('dropdown-preview-graph-z-axis', 'value'))
def update_graph(selected, value_x, value_y, value_z):
    values_xyz = [value_x, value_y, value_z]
    for i in range(len(values_xyz)):
        if values_xyz[i] == "None":
            values_xyz[i] = None
    if selected:
        dff = pd.DataFrame(selected)
        fig = px.scatter(
            dff,
            x=values_xyz[0],
            y=values_xyz[1],
            size=values_xyz[2],
            color='mpn',
            template=temp,
            width=scatter_width,
            height=scatter_height
        )
        return fig
    else:
        fig = px.scatter(
            df,
            x=default_x_param,
            y=default_y_param,
            size=default_z_param,
            color='mpn',
            template=temp,
            width=scatter_width,
            height=scatter_height
        )
        return fig


@app.callback(Output("content-home", "style"), [Input("url", "pathname")])
def render_page_home(pathname):
    return {'display': 'inline'} if (pathname == "/") else {'display': 'None'}


@app.callback(Output("content-setup", "style"), [Input("url", "pathname")])
def render_page_setup(pathname):
    return {'display': 'inline'} if (pathname == "/setup") else {'display': 'None'}


@app.callback(Output("content-result", "style"), [Input("url", "pathname")])
def render_page_result(pathname):
    return {'display': 'inline'} if (pathname == "/result") else {'display': 'None'}


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
