from src.IGameEngine import IGameEngine
from typing import List
from src.domain import GameStatus, Role
from src.engine.twin_checker import TwinChecker

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
        self.turn = Role.INSERTER
        self.choosen_index = index
        return True

    def apply_letter(self, letter: str) -> bool:
        if self.turn != Role.INSERTER:
            raise Exception("Tryied to insert letter while it's 'pointer' turn")
        if letter not in self.alphabet:
            raise Exception("Letter is not in the alphabet")
        self.choosen_letter = letter
        self.current_word.insert(self.choosen_index, letter)
        if TwinChecker.check_for_close_twins(self.get_current_word(), self.choosen_index):
            self.game_status = GameStatus.P1_WINS_TWINS
        elif len(self.current_word) >= self.max_length:
            self.game_status = GameStatus.P2_WINS_LIMIT
        self.turn = Role.POINTER
        return True
    
    def clone(self):
        cloned_game = Game(list(self.alphabet), self.max_length)
        cloned_game.current_word = list(self.current_word)
        cloned_game.game_status = self.game_status
        cloned_game.turn = self.turn
        cloned_game.chosen_index = self.chosen_index
        cloned_game.chosen_letter = self.chosen_letter
        return cloned_game
    
    def get_legal_moves(self) -> List:
        if self.game_status != GameStatus.ONGOING:
            return []
            
        if self.turn == Role.POINTER:
            return list(range(len(self.current_word) + 1))
        elif self.turn == Role.INSERTER:
            return list(self.alphabet)