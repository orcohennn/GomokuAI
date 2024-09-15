from src.Agents.agent import Agent

class HumanAgent(Agent):
    game = None

    def __init__(self):
        super().__init__()

    def make_move(self, game_state):
        return

    def on_canvas_click(self, event):
        """Handles the click event on the canvas for the human player."""

        # Calculate the row and column based on the click coordinates
        col = event.x // self.game.cell_size
        row = event.y // self.game.cell_size

        if self.game.board[row][col] is None:
            self.game.make_move(row, col)

    def set_game(self, gomoku):
        self.game = gomoku

    def get_type(self):
        return 'Human'
