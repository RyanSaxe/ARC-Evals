import time

import dash
import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, Patch, State, callback, dcc, html


def create_claude_chat(json_id, eval_folder):
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Store(id="current-task", data=dict(json_id=json_id, eval_folder=eval_folder)),
                dcc.Store(id="chat-history", data=[]),
                dcc.Store(id="trigger-llm", data=[0]),
                dbc.Row(
                    dbc.Col(
                        dbc.InputGroup(
                            [
                                dbc.Textarea(
                                    id="user-input",
                                    placeholder="Ask Claude anything ...",
                                    # className="form-control",
                                    debounce=True,
                                ),
                                dbc.Button(
                                    children=[
                                        html.P(
                                            " Ask",
                                            id="button-history-label",
                                        ),
                                        dbc.Spinner(
                                            id="llm-spinner",
                                            spinner_style={"display": "none"},
                                        ),
                                    ],
                                    id="button-history",
                                ),
                            ],
                        ),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        children=[],
                        id="shown-history",
                        className="mt-4",
                        style={"max-height": "320px", "overflowY": "auto"},
                    )
                ),
            ]
        ),
        className="mb-4",
        style={"min-height": "232px"},
    )


def format_message(message, person=True):
    formatted_input = message.split("\n")
    alert = dbc.Alert(
        children=[html.Hr() if sentence.strip() == "" else html.P(sentence) for sentence in formatted_input],
        color="secondary" if person else "primary",
        className="user-message" if person else "bot-message",
    )
    return dbc.Row(dbc.Col(alert))


def query_claude(history):
    return "\n\n".join(history)


@callback(
    [
        Output("chat-history", "data", allow_duplicate=True),
        Output("shown-history", "children", allow_duplicate=True),
        Output("trigger-llm", "data"),
        Output("user-input", "value"),
    ],
    [Input("user-input", "n_submit"), Input("button-history", "n_clicks")],
    State("user-input", "value"),
    prevent_initial_call=True,
)
def add_to_chat_history(n_submits, n_clicks, value):
    history = Patch()
    history.append(value)
    chat = Patch()
    person_response = format_message(value)
    chat.append(person_response)
    trigger_llm = Patch()
    trigger_llm[0] += 1
    return history, chat, trigger_llm, ""


@callback(
    [
        Output("shown-history", "children", allow_duplicate=True),
        Output("chat-history", "data", allow_duplicate=True),
    ],
    Input("trigger-llm", "data"),
    State("chat-history", "data"),
    prevent_initial_call=True,
    running=[
        (Output("button-history", "disabled"), True, False),
        (
            Output("button-history-label", "style"),
            {"display": "none"},
            {"display": "block"},
        ),
        (
            Output("llm-spinner", "spinner_style"),
            {"display": "block"},
            {"display": "none"},
        ),
    ],
)
def update_chat_history(_, history):
    if history is None or len(history) == 0:
        return [], []

    response = query_claude(history)
    history = Patch()
    history.append(response)
    format_response = format_message(response, person=False)
    chat = Patch()
    chat.append(format_response)
    time.sleep(2)
    return chat, history
