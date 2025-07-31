import pygame
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
ROWS = 8
COLS = 8
SQUARE_SIZE = WIDTH // COLS


# Colors
WHITE = (245, 245, 245)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# Load images
IMAGES = {}
PIECES = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk',
          'bp', 'br', 'bn', 'bb', 'bq', 'bk']

def load_images():
    for piece in PIECES:
        path = os.path.join('Mini-game/images', f'{piece}.png')
        IMAGES[piece] = pygame.transform.scale(pygame.image.load(path), (SQUARE_SIZE, SQUARE_SIZE))

# Draw board
def draw_board(win):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 != 0:
                pygame.draw.rect(win, GRAY, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw pieces
def draw_pieces(win, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "--":
                win.blit(IMAGES[piece], (col*SQUARE_SIZE, row*SQUARE_SIZE))

# Initialize board
def create_board():
    return [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp"]*8,
        ["--"]*8,
        ["--"]*8,
        ["--"]*8,
        ["--"]*8,
        ["wp"]*8,
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
    ]

# Main
def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess by Divy")
    clock = pygame.time.Clock()
    board = create_board()
    load_images()

    selected = None  # (row, col)

    run = True
    while run:
        clock.tick(60)
        draw_board(win)
        draw_pieces(win, board)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                if selected:
                    # Move piece (no validation yet)
                    board[row][col] = board[selected[0]][selected[1]]
                    board[selected[0]][selected[1]] = "--"
                    selected = None
                else:
                    if board[row][col] != "--":
                        selected = (row, col)

    pygame.quit()

if __name__ == "__main__":
    main()
