import time

import dash
import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, Patch, State, callback, dcc, html


def create_claude_chat(json_id, eval_folder):
    return dbc.Card(
        dbc.CardBody(
            [
                dcc.Store(id={"type": "chat-history", "task": json_id, "eval": eval_folder}, data=[]),
                dcc.Store(id={"type": "trigger-llm", "task": json_id, "eval": eval_folder}, data=[0]),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Textarea(
                                id={"type": "user-input", "task": json_id, "eval": eval_folder},
                                placeholder="Ask Claude anything ...",
                                className="form-control",
                                debounce=True,
                            ),
                            width=9,
                        ),
                        dbc.Col(
                            dbc.Button(
                                children=[
                                    html.P(
                                        "Clear",
                                        id="clear-history-label",
                                    ),
                                    dbc.Spinner(
                                        id="llm-spinner",
                                        spinner_style={"display": "none"},
                                    ),
                                ],
                                id="clear-history",
                            ),
                            width=3,
                        ),
                    ]
                ),
                dbc.Row(
                    dbc.Col(
                        children=[],
                        id={"type": "shown-history", "task": json_id, "eval": eval_folder},
                        className="mt-4",
                        style={"max-height": "300px", "overflowY": "auto"},
                    )
                ),
            ]
        ),
        className="mb-4",
        style={"min-height": "200px"},
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
        Output({"type": "chat-history", "task": MATCH, "eval": MATCH}, "data", allow_duplicate=True),
        Output({"type": "shown-history", "task": MATCH, "eval": MATCH}, "children", allow_duplicate=True),
    ],
    Input({"type": "clear-history", "task": MATCH, "eval": MATCH}, "n_clicks"),
    prevent_initial_call=True,
)
def clear_history(_):
    return [], []


@callback(
    [
        Output({"type": "chat-history", "task": MATCH, "eval": MATCH}, "data", allow_duplicate=True),
        Output({"type": "shown-history", "task": MATCH, "eval": MATCH}, "children", allow_duplicate=True),
        Output({"type": "trigger-llm", "task": MATCH, "eval": MATCH}, "data"),
        Output({"type": "user-input", "task": MATCH, "eval": MATCH}, "value"),
    ],
    Input({"type": "user-input", "task": MATCH, "eval": MATCH}, "n_submit"),
    State({"type": "user-input", "task": MATCH, "eval": MATCH}, "value"),
    prevent_initial_call=True,
)
def add_to_chat_history(_, value):
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
        Output({"type": "shown-history", "task": MATCH, "eval": MATCH}, "children", allow_duplicate=True),
        Output({"type": "chat-history", "task": MATCH, "eval": MATCH}, "data", allow_duplicate=True),
    ],
    Input({"type": "trigger-llm", "task": MATCH, "eval": MATCH}, "data"),
    State({"type": "chat-history", "task": MATCH, "eval": MATCH}, "data"),
    prevent_initial_call=True,
    running=[
        (Output("clear-history", "disabled"), True, False),
        (
            Output("clear-history-label", "style"),
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
