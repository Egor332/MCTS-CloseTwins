from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.runner.player_config import PlayerConfig


@dataclass
class MatchConfig:
    name: str
    alphabet_size: int
    max_word_length: int
    num_games: int
    base_seed: int
    pointer: PlayerConfig
    inserter: PlayerConfig


def _parse_player(data: dict) -> PlayerConfig:
    return PlayerConfig(
        name=data["name"],
        iterations=data["iterations"],
        selection=data.get("selection", "uct"),
        simulation=data.get("simulation", "random"),
        backpropagation=data.get("backpropagation", "standard"),
        exploration_constant=data.get("exploration_constant", math.sqrt(2)),
    )


def load_match_configs(yaml_path: str | Path) -> list[MatchConfig]:
    path = Path(yaml_path)
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    configs: list[MatchConfig] = []
    for entry in raw["matches"]:
        configs.append(
            MatchConfig(
                name=entry["name"],
                alphabet_size=entry["alphabet_size"],
                max_word_length=entry["max_word_length"],
                num_games=entry["num_games"],
                base_seed=entry.get("base_seed", 0),
                pointer=_parse_player(entry["pointer"]),
                inserter=_parse_player(entry["inserter"]),
            )
        )
    return configs
