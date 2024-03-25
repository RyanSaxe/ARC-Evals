import json
import time

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, callback_context, dcc

from arc_evals.app.llm_chat import create_claude_chat
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
        hovermode=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False),
    )
    return dcc.Graph(
        figure=fig,
        config={
            "displayModeBar": False,
            "staticPlot": True,  # Disable zooming and other interactions
            "doubleClick": "reset",  # Disable double-click to zoom
            "showTips": False,  # Disable tooltips
        },
        className="task-graph",
    )


def create_grid_card(figs):
    col_w = 12 // len(figs)
    return dbc.Card(
        dbc.CardBody(
            dbc.Row(
                [dbc.Col(fig, md=col_w) for fig in figs],
            )
        ),
        className="mb-4",
    )


def create_training_grids(samples: list[dict[str, list[list[int]]]], n: int = 3):
    col_w = 12 // n
    rows = []
    cards = []
    for i, sample in enumerate(samples):
        in_fig = create_grid(sample["input"])
        out_fig = create_grid(sample["output"])
        figs = [in_fig, out_fig]
        cards.append(create_grid_card(figs))
        if len(cards) % n == 0 or i == len(samples) - 1:
            row = dbc.Row([dbc.Col(card, md=col_w) for card in cards])
            rows.append(row)
            cards = []
    return dbc.Container(rows, style={"padding-left": "0px", "padding-right": "0px"})


def create_evaluation_grids(
    samples: list[dict[str, list[list[int]]]],
    json_id: str,
    eval_folder: str,
    predictions: list[list[list[int]]] | None = None,
):
    rows = []
    for i, sample in enumerate(samples):
        in_fig = create_grid(sample["input"])
        out_fig = create_grid(sample["output"])
        if predictions is not None:
            pred_fig = create_grid(predictions[i])
            figs = [in_fig, pred_fig, out_fig]
        else:
            figs = [in_fig, out_fig]
        card = create_grid_card(figs)
        row = dbc.Row(dbc.Col(card, md=12))
        rows.append(row)
    grid_container = dbc.Container(rows, style={"padding-left": "0px", "padding-right": "0px"})
    chat_card = create_claude_chat(json_id, eval_folder)
    chat_container = dbc.Container(
        dbc.Row(dbc.Col(chat_card, md=12)), style={"padding-left": "0px", "padding-right": "0px"}
    )
    return dbc.Container(
        dbc.Row(children=[dbc.Col(grid_container, md=6), dbc.Col(chat_container, md=6)]),
        style={"padding-left": "0px", "padding-right": "0px"},
    )


task_modal = dbc.Modal(
    [
        dbc.ModalBody(children=[create_claude_chat("", "")], id="modal-task-body"),
    ],
    id="modal-task",
    is_open=False,
    size="xl",
)


@callback(
    Output("modal-task-body", "children"),
    Input({"type": "task-link", "task": ALL, "eval": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def create_task_figs(_):
    triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    triggered_id_dict = json.loads(triggered_id)
    json_id = triggered_id_dict["task"]
    eval_folder = triggered_id_dict["eval"]
    data = paths.load(paths.TRAINING, json_id)
    output = paths.load(paths.OUTPUT / eval_folder, json_id)
    left_plots = create_training_grids(data["train"])
    right_plots = create_evaluation_grids(
        samples=data["test"], predictions=output["predictions"], json_id=json_id, eval_folder=eval_folder
    )
    output = dbc.Tabs(
        [dbc.Tab(left_plots, label="Train Examples"), dbc.Tab(right_plots, label="Evaluation")],
        style={"padding-left": "10px;"},
    )
    return dbc.Container(output)


@callback(
    Output("modal-task", "is_open"),
    Input("modal-task-body", "children"),
    prevent_initial_call=True,
)
def open_task_figs(_):
    return True
