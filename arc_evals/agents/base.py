import abc
import json
import os
from operator import itemgetter
from pathlib import Path

import numpy as np


class Agent(abc.ABC):
    def __init__(self, data_path: Path | str, eval_path: Path | str, name: str, overwrite: bool = False):
        self.data_path = Path(data_path)
        self.name = name
        if overwrite:
            self.eval_path = Path(eval_path) / self.name
        else:
            i = 1
            while self.name in os.listdir(eval_path):
                i += 1
                self.name = f"{name}_{i}"
            self.eval_path = Path(eval_path) / self.name
        self.eval_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, json_filename: str) -> None:
        predictions = None
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
            output_metrics["metrics"] = [{k: np.average(v) for k, v in metric.items()} for metric in metrics]
            output_metrics["predictions"] = predictions
        except Exception as e:
            # log e I guess . . . maybe even in this file?
            output_metrics["status"] = "failure"
            output_metrics["traceback"] = str(e)
            # if the error happens during metric calculation, we still want access to prediction
            output_metrics["predictions"] = predictions
        with open(self.eval_path / json_filename, "w") as f:
            json.dump(output_metrics, f)

    @abc.abstractmethod
    def call(self, data: dict) -> list[list[list[int]]]: ...

    def evaluate(self, answer: list[list[int]], prediction: list[list[int]]) -> dict[str, float]:
        metrics = dict()
        answer_np, prediction_np = np.asarray(answer), np.asarray(prediction)
        metrics["cell_accuracy_all"] = np.average(answer_np == prediction_np)
        for i in range(10):
            idx = np.where(answer_np == i)
            indexed_answer = answer_np[idx]
            if indexed_answer.size > 0:
                metrics[f"cell_accuracy_{i}"] = np.average(answer_np[idx] == prediction_np[idx])
        return metrics
