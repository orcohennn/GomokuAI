import tkinter as tk
from src.WelcomeScreen import WelcomeScreen
from datetime import datetime
import json

TIME_BETWEEN_TURNS = 1 # in milliseconds
TIME_BETWEEN_GAMES = 1  # in milliseconds
NUMER_OF_GAMES = 50


class Gomoku:
    def __init__(self, root, black_agent, white_agent, collect_data=True):

        self.collect_data = collect_data
        self.missed_opportunities_black = 0
        self.missed_opportunities_white = 0
        self.blocks_by_black = 0
        self.blocks_by_white = 0
        self.steps_by_black = 0
        self.steps_by_white = 0
        self.winner = None  # Track the winner of the game
        self.root = root
        self.root.title("Gomoku Game")

        self.board_size = 15
        self.cell_size = 40
        self.canvas_size = self.board_size * self.cell_size

        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack()

        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'black'
        self.game_over = False

        self.black_agent = black_agent
        self.white_agent = white_agent

        if black_agent.get_type() == 'Human':
            black_agent.set_game(self)
            self.canvas.bind("<Button-1>", self.black_agent.on_canvas_click)

        elif white_agent.get_type() == 'Human':
            white_agent.set_game(self)
            self.canvas.bind("<Button-1>", self.white_agent.on_canvas_click)

        self.draw_board()
        self.play_turn()  # Start the game loop

    def draw_board(self):
        """Draws the Gomoku board."""
        for i in range(self.board_size):
            # Horizontal lines
            self.canvas.create_line(0, i * self.cell_size, self.canvas_size, i * self.cell_size)
            # Vertical lines
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.canvas_size)

    def make_move(self, row, col, without_graphics=True):
        """Places the stone and checks for a win."""
        if self.board[row][col] is not None:
            return

        x = col * self.cell_size + self.cell_size // 2
        y = row * self.cell_size + self.cell_size // 2

        if self.current_player == 'black':
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill='black')
            self.board[row][col] = 'black'
            self.steps_by_black += 1
            self.current_player = 'white'
        else:
            self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill='white')
            self.board[row][col] = 'white'
            self.steps_by_white += 1
            self.current_player = 'black'

        if self.check_win(row, col) or len(self.get_valid_moves()) == 0:
            self.game_over = True

            # Wait for TIME_BETWEEN_GAMES seconds (TIME_BETWEEN_GAMES milliseconds) before closing
            self.root.after(TIME_BETWEEN_GAMES, self.close_window)
        else:
            self.play_turn()  # Schedule the next turn
    def get_valid_moves(self):
        """Returns a list of valid moves (empty cells) on the board."""
        return [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] is None]
    def close_window(self):
        """Closes the window after a delay."""
        self.root.quit()  # Ends the Tkinter main loop
        self.root.destroy()  # Destroys the window

    def play_turn(self):
        """Alternates between agents to play each turn."""
        if self.game_over:
            return
        self.root.after(TIME_BETWEEN_TURNS, self.make_agent_move)

    def make_agent_move(self):
        """Determines and makes a move based on the current player."""
        if self.game_over:
            return
        game_state = {'board': self.board,
                      'game': self}

        if self.current_player == 'black':
            game_state['opponent'] = self.white_agent
            game_state['current_player'] = 'black'
            if self.black_agent.get_type() == 'Human':
                return
            move = self.black_agent.make_move(game_state)
        else:
            game_state['opponent'] = self.black_agent
            game_state['current_player'] = 'white'
            if self.white_agent.get_type() == 'Human':
                return
            move = self.white_agent.make_move(game_state)

        if self.collect_data:
            if self.current_player == 'black':
                # Check for missed win and blocks for black
                self.track_opportunities('black', move[0], move[1])
            else:
                # Check for missed win and blocks for white
                self.track_opportunities('white', move[0], move[1])

        self.make_move(move[0], move[1])

    def check_win(self, row, col):
        """Checks if the current move leads to a win."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonal, Anti-diagonal
        player = self.board[row][col]

        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                    count += 1
                else:
                    break

            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                    count += 1
                else:
                    break

            if count >= 5:
                if self.collect_data:
                    self.winner = player

                return True
        return False

    def track_opportunities(self, player, row, col):
        """Track missed win opportunities and blocks by scanning the board."""
        opponent = 'white' if player == 'black' else 'black'
        missed_opportunities_list = self.find_potential_win_spots(opponent)

        # Check if the current move (row, col) is blocking an opponent win
        if player == 'black':
            if (row, col) not in missed_opportunities_list and missed_opportunities_list != []:
                self.missed_opportunities_black += 1  # Increment for black if it didn’t block an opportunity
            elif (row, col) in missed_opportunities_list:
                self.blocks_by_black += 1  # Increment for black if it blocked an opportunity
        else:
            if (row, col) not in missed_opportunities_list and missed_opportunities_list != []:
                self.missed_opportunities_white += 1  # Increment for white if it didn’t block an opportunity
            elif (row, col) in missed_opportunities_list:
                self.blocks_by_white += 1  # Increment for white if it blocked an opportunity

    def find_potential_win_spots(self, opponent):
        """Find all spots where placing a stone would complete a continuous five-in-a-row for the opponent."""
        potential_win_spots = []

        # Check rows
        for r in range(self.board_size):
            for c in range(self.board_size - 4):
                line = self.board[r][c:c + 5]
                if self.is_valid_continuous_sequence(line, opponent):
                    empty_spot = line.index(None)
                    potential_win_spots.append((r, c + empty_spot))

        # Check columns
        for c in range(self.board_size):
            for r in range(self.board_size - 4):
                line = [self.board[r + i][c] for i in range(5)]
                if self.is_valid_continuous_sequence(line, opponent):
                    empty_spot = line.index(None)
                    potential_win_spots.append((r + empty_spot, c))

        # Check diagonals (top-left to bottom-right)
        for r in range(self.board_size - 4):
            for c in range(self.board_size - 4):
                line = [self.board[r + i][c + i] for i in range(5)]
                if self.is_valid_continuous_sequence(line, opponent):
                    empty_spot = line.index(None)
                    potential_win_spots.append((r + empty_spot, c + empty_spot))

        # Check anti-diagonals (bottom-left to top-right)
        for r in range(4, self.board_size):
            for c in range(self.board_size - 4):
                line = [self.board[r - i][c + i] for i in range(5)]
                if self.is_valid_continuous_sequence(line, opponent):
                    empty_spot = line.index(None)
                    potential_win_spots.append((r - empty_spot, c + empty_spot))

        return potential_win_spots

    def is_valid_continuous_sequence(self, line, opponent):
        """
        Checks if the given line contains exactly four continuous opponent stones and one None.
        """
        if line.count(opponent) == 4 and line.count(None) == 1:
            if line[0] is None or line[1] is None or line[2] is None or line[3] is None or line[4] is None:
                return True
            else:
                return False
        return False


def start_game(black_agent, white_agent, n=NUMER_OF_GAMES, collect_data=True):
    """Starts the Gomoku game with the selected agents and runs `n` times."""
    results = {
        'black_player': black_agent.get_type(),
        'white_player': white_agent.get_type(),
        'games': []  # List to store individual game results
    }

    for i in range(n):
        print(f'-DEBUG- Game: {i + 1}')
        root = tk.Tk()
        game = Gomoku(root, black_agent, white_agent, collect_data=collect_data)
        root.mainloop()

        # Save the game result after each game
        if collect_data:
            results['games'].append({
                'game_number': i + 1,
                'winner': game.winner if game.winner is not None else 'Draw',
                'winner_type': game.black_agent.get_type() if game.winner == 'black' else game.white_agent.get_type(),
                'missed_opportunities_black': game.missed_opportunities_black,
                'missed_opportunities_white': game.missed_opportunities_white,
                'blocks_by_black': game.blocks_by_black,
                'blocks_by_white': game.blocks_by_white,
                'steps_by_black': game.steps_by_black,
                'steps_by_white': game.steps_by_white})

    if collect_data:
        filename = get_filename(black_agent, n, white_agent)
        with open(filename, 'w') as file:
            json.dump(results, file, indent=4)
        print(f"Results saved to {filename}")


def get_filename(black_agent, n, white_agent):
    return (f"game_logs/gomoku_results_{datetime.now().strftime('%d')}_{datetime.now().strftime('%m')}_"
            f"{datetime.now().strftime('%Y')}_{datetime.now().strftime('%H')}_{datetime.now().strftime('%M')}_"
            f"B{black_agent.get_type()}_W{white_agent.get_type()}_n_{n}.json")


if __name__ == "__main__":
    root = tk.Tk()
    welcome_screen = WelcomeScreen(root, start_game)
    root.mainloop()
