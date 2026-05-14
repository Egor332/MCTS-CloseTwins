from IGameEngine import IGameEngine
from typing import List
from domain import GameStatus, Role
from twin_checker import TwinChecker

class Game(IGameEngine):
    def __init__(self, alphabet: List[str], max_length: int):
        self.current_word = []
        self.max_length = max_length
        self.alphabet = set(alphabet)

        self.game_status = GameStatus.ONGOING

        self.turn = Role.POINTER
        self.choosen_index = None
        self.choosen_letter = None

    def get_current_word(self) -> str:
        return "".join(self.current_word)

    def get_alphabet(self) -> List[str]:
        return list(self.alphabet)

    def get_max_length(self) -> int:
        return self.max_length

    def apply_index(self, index) -> bool:
        if self.turn != Role.POINTER:
            raise Exception("Tryied to choose index while it's 'insrter' turn")
        if index < 0 or index > len(self.current_word):
            raise Exception("Index is out of range")
        self.choosen_index = index

    def apply_letter(self, letter: str) -> bool:
        if self.turn != Role.INSERTER:
            raise Exception("Tryied to insert letter while it's 'pointer' turn")
        if letter not in self.alphabet:
            raise Exception("Letter is not in the alphabet")
        self.choosen_letter = letter
        self.current_word.insert(self.choosen_index, letter)
        if TwinChecker.check_for_close_twins(self.get_current_word, self.choosen_index):
            self.game_status = GameStatus.P1_WINS_TWINS
        elif len(self.current_word) >= self.max_length:
            self.game_status = GameStatus.P2_WINS_LIMIT
        return True