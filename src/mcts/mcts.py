from __future__ import annotations

import numpy as np

from src.domain import GameStatus, Role
from src.engine.game import Game
from src.mcts.node import Node
from src.mcts.strategies.selection import SelectionStrategy
from src.mcts.strategies.simulation import SimulationStrategy
from src.mcts.strategies.backpropagation import BackpropagationStrategy


class MCTS:
    def __init__(
        self,
        iterations: int,
        selection: SelectionStrategy,
        simulation: SimulationStrategy,
        backpropagation: BackpropagationStrategy,
        rng: np.random.Generator | None = None,
    ):
        self.iterations = iterations
        self.selection = selection
        self.simulation = simulation
        self.backpropagation = backpropagation
        self.rng = rng if rng is not None else np.random.default_rng()

    def get_best_move(self, initial_state: Game) -> object:
        root = Node(initial_state.clone(), rng=self.rng)

        for _ in range(self.iterations):
            node = self._select(root)

            if (not node.is_terminal_node()) and (not node.is_fully_expanded()):
                node = node.expand()

            result = self.simulation.simulate(node.state, self.rng)
            self.backpropagation.backpropagate(node, result)

        if not root.children:
            return None
        return self._get_best_move(root).move

    def _select(self, node: Node) -> Node:
        while (not node.is_terminal_node()) and node.is_fully_expanded():
            proven = self._pick_proven_child(node)
            if proven is not None:
                node = proven
            else:
                node = max(
                    node.children, key=lambda child: self.selection.score(child)
                )
        return node

    @staticmethod
    def _pick_proven_child(node: Node) -> Node | None:
        """If any child is a proven win for the current mover, return it."""
        if not node.children:
            return None
        mover = node.state.turn
        for child in node.children:
            if child.proven_status is not None and child.proven_status != GameStatus.ONGOING:
                if mover == Role.POINTER and child.proven_status == GameStatus.P1_WINS_TWINS:
                    return child
                if mover == Role.INSERTER and child.proven_status == GameStatus.P2_WINS_LIMIT:
                    return child
        return None

    @staticmethod
    def _get_best_move(root: Node) -> Node:
        if not root.children:
            raise RuntimeError("Root has no children")
        return max(root.children, key=lambda child: child.visits)
