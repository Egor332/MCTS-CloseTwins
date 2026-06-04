from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from src.domain import GameStatus, Role
from src.engine.game import Game
from src.mcts.mcts import MCTS
from src.runner.match_config import MatchConfig
from src.runner.player_factory import build_mcts


@dataclass
class GameResult:
    match_name: str
    game_id: int
    seed: int
    alphabet_size: int
    max_word_length: int
    winner: str
    num_turns: int
    final_word: str
    duration_seconds: float
    pointer_name: str
    pointer_iterations: int
    pointer_selection: str
    pointer_simulation: str
    pointer_backpropagation: str
    pointer_exploration_constant: float
    pointer_progressive_bias: bool
    pointer_bias_weight: float
    inserter_name: str
    inserter_iterations: int
    inserter_selection: str
    inserter_simulation: str
    inserter_backpropagation: str
    inserter_exploration_constant: float
    inserter_progressive_bias: bool
    inserter_bias_weight: float


def play_game(
    engine: Game,
    ai_pointer: MCTS,
    ai_inserter: MCTS,
) -> tuple[GameStatus, int, str]:
    """Play a single game to completion. Returns (status, num_turns, final_word)."""
    engine.apply_index(0)
    num_turns = 1

    while engine.game_status == GameStatus.ONGOING:
        if engine.turn == Role.POINTER:
            move = ai_pointer.get_best_move(engine)
            engine.apply_index(move)
        else:
            move = ai_inserter.get_best_move(engine)
            engine.apply_letter(move)
        num_turns += 1

    return engine.game_status, num_turns, engine.get_current_word()


def run_match(config: MatchConfig) -> list[GameResult]:
    results: list[GameResult] = []
    alphabet = [chr(ord("a") + i) for i in range(config.alphabet_size)]

    for game_id in range(config.num_games):
        seed = config.base_seed + game_id
        rng_pointer = np.random.default_rng(seed)
        rng_inserter = np.random.default_rng(seed + config.num_games)

        ai_pointer = build_mcts(config.pointer, rng=rng_pointer)
        ai_inserter = build_mcts(config.inserter, rng=rng_inserter)

        engine = Game(alphabet, config.max_word_length)

        t0 = time.perf_counter()
        status, num_turns, final_word = play_game(engine, ai_pointer, ai_inserter)
        duration = time.perf_counter() - t0

        results.append(
            GameResult(
                match_name=config.name,
                game_id=game_id,
                seed=seed,
                alphabet_size=config.alphabet_size,
                max_word_length=config.max_word_length,
                winner=status.name,
                num_turns=num_turns,
                final_word=final_word,
                duration_seconds=round(duration, 4),
                pointer_name=config.pointer.name,
                pointer_iterations=config.pointer.iterations,
                pointer_selection=config.pointer.selection,
                pointer_simulation=config.pointer.simulation,
                pointer_backpropagation=config.pointer.backpropagation,
                pointer_exploration_constant=config.pointer.exploration_constant,
                pointer_progressive_bias=config.pointer.progressive_bias,
                pointer_bias_weight=config.pointer.bias_weight,
                inserter_name=config.inserter.name,
                inserter_iterations=config.inserter.iterations,
                inserter_selection=config.inserter.selection,
                inserter_simulation=config.inserter.simulation,
                inserter_backpropagation=config.inserter.backpropagation,
                inserter_exploration_constant=config.inserter.exploration_constant,
                inserter_progressive_bias=config.inserter.progressive_bias,
                inserter_bias_weight=config.inserter.bias_weight,
            )
        )

    return results
