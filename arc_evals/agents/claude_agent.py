import json
import os
import sys

import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv

from arc_evals.agents.base import Agent, run_agent
from arc_evals.utils.paths import OUTPUT, TRAINING

load_dotenv()


def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def create_task_prompts(task, separate_output_prompts=True, include_answers=False, predictions=None):
    task_prompts = []
    train_prompt = ""
    for i, example in enumerate(task["train"]):
        input_text = f"<input {i + 1}>: {example['input']}\n"
        output_text = f"<output {i + 1}>: {example['output']}\n"
        train_prompt += input_text + output_text + "\n"

    for j, output in enumerate(task["test"]):
        full_prompt = train_prompt
        full_prompt += f"<input {j + i + 1}>: {output['input']}"

        if predictions is not None and predictions[j] is not None:
            full_prompt += f"\n<prediction {j + i + 1}>: {predictions[j]}"

        full_prompt += f"\n<output {j + i + 1}>: {output['output'] if include_answers else ''}"
        if separate_output_prompts:
            task_prompts.append(full_prompt)
        else:
            train_prompt = full_prompt
    if not separate_output_prompts:
        return train_prompt
    return task_prompts


# TODO: have an LLMAgent generic class that has the chat interface


class ClaudeAgent(Agent):
    """An Agent that is allowed to cheat, so all metrics should be perfect"""

    def __init__(
        self,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        model: str = "claude-3-opus-20240229",
    ):
        self.system_prompt = "\n\n".join(
            [self.system_description, self.system_goal, self.system_context, self.system_format]
        )
        self.client = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model

    @property
    def system_description(self):
        return "You are an expert in visual-spacial problem solving with an IQ of 300."

    @property
    def system_goal(self):
        return (
            "Your goal is to be able to solve problems by example. "
            "I will give you examples of <input> <output> pairs where both <input> and <output> are 2D grids "
            "(NOTE: <input> and <output> can be grids of different sizes, so keep that in mind). "
            "Then, I will give you just an <input>, and it is your goal to take the context of the prior "
            "<input> <output> pairs and respond with the correct <output> to the given <input>."
        )

    @property
    def system_context(self):
        return """All grids will contain only numbers 0-9 such that each number has a corresponding color:

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

    @property
    def system_format(self):
        return (
            "Remember to take your time, think critically, "
            "and respond with just the correct 2D grid and no explanation. "
            "Please solve the following problem:\n\n"
        )

    def convert_message_to_grid(self, message):
        grid = json.loads(message.content[0].text)
        if not isinstance(grid, list):
            raise ValueError("Claude did not send a valid output. Could not convert to list.")
        return grid

    def chat(self, data, history: list[str], predictions=None, temperature=None, max_tokens=None, model=None):
        task_prompt = create_task_prompts(
            data, separate_output_prompts=False, include_answers=True, predictions=predictions
        )
        system_prompt = self.system_description
        chat_goal = (
            "Your goal is to help an AI expert explore a problem space in which 2D grids are transformed to other 2D grids. "
            + self.system_context
        )
        system_prompt += (
            chat_goal
            + "\n\nRemember to think critically. Here is the data that describes this problem: \n\n"
            + task_prompt
        )
        message = self.client.messages.create(
            model=self.model if model is None else model,
            max_tokens=self.max_tokens if max_tokens is None else max_tokens,
            temperature=self.temperature if temperature is None else temperature,
            system=system_prompt,
            messages=[
                {"role": "user" if i % 2 == 0 else "assistant", "content": chat} for i, chat in enumerate(history)
            ],
        )
        return message.content[0].text

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
                model=self.model,
                max_tokens=min(self.max_tokens, upper_bound_tokens),
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[{"role": "user", "content": task_prompt}],
            )
            output = self.convert_message_to_grid(message)
            outputs.append(output)

        return outputs


if __name__ == "__main__":
    args = sys.argv
    args = sys.argv[1:]
    stop_after = int(args[0]) if len(args) > 0 else None
    agent = ClaudeAgent()
    run_agent(agent, "claude_fix", OUTPUT, TRAINING, limit=stop_after)
