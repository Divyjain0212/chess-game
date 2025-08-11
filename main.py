# main.py
"""
Pygame UI for the chess engine.
- Click squares to move
- Undo: Z, Restart: R
- Pawn promotion choice popup (Q,R,B,N)
- Highlights: selected square, valid moves, last move
- Move log on the right and status in window caption (Check / Checkmate / Stalemate / Draw)
"""

import pygame
import sys
from chess_engine import GameState, Move

# UI constants
HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MOVE_LOG_PANEL_WIDTH = 300
WIDTH = HEIGHT + MOVE_LOG_PANEL_WIDTH
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Chess")
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    load_images()
    running = True
    sq_selected = ()  # (r, c)
    player_clicks = []
    last_move = None

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if location[0] < HEIGHT:
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        for m in valid_moves:
                            if m == move:
                                move = m
                                break
                        if move in valid_moves:
                            gs.make_move(move)
                            last_move = move
                            move_made = True
                            sq_selected = ()
                            player_clicks = []

                            if gs.pawn_promotion:
                                color, r_prom, c_prom = gs.pawn_promotion
                                promoted_piece_code = choose_promotion(screen, color)
                                gs.board[r_prom][c_prom] = promoted_piece_code
                                gs.move_log[-1].piece_moved = promoted_piece_code # Update the move object
                                gs.pawn_promotion = None
                        else:
                            player_clicks = [sq_selected]
                else:
                    pass
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
                    last_move = None
                elif e.key == pygame.K_r:
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    move_made = False
                    sq_selected = ()
                    player_clicks = []
                    last_move = None

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, valid_moves, sq_selected, last_move)
        if gs.checkmate:
            pygame.display.set_caption("Checkmate! Game Over")
        elif gs.stalemate:
            pygame.display.set_caption("Stalemate! Draw")
        elif gs.check:
            pygame.display.set_caption("Check!")
        elif gs.insufficient_material() or gs.halfmove_clock >= 100:
            pygame.display.set_caption("Draw (Insufficient material / 50-move)")
        else:
            pygame.display.set_caption("Chess")

        clock.tick(MAX_FPS)
        pygame.display.flip()

def draw_game_state(screen, gs, valid_moves, sq_selected, last_move):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected, last_move)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs)

def draw_board(screen):
    colors = [pygame.Color("burlywood1"), pygame.Color("saddlebrown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlight_squares(screen, gs, valid_moves, sq_selected, last_move):
    s = pygame.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(120)
    if last_move:
        s.fill(pygame.Color("yellow"))
        screen.blit(s, (last_move.start_col * SQ_SIZE, last_move.start_row * SQ_SIZE))
        screen.blit(s, (last_move.end_col * SQ_SIZE, last_move.end_row * SQ_SIZE))
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c] != "--" and ((gs.board[r][c][0] == 'w') == gs.white_to_move):
            s.fill(pygame.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(pygame.Color("green"))
            for mv in valid_moves:
                if mv.start_row == r and mv.start_col == c:
                    screen.blit(s, (mv.end_col * SQ_SIZE, mv.end_row * SQ_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_move_log(screen, gs):
    font = pygame.font.SysFont("Arial", 16)
    move_log_surface = pygame.Surface((MOVE_LOG_PANEL_WIDTH, HEIGHT))
    move_log_surface.fill(pygame.Color("lightgray"))
    move_texts = []
    for i in range(0, len(gs.move_log), 2):
        move_string = str(i//2 + 1) + ". "
        move_string += gs.move_log[i].get_chess_notation() + " "
        if i + 1 < len(gs.move_log):
            move_string += gs.move_log[i + 1].get_chess_notation()
        move_texts.append(move_string)
    padding = 5
    text_y = padding
    for line in move_texts:
        text_object = font.render(line, True, pygame.Color("black"))
        move_log_surface.blit(text_object, (padding, text_y))
        text_y += 20
    screen.blit(move_log_surface, (HEIGHT, 0))

def choose_promotion(screen, color):
    pieces = [color + p for p in ['q', 'r', 'b', 'n']]
    overlay = pygame.Surface((HEIGHT, SQ_SIZE + 20))
    overlay.fill(pygame.Color("darkgray"))
    overlay.set_alpha(230)
    start_x = (HEIGHT - (SQ_SIZE * 4 + 30)) // 2
    start_y = (HEIGHT // 2) - (SQ_SIZE // 2)
    option_rects = []
    screen.blit(overlay, (0, start_y - 10))
    for i, p in enumerate(pieces):
        rect = pygame.Rect(start_x + i * (SQ_SIZE + 10), start_y, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, pygame.Color("white"), rect)
        screen.blit(IMAGES[p], rect)
        option_rects.append((rect, p))
    pygame.display.flip()
    selecting = True
    while selecting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for rect, p in option_rects:
                    if rect.collidepoint(pos):
                        return p
        pygame.time.wait(50)

if __name__ == "__main__":
    main()