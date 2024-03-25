import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Define your grid data as lists of lists of integers
grid1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
grid2 = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]
interactive_grid = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

# Define your color scale
color_scale = [
    [0.0, "rgb(255, 255, 255)"],
    [0.1, "rgb(255, 0, 0)"],
    [0.2, "rgb(0, 255, 0)"],
    [0.3, "rgb(0, 0, 255)"],
    [0.4, "rgb(255, 255, 0)"],
    [0.5, "rgb(255, 0, 255)"],
    [0.6, "rgb(0, 255, 255)"],
    [0.7, "rgb(128, 0, 0)"],
    [0.8, "rgb(0, 128, 0)"],
    [0.9, "rgb(0, 0, 128)"],
]

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Graph(figure=go.Figure(data=[go.Heatmap(z=grid1, hoverinfo="none", colorscale=color_scale)])),
                dcc.Graph(figure=go.Figure(data=[go.Heatmap(z=grid2, hoverinfo="none", colorscale=color_scale)])),
            ]
        ),
        html.Div(
            [
                dcc.Graph(
                    id="interactive-grid",
                    figure=go.Figure(data=[go.Heatmap(z=interactive_grid, hoverinfo="text", colorscale=color_scale)]),
                )
            ]
        ),
        html.Div(
            [
                html.Button("Color 1", id="color-1", style={"background-color": "rgb(255, 0, 0)"}),
                html.Button("Color 2", id="color-2", style={"background-color": "rgb(0, 255, 0)"}),
                html.Button("Color 3", id="color-3", style={"background-color": "rgb(0, 0, 255)"}),
                html.Button("Color 4", id="color-4", style={"background-color": "rgb(255, 255, 0)"}),
                html.Button("Color 5", id="color-5", style={"background-color": "rgb(255, 0, 255)"}),
                html.Button("Color 6", id="color-6", style={"background-color": "rgb(0, 255, 255)"}),
                html.Button("Color 7", id="color-7", style={"background-color": "rgb(128, 0, 0)"}),
                html.Button("Color 8", id="color-8", style={"background-color": "rgb(0, 128, 0)"}),
                html.Button("Color 9", id="color-9", style={"background-color": "rgb(0, 0, 128)"}),
                html.Button("Color 10", id="color-10", style={"background-color": "rgb(255, 255, 255)"}),
            ]
        ),
    ]
)


@app.callback(
    Output("interactive-grid", "figure"),
    [
        Input("interactive-grid", "clickData"),
        Input("color-1", "n_clicks"),
        Input("color-2", "n_clicks"),
        Input("color-3", "n_clicks"),
        Input("color-4", "n_clicks"),
        Input("color-5", "n_clicks"),
        Input("color-6", "n_clicks"),
        Input("color-7", "n_clicks"),
        Input("color-8", "n_clicks"),
        Input("color-9", "n_clicks"),
        Input("color-10", "n_clicks"),
    ],
)
def update_grid(
    click_data,
    color1_clicks,
    color2_clicks,
    color3_clicks,
    color4_clicks,
    color5_clicks,
    color6_clicks,
    color7_clicks,
    color8_clicks,
    color9_clicks,
    color10_clicks,
):
    # Retrieve the clicked cell's row and column indices
    if click_data:
        row = click_data["points"][0]["pointNumber"]
        col = click_data["points"][0]["curveNumber"]
        # Update the color of the clicked cell based on the selected color
        if dash.callback_context.triggered_id == "color-1":
            interactive_grid[row][col] = 1
        elif dash.callback_context.triggered_id == "color-2":
            interactive_grid[row][col] = 2
        elif dash.callback_context.triggered_id == "color-3":
            interactive_grid[row][col] = 3
        elif dash.callback_context.triggered_id == "color-4":
            interactive_grid[row][col] = 4
        elif dash.callback_context.triggered_id == "color-5":
            interactive_grid[row][col] = 5
        elif dash.callback_context.triggered_id == "color-6":
            interactive_grid[row][col] = 6
        elif dash.callback_context.triggered_id == "color-7":
            interactive_grid[row][col] = 7
        elif dash.callback_context.triggered_id == "color-8":
            interactive_grid[row][col] = 8
        elif dash.callback_context.triggered_id == "color-9":
            interactive_grid[row][col] = 9
        elif dash.callback_context.triggered_id == "color-10":
            interactive_grid[row][col] = 0

    # Update the figure with the modified interactive_grid
    fig = go.Figure(data=[go.Heatmap(z=interactive_grid, hoverinfo="text", colorscale=color_scale)])
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
