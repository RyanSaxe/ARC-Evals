import json
import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from arc_evals.utils import paths

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])


def load(data_dir: Path, sample_f: str):
    if not sample_f.endswith(".json"):
        sample_f = f"{sample_f}.json"
    with open(data_dir / sample_f, "r") as f:
        data = json.load(f)
    return data


n_cols = 6


def build_json_cards(eval_folder):
    eval_dir = paths.OUTPUT / eval_folder
    json_files = os.listdir(eval_dir)
    json_cards = []

    for i, json_file in enumerate(json_files):
        json_id = json_file.split(".")[0]
        if i % n_cols == 0:
            json_cards.append(dbc.Row(children=[]))
        metrics = load(eval_dir, json_file)
        metric_viz = dbc.Row(children=[])
        for metric, value in metrics.items():
            if metric in ["status", "traceback"]:
                continue
            cols = [
                dbc.Col(
                    dbc.Card(
                        style={
                            "background-color": "blue",
                            "height": "20px",
                            "width": "20px",
                        }
                    ),
                    className="m-1",
                    width=1,
                )
            ] * 6
            metric_viz.children += cols
        task_button = dbc.Button(
            "Inspect Task",
            id={"type": "task-button", "task": json_id, "eval": eval_folder},
            color="success",
            size="sm",
        )
        header = dbc.CardHeader(task_button)

        col = dbc.Col(
            dbc.Card(
                [
                    header,
                    dbc.CardBody(
                        metric_viz,
                        # style={"background-color": "rgba(0,255,0,0.2)"},
                    ),
                ],
                className="my-2",
            ),
            width=12 // n_cols,
        )
        json_cards[-1].children.append(col)

    return json_cards


all_evals = os.listdir(paths.OUTPUT)
tabs = []
for eval_folder in all_evals:
    json_cards = build_json_cards(eval_folder)
    eval_tab = dbc.Tab(json_cards, label=eval_folder)
    tabs.append(eval_tab)

app.layout = dbc.Container(dbc.Tabs(tabs))

if __name__ == "__main__":
    app.run_server(debug=True)
