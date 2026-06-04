from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from src.domain import GameStatus, Role
from src.engine.game import Game
from src.engine.twin_checker import TwinChecker


class SimulationStrategy(ABC):
    @abstractmethod
    def simulate(self, game: Game, rng: np.random.Generator) -> GameStatus: ...


class RandomSimulation(SimulationStrategy):
    def simulate(self, game: Game, rng: np.random.Generator) -> GameStatus:
        current = game.clone()

        while current.game_status == GameStatus.ONGOING:
            legal_moves = sorted(current.get_legal_moves())
            if not legal_moves:
                break

            move = legal_moves[rng.integers(0, len(legal_moves))]

            if current.turn == Role.POINTER:
                current.apply_index(move)
            else:
                current.apply_letter(move)

        return current.game_status


class HeuristicSimulation(SimulationStrategy):
    """Simulation with domain-knowledge filters from the conspectus:
    - Inserter: reject letters that immediately create twins.
    - Pointer: if a position forces a twin regardless of letter, pick it.
    """

    def simulate(self, game: Game, rng: np.random.Generator) -> GameStatus:
        current = game.clone()

        while current.game_status == GameStatus.ONGOING:
            if current.turn == Role.POINTER:
                self._pointer_move(current, rng)
            else:
                self._inserter_move(current, rng)

        return current.game_status

    @staticmethod
    def _pointer_move(game: Game, rng: np.random.Generator) -> None:
        positions = game.get_legal_moves()
        alphabet = game.get_alphabet()

        for pos in positions:
            if HeuristicSimulation._is_forced_win(game, pos, alphabet):
                game.apply_index(pos)
                return

        game.apply_index(positions[rng.integers(0, len(positions))])

    @staticmethod
    def _inserter_move(game: Game, rng: np.random.Generator) -> None:
        letters = sorted(game.get_legal_moves())
        index = game.chosen_index
        word = game.get_current_word()

        safe = []
        for letter in letters:
            test_word = word[:index] + letter + word[index:]
            if not TwinChecker.check_for_close_twins(test_word, index):
                safe.append(letter)

        if safe:
            game.apply_letter(safe[rng.integers(0, len(safe))])
        else:
            game.apply_letter(letters[rng.integers(0, len(letters))])

    @staticmethod
    def _is_forced_win(game: Game, position: int, alphabet: list[str]) -> bool:
        """Return True if every letter at *position* creates a twin."""
        word = game.get_current_word()
        for letter in alphabet:
            test_word = word[:position] + letter + word[position:]
            if not TwinChecker.check_for_close_twins(test_word, position):
                return False
        return True
