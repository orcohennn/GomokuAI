import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jsons_reader import read_json_files
from datetime import datetime


def plot_game_analysis(data, unique_filename=False, save_plot=True, show_plot=False):
    for players, games in data.items():
        black_player, white_player = players
        df = pd.DataFrame(games)

        # Calculate the average moves for black and white players
        avg_total_moves = (df['steps_by_black'] + df['steps_by_white']).mean()
        total_games = len(df)

        # Create a figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'Game Analysis: {black_player} (Black) vs {white_player} (White)\n'
                     f'Total Games Played: {total_games}\n'
                     f'Average Total Game Moves: {avg_total_moves:.2f}\n'
                     f'Each Player Did ~{int(avg_total_moves//2)} Moves On Average',
                     fontsize=16)

        # 1. Top Left: Bar for Black Player Wins and White Player Wins
        win_counts = df['winner'].value_counts()
        sns.barplot(x=win_counts.index, y=win_counts.values, ax=axs[0, 0], palette='Set1')
        axs[0, 0].set_title('Wins by Player')
        axs[0, 0].set_ylabel('Number of Wins')

        # 2. Top Right: Bar for Missed Opportunities by Black and White Player
        missed_opportunities = df[['missed_opportunities_black', 'missed_opportunities_white']].sum()
        sns.barplot(x=missed_opportunities.index.str.replace('missed_opportunities_', ''),
                    y=missed_opportunities.values, ax=axs[0, 1], palette='Set2')
        axs[0, 1].set_title('Total Missed Opportunities')
        axs[0, 1].set_ylabel('Missed Opportunities')

        # 3. Bottom Left: Bar for Blocks by Black and White Player
        blocks = df[['blocks_by_black', 'blocks_by_white']].sum()
        sns.barplot(x=blocks.index.str.replace('blocks_by_', ''), y=blocks.values, ax=axs[1, 0], palette='Set2')
        axs[1, 0].set_title('Total Blocks')
        axs[1, 0].set_ylabel('Blocks')

        # 4. Bottom Right: Pie chart for Black Wins, White Wins, and Draws
        win_types = df['winner'].value_counts()

        # Ensure that we have black, white, and draw counts (if draw is not in the dataset, add it with value 0)
        if 'black' not in win_types:
            win_types['black'] = 0
        if 'white' not in win_types:
            win_types['white'] = 0
        if 'draw' not in win_types:
            win_types['draw'] = 0

        axs[1, 1].pie(win_types.values, labels=win_types.index, autopct='%1.1f%%',
                      colors=['#FF9999', '#66B2FF', '#99FF99'], startangle=90)
        axs[1, 1].set_title('Win Ratio (Black/White/Draw)')

        # Adjust layout
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_plot:
            filename = f'game_analysis_{black_player}_vs_{white_player}'
            if unique_filename:
                # use the filename with the unique timestamp and date

                filename = filename + f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            plt.savefig(f'plots/{filename}.png')
        if show_plot:
            plt.show()


if __name__ == "__main__":
    # Get directory input
    # directory = input("Enter the path to the directory containing JSON files: ")
    directory = "../game_logs"
    # Get the merged data from file_1.py
    data = read_json_files(directory)

    # Plot the game analysis
    plot_game_analysis(data)
