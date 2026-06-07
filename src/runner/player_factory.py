from __future__ import annotations

import numpy as np

from src.mcts.mcts import MCTS
from src.mcts.strategies.selection import (
    SelectionStrategy,
    UCTStrategy,
    UCB1TunedStrategy,
    ProgressiveBias,
)
from src.mcts.strategies.simulation import (
    SimulationStrategy,
    RandomSimulation,
    HeuristicSimulation,
)
from src.mcts.strategies.backpropagation import (
    BackpropagationStrategy,
    StandardBackprop,
    SolverBackprop,
)
from src.runner.player_config import PlayerConfig

SELECTION_REGISTRY: dict[str, type[SelectionStrategy]] = {
    "uct": UCTStrategy,
    "ucb1_tuned": UCB1TunedStrategy,
}

SIMULATION_REGISTRY: dict[str, type[SimulationStrategy]] = {
    "random": RandomSimulation,
    "heuristic": HeuristicSimulation,
}

BACKPROPAGATION_REGISTRY: dict[str, type[BackpropagationStrategy]] = {
    "standard": StandardBackprop,
    "solver": SolverBackprop,
}


def build_mcts(config: PlayerConfig, rng: np.random.Generator | None = None) -> MCTS:
    sel_cls = SELECTION_REGISTRY.get(config.selection)
    if sel_cls is None:
        raise ValueError(
            f"Unknown selection strategy '{config.selection}'. "
            f"Available: {list(SELECTION_REGISTRY)}"
        )

    sim_cls = SIMULATION_REGISTRY.get(config.simulation)
    if sim_cls is None:
        raise ValueError(
            f"Unknown simulation strategy '{config.simulation}'. "
            f"Available: {list(SIMULATION_REGISTRY)}"
        )

    bp_cls = BACKPROPAGATION_REGISTRY.get(config.backpropagation)
    if bp_cls is None:
        raise ValueError(
            f"Unknown backpropagation strategy '{config.backpropagation}'. "
            f"Available: {list(BACKPROPAGATION_REGISTRY)}"
        )

    selection: SelectionStrategy = sel_cls(exploration_constant=config.exploration_constant)
    if config.progressive_bias:
        selection = ProgressiveBias(base=selection, weight=config.bias_weight)

    simulation = sim_cls()
    backpropagation = bp_cls()

    return MCTS(
        iterations=config.iterations,
        selection=selection,
        simulation=simulation,
        backpropagation=backpropagation,
        rng=rng,
    )
