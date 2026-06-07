from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.domain import Role
from src.engine.twin_checker import TwinChecker

if TYPE_CHECKING:
    from src.mcts.node import Node


class SelectionStrategy(ABC):
    @abstractmethod
    def score(self, node: Node) -> float: ...


class UCTStrategy(SelectionStrategy):
    def __init__(self, exploration_constant: float = math.sqrt(2)):
        self.c = exploration_constant

    def score(self, node: Node) -> float:
        if node.visits == 0:
            return float("inf")

        exploitation = node.wins / node.visits
        exploration = self.c * math.sqrt(math.log(node.parent.visits) / node.visits)
        return exploitation + exploration


class UCB1TunedStrategy(SelectionStrategy):
    """UCB1-Tuned: uses empirical variance to dynamically adjust exploration."""

    def __init__(self, exploration_constant: float = math.sqrt(2)):
        self.c = exploration_constant

    def score(self, node: Node) -> float:
        if node.visits == 0:
            return float("inf")

        mean = node.wins / node.visits
        variance = node.sum_of_squared_results / node.visits - mean ** 2
        v = variance + math.sqrt(2 * math.log(node.parent.visits) / node.visits)

        exploration = self.c * math.sqrt(
            (math.log(node.parent.visits) / node.visits) * min(0.25, v)
        )
        return mean + exploration


class ProgressiveBias(SelectionStrategy):
    """Decorator that adds a heuristic bias term to any base SelectionStrategy.

    score = base_score + weight * H(node) / (n_i + 1)

    The bias dominates early (low visit count) and vanishes as n_i grows,
    letting the statistical base strategy take over.

    Heuristic H(node):
    - For Inserter moves (node.move is a letter): how "safe" the letter is,
      measured as 1 minus its relative frequency in the neighborhood of the
      insertion point.  Letters that rarely appear nearby are less likely to
      form close twins.
    - For Pointer moves (node.move is an index): what fraction of alphabet
      letters would create a twin at that position.  Higher = better for
      Pointer (harder for Inserter to dodge).
    """

    NEIGHBORHOOD_RADIUS = 3

    def __init__(self, base: SelectionStrategy, weight: float = 1.0):
        self.base = base
        self.weight = weight

    def score(self, node: Node) -> float:
        base_score = self.base.score(node)
        if node.visits == 0:
            return base_score

        h = self._heuristic(node)
        bias = self.weight * h / (node.visits + 1)
        return base_score + bias

    @staticmethod
    def _heuristic(node: Node) -> float:
        parent = node.parent
        if parent is None:
            return 0.0

        parent_state = parent.state
        move = node.move

        if parent_state.turn == Role.INSERTER:
            return ProgressiveBias._heuristic_inserter(parent_state, move)
        else:
            return ProgressiveBias._heuristic_pointer(parent_state, move)

    @staticmethod
    def _heuristic_inserter(state, letter: str) -> float:
        """Safety of inserting *letter*: 1 - (frequency near cursor)."""
        word = state.get_current_word()
        index = state.chosen_index
        if not word:
            return 1.0

        r = ProgressiveBias.NEIGHBORHOOD_RADIUS
        start = max(0, index - r)
        end = min(len(word), index + r)
        neighborhood = word[start:end]

        if not neighborhood:
            return 1.0

        freq = neighborhood.count(letter) / len(neighborhood)
        return 1.0 - freq

    @staticmethod
    def _heuristic_pointer(state, position: int) -> float:
        """Danger of *position* for Inserter: fraction of letters that create a twin."""
        word = state.get_current_word()
        alphabet = state.get_alphabet()
        if not alphabet:
            return 0.0

        twin_count = 0
        for letter in alphabet:
            test_word = word[:position] + letter + word[position:]
            if TwinChecker.check_for_close_twins(test_word, position):
                twin_count += 1

        return twin_count / len(alphabet)
