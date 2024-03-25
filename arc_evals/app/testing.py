import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data
df1 = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})

df2 = pd.DataFrame({"x": ["A", "B", "C", "D", "E"], "y": [10, 7, 5, 3, 1]})

# Layout
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [dcc.Graph(id="figure1", config={"displayModeBar": False})], style={"padding": "0"}
                                )
                            ],
                            className="mb-4",
                            style={"height": "100%"},
                        )
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [dcc.Graph(id="figure2", config={"displayModeBar": False})], style={"padding": "0"}
                                )
                            ],
                            className="mb-4",
                            style={"height": "100%"},
                        )
                    ],
                    width=6,
                ),
            ]
        )
    ],
    fluid=True,
)


# Callbacks
@app.callback(Output("figure1", "figure"), Input("figure1", "id"))
def update_figure1(id):
    fig = px.line(df1, x="x", y="y")
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


@app.callback(Output("figure2", "figure"), Input("figure2", "id"))
def update_figure2(id):
    fig = px.bar(df2, x="x", y="y")
    fig.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        margin=dict(t=0, b=0, l=0, r=0),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
