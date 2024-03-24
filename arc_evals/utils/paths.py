from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

OUTPUT = ROOT / "evals"
DATA = ROOT / "data"
TRAINING = DATA / "training"
# TODO: set up a warning when importing TESTING path because looking at the evaluation set
#       creates leakage in terms of fair evaluations on ARC. Differentiation from training and
#       evaluation should come from keeping subsets of TRAINING out of sample
TESTING = DATA / "evaluation"
