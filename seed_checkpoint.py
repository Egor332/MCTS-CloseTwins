"""One-time script to seed _checkpoint.json from already-completed experiment plots."""
import json
from pathlib import Path

OUTPUT_DIR = Path("experiment_comp")
CHECKPOINT_PATH = OUTPUT_DIR / "_checkpoint.json"

MAX_WORD_LENGTHS = [5, 10, 15, 20, 25, 30, 35, 40]
ALPHABET_SIZES = [3, 4, 5, 6, 7, 8, 9, 10]

COMPLETED = {
    "UCB1-Tuned (Pointer) vs Classic (Inserter)": [
        [100,   0,   0,   0,   0,   0,   0,   0],
        [100,  90,   0,   0,   0,   0,   0,   0],
        [100, 100,  15,   0,   0,   0,   0,   0],
        [100, 100,  90,  45,   0,   0,   0,   0],
        [100, 100, 100,  95,  50,  10,   5,   0],
        [100, 100, 100, 100,  85,  75,  25,   5],
        [100, 100, 100, 100,  95,  90,  85,  25],
        [100, 100, 100, 100, 100,  95,  85,  90],
    ],
    "Classic (Pointer) vs UCB1-Tuned (Inserter)": [
        [100,   0,   0,   0,   0,   0,   0,   0],
        [100,  90,   0,   0,   0,   0,   0,   0],
        [100, 100,  25,   0,   0,   0,   0,   0],
        [100, 100,  85,  45,  10,   0,   0,   0],
        [100, 100, 100,  85,  50,  20,   0,   0],
        [100, 100, 100, 100,  95,  65,  25,   5],
        [100, 100, 100, 100, 100,  85,  70,  60],
        [100, 100, 100, 100, 100,  95,  90,  80],
    ],
    "MCTS-Solver (Pointer) vs Classic (Inserter)": [
        [ 60,   0,   0,   0,   0,   0,   0,   0],
        [100,  55,   0,   0,   0,   0,   0,   0],
        [100,  95,  20,   0,   0,   0,   0,   0],
        [100, 100,  90,  40,   0,   0,   0,   0],
        [100, 100, 100, 100,  45,  10,   5,   0],
        [100, 100, 100, 100,  90,  75,  30,   0],
        [100, 100, 100, 100,  95,  85,  70,  35],
        [100, 100, 100, 100, 100,  95,  95,  85],
    ],
    "Classic (Pointer) vs MCTS-Solver (Inserter)": [
        [100,  40,  35,  30,  40,   5,  25,  25],
        [100, 100,  65,  35,  30,  20,  30,  15],
        [100, 100,  90,  40,  30,  15,  20,  25],
        [100, 100, 100,  80,  40,  35,   5,  15],
        [100, 100, 100, 100,  70,  40,  30,  20],
        [100, 100, 100, 100,  95,  85,  40,  35],
        [100, 100, 100, 100, 100,  85,  80,  55],
        [100, 100, 100, 100, 100, 100, 100,  95],
    ],
    "Heuristic-Sim (Pointer) vs Classic (Inserter)": [
        [100,   0,   0,   0,   0,   0,   0,   0],
        [100, 100,   0,   0,   0,   0,   0,   0],
        [100, 100,  35,   0,   0,   0,   0,   0],
        [100, 100,  95,  35,   0,   0,   0,   0],
        [100, 100, 100, 100,  85,  20,   5,   0],
        [100, 100, 100, 100,  95,  75,  30,   5],
        [100, 100, 100, 100, 100, 100,  75,  35],
        [100, 100, 100, 100, 100, 100, 100,  85],
    ],
}

ckpt: dict[str, float] = {}
for exp_name, grid in COMPLETED.items():
    for r, mwl in enumerate(MAX_WORD_LENGTHS):
        for c, alph in enumerate(ALPHABET_SIZES):
            key = f"{exp_name}|{mwl}|{alph}"
            ckpt[key] = float(grid[r][c])

CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(CHECKPOINT_PATH, "w") as f:
    json.dump(ckpt, f)

print(f"Wrote {len(ckpt)} entries to {CHECKPOINT_PATH}")
