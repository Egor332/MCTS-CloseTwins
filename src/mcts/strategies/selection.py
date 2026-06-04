from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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

        exploration = math.sqrt(
            (math.log(node.parent.visits) / node.visits) * min(0.25, v)
        )
        return mean + exploration
