import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from tictactoegui import Ui_MainWindow
import random

# The main class for the Tic Tac Toe game.
class TicTacToe(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.board = [""]*9
        self.human_player = "X"
        self.ai_player= "O"

        self.current_player = "X"
        self.ai_player = "O"
        self.is_player_turn = True
        self.is_first_move = True

        self.ai_frames = ["gamemaster0.png", "gamemaster1.png", "gamemaster2.png", "gamemaster3.png"]
        self.current_frame = 0
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_ai_thinking_frame)

        self.buttons = [self.pushButton_1, self.pushButton_2, self.pushButton_3,
                        self.pushButton_4, self.pushButton_5, self.pushButton_6,
                        self.pushButton_7, self.pushButton_8, self.pushButton_9]
        
        for index, button in enumerate(self.buttons):
            button.clicked.connect(lambda _, i=index: self.player_move(i))

        self.new_game_button.clicked.connect(self.new_game)
        self.update_ai_message("Let's play Tic Tac Toe!")
        self.display_default_frame()

    # Start a new game
    def new_game(self):
        self.board = [""]*9
        self.is_first_move = True

        self.current_player = random.choice(["X", "O"])

        if self.current_player == "X":
            self.ai_player = "O"
            self.human_player = "X"
            self.is_player_turn = True
            self.is_first_move = False
            self.update_ai_message("You go first.")

        else:
            self.ai_player = "X"
            self.human_player = "O"
            self.is_player_turn = False
            self.update_ai_message("My turn! I go first!")
            self.start_ai_thinking()

        for button in self.buttons:
            button.setText("")
            button.setEnabled(True)

        self.display_default_frame()

    # Display the default frame of the AI
    def display_default_frame(self):
        # check if the application is frozen. if frozen = True means the application is packaged using PyInstaller
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        pixmap = QPixmap(os.path.join(base_path, self.ai_frames[0]))
        self.ai_label.setPixmap(pixmap)
    
    # Handle the player move
    def player_move(self, index):
        if self.is_player_turn and self.board[index] == "":
            self.board[index] = self.human_player
            self.buttons[index].setText(self.human_player)
            self.disable_buttons()

            if self.check_win(self.current_player):
                self.update_ai_message(f"You win..")
                return
            elif "" not in self.board:
                self.update_ai_message("Game drawn!")
                return
        self.is_player_turn = False

        self.update_ai_message("My turn!!")
        self.start_ai_thinking()

    def start_ai_thinking(self):
        self.current_frame = 1
        self.thinking_timer.start(400)
        QTimer.singleShot(2000, self.ai_move)

    def update_ai_thinking_frame(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        frame_path = os.path.join(base_path, self.ai_frames[self.current_frame])
        pixmap = QPixmap(frame_path)
        if not pixmap.isNull():
            self.ai_label.setPixmap(pixmap)
        self.current_frame = (self.current_frame + 1) % len(self.ai_frames)

    # Method to handle the AI move
    def ai_move(self):
        self.disable_buttons()
        self.thinking_timer.stop()
        self.display_default_frame()

        # Check if the AI can win in the next move
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = self.ai_player
                if self.check_win(self.ai_player):
                    self.finalize_move(i)
                    return
                self.board[i] = ""
        
        # Check if the human player can win in the next move
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = self.human_player
                if self.check_win(self.human_player):
                    self.board[i] = self.ai_player
                    self.finalize_move(i)
                    return
                self.board[i] = ""

        best_move = None

        # If it is the first move, choose a random move
        if self.is_first_move:

            self.is_first_move = False
            move_scores = []
            for i in range(9):
                if self.board[i] =="":
                    self.board[i] = self.ai_player
                    score = self.minimax(0, False, -float("inf"), float("inf"))
                    self.board[i] = ""
                    move_scores.append((score, i))
            
            top_moves = sorted(move_scores, reverse = True, key = lambda x: x[0])[:5]
            best_move = random.choice([move for score, move in top_moves])
        else:

            # otherwise, use the minimax algorithm to find the best move
            best_score = -float("inf")

            for i in range(9):
                if self.board[i] =="":
                    self.board[i] = self.ai_player
                    score = self.minimax(0, False, -float("inf"), float("inf"))
                    self.board[i] = ""
                    if score > best_score:
                        best_score = score
                        best_move = i
            
        if best_move is not None:
            self.finalize_move(best_move)
    
    def finalize_move(self, best_move):
        self.board[best_move] = self.ai_player
        self.buttons[best_move].setText(self.ai_player)
        self.buttons[best_move].setEnabled(False)

        if self.check_win(self.ai_player):
            self.update_ai_message("I win! Better luck next time!")
            return
        
        if "" not in self.board:
            self.update_ai_message("It's a draw...")
            return
        
        self.current_player = "X"
        self.is_player_turn = True
        self.update_ai_message("Your turn! Hurry up!!")
        self.enable_buttons()

    def disable_buttons(self):
        for button in self.buttons:
            button.setEnabled(False)

    def enable_buttons(self):
        for index, button in enumerate(self.buttons):
            if self.board[index] == "":
                button.setEnabled(True)

    # Minimax algorithm with alpha-beta pruning
    # this method returns the best score for the current player. it takes in the depth of the search tree, a boolean value to check if it is maximizing
    # or minimizing player, and alpha and beta values for pruning
    def minimax(self, depth, is_maximizing, alpha, beta):
        # If the ai player wins, return a score of 10 - depth. The depth is subtracted to prioritize the moves that lead to a win in fewer moves
        # This is because the minimax algorithm assumes that both players play optimally.
        if self.check_win(self.ai_player):
            return 10 - depth
        # if the human player wins, return a score of -10 + depth. The depth is added to prioritize the moves that lead to a win in fewer moves
        elif self.check_win(self.human_player):
            return depth - 10
        # if the game is drawn, return 0. This is a neutral score
        elif "" not in self.board:
            return 0
        
        # if the current player is maximizing
        if is_maximizing:
            best_score = -float("inf")

        # check all possible moves and calculate the best score
            for i in range(9):
                if self.board[i] == "":
                    self.board[i] = self.ai_player
                    score = self.minimax(depth+1, False, alpha, beta)
                    self.board[i] = ""
                    best_score = max(score, best_score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break
            return best_score
        else:
            best_score = float("inf")
            for i in range(9):
                if self.board[i] == "":
                    self.board[i] = self.human_player
                    score = self.minimax(depth+1, True, alpha, beta)
                    self.board[i] = ""
                    best_score = min(score, best_score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break
            return best_score

    # check if a player has won
    def check_win(self, player):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

        for combination in winning_combinations:
            if all(self.board[i] == player for i in combination):
                return True
        return False
        
    def update_ai_message(self, message):
        self.ai_text_label.setText(message)

    def show_message(self, message):
        self.update_ai_message(message)
        QTimer.singleShot(2000, self.new_game)

# load the QSS stylesheet
def load_stylesheet():
    # check if the application is frozen
    if getattr(sys, 'frozen', False):
        # if it is, get the base path
        base_path = sys._MEIPASS
    else:
        # if it is not, get the base path of the script
        base_path = os.path.dirname(os.path.abspath(__file__))

    # load the QSS file
    stylesheet_path = os.path.join(base_path, 'style.qss')
    with open(stylesheet_path, 'r') as file:
        return file.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    stylesheet = load_stylesheet()
    app.setStyleSheet(stylesheet)
    window = TicTacToe()
    window.show()
    sys.exit(app.exec_())