import abc
import json
import os
from operator import itemgetter
from pathlib import Path

import numpy as np


def create_eval_dir(eval_path: Path | str, name: str, overwrite: bool = False) -> Path:
    name = name
    if overwrite:
        eval_path = Path(eval_path) / name
    else:
        i = 1
        while name in os.listdir(eval_path):
            i += 1
            name = f"{name}_{i}"
        eval_path = Path(eval_path) / name
    eval_path.mkdir(parents=True, exist_ok=True)
    return eval_path


def run_agent(agent, name, eval_path, data_path, overwrite=False, limit=None):
    eval_path = create_eval_dir(eval_path, name, overwrite=overwrite)
    json_files = [f for f in os.listdir(data_path) if f.endswith(".json")]
    for i, json_filename in enumerate(json_files):
        with open(data_path / json_filename, "r") as f:
            data = json.load(f)
        metrics = agent(data)
        with open(eval_path / json_filename, "w") as f:
            json.dump(metrics, f)
        if limit is not None and (limit - 1) <= i:
            break


# TODO: separate out responsibility in this call with respect to metrics to support compositionality


class Agent(abc.ABC):

    def __call__(self, data: dict) -> dict:
        predictions = None
        output_metrics = {"status": "success"}
        try:
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
        return output_metrics

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
