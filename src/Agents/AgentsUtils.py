import heapq

import numpy as np
import random

MAX_VALID_MOVES = 255


def in_bounds(r, c, max_r, max_c):
    return 0 <= r < max_r and 0 <= c < max_c


def find_shared_border_cells(board, distance=1, max_valid_moves=MAX_VALID_MOVES):
    # Ensure the input is a numpy array
    if not isinstance(board, np.ndarray):
        board = np.array(board)

    # Get the shape of the board
    rows, cols = board.shape

    # Initialize list to store valid cells
    shared_border_cells = []
    none_cells = []

    # Function to check if a position is within the board boundaries

    # Iterate over the entire board
    for r in range(rows):
        for c in range(cols):
            # We're only interested in None cells
            if board[r, c] is None:
                has_neighbor = False

                # Check all four neighbors (up, down, left, right)
                neighbors = [
                    (r - 1, c),  # Up
                    (r + 1, c),  # Down
                    (r, c - 1),  # Left
                    (r, c + 1),  # Right
                    (r - 1, c - 1),  # Top-left diagonal
                    (r - 1, c + 1),  # Top-right diagonal
                    (r + 1, c - 1),  # Bottom-left diagonal
                    (r + 1, c + 1)  # Bottom-right diagonal
                ]
                if distance == 2:
                    neighbors += [(r - 2, c), (r + 2, c), (r, c - 2), (r, c + 2),
                                  (r - 2, c - 2), (r - 2, c + 2), (r + 2, c - 2), (r + 2, c + 2),
                                  (r - 2, c - 1), (r - 2, c + 1), (r + 2, c - 1), (r + 2, c + 1),
                                  (r - 1, c - 2), (r - 1, c + 2), (r + 1, c - 2), (r + 1, c + 2)]

                for nr, nc in neighbors:
                    if in_bounds(nr, nc, rows, cols):
                        if board[nr, nc] is not None:
                            has_neighbor = True
                            break

                # If this None cell has both Black and White as neighbors
                if has_neighbor:
                    shared_border_cells.append((r, c))
                else:
                    none_cells.append((r, c))

    # If there are no shared border cells, return the center cell
    if len(shared_border_cells) == 0 and len(none_cells) > 0:
        return random.sample(none_cells, min(2, len(none_cells)))
    elif len(shared_border_cells) == 0 and len(none_cells) == 0:
        return []

    # Randomly select between 20 and the total number of valid cells
    num_to_select = min(MAX_VALID_MOVES, len(shared_border_cells))

    # Randomly sample cells
    selected_cells = random.sample(shared_border_cells, num_to_select)

    return selected_cells


def bounding_box_heuristic(board, buffer=1):
    n = len(board)
    min_row, max_row, min_col, max_col = n, 0, n, 0

    # Find the bounding box of occupied cells
    for i in range(n):
        for j in range(n):
            if board[i][j] in ('B', 'W'):
                min_row, max_row = min(min_row, i), max(max_row, i)
                min_col, max_col = min(min_col, j), max(max_col, j)

    # Expand the bounding box by a buffer
    min_row, max_row = max(0, min_row - buffer), min(n - 1, max_row + buffer)
    min_col, max_col = max(0, min_col - buffer), min(n - 1, max_col + buffer)

    # Collect all empty cells in the bounding box
    relevant_moves = [(i, j) for i in range(min_row, max_row + 1)
                      for j in range(min_col, max_col + 1)
                      if board[i][j] == "EMPTY"]

    return relevant_moves


def neighbors_heuristic(board):
    n = len(board)
    scores = [[0 for i in range(n)] for j in range(n)]
    empty_board = True

    def num_of_neighbors(i, j):
        neighbors_sum = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n:
                if board[ni][nj] is not None:
                    neighbors_sum += 1
        return neighbors_sum

    for i in range(n):
        for j in range(n):
            if board[i][j] is None:
                scores[i][j] = num_of_neighbors(i, j)
            else:
                empty_board = False

    return scores, empty_board  # Return the found neighbors (could be less than k if there are fewer cells)


def offensive_heuristic(board, color):
    n = len(board)
    scores = [[0 for i in range(n)] for j in range(n)]

    def sequence_found_in_direction(row, col, direction):
        n = len(board)
        consec = 0  # Count the current empty cell we're testing

        # Check forward in the given direction
        i, j = row + direction[0], col + direction[1]
        while 0 <= i < n and 0 <= j < n and board[i][j] == color:
            consec += 1
            i += direction[0]
            j += direction[1]

        # Check backward in the opposite direction
        i, j = row - direction[0], col - direction[1]
        while 0 <= i < n and 0 <= j < n and board[i][j] == color:
            consec += 1
            i -= direction[0]
            j -= direction[1]

        return int(10 ** (consec - 1))

    def evaluate_position(row, col):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for direction in directions:
            score += sequence_found_in_direction(row, col, direction)
        return score

    for i in range(n):
        for j in range(n):
            if board[i][j] is None:
                scores[i][j] = evaluate_position(i, j)

    return scores


