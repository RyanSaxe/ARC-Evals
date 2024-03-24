import abc
import json
import os
from operator import itemgetter
from pathlib import Path

import numpy as np


class Agent(abc.ABC):
    def __init__(self, data_path: Path | str, eval_path: Path | str, name: str):
        self.data_path = Path(data_path)
        self.name = name
        i = 1
        while self.name in os.listdir(eval_path):
            i += 1
            self.name = f"{name}_{i}"
        self.eval_path = Path(eval_path) / self.name
        os.mkdir(self.eval_path)

    def __call__(self, json_filename: str) -> None:
        if not json_filename.endswith(".json"):
            json_filename = f"{json_filename}.json"
        output_metrics = {"status": "success"}
        try:
            with open(self.data_path / json_filename, "r") as f:
                data = json.load(f)
            predictions = self.call(data)
            metrics = [
                self.evaluate(answer["output"], prediction) for answer, prediction in zip(data["test"], predictions)
            ]
            metrics = {k: np.average(list(map(itemgetter(k), metrics))) for k in metrics[0].keys()}
        except Exception as e:
            # log e I guess . . . maybe even in this file?
            metrics = {"status": "failure", "traceback": str(e)}
        output_metrics |= metrics
        with open(self.eval_path / json_filename, "w") as f:
            json.dump(output_metrics, f)

    @abc.abstractmethod
    def call(self, data: dict) -> list[list[list[int]]]: ...

    def evaluate(self, answer: list[list[int]], prediction: list[list[int]]) -> dict[str, float]:
        answer, prediction = np.asarray(answer), np.asarray(prediction)
        return {"cell_accuracy": 1 - np.average(answer == prediction)}
