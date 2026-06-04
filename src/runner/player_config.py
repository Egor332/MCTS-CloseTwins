from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class PlayerConfig:
    name: str
    iterations: int
    selection: str = "uct"
    simulation: str = "random"
    backpropagation: str = "standard"
    exploration_constant: float = math.sqrt(2)
