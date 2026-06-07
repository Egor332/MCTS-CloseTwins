from src.mcts.config import MCTSConfig
from src.mcts.mcts import MCTS
from src.engine.game import Game

def test_mcts():
    # Force use of solver
    MCTSConfig.USE_SOLVER = True
    
    print("Testing MCTS with Solver enabled...")
    game = Game(alphabet=['A', 'B'], max_length=5)
    mcts = MCTS(iterations=100)
    best_move = mcts.get_best_move(game)
    
    print(f"Best move found: {best_move}")
    
    MCTSConfig.USE_SOLVER = False
    print("Testing MCTS with Solver disabled...")
    mcts_classic = MCTS(iterations=100)
    best_move_classic = mcts_classic.get_best_move(game)
    print(f"Best move found: {best_move_classic}")
    
if __name__ == '__main__':
    test_mcts()
