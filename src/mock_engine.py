"""
Temporary game engine for UI testing.
Replace with real IGameEngine implementation when ready.
"""
import random
from typing import List, Optional
from src.domain import GameStatus


class MockGameEngine:
    """Mock implementation of IGameEngine interface"""
    
    def __init__(self, alphabet_size: int, max_length: int):
        self._alphabet = [chr(ord('a') + i) for i in range(min(alphabet_size, 26))]
        self._max_length = max_length
        self._current_word = ""
        self._pending_index: Optional[int] = None
        self._status = GameStatus.ONGOING

    def get_current_word(self) -> str:
        return self._current_word

    def get_alphabet(self) -> List[str]:
        return self._alphabet

    def get_max_length(self) -> int:
        return self._max_length

    def get_status(self) -> GameStatus:
        return self._status

    def get_pending_index(self) -> Optional[int]:
        return self._pending_index

    def apply_index(self, index: int) -> bool:
        """POINTER chooses where to insert next letter"""
        if self._status != GameStatus.ONGOING:
            return False
        if not (0 <= index <= len(self._current_word)):
            return False
        self._pending_index = index
        return True

    def apply_letter(self, letter: str) -> bool:
        """INSERTER adds letter at pending position"""
        if self._status != GameStatus.ONGOING:
            return False
        if letter not in self._alphabet or self._pending_index is None:
            return False

        idx = self._pending_index
        word = self._current_word
        new_word = word[:idx] + letter + word[idx:]
        self._current_word = new_word
        self._pending_index = None

        # Check win conditions
        if self._has_twins(new_word):
            self._status = GameStatus.POINTER_WINS
        elif len(new_word) >= self._max_length:
            self._status = GameStatus.INSERTER_WINS

        return True

    def _has_twins(self, word: str) -> bool:
        """Check for repeated substring (tight twins)"""
        n = len(word)
        for length in range(1, n // 2 + 1):
            for i in range(n - 2 * length + 1):
                if word[i:i + length] == word[i + length:i + 2 * length]:
                    return True
        return False

    def get_ai_index(self) -> int:
        """AI move for POINTER role - TODO: replace with MCTS"""
        return random.randint(0, len(self._current_word))

    def get_ai_letter(self) -> str:
        """AI move for INSERTER role - TODO: replace with MCTS"""
        # Simple heuristic: avoid creating twins
        if len(self._current_word) > 0 and self._pending_index is not None:
            idx = self._pending_index
            # Try to pick letter that doesn't match neighbors
            safe_letters = self._alphabet.copy()
            
            if idx > 0:
                prev = self._current_word[idx - 1]
                safe_letters = [l for l in safe_letters if l != prev]
            
            if idx < len(self._current_word):
                next_char = self._current_word[idx]
                safe_letters = [l for l in safe_letters if l != next_char]
            
            if safe_letters:
                return random.choice(safe_letters)
        
        return random.choice(self._alphabet)