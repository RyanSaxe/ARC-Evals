import json

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, callback_context, dcc

from arc_evals.utils import paths

COLOR_MAP = [
    "#000",
    "#0074D9",
    "#FF4136",
    "#2ECC40",
    "#FFDC00",
    "#AAAAAA",
    "#F012BE",
    "#FF851B",
    "#7FDBFF",
    "#870C25",
]


def hex_to_rgb(hex_str: str):
    if hex_str.startswith("#"):
        hex_str = hex_str[1:]
    if len(hex_str) == 3:
        hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2
    assert len(hex_str) == 6
    r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16)
    return [r, g, b]


def create_grid(grid_data: list[list[int]]):
    color_grid = []
    for row in grid_data:
        colored_row = [hex_to_rgb(COLOR_MAP[color]) for color in row]
        color_grid.append(colored_row)
    fig = go.Figure(go.Image(z=color_grid))
    height, width = len(color_grid), len(color_grid[0])
    # create vertical lines on grid
    for i in range(width):
        fig.add_shape(type="line", x0=i - 0.5, y0=-0.5, x1=i - 0.5, y1=height - 0.5, line=dict(color="white", width=1))
    # create horizontal lines on grid
    for i in range(height):
        fig.add_shape(type="line", x0=-0.5, y0=i + 0.5, x1=width - 0.5, y1=i + 0.5, line=dict(color="white", width=1))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False)
    )
    return fig


def create_grids_from_data(samples: list[dict[str, list[list[int]]]]):
    rows = []
    for sample in samples:
        in_fig = dcc.Graph(figure=create_grid(sample["input"]), config={"displayModeBar": False})
        out_fig = dcc.Graph(figure=create_grid(sample["output"]), config={"displayModeBar": False})
        rows.append(dbc.Row([dbc.Col(in_fig, md=6), dbc.Col(out_fig, md=6)]))
    return dbc.Container(
        rows,
        className="p-3 bg-light rounded-3",
    )


task_modal = dbc.Modal(
    [
        dbc.ModalHeader("HEADER HERE"),
        dbc.ModalBody(children=[], id="modal-task-body"),
        dbc.ModalFooter(
            [
                dbc.Button("Submit", id="submit-task-data", n_clicks=0, size="sm"),
            ]
        ),
    ],
    id="modal-task",
    is_open=False,
    size="xl",
)


@callback(
    [Output("modal-task", "is_open"), Output("modal-task-body", "children")],
    Input({"type": "task-link", "task": ALL, "eval": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def open_task(n_clicks):
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    triggered_id_dict = json.loads(triggered_id)
    json_id = triggered_id_dict["task"]
    eval_folder = triggered_id_dict["eval"]
    data = paths.load(paths.TRAINING, json_id)
    output = paths.load(paths.OUTPUT / eval_folder, json_id)
    left_plots = create_grids_from_data(data["train"])
    right_plots = create_grids_from_data(samples=data["test"])
    output = dbc.Row([dbc.Col(left_plots), dbc.Col(right_plots)])
    return True, output
