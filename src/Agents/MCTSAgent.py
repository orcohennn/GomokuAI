import copy
import random
import numpy as np
from src.Agents import AgentsUtils as utils
from src.Agents.agent import Agent


class MCTSAgent(Agent):
    def __init__(self, n_simulations=2, m_steps=2, evaluation_fn=None, exploration_weight=1.41):
        super(MCTSAgent, self).__init__()
        self.n_simulations = n_simulations
        self.m_steps = m_steps
        self.evaluation_fn = evaluation_fn if evaluation_fn is not None else utils.evaluation_function
        self.exploration_weight = exploration_weight

    def make_move(self, game_state):
        """
        Make a move using MCTS logic.
        :param game_state: Current state of the game (the board).
        :return: The selected move (row, col).
        """
        board = game_state['board']
        current_player = game_state['current_player']

        root_node = MCTSNode(board, current_player)

        # Run n_simulations to explore the game tree
        for _ in range(self.n_simulations):
            node = self._select(root_node)
            if not node.is_fully_expanded():
                node = node.expand()
            result = self.simulate_move(node, game_state)
            node.backpropagate(result)

        # Return the move with the highest number of visits
        best_child = max(root_node.children, key=lambda child: child.visits)
        return best_child.move

    @staticmethod
    def _make_move_on_board(board, row, col, color):
        """
        Make a move on the board.
        :param board: The current state of the board.
        :param row: The row to place the stone.
        :param col: The column to place the stone.
        :param color: The color of the stone ('black' or 'white').
        """
        if board[row][col] is None:
            board[row][col] = color
        else:
            return

    @staticmethod
    def _check_win_on_board(board, row, col, color):
        """Checks if the current move leads to a win."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonal, Anti-diagonal
        player = board[row][col]
        board_size = len(board)

        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < board_size and 0 <= c < board_size and board[r][c] == color:
                    count += 1
                else:
                    break

            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < board_size and 0 <= c < board_size and board[r][c] == color:
                    count += 1
                else:
                    break

            if count >= 5:
                return True
        return False

    def _select(self, node):
        """
        Traverse the tree by selecting the best child until a leaf node is found.
        """
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.exploration_weight)
        return node

    def simulate_move(self, node, game_state):
        """
        Simulate a game for a specific move, alternating between the current player and the opponent.
        :param game_state: The game state to simulate.
        :param move: The initial move to simulate.
        :param opponent_agent: The opponent agent, whose make_move() will be called during their turn.
        :return: The score of the board after simulating the move.
        """
        simulated_board = copy.deepcopy(node.board)
        current_player = 'white' if node.current_player == 'black' else 'black'

        # Simulate for `m_steps` or until the game ends
        for _ in range(self.m_steps):
            if current_player == node.current_player:

                # Current player (MCTS agent)
                legal_moves = utils.mixed_heuristic(simulated_board, current_player, k=30)
                if legal_moves == []:
                    legal_moves = utils.find_shared_border_cells(simulated_board, distance=1)

                if not legal_moves:  # No more legal moves, draw
                    return 0

                move = random.choice(legal_moves)
                MCTSAgent._make_move_on_board(simulated_board, move[0], move[1], current_player)
            else:
                # Opponent agent moves
                move = random.choice(utils.find_shared_border_cells(simulated_board, distance=1))
                MCTSAgent._make_move_on_board(simulated_board, move[0], move[1], current_player)

            if MCTSAgent._check_win_on_board(simulated_board, move[0], move[1], current_player):
                # Will calculate the score after the loop
                break

            # Switch player
            current_player = 'white' if current_player == 'black' else 'black'

        return self.evaluation_fn(simulated_board, game_state['current_player'])

    def get_type(self):
        return 'MCTS'


class MCTSNode:
    def __init__(self, board, current_player, parent=None, move=None):
        self.board = board  # The current state of the game board (2D array)
        self.current_player = current_player  # 'black' or 'white'
        self.parent = parent  # Parent node (None for the root node)
        self.move = move  # The move that led to this node (row, col)
        self.children = []  # List of child nodes (future game states)
        self.visits = 0  # Number of times this node has been visited
        self.total_score = 0  # Cumulative evaluation score from all simulations
        self.untried_moves = utils.find_shared_border_cells(board, distance=1)  # List of legal moves from this state

    def is_fully_expanded(self):
        """Returns True if all legal moves from this state have been expanded."""
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.41):
        """
        Select the child node with the best UCB1 value, balancing exploration and exploitation.
        """
        return max(self.children, key=lambda child: (child.total_score / child.visits) + exploration_weight * (
            np.sqrt(np.log(self.visits) / child.visits)))

    def expand(self):
        """
        Expand the tree by trying an untried move, create a child node.
        """
        move = self.untried_moves.pop()  # Remove the move from the list of untried moves
        next_board = copy.deepcopy(self.board)
        MCTSAgent._make_move_on_board(next_board, move[0], move[1], self.current_player)

        # Since we are only saving nodes for your player, the child node is for your next move
        child_node = MCTSNode(next_board, self.current_player, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def backpropagate(self, result):
        """
        Backpropagate the evaluation score from the simulation up the tree.
        :param result: The evaluation score returned by the evaluation function.
        """
        self.visits += 1
        self.total_score += result  # Update the total score for this node with the evaluation result
        if self.parent:
            self.parent.backpropagate(result)

    @staticmethod
    def find_legal_moves_all_board(board):
        """
        Find all legal moves (empty cells) on the board.
        """
        legal_moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] is None:  # Empty cell
                    legal_moves.append((row, col))
        return legal_moves
