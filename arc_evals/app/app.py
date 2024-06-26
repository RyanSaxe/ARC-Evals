import json
import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

from arc_evals.utils import paths

THEME = "ZEPHYR"
with open(Path(__file__).parent / "assets/theme_colors.json", "r") as f:
    THEME_COLORS = json.load(f)[THEME]
app = dash.Dash(__name__, external_stylesheets=[getattr(dbc.themes, THEME), dbc.icons.FONT_AWESOME])


n_cols = 6


def build_json_cards(eval_folder):
    eval_dir = paths.OUTPUT / eval_folder
    json_files = [f for f in os.listdir(eval_dir) if f.endswith(".json")]
    json_cards = []

    for i, json_file in enumerate(json_files):
        json_id = json_file.split(".")[0]
        if i % n_cols == 0:
            json_cards.append(dbc.Row(children=[]))
        result = paths.load(eval_dir, json_file)
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
                if status == "failure":
                    class_name_border = "fail"
                if value <= 0.0:
                    class_name_border = "fail"
                elif value <= 0.4:
                    class_name_border = "bad"
                elif value <= 0.6:
                    class_name_border = "okay"
                elif value < 1.0:
                    class_name_border = "good"
                else:
                    class_name_border = "perf"
                class_name = f"eval {class_name_background} {class_name_border}"
                cols = [
                    dbc.Col(
                        dbc.Card(
                            className=class_name,
                        ),
                        className="me-2 my-2",
                        width=1,
                    )
                ]
                metric_viz.children += cols
            metric_rows.append(metric_viz)
        task_link = dbc.CardLink(
            json_id,
            # href=f"#{eval_folder}-{json_id}",
            id={"type": "task-link", "task": json_id, "eval": eval_folder},
            className="task-card-link",
        )

        header = dbc.CardHeader([task_link])
        if status == "failure":
            warning_icon = dash.html.I(className="fas fa-exclamation-triangle text-warning float-end mt-1")
            header.children.append(warning_icon)
        footer = dbc.CardFooter(
            style={
                "background": f"linear-gradient(90deg, {THEME_COLORS['success']} {button_value * 100}%, {THEME_COLORS['danger']} {button_value * 100}%)"
            },
        )

        col = dbc.Col(
            dbc.Card(
                [
                    header,
                    dbc.CardBody(metric_viz, className="metric-body"),
                    footer,
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
    if eval_folder[0] == ".":
        continue
    json_cards = build_json_cards(eval_folder)
    eval_tab = dbc.Tab(
        json_cards,
        label=eval_folder,
    )
    tabs.append(eval_tab)

from arc_evals.app.task import task_modal

app.layout = dbc.Container(
    [
        task_modal,
        dbc.Tabs(
            tabs,
            id="eval-tabs",
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)
