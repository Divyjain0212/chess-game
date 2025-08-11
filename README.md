# Chess Game

A full-featured chess game developed in Python using the `pygame` library for the graphical user interface. This project includes a comprehensive chess engine that handles all standard rules, special moves, and end-of-game conditions.

---

### ✨ Features

* **Pygame UI**: A clean and interactive graphical interface for playing chess.
* **Complete Game Logic**: The chess engine handles all legal moves, including:
    * Standard piece movements (pawn, rook, knight, bishop, queen, king).
    * **Special Moves**: Castling, En Passant, and Pawn Promotion.
* **Game State Detection**: The engine can detect and display:
    * Check, Checkmate, and Stalemate.
    * Draws by Insufficient Material and the 50-move rule.
* **Interactive Controls**:
    * **Mouse Clicks**: Select and move pieces.
    * **Keyboard Shortcuts**: Press `Z` to undo the last move, and `R` to restart the game.
* **User-Friendly Interface**:
    * Highlights for the selected piece, valid moves, and the last move played.
    * A visual move log displayed on the side.
    * A pawn promotion selection menu.

---

### 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Install the necessary library (`pygame`):**
    ```bash
    pip install pygame
    ```

3.  **Run the game:**
    ```bash
    python main.py
    ```

---

### 🎮 How to Play

1.  **Start**: Run the `main.py` file. A chess board window will appear.
2.  **Select a Piece**: Click on a piece to select it. The valid squares where it can move will be highlighted.
3.  **Make a Move**: Click on a highlighted square to move the piece.
4.  **Undo**: Press the `Z` key on your keyboard to undo the last move.
5.  **Restart**: Press the `R` key to reset the board and start a new game.
6.  **Pawn Promotion**: When a pawn reaches the opposite end of the board, a pop-up window will appear, allowing you to choose a new piece (Queen, Rook, Bishop, or Knight).

---

### 👨‍💻 Credits

This project was created by **Divy Jain**. The core game logic and UI were developed from scratch, following the rules of chess.