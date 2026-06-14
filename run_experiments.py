"""Run comparison experiments: modified MCTS strategies vs classic UCT.

Each comparison is run in both role assignments (modified as Pointer,
then modified as Inserter), giving 6 experiments total.

Generates heatmap plots of Pointer win % across (max_word_length, alphabet_size).

Supports stop/resume: progress is checkpointed to a JSON file after every
grid cell.  Re-run the same command to pick up where you left off.
Use --reset to discard the checkpoint and start fresh.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from itertools import product

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from src.domain import GameStatus
from src.engine.game import Game
from src.runner.player_config import PlayerConfig
from src.runner.player_factory import build_mcts
from src.runner.game_runner import play_game

OUTPUT_DIR = Path("experiment_comp")
CHECKPOINT_PATH = OUTPUT_DIR / "_checkpoint.json"
NUM_GAMES = 20
ITERATIONS = 1000
BASE_SEED = 42

MAX_WORD_LENGTHS = [5, 10, 15, 20, 25, 30, 35, 40]
ALPHABET_SIZES = [3, 4, 5, 6, 7, 8, 9, 10]

CLASSIC = PlayerConfig(
    name="Classic-UCT",
    iterations=ITERATIONS,
    selection="uct",
    simulation="random",
    backpropagation="standard",
)

MODIFIED_STRATEGIES: list[tuple[str, PlayerConfig]] = [
    (
        "UCB1-Tuned",
        PlayerConfig(
            name="UCB1-Tuned",
            iterations=ITERATIONS,
            selection="ucb1_tuned",
            simulation="random",
            backpropagation="standard",
        ),
    ),
    (
        "MCTS-Solver",
        PlayerConfig(
            name="MCTS-Solver",
            iterations=ITERATIONS,
            selection="uct",
            simulation="random",
            backpropagation="solver",
        ),
    ),
    (
        "Heuristic-Sim",
        PlayerConfig(
            name="Heuristic-Sim",
            iterations=ITERATIONS,
            selection="uct",
            simulation="heuristic",
            backpropagation="standard",
        ),
    ),
]

EXPERIMENTS: list[tuple[str, PlayerConfig, PlayerConfig]] = [
    ("Classic (Pointer) vs Classic (Inserter)", CLASSIC, CLASSIC),
]
for label, modified in MODIFIED_STRATEGIES:
    EXPERIMENTS.append((f"{label} (Pointer) vs Classic (Inserter)", modified, CLASSIC))
    EXPERIMENTS.append((f"Classic (Pointer) vs {label} (Inserter)", CLASSIC, modified))


def _safe_name(exp_name: str) -> str:
    return exp_name.lower().replace(" ", "_").replace("(", "").replace(")", "")


# -- Checkpoint helpers -------------------------------------------------------

def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, "r") as f:
            return json.load(f)
    return {}


def save_checkpoint(ckpt: dict) -> None:
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(ckpt, f)


def _cell_key(exp_name: str, mwl: int, alph: int) -> str:
    return f"{exp_name}|{mwl}|{alph}"


# -- Core logic ---------------------------------------------------------------

def run_comparison(
    pointer_cfg: PlayerConfig,
    inserter_cfg: PlayerConfig,
    alphabet_size: int,
    max_word_length: int,
    num_games: int,
    base_seed: int,
) -> float:
    """Return Pointer win fraction over *num_games* games."""
    alphabet = [chr(ord("a") + i) for i in range(alphabet_size)]
    pointer_wins = 0

    for gid in range(num_games):
        seed = base_seed + gid
        ai_pointer = build_mcts(pointer_cfg, rng=np.random.default_rng(seed))
        ai_inserter = build_mcts(inserter_cfg, rng=np.random.default_rng(seed + num_games))
        engine = Game(alphabet, max_word_length)

        status, _, _ = play_game(engine, ai_pointer, ai_inserter)
        if status == GameStatus.P1_WINS_TWINS:
            pointer_wins += 1

    return pointer_wins / num_games


def make_heatmap(
    data: np.ndarray,
    title: str,
    filename: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        data,
        annot=True,
        fmt=".0f",
        cmap="RdYlGn",
        vmin=0,
        vmax=100,
        xticklabels=ALPHABET_SIZES,
        yticklabels=MAX_WORD_LENGTHS,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_xlabel("Alphabet Size")
    ax.set_ylabel("Max Word Length")
    ax.set_title(title)

    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset", action="store_true",
        help="Discard the checkpoint and start all experiments from scratch.",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help=(
            "Run only experiments whose name contains this substring "
            "(case-insensitive). Example: --only baseline"
        ),
    )
    args = parser.parse_args()

    experiments = EXPERIMENTS
    if args.only:
        needle = args.only.lower()
        experiments = [e for e in EXPERIMENTS if needle in e[0].lower()]
        if not experiments:
            available = "\n  ".join(name for name, _, _ in EXPERIMENTS)
            raise SystemExit(
                f"No experiment matches --only '{args.only}'. Available:\n  {available}"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.reset and CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("Checkpoint cleared.\n")

    ckpt = load_checkpoint()

    total_configs = len(MAX_WORD_LENGTHS) * len(ALPHABET_SIZES)
    total_games = len(experiments) * total_configs * NUM_GAMES
    print(f"Total: {len(experiments)} experiments × {total_configs} configs × "
          f"{NUM_GAMES} games = {total_games} games")
    if ckpt:
        print(f"Resuming from checkpoint ({len(ckpt)} cells already done)\n")

    for exp_name, pointer_cfg, inserter_cfg in experiments:
        combos = list(product(enumerate(MAX_WORD_LENGTHS), enumerate(ALPHABET_SIZES)))

        already_done = sum(
            1 for (_, mwl), (_, alph) in combos
            if _cell_key(exp_name, mwl, alph) in ckpt
        )

        if already_done == len(combos):
            print(f"\n[SKIP] {exp_name} — fully cached")
            grid = np.zeros((len(MAX_WORD_LENGTHS), len(ALPHABET_SIZES)))
            for (r, mwl), (c, alph) in combos:
                grid[r, c] = ckpt[_cell_key(exp_name, mwl, alph)]
            make_heatmap(
                grid,
                title=f"{exp_name}\nPointer Win % ({NUM_GAMES} games, {ITERATIONS} iter, seed={BASE_SEED})",
                filename=f"{_safe_name(exp_name)}.png",
            )
            continue

        print(f"\n{'='*60}")
        print(f"Experiment: {exp_name}")
        print(f"  Pointer  = {pointer_cfg.name} (iter={pointer_cfg.iterations})")
        print(f"  Inserter = {inserter_cfg.name} (iter={inserter_cfg.iterations})")
        remaining = len(combos) - already_done
        print(f"  {remaining}/{len(combos)} configs remaining ({NUM_GAMES} games each)")
        print(f"{'='*60}")

        grid = np.zeros((len(MAX_WORD_LENGTHS), len(ALPHABET_SIZES)))
        t0 = time.perf_counter()

        for (r, mwl), (c, alph) in tqdm(combos, desc=exp_name):
            key = _cell_key(exp_name, mwl, alph)

            if key in ckpt:
                grid[r, c] = ckpt[key]
                continue

            win_pct = run_comparison(
                pointer_cfg=pointer_cfg,
                inserter_cfg=inserter_cfg,
                alphabet_size=alph,
                max_word_length=mwl,
                num_games=NUM_GAMES,
                base_seed=BASE_SEED,
            )
            grid[r, c] = win_pct * 100

            ckpt[key] = grid[r, c]
            save_checkpoint(ckpt)

        elapsed = time.perf_counter() - t0
        print(f"  Finished in {elapsed:.1f}s")

        make_heatmap(
            grid,
            title=f"{exp_name}\nPointer Win % ({NUM_GAMES} games, {ITERATIONS} iter, seed={BASE_SEED})",
            filename=f"{_safe_name(exp_name)}.png",
        )


if __name__ == "__main__":
    main()
