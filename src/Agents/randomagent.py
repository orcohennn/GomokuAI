import random
from src.Agents.agent import Agent


class RandomAgent(Agent):
    def __init__(self):
        super().__init__()

    def get_type(self):
        return 'Random'

    def make_move(self, game_state):
        """Returns a random valid move."""
        board = game_state['board']
        valid_moves = [(r, c) for r in range(len(board)) for c in range(len(board[0])) if board[r][c] is None]
        if valid_moves:
            return random.choice(valid_moves)
        return None
