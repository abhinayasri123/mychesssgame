import tkinter as tk
from tkinter import messagebox
from tkvideo import tkvideo
import pygame
import chess
import chess.engine

# Setup
MOVE_SOUND = "move.mp3"
BGM_SOUND ="bgm.mp3"
STOCKFISH_PATH = r"C:\\Users\\VIJAY\\Downloads\\stockfish-windows-x86-64-avx2\\stockfish\\stockfish-windows-x86-64-avx2.exe"
LAUNCHER_BG = "bg.,mp4.mp4"
GAME_BG = "bg2.mp4.mp4"

PIECE_SYMBOLS = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚"
}

class ChessApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("♛ Ultimate Chess Battle ♚")
        self.window.attributes("-fullscreen", True)

        pygame.mixer.init()
        try:
            pygame.mixer.music.load(BGM_SOUND)
            pygame.mixer.music.play(-1)
        except:
            print("BGM failed")

        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        except:
            messagebox.showerror("Stockfish Error", "Stockfish engine not found.")
            self.engine = None

        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.username = "Player"
        self.difficulty = 4

        self.init_home()
        self.window.mainloop()

    def init_home(self):
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill="both", expand=True)

        bg_label = tk.Label(self.main_frame)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        tkvideo(LAUNCHER_BG, bg_label, loop=1, size=(1920, 1080)).play()

        tk.Label(self.main_frame, text="♛ Ultimate Chess Battle ♚",
                 font=("Impact", 60), fg="white", bg="black").pack(pady=30)

        input_frame = tk.Frame(self.main_frame, bg="black")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="🧑 Name:", font=("Arial", 18), bg="black", fg="white").grid(row=0, column=0, padx=10)
        self.name_entry = tk.Entry(input_frame, font=("Arial", 18), width=20)
        self.name_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="🎯 Difficulty:", font=("Arial", 18), bg="black", fg="white").grid(row=0, column=2, padx=10)
        self.difficulty_slider = tk.Scale(input_frame, from_=1, to=10, orient=tk.HORIZONTAL, length=200)
        self.difficulty_slider.set(4)
        self.difficulty_slider.grid(row=0, column=3)

        for text, cmd, color in [
            ("▶ Start Game", self.start_game, "#4CAF50"),
            ("❓ Help", lambda: messagebox.showinfo("Help", "Move pieces. Win the game!"), "#2196F3"),
            ("👤 About", lambda: messagebox.showinfo("About", "By Abhinaya Gasi"), "#9C27B0"),
            ("❌ Exit", self.window.destroy, "#f44336")
        ]:
            tk.Button(self.main_frame, text=text, font=("Arial", 18, "bold"),
                      width=20, height=1, bg=color, fg="white", command=cmd).pack(pady=10)

    def start_game(self):
        self.username = self.name_entry.get() or "Player"
        self.difficulty = self.difficulty_slider.get()
        self.main_frame.destroy()
        self.board = chess.Board()
        self.selected_square = None

        self.game_frame = tk.Frame(self.window)
        self.game_frame.pack(fill="both", expand=True)

        bg_label = tk.Label(self.game_frame)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_player = tkvideo(GAME_BG, bg_label, loop=1, size=(1920, 1080))
        self.bg_player.play()

        # Labels & Buttons - Left Side
        self.status_label = tk.Label(self.game_frame, text="Your Turn", font=("Arial", 20, "bold"),
                                     bg="black", fg="white")
        self.status_label.place(x=50, y=30)

        self.score_label = tk.Label(self.game_frame, text=self.get_score_text(), font=("Arial", 16),
                                    bg="black", fg="white")
        self.score_label.place(x=50, y=80)

        buttons = [
            ("🔄 Reset", self.reset_board, "#FFD700"),
            ("🏠 Home", self.back_to_home, "#FF6F61"),
            ("💡 Hint", self.show_hint, "#8BC34A"),
            ("🔥 Best Move", self.show_best_move, "#00BCD4"),
            ("📜 Show Moves", self.show_all_moves, "#9C27B0"),
            ("🔙 Exit", self.window.destroy, "#e91e63")
        ]

        for i, (text, cmd, color) in enumerate(buttons):
            tk.Button(self.game_frame, text=text, command=cmd, font=("Arial", 16),
                      bg=color, width=16).place(x=50, y=140 + i * 60)

        # Chess Board
        self.canvas = tk.Canvas(self.game_frame, width=640, height=640, bg="white", highlightthickness=2)
        self.canvas.place(x=640, y=100)
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 80, row * 80
                x2, y2 = x1 + 80, y1 + 80
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)
                symbol = PIECE_SYMBOLS[piece.symbol()]
                self.canvas.create_text(col * 80 + 40, row * 80 + 40,
                                        text=symbol, font=("Arial", 36, "bold"))

    def on_click(self, event):
        col = event.x // 80
        row = 7 - (event.y // 80)
        square = chess.square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.highlight_moves(square)
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                pygame.mixer.Sound(MOVE_SOUND).play()
                self.selected_square = None
                self.draw_board()
                if self.board.is_game_over():
                    self.handle_game_over()
                else:
                    self.status_label.config(text="AI is thinking...")
                    self.window.after(500, self.make_ai_move)
            else:
                self.selected_square = None
                self.draw_board()

    def highlight_moves(self, square):
        self.draw_board()
        for move in self.board.legal_moves:
            if move.from_square == square:
                r = 7 - chess.square_rank(move.to_square)
                c = chess.square_file(move.to_square)
                self.canvas.create_oval(c * 80 + 30, r * 80 + 30, c * 80 + 50, r * 80 + 50, fill="yellow")

    def make_ai_move(self):
        if self.engine and not self.board.is_game_over():
            move = self.engine.play(self.board, chess.engine.Limit(time=self.difficulty * 0.1)).move
            self.board.push(move)
            pygame.mixer.Sound(MOVE_SOUND).play()
            self.draw_board()
            self.status_label.config(text="Your Turn")

        if self.board.is_game_over():
            self.handle_game_over()

    def handle_game_over(self):
        result = self.board.result()
        if result == "1-0":
            self.wins += 1
            self.show_celebration("🏆 You Win! 🥳")
        elif result == "0-1":
            self.losses += 1
            self.show_celebration("😞 You Lost!")
        else:
            self.draws += 1
            self.show_celebration("🤝 Draw!")
        self.score_label.config(text=self.get_score_text())

    def show_celebration(self, message):
        top = tk.Toplevel(self.window)
        top.attributes("-fullscreen", True)
        top.config(bg="black")
        tk.Label(top, text=message, font=("Arial", 72, "bold"), fg="yellow", bg="black").pack(pady=200)
        tk.Button(top, text="🏠 Back to Home", font=("Arial", 24),
                  command=lambda: [top.destroy(), self.back_to_home()]).pack()

    def get_score_text(self):
        return f"{self.username} | Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}"

    def reset_board(self):
        self.board.reset()
        self.status_label.config(text="Your Turn")
        self.draw_board()

    def show_hint(self):
        if self.engine and not self.board.is_game_over():
            move = self.engine.play(self.board, chess.engine.Limit(time=0.05)).move
            messagebox.showinfo("Hint", f"Try: {chess.square_name(move.from_square)} to {chess.square_name(move.to_square)}")

    def show_best_move(self):
        if self.engine and not self.board.is_game_over():
            move = self.engine.play(self.board, chess.engine.Limit(time=0.1)).move
            self.highlight_move_squares(move)

    def highlight_move_squares(self, move):
        self.draw_board()
        for square in [move.from_square, move.to_square]:
            r = 7 - chess.square_rank(square)
            c = chess.square_file(square)
            self.canvas.create_rectangle(c * 80, r * 80, c * 80 + 80, r * 80 + 80, outline="red", width=3)

    def show_all_moves(self):
        self.draw_board()
        for move in self.board.legal_moves:
            r = 7 - chess.square_rank(move.to_square)
            c = chess.square_file(move.to_square)
            self.canvas.create_oval(c * 80 + 30, r * 80 + 30, c * 80 + 50, r * 80 + 50, fill="green")

    def back_to_home(self):
        if self.engine:
            self.engine.quit()
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.game_frame.destroy()
        self.init_home()

    def show_help(self):
        messagebox.showinfo("Help", "You play as White.\nClick to select a piece.\nClick destination to move.\nTry to checkmate!")

    def show_about(self):
        messagebox.showinfo("About", "Made by Abhinaya Gasi.\nBuilt with Python, Tkinter, Stockfish.")

ChessApp()