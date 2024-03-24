import json
import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from arc_evals.utils import paths

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])


def gradient_button(value, status, json_id, eval_folder):
    if status == "failure":
        return dbc.Button(
            "Inspect Task",
            id={"type": "task-button", "task": json_id, "eval": eval_folder},
            color="danger",
            size="sm",
        )
    percentage = value * 100
    gradient_style = {"background": f"linear-gradient(90deg, green {percentage}%, red {percentage}%)"}
    return dbc.Button(
        "Inspect Task",
        id={"type": "task-button", "task": json_id, "eval": eval_folder},
        style=gradient_style,
        size="sm",
    )


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
        result = load(eval_dir, json_file)
        status = result["status"]
        metrics = result.get("metrics", [])
        button_value = 0.0
        metric_rows = []
        for metric in metrics:
            metric_viz = dbc.Row(children=[])
            for key, value in metric.items():
                name = key.split("_")[-1]
                if name == "all":
                    button_value = value
                    continue
                class_name_background = f"symbol_{name}"
                if value <= 0.0:
                    class_name_shadow = "fail_eval"
                elif value <= 0.4:
                    class_name_shadow = "bad_eval"
                elif value <= 0.6:
                    class_name_shadow = "okay_eval"
                elif value < 1.0:
                    class_name_shadow = "good_eval"
                else:
                    class_name_shadow = "perfect_eval"
                class_name = f"{class_name_background} {class_name_shadow}"
                cols = [
                    dbc.Col(
                        dbc.Card(
                            style={
                                "height": "20px",
                                "width": "20px",
                            },
                            className=class_name,
                        ),
                        className="m-1",
                        width=1,
                    )
                ] * 6
                metric_viz.children += cols
            metric_rows.append(metric_viz)
        task_button = gradient_button(button_value, status, json_id, eval_folder)
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
