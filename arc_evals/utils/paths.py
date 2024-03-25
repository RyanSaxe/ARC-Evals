import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

OUTPUT = ROOT / "evals"
DATA = ROOT / "data"
TRAINING = DATA / "training"
# TODO: set up a warning when importing TESTING path because looking at the evaluation set
#       creates leakage in terms of fair evaluations on ARC. Differentiation from training and
#       evaluation should come from keeping subsets of TRAINING out of sample
TESTING = DATA / "evaluation"


def load(data_dir: Path, sample_f: str):
    if not sample_f.endswith(".json"):
        sample_f = f"{sample_f}.json"
    with open(data_dir / sample_f, "r") as f:
        data = json.load(f)
    return data
