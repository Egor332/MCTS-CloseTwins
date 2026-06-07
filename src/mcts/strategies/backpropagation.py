from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from src.domain import GameStatus, Role

if TYPE_CHECKING:
    from src.mcts.node import Node


class BackpropagationStrategy(ABC):
    @abstractmethod
    def backpropagate(self, node: Node, result: GameStatus) -> None: ...


class StandardBackprop(BackpropagationStrategy):
    def backpropagate(self, node: Node, result: GameStatus) -> None:
        while node is not None:
            node.update(result)
            node = node.parent


class SolverBackprop(BackpropagationStrategy):
    """MCTS-Solver: propagates proven win/loss flags up the tree.

    After the standard statistical update, terminal or fully-explored
    nodes get a ``proven_status``.  The status propagates upward:
    - If *all* children are proven losses for the current mover -> node is a proven win for the opponent.
    - If *any* child is a proven win for the current mover -> node is a proven win for the current mover.
    """

    def backpropagate(self, node: Node, result: GameStatus) -> None:
        while node is not None:
            node.update(result)
            self._try_prove(node)
            node = node.parent

    @staticmethod
    def _try_prove(node: Node) -> None:
        if node.proven_status is not None:
            return

        if node.state.game_status != GameStatus.ONGOING:
            node.proven_status = node.state.game_status
            return

        if not node.is_fully_expanded() or not node.children:
            return

        mover = node.state.turn

        if mover == Role.POINTER:
            my_win = GameStatus.P1_WINS_TWINS
            opponent_win = GameStatus.P2_WINS_LIMIT
        else:
            my_win = GameStatus.P2_WINS_LIMIT
            opponent_win = GameStatus.P1_WINS_TWINS

        if any(c.proven_status == my_win for c in node.children):
            node.proven_status = my_win
            return

        if all(c.proven_status == opponent_win for c in node.children):
            node.proven_status = opponent_win
