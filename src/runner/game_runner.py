from __future__ import annotations

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
    pointer_name: str
    inserter_name: str
    alphabet_size: int
    max_word_length: int
    winner: str
    num_turns: int
    final_word: str
    pointer_iterations: int
    inserter_iterations: int


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
        status, num_turns, final_word = play_game(engine, ai_pointer, ai_inserter)

        results.append(
            GameResult(
                match_name=config.name,
                game_id=game_id,
                seed=seed,
                pointer_name=config.pointer.name,
                inserter_name=config.inserter.name,
                alphabet_size=config.alphabet_size,
                max_word_length=config.max_word_length,
                winner=status.name,
                num_turns=num_turns,
                final_word=final_word,
                pointer_iterations=config.pointer.iterations,
                inserter_iterations=config.inserter.iterations,
            )
        )

    return results
