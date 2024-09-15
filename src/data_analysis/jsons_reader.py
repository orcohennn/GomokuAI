import json
import os
import sys
import numpy as np
from collections import defaultdict

STATISTICS = "statistics"
READER = "reader"
MODE = READER

def calculate_statistics(json_files):
    # Process each file
    for json_file in json_files:
        print(f"Processing file: {json_file}")
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Initialize cumulative statistics
        total_games = 0
        wins_black = 0
        wins_white = 0
        missed_opportunities_black_list = []
        missed_opportunities_white_list = []
        blocks_by_black_list = []
        blocks_by_white_list = []

        player_types = {"black": None, "white": None}

        # Store player types (same across all games in the file)
        if player_types["black"] is None:
            player_types["black"] = data["black_player"]
        if player_types["white"] is None:
            player_types["white"] = data["white_player"]

        games = data['games']
        total_games += len(games)

        # Collect statistics from each game
        for game in games:
            if game['winner'] == "black":
                wins_black += 1
            elif game['winner'] == "white":
                wins_white += 1

            # Append values to the lists for calculating averages later
            missed_opportunities_black_list.append(game['missed_opportunities_black'])
            missed_opportunities_white_list.append(game['missed_opportunities_white'])
            blocks_by_black_list.append(game['blocks_by_black'])
            blocks_by_white_list.append(game['blocks_by_white'])

    # Calculate win rates
    win_rate_black = (wins_black / total_games) * 100 if total_games > 0 else 0
    win_rate_white = (wins_white / total_games) * 100 if total_games > 0 else 0

    # Calculate averages
    avg_missed_opportunities_black = np.mean(missed_opportunities_black_list) if missed_opportunities_black_list else 0
    avg_missed_opportunities_white = np.mean(missed_opportunities_white_list) if missed_opportunities_white_list else 0
    avg_blocks_by_black = np.mean(blocks_by_black_list) if blocks_by_black_list else 0
    avg_blocks_by_white = np.mean(blocks_by_white_list) if blocks_by_white_list else 0

    # Print out the statistics
    print(f"Player Types: Black = {player_types['black']}, White = {player_types['white']}")
    print(f"Total Games: {total_games}")
    print(f"Win Rate of Black Player ({player_types['black']}): {win_rate_black:.2f}%")
    print(f"Win Rate of White Player ({player_types['white']}): {win_rate_white:.2f}%")
    print(f"Average Missed Opportunities (Black): {avg_missed_opportunities_black:.2f}")
    print(f"Average Missed Opportunities (White): {avg_missed_opportunities_white:.2f}")
    print(f"Average Blocks by Black: {avg_blocks_by_black:.2f}")
    print(f"Average Blocks by White: {avg_blocks_by_white:.2f}")

def get_json_files_from_cmd():
    # Command line argument input for json files
    if len(sys.argv) < 2:
        print("No json paths provided in the command line arguments.")
        return []

    json_files = sys.argv[1:]
    for file in json_files:
        if not os.path.exists(file) or not file.endswith('.json'):
            print(f"File '{file}' does not exist or is not a JSON file.")
            sys.exit(1)

    return json_files


def read_json_files(directory_path):
    merged_data = defaultdict(list)

    # Loop through all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)

            # Open and load the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                key = (data["black_player"], data["white_player"])

                # Append the games list to the merged data dictionary
                merged_data[key].extend(data["games"])

    return dict(merged_data)

if __name__ == "__main__":

    if MODE == STATISTICS:
        # Get JSON file paths from the command line or hard-code paths here:
        hard_code_paths = ['../game_logs/gomoku_results_09_09_2024_23_33_BMinimax_WRandom_n_100.json',
                           ]
        json_files = get_json_files_from_cmd() + hard_code_paths

        # Calculate statistics for the provided JSON files
        calculate_statistics(json_files)
    elif MODE == READER:
        # directory = input("Enter the path to the directory containing JSON files: ")
        directory = '../game_logs'
        data = read_json_files(directory)
        print(data)
