from abc import ABC, abstractmethod
from typing import List

class IGameEngine(ABC):
    @abstractmethod
    def get_current_word(self) -> str:
        pass

    @abstractmethod
    def get_alphabet(self) -> List[str]:
        pass

    @abstractmethod
    def get_max_length(self) -> int:
        pass

    @abstractmethod
    def apply_index(self, index) -> bool:
        "Validates and applyes index choosed by player 1"
        pass

    @abstractmethod
    def apply_letter(self, letter: str) -> bool:
        "Inserts letter (player 2 move), check for twins after letter insertion, actualize game"
        pass