"""CLI entry point for running headless AI-vs-AI matches.

Usage:
    python -m src.run_match --config experiments/example.yaml --output results/
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from tqdm import tqdm

from src.runner.match_config import load_match_configs
from src.runner.game_runner import run_match, GameResult
from src.runner.result_writer import write_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run headless AI-vs-AI Close Twins matches from a YAML config."
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to a YAML file defining matches.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Directory where result CSVs will be saved (default: results/).",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    output_root = Path(args.output)

    matches = load_match_configs(config_path)
    print(f"Loaded {len(matches)} match config(s) from {config_path}")

    for match_cfg in matches:
        match_dir = output_root / match_cfg.name
        match_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(config_path, match_dir / "config.yaml")

        print(f"\n{'='*60}")
        print(f"Match: {match_cfg.name}")
        print(f"  Pointer:  {match_cfg.pointer.name} ({match_cfg.pointer.selection}, "
              f"{match_cfg.pointer.simulation}, {match_cfg.pointer.backpropagation}, "
              f"iter={match_cfg.pointer.iterations})")
        print(f"  Inserter: {match_cfg.inserter.name} ({match_cfg.inserter.selection}, "
              f"{match_cfg.inserter.simulation}, {match_cfg.inserter.backpropagation}, "
              f"iter={match_cfg.inserter.iterations})")
        print(f"  Alphabet: {match_cfg.alphabet_size}, Max length: {match_cfg.max_word_length}")
        print(f"  Games: {match_cfg.num_games}, Base seed: {match_cfg.base_seed}")
        print(f"{'='*60}")

        results: list[GameResult] = []
        alphabet = [chr(ord("a") + i) for i in range(match_cfg.alphabet_size)]

        import numpy as np
        from src.engine.game import Game
        from src.runner.player_factory import build_mcts
        from src.runner.game_runner import play_game

        for game_id in tqdm(range(match_cfg.num_games), desc="Games"):
            seed = match_cfg.base_seed + game_id
            rng_pointer = np.random.default_rng(seed)
            rng_inserter = np.random.default_rng(seed + match_cfg.num_games)

            ai_pointer = build_mcts(match_cfg.pointer, rng=rng_pointer)
            ai_inserter = build_mcts(match_cfg.inserter, rng=rng_inserter)

            engine = Game(alphabet, match_cfg.max_word_length)
            status, num_turns, final_word = play_game(engine, ai_pointer, ai_inserter)

            results.append(
                GameResult(
                    match_name=match_cfg.name,
                    game_id=game_id,
                    seed=seed,
                    pointer_name=match_cfg.pointer.name,
                    inserter_name=match_cfg.inserter.name,
                    alphabet_size=match_cfg.alphabet_size,
                    max_word_length=match_cfg.max_word_length,
                    winner=status.name,
                    num_turns=num_turns,
                    final_word=final_word,
                    pointer_iterations=match_cfg.pointer.iterations,
                    inserter_iterations=match_cfg.inserter.iterations,
                )
            )

        csv_path = match_dir / "results.csv"
        write_results(results, csv_path)

        p1_wins = sum(1 for r in results if r.winner == "P1_WINS_TWINS")
        p2_wins = len(results) - p1_wins
        print(f"\nResults saved to {csv_path}")
        print(f"  Pointer wins: {p1_wins}/{len(results)} ({100*p1_wins/len(results):.1f}%)")
        print(f"  Inserter wins: {p2_wins}/{len(results)} ({100*p2_wins/len(results):.1f}%)")


if __name__ == "__main__":
    main()
