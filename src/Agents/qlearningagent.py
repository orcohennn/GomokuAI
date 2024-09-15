import pickle
import random
import numpy as np

from src.Agents import AgentsUtils
from src.Agents.agent import Agent
LEARNING_MODE = False


class QLearningAgent(Agent):
    def __init__(self, current_player, alpha=0.1, gamma=0.98, epsilon=0.2, initial_q_value=0.1):
        super().__init__()
        self.save_path = "./trained/q_table.pkl"
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon if LEARNING_MODE else 0 # Exploration rate
        self.initial_q_value = initial_q_value  # Initial Q-value for new state-action pairs
        self.q_table = {}  # Q-table to store state-action values
        self.load_q_table()  # Q-table to store state-action values
        self.last_state = None
        self.last_action = None
        self.game_counter = 0
        self.current_player = current_player

    def make_move(self, game_state):
        """Selects an action using the epsilon-greedy policy."""

        board = game_state['board']
        state_key = self.get_state_key(board)

        if state_key not in self.q_table:
            self.q_table[state_key] = {}

        valid_moves = [(r, c) for r in range(len(board)) for c in range(len(board[0])) if board[r][c] is None]
        if len(valid_moves) == (len(board) * len(board) - 1):
            return (4, 4) if board[4][4] is None else valid_moves[0]

        # Exploit: choose the move with the highest Q-value
        move_q_values = {move: self.q_table[state_key].get(move, self.initial_q_value) for move in valid_moves}
        max_q_value = max(move_q_values.values(), default=self.initial_q_value)
        best_moves = [move for move, q in move_q_values.items() if q == max_q_value]
        move = random.choice(best_moves)

        self.last_state = state_key
        self.last_action = move
        self.update_q_table(game_state, self.current_player)
        return move

    def rotate_90(self, board):
        return np.rot90(board)

    def reflect_horizontal(self, board):
        return np.fliplr(board)

    def get_minimal_representation(self, board):
        """Finds the lexicographically smallest board representation considering rotations and reflections."""
        board = np.array(board)
        transformations = []

        for _ in range(4):
            transformations.append(board)
            transformations.append(self.reflect_horizontal(board))
            board = self.rotate_90(board)

        min_representation = min([board.tostring() for board in transformations])

        return min_representation

    def get_state_key(self, board):
        """Converts the board state to a normalized key."""
        minimal_rep = self.get_minimal_representation(board)
        return hash(minimal_rep)

    def get_type(self):
        return 'QLearning'

    def count_adjacent_cells(self, board, player):
        """Counts the number of adjacent cells that have the same player's stones for all stones on the board."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonal, Anti-diagonal
        total_adjacent_count = 0

        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == player:
                    # Check adjacent cells for the player's stone at (row, col)
                    for dr, dc in directions:
                        count = 0

                        # Check in one direction
                        for i in range(1, 5):  # Check up to 4 cells in the direction
                            r, c = row + dr * i, col + dc * i
                            if 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
                                count += 1
                            else:
                                break

                        # Check in the opposite direction
                        for i in range(1, 5):  # Check up to 4 cells in the opposite direction
                            r, c = row - dr * i, col - dc * i
                            if 0 <= r < len(board) and 0 <= c < len(board[0]) and board[r][c] == player:
                                count += 1
                            else:
                                break

                        # Add this count to the total adjacent count
                        total_adjacent_count += count

        return total_adjacent_count

    def update_q_table(self, game_state, current_player):
        """Updates the Q-table based on the new game state, reward, and current player."""
        board = game_state['board']
        state_key = self.get_state_key(board)

        if self.last_state is None or self.last_action is None:
            # No previous state-action to update
            return

        if self.last_state not in self.q_table:
            self.q_table[self.last_state] = {}

        if state_key not in self.q_table:
            self.q_table[state_key] = {}

        # Calculate a smarter reward based on the number of adjacent stones and potential winning lines
        smarter_reward = AgentsUtils.evaluation_function(board, current_player)

        # Q-value update rule
        current_q = self.q_table[self.last_state].get(self.last_action, self.initial_q_value)
        max_future_q = max(self.q_table[state_key].values(), default=self.initial_q_value)
        new_q = current_q + self.alpha * (smarter_reward + self.gamma * max_future_q - current_q)

        self.q_table[self.last_state][self.last_action] = new_q
        print(f"Updated Q-value: {new_q} (Reward: {smarter_reward})")

        # Reset last_state and last_action for next move
        self.last_state = None
        self.last_action = None
        self.game_counter += 1

        # self.save_q_table() When train add also epsilon with random moves


    def calculate_smarter_reward(self, board, current_player):
        """Calculate a smarter reward based on the current board state and player."""
        opponent = 'white' if current_player == 'black' else 'black'
        reward = 0

        # Check if the current player has won
        if self.check_win(board, current_player):
            return 1000  # Large reward for winning

        # Check if the opponent has won
        if self.check_win(board, opponent):
            return -1000  # Large penalty for opponent winning

        # Evaluate blocking and sequence formation
        reward += self.evaluate_sequences(board, current_player)
        reward -= self.evaluate_threats(board, opponent)

        return reward

    def evaluate_sequences(self, board, player):
        """Evaluate the board and give rewards for sequences of 2, 3, and 4."""
        reward = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:  # (row_dir, col_dir)
                    sequence_length = self.count_sequence(board, row, col, direction, player)
                    if sequence_length >= 5:
                        reward += 100  # Winning
                    elif sequence_length == 4:
                        reward += 10  # Strong position
                    elif sequence_length == 3:
                        reward += 5  # Moderate position
                    elif sequence_length == 2:
                        reward += 1  # Weak position
        return reward

    def evaluate_threats(self, board, player):
        """Evaluate the board and give penalties for opponent's threats."""
        reward = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:  # (row_dir, col_dir)
                    sequence_length = self.count_sequence(board, row, col, direction, player)
                    if sequence_length == 4:
                        reward -= 20  # Strong threat
                    elif sequence_length == 3:
                        reward -= 10  # Moderate threat
                    elif sequence_length == 2:
                        reward -= 5  # Weak threat
        return reward

    def count_sequence(self, board, start_row, start_col, direction, player):
        """Count the length of a sequence for a player starting from a given position and direction."""
        row_dir, col_dir = direction
        length = 0
        row, col = start_row, start_col

        while 0 <= row < len(board) and 0 <= col < len(board[row]) and board[row][col] == player:
            length += 1
            row += row_dir
            col += col_dir

        return length

    def check_win(self, board, player):
        """Check if the given player has won with a sequence of 5 in a row."""

        def has_five_in_a_row(start_row, start_col, row_dir, col_dir):
            """Check for a sequence of 5 in a row starting from (start_row, start_col)."""
            count = 0
            row, col = start_row, start_col
            while 0 <= row < len(board) and 0 <= col < len(board[row]) and board[row][col] == player:
                count += 1
                if count == 5:
                    return True
                row += row_dir
                col += col_dir
            return False

        board_size = len(board)

        for row in range(board_size):
            for col in range(board_size):
                # Check horizontal
                if col <= board_size - 5:
                    if has_five_in_a_row(row, col, 0, 1):
                        return True

                # Check vertical
                if row <= board_size - 5:
                    if has_five_in_a_row(row, col, 1, 0):
                        return True

                # Check bottom-right diagonal
                if row <= board_size - 5 and col <= board_size - 5:
                    if has_five_in_a_row(row, col, 1, 1):
                        return True

                # Check bottom-left diagonal
                if row <= board_size - 5 and col >= 4:
                    if has_five_in_a_row(row, col, 1, -1):
                        return True

        return False

    def save_q_table(self):
        """Saves the Q-table to a file."""
        with open(self.save_path, 'wb') as f:
            pickle.dump(self.q_table, f)
        print(f"Q-table saved to {self.save_path}")

    def load_q_table(self):
        """Loads the Q-table from a file."""
        try:
            with open(self.save_path, 'rb') as f:
                self.q_table = pickle.load(f)
            print(f"Q-table loaded from {self.save_path}")
        except FileNotFoundError:
            print(f"No saved Q-table found at {self.save_path}, starting fresh.")