def defensive_heuristic(board, color):
    n = len(board)
    scores = [[0 for i in range(n)] for j in range(n)]
    op_color = "black" if color == "white" else "white"

    def sequence_found_in_direction(row, col, direction):
        n = len(board)
        consec = 0  # Count the current empty cell we're testing

        # Check forward in the given direction
        i, j = row + direction[0], col + direction[1]
        while 0 <= i < n and 0 <= j < n and board[i][j] == op_color:
            consec += 1
            i += direction[0]
            j += direction[1]

        # Check backward in the opposite direction
        i, j = row - direction[0], col - direction[1]
        while 0 <= i < n and 0 <= j < n and board[i][j] == op_color:
            consec += 1
            i -= direction[0]
            j -= direction[1]

        return int(10 ** (consec - 1))

    def evaluate_position(row, col):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for direction in directions:
            score += sequence_found_in_direction(row, col, direction)
        return score

    for i in range(n):
        for j in range(n):
            if board[i][j] is None:
                scores[i][j] = evaluate_position(i, j)

    return scores


def get_top_k_moves(combined_scores, k):
    n = len(combined_scores)
    moves = []

    # Create a max heap of moves based on their score
    for i in range(n):
        for j in range(n):
            if combined_scores[i][j] > 0:
                heapq.heappush(moves, (
                    -add_random_noise(combined_scores[i][j]), (i, j)))  # Use negative score to simulate max heap

    # Extract top k moves
    top_k_moves = []
    for _ in range(min(k, len(moves))):
        _, move = heapq.heappop(moves)
        top_k_moves.append(move)

    return top_k_moves


def mixed_heuristic(board, player_color, k):
    n = len(board)

    offensive_scores = offensive_heuristic(board, player_color)
    defensive_scores = defensive_heuristic(board, player_color)
    neighbor_scores, empty_board = neighbors_heuristic(board)
    # bounding_box_scores = bounding_box_heuristic(board)

    if empty_board:
        return [(int(n / 2), int(n / 2))]

    combined_scores = [[0 for i in range(n)] for j in range(n)]

    for i in range(n):
        for j in range(n):
            combined_scores[i][j] = (offensive_scores[i][j] + defensive_scores[i][j]) * neighbor_scores[i][j]

    relevant_moves = get_top_k_moves(combined_scores, k)

    return relevant_moves


def print_2d_array(array, title):
    print("_______________________")
    print(title)
    for row in array:
        print(" ".join(str(x) for x in row))
    print("_______________________")


def add_random_noise(score):
    return int(score + random.uniform(0.2 * score, -0.2 * score))


def evaluation_function(board, current_color):
    return add_random_noise(evaluation_state(board, current_color))


def evaluation_state(state, current_color):
    black_total_score = evaluate_color(state, "black", current_color) - \
                        evaluate_color(state, "white", current_color)
    return black_total_score if current_color == "black" else -1 * black_total_score


def evaluate_color(board, color, current_color):
    size = len(board)  # Assuming square board
    current = color == current_color
    evaluation = 0

    # Evaluate rows and columns
    for i in range(size):
        # Evaluate row i
        evaluation += evaluate_line([board[i][j] for j in range(size)], color, current)
        # Evaluate column j
        evaluation += evaluate_line([board[j][i] for j in range(size)], color, current)

    # Evaluate diagonals
    for i in range(-size + 5, size - 4):
        evaluation += evaluate_line(np.diag(board, k=i), color, current)
        evaluation += evaluate_line(np.diag(np.fliplr(board), k=i), color, current)
    return evaluation


def evaluate_line(line, color, current):
    evaluation = 0
    size = len(line)
    consec = 0
    block_count = 2
    empty = False

    for i in range(size):
        value = line[i]
        if value == color:
            consec += 1
        elif value is None and consec > 0:  # Adjust for empty cells
            if not empty and i < size - 1 and line[i + 1] == color:
                empty = True
            else:
                evaluation += calc(consec, block_count - 1, current, empty)
                consec = 0
                block_count = 1
                empty = False
        elif value is None:
            block_count = 1
        elif consec > 0:
            evaluation += calc(consec, block_count, current)
            consec = 0
            block_count = 2
        else:
            block_count = 2

    if consec > 0:
        evaluation += calc(consec, block_count, current)
    return evaluation


def calc(sequence, block_from_sides, is_current, has_empty_space=False):
    if block_from_sides == 2 and sequence < 5:  # not relevant sequence
        return 0

    sequence_score = [0, 1, 5, 1000, 10000, 100000]
    if sequence >= 5:
        if has_empty_space:
            return sequence_score[4]
        return sequence_score[5]

    score = sequence_score[sequence]
    penalty = 0.5
    if block_from_sides == 1:  # (and not 0)
        if sequence == 4:
            score *= 0.25
        if sequence == 3:
            score *= 0.01
        else:
            score *= penalty
    if has_empty_space and sequence == 4:
        score *= penalty

    if not is_current:
        if sequence in (3, 4):
            score *= 0.1
    return int(score)

