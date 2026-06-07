from __future__ import annotations

import csv
from dataclasses import asdict, fields
from pathlib import Path

from src.runner.game_runner import GameResult

FIELDNAMES = [f.name for f in fields(GameResult)]


def write_results(results: list[GameResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists() and path.stat().st_size > 0

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))
