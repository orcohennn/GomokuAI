import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk, ImageFilter
from Agents.agentsFactory import AgentFactory


class WelcomeScreen:
    def __init__(self, root, start_game_callback):
        self.root = root
        self.root.title("Gomoku - Select Opponents")
        self.root.geometry("800x600")  # Set window size

        # Load and optionally blur the background image for a modern look
        self.background_image = Image.open("assets/background.jpg")
        self.bg_image = ImageTk.PhotoImage(self.background_image)

        # Create canvas to hold background image
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.start_game_callback = start_game_callback

        self.black_agent_choice = tk.StringVar(value="minimax")
        self.white_agent_choice = tk.StringVar(value="human")

        # Custom font with slightly smaller size for better alignment
        title_font = font.Font(family="Helvetica", size=13, weight="bold")
        label_font = font.Font(family="Helvetica", size=8)

        # Move the labels slightly lower and add shadow text for better contrast
        self.create_shadowed_text(250, 30, "Select Black Player Agent:", title_font)
        self.create_shadowed_text(500, 30, "Select White Player Agent:", title_font)

        # Frame for the black player buttons, centered with padding
        self.black_frame = tk.Frame(self.root, bg='#222')
        self.canvas.create_window(250, 300, anchor="center", window=self.black_frame)

        # Radio buttons for selecting black player agent
        self.black_radiobuttons = [
            self.create_radiobutton(self.black_frame, "Minimax Agent", self.black_agent_choice, "minimax", label_font),
            self.create_radiobutton(self.black_frame, "Random Agent", self.black_agent_choice, "random", label_font),
            self.create_radiobutton(self.black_frame, "Human Player", self.black_agent_choice, "human", label_font),
            self.create_radiobutton(self.black_frame, "QLearning Player", self.black_agent_choice, "qlearning", label_font),
            self.create_radiobutton(self.black_frame, "MCTSAgent Player", self.black_agent_choice, "mcts", label_font),
            self.create_radiobutton(self.black_frame, "AlphaBeta Player", self.black_agent_choice, "alphabeta", label_font),
            self.create_radiobutton(self.black_frame, "Expectimax Player", self.black_agent_choice, "expectimax", label_font),
            self.create_radiobutton(self.black_frame, "MultiAStarAgent Player", self.black_agent_choice, "multiastar", label_font)
        ]

        # Frame for the white player buttons, centered with padding
        self.white_frame = tk.Frame(self.root, bg='#222')
        self.canvas.create_window(500, 300, anchor="center", window=self.white_frame)

        # Radio buttons for selecting white player agent
        self.white_radiobuttons = [
            self.create_radiobutton(self.white_frame, "Minimax Agent", self.white_agent_choice, "minimax", label_font),
            self.create_radiobutton(self.white_frame, "Random Agent", self.white_agent_choice, "random", label_font),
            self.create_radiobutton(self.white_frame, "Human Player", self.white_agent_choice, "human", label_font),
            self.create_radiobutton(self.white_frame, "QLearning Player", self.white_agent_choice, "qlearning", label_font),
            self.create_radiobutton(self.white_frame, "MCTSAgent Player", self.white_agent_choice, "mcts", label_font),
            self.create_radiobutton(self.white_frame, "AlphaBeta Player", self.white_agent_choice, "alphabeta", label_font),
            self.create_radiobutton(self.white_frame, "Expectimax Player", self.white_agent_choice, "expectimax", label_font),
            self.create_radiobutton(self.white_frame, "MultiAStarAgent Player", self.white_agent_choice, "multiastar", label_font)
        ]

        # Start button with modern rounded style and color change on hover
        self.start_button = tk.Button(root, text="Start Game", command=self.start_game, font=label_font,
                                      bg="#6936AB", fg="white", activebackground="#2980B9", relief="flat", bd=0,
                                      padx=20, pady=10, highlightthickness=0)
        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg="#6936AB"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg="#8E5CD0"))
        self.start_button_window = self.canvas.create_window(375, 570, anchor="center", window=self.start_button)

        # Update the button styles initially
        self.update_button_styles()

    def create_radiobutton(self, frame, text, variable, value, font):
        radio_button = tk.Radiobutton(frame, text=text, variable=variable, value=value, font=font,
                                      bg="#222", fg="white", command=self.update_button_styles, indicatoron=0,
                                      selectcolor="#444", width=18, height=2, relief="flat", bd=0, padx=10, pady=5)
        radio_button.pack(pady=5)  # Use pack to stack the buttons vertically with some padding
        return radio_button

    def update_button_styles(self):
        # Update black agent buttons
        for rb in self.black_radiobuttons:
            if rb.cget('value') == self.black_agent_choice.get():
                rb.config(bg="green", fg="white")  # Highlight selected option
            else:
                rb.config(bg="#222", fg="white")  # Default background

        # Update white agent buttons
        for rb in self.white_radiobuttons:
            if rb.cget('value') == self.white_agent_choice.get():
                rb.config(bg="blue", fg="white")  # Highlight selected option
            else:
                rb.config(bg="#222", fg="white")  # Default background

    def create_shadowed_text(self, x, y, text, font):
        """Create shadowed text on canvas for better readability."""
        # Create shadow text for better contrast
        self.canvas.create_text(x+1, y+1, text=text, font=font, fill="black", anchor="center")  # Shadow
        self.canvas.create_text(x, y, text=text, font=font, fill="white", anchor="center")  # Main text

    def start_game(self):
        """Callback when the Start Game button is clicked."""
        black_agent = AgentFactory.create_agent(self.black_agent_choice.get(), color="black")
        white_agent = AgentFactory.create_agent(self.white_agent_choice.get(), color="white")
        self.root.destroy()  # Close the welcome screen
        self.start_game_callback(black_agent, white_agent)  # Start the game with selected agents


# Run the WelcomeScreen
if __name__ == "__main__":
    root = tk.Tk()
    WelcomeScreen(root, lambda black_agent, white_agent: print("Starting Game!"))
    root.mainloop()
