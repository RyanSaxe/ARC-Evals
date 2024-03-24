import json
import os
import sys
from pathlib import Path
from typing import LiteralString

import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv

from arc_evals.agents.base import Agent

load_dotenv()


def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def create_task_prompts(task):
    task_prompts = []
    train_prompt = ""
    for example in task["train"]:
        input_text = f"<input>: {example['input']}\n"
        output_text = f"<output>: {example['output']}\n"
        train_prompt += input_text + output_text + "\n"

    for output in task["test"]:
        full_prompt = train_prompt + f"<input>: {task['test'][0]['input']}\n<output>: "
        task_prompts.append(full_prompt)
    return task_prompts


class ClaudeAgent(Agent):
    """An Agent that is allowed to cheat, so all metrics should be perfect"""

    def __init__(self, data_path: Path | str, eval_path: Path | str, name: str, overwrite: bool = False):
        super().__init__(data_path, eval_path, name, overwrite)
        self.system_prompt = self.create_system_prompt()
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def create_system_prompt(self) -> LiteralString:
        system_desc = "You are an expert in visual-spacial problem solving with an IQ of 300."
        system_def = """Your goal is to be able to solve problems by example. 
        I will give you examples of <input> <output> pairs where both <input> and <output> are 2D grids 
        (NOTE: <input> and <output> can be grids of different sizes, so keep that in mind). 
        Then, I will give you just an <input>, and it is your goal to take the context of the prior 
        <input> <output> pairs and respond with the correct <output> to the given <input>.""".replace(
            "\n", ""
        )
        system_context = """All grids will contain only numbers 0-9 such that each number has a corresponding color:

        0: black
        1: blue
        2: red
        3: green
        4: yellow
        5: grey
        6: fuschia
        7: orange
        8: teal
        9: brown"""
        system_format = (
            """Remember to take your time, think critically, 
        and respond with just the correct 2D grid and no explanation. 
        Please solve the following problem:""".replace(
                "\n", ""
            )
            + "\n\n"
        )

        return "\n\n".join([system_desc, system_def, system_context, system_format])

    def convert_message_to_grid(self, message):
        grid = json.loads(message.content[0].text)
        if not isinstance(grid, list):
            raise ValueError("Claude did not send a valid output. Could not convert to list.")
        return grid

    def call(self, data):
        task_prompts = create_task_prompts(data)
        outputs = []
        # NOTE: maybe there is a more efficient way of doing this without querying multiple times
        #       with the same system prompt. However, having multiple outputs increases difficulty
        #       by quite a bit in terms of response formatting and proper performance
        # NOTE: confirmed that with current prompt structure, n tokens of correct output is always less than
        #       the n tokens of input for all training and evaluation json files. Need to integrate as a unit test
        #       in case my prompt structure changes.
        for task_prompt in task_prompts:
            upper_bound_tokens = count_tokens(task_prompt)
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=min(4096, upper_bound_tokens),  # 4096 is upper bound of this param
                temperature=0,
                system=self.system_prompt,
                messages=[{"role": "user", "content": task_prompt}],
            )
            output = self.convert_message_to_grid(message)
            outputs.append(output)

        return outputs


EVAL_PATH = Path(__file__).parent.parent.parent / "evals"
DATA_PATH = Path(__file__).parent.parent.parent / "data/training"

if __name__ == "__main__":
    args = sys.argv
    args = sys.argv[1:]
    stop_after = int(args[0]) if len(args) > 0 else None
    agent = ClaudeAgent(DATA_PATH, EVAL_PATH, "claude", overwrite=True)
    for i, json_filename in enumerate(os.listdir(DATA_PATH)):
        agent(json_filename)
        if stop_after == i + 1:
            break
