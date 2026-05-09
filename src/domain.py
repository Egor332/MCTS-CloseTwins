from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

# Player 1 -- points index
# Player 2 -- inserts letter

class Role(Enum): 
    POINTER = 1 # Player 1, who shows index
    INSERTER = 2 # Player 2, who inserts letter 

class GameStatus(Enum):
    ONGOING = 0
    P1_WINS_TWINS = 1
    P2_WINS_LIMIT = 2

class Player(ABC):
    def __init__(self, name: str, role: Role):
        self.name = name
        self.role = role

    @abstractmethod
    def get_index(self, current_word: str, max_length : int) -> int:
        """
        Represent move of Player 1: returns index
        """
        pass

    @abstractmethod
    def get_letter(self, current_word: str, forced_index: int, alphabet: List[str]) -> str:
        """
        Represent move of Player 2: returns letter
        """
        pass

