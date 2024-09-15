import heapq
from src.Agents.agent import Agent
from src.Agents import AgentsUtils


class QueueNode:
    def __init__(self, score, state, path):
        self.score = score
        self.state = state
        self.path = path

    def __lt__(self, other):
        return self.score < other.score



class MultiAStarAgent(Agent):
    def __init__(self, player, depth):
        super().__init__()
        self.heuristics = [self.heuristic_3] * 10 + [self.heuristic_2, self.heuristic_4]
        self.current_heuristic = 0
        self.player = player
        self.search_depth = depth

    def get_type(self):
        return 'StarMultiHeuristic'

    def make_move(self, game_state):
        board = game_state['board']

        # Apply round-robin heuristic selection
        heuristic = self.heuristics[self.current_heuristic]
        self.current_heuristic = (self.current_heuristic + 1) % len(self.heuristics)
        best_move = self.a_star_search(board, self.player, heuristic, self.search_depth)
        return best_move[0]

    def a_star_search(self, board, player, heuristic, search_depth):
        """
        Search the node that has the lowest combined cost and heuristic first.
        """
        start_state = board
        frontier = []
        heapq.heappush(frontier, QueueNode(0, start_state, []))
        visited = []

        while frontier:
            cur_queue_node = heapq.heappop(frontier)

            cur_state = cur_queue_node.state
            cur_path = cur_queue_node.path
            cur_cost = cur_queue_node.score

            if self.is_goal_state(cur_state, player) or search_depth == 0:
                return cur_path

            if cur_state in visited:
                continue

            visited.append(cur_state)

            for successor, action, step_cost in self.get_successors(cur_state, player):
                if successor in visited:
                    continue

                new_path = cur_path + [action]
                new_cost = cur_cost + heuristic(successor, player)

                heapq.heappush(frontier, QueueNode(new_cost, successor, new_path))

            search_depth -= 1
        return None

    def is_goal_state(self, board, player):
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

    def get_successors(self, board, player):
        successors = []
        rows = len(board)
        cols = len(board[0])

        for r in range(rows):
            for c in range(cols):
                if board[r][c] is None:  # Assuming empty cells are represented by an empty string
                    # Create a copy of the board
                    new_board = [row[:] for row in board]
                    # Place the player's mark in the empty cell
                    new_board[r][c] = player
                    successors.append((new_board, [r, c], self.heuristics[self.current_heuristic](new_board, player)))
                    if self.is_goal_state(board, player):
                        return [new_board, [r, c], 0]

        return successors

    def heuristic_3(self, state, current_color):
        opponent = 'white' if current_color == 'black' else 'black'
        black_total_score = AgentsUtils.evaluate_color(state, opponent, current_color)
        return black_total_score if current_color == "black" else -1 * black_total_score

    def heuristic_2(self, state, current_color):
        opponent = 'black' if current_color == 'white' else 'white'
        return 100000 if self.is_goal_state(state, opponent) else self.heuristic_3(state, opponent)

    def heuristic_4(self, state, current_color):
        return 100000 if self.is_goal_state(state, current_color) else self.heuristic_3(state, current_color)

