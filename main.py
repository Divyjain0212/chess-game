import pygame
import os

pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
ROWS = 8
COLS = 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (0, 255, 0)

# Load piece images
IMAGES = {}
PIECES = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk',
          'bp', 'br', 'bn', 'bb', 'bq', 'bk']


def load_images():
    for piece in PIECES:
        path = os.path.join('images', f'{piece}.png')
        IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE))


def create_board():
    return [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["--"] * 8,
        ["wp"] * 8,
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
    ]


def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(win, color, (col*SQUARE_SIZE,
                             row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(win, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "--":
                win.blit(IMAGES[piece], (col*SQUARE_SIZE, row*SQUARE_SIZE))


def is_valid_move(piece, start, end, board):
    sr, sc = start
    er, ec = end
    dr, dc = er - sr, ec - sc
    target = board[er][ec]

    if piece == "--":
        return False

    color = piece[0]
    p_type = piece[1]

    if target != "--" and target[0] == color:
        return False  # Can't capture own piece

    # PAWN
    if p_type == "p":
        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1
        # Move forward
        if dc == 0:
            if dr == direction and board[er][ec] == "--":
                return True
            if sr == start_row and dr == 2 * direction and board[er][ec] == "--" and board[sr + direction][sc] == "--":
                return True
        # Capture
        if abs(dc) == 1 and dr == direction and board[er][ec] != "--" and board[er][ec][0] != color:
            return True
        return False

    # ROOK
    elif p_type == "r":
        if sr == er:
            step = 1 if ec > sc else -1
            for c in range(sc + step, ec, step):
                if board[sr][c] != "--":
                    return False
            return True
        elif sc == ec:
            step = 1 if er > sr else -1
            for r in range(sr + step, er, step):
                if board[r][sc] != "--":
                    return False
            return True
        return False

    # KNIGHT
    elif p_type == "n":
        return (abs(dr), abs(dc)) in [(2, 1), (1, 2)]

    # BISHOP
    elif p_type == "b":
        if abs(dr) == abs(dc):
            step_r = 1 if er > sr else -1
            step_c = 1 if ec > sc else -1
            for i in range(1, abs(dr)):
                if board[sr + i * step_r][sc + i * step_c] != "--":
                    return False
            return True
        return False

    # QUEEN
    elif p_type == "q":
        return is_valid_move(color + "r", start, end, board) or is_valid_move(color + "b", start, end, board)

    # KING
    elif p_type == "k":
        return max(abs(dr), abs(dc)) == 1

    return False


def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess by Divy")
    clock = pygame.time.Clock()

    board = create_board()
    load_images()

    selected = None
    turn = 'w'  # w for white, b for black

    running = True
    while running:
        clock.tick(60)
        draw_board(win)
        draw_pieces(win, board)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                clicked = (row, col)

                if selected:
                    piece = board[selected[0]][selected[1]]
                    if is_valid_move(piece, selected, clicked, board):
                        # Move the piece
                        board[clicked[0]][clicked[1]] = piece
                        board[selected[0]][selected[1]] = "--"
                        turn = 'b' if turn == 'w' else 'w'
                    selected = None
                else:
                    piece = board[row][col]
                    if piece != "--" and piece[0] == turn:
                        selected = (row, col)

    pygame.quit()


if __name__ == "__main__":
    main()
