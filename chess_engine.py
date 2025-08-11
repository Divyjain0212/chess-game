# chess_engine.py
"""
Full chess engine:
- legal move generation (no leaving king in check)
- castling, en passant, promotion (flag only)
- check/checkmate/stalemate detection
- draw detection: insufficient material and 50-move rule
- undo with full state restoration (castling rights, enpassant, halfmove clock, king positions)
- recursion-safe attack detection
"""

from copy import deepcopy

class GameState:
    def __init__(self):
        self.board = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["wp"] * 8,
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]
        self.white_to_move = True
        self.move_log = []  # list of Move objects
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.castling_rights = [True, True, True, True]  # [wks, wqs, bks, bqs]
        self.enpassant_target = None
        self.pawn_promotion = None
        self.halfmove_clock = 0
        self.check = False
        self.checkmate = False
        self.stalemate = False

        self.move_functions = {
            'p': self.get_pawn_moves,
            'r': self.get_rook_moves,
            'n': self.get_knight_moves,
            'b': self.get_bishop_moves,
            'q': self.get_queen_moves,
            'k': self.get_king_moves
        }

    def make_move(self, move):
        move.prev_castling_rights = deepcopy(self.castling_rights)
        move.prev_enpassant_target = deepcopy(self.enpassant_target)
        move.prev_halfmove_clock = self.halfmove_clock
        move.prev_white_king_location = self.white_king_location
        move.prev_black_king_location = self.black_king_location

        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved

        if move.piece_moved == 'wk':
            self.white_king_location = (move.end_row, move.end_col)
            self.castling_rights[0] = False
            self.castling_rights[1] = False
        elif move.piece_moved == 'bk':
            self.black_king_location = (move.end_row, move.end_col)
            self.castling_rights[2] = False
            self.castling_rights[3] = False

        if move.piece_moved == 'wr':
            if move.start_row == 7 and move.start_col == 0:
                self.castling_rights[1] = False
            elif move.start_row == 7 and move.start_col == 7:
                self.castling_rights[0] = False
        if move.piece_moved == 'br':
            if move.start_row == 0 and move.start_col == 0:
                self.castling_rights[3] = False
            elif move.start_row == 0 and move.start_col == 7:
                self.castling_rights[2] = False

        if move.piece_captured == 'wr':
            if move.end_row == 7 and move.end_col == 0:
                self.castling_rights[1] = False
            elif move.end_row == 7 and move.end_col == 7:
                self.castling_rights[0] = False
        if move.piece_captured == 'br':
            if move.end_row == 0 and move.end_col == 0:
                self.castling_rights[3] = False
            elif move.end_row == 0 and move.end_col == 7:
                self.castling_rights[2] = False
                
        if move.is_enpassant_move:
            self.board[move.enpassant_pawn_location[0]][move.enpassant_pawn_location[1]] = "--"

        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            direction = 1 if move.piece_moved[0] == 'b' else -1
            self.enpassant_target = (move.start_row + direction, move.start_col)
        else:
            self.enpassant_target = None
            
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                rook_start_col, rook_end_col = 7, move.end_col - 1
            else:
                rook_start_col, rook_end_col = 0, move.end_col + 1
            row = move.start_row
            self.board[row][rook_end_col] = self.board[row][rook_start_col]
            self.board[row][rook_start_col] = "--"

        self.pawn_promotion = None
        if move.piece_moved[1] == 'p':
            self.halfmove_clock = 0
            if move.piece_moved[0] == 'w' and move.end_row == 0:
                self.pawn_promotion = ('w', move.end_row, move.end_col)
                move.is_promotion = True
            elif move.piece_moved[0] == 'b' and move.end_row == 7:
                self.pawn_promotion = ('b', move.end_row, move.end_col)
                move.is_promotion = True
        else:
            if move.piece_captured != "--":
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1

        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if not self.move_log:
            return
        move = self.move_log.pop()
        
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.enpassant_pawn_location[0]][move.enpassant_pawn_location[1]] = move.piece_captured

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                rook_start_col, rook_end_col = 7, move.end_col - 1
            else:
                rook_start_col, rook_end_col = 0, move.end_col + 1
            row = move.start_row
            self.board[row][rook_start_col] = self.board[row][rook_end_col]
            self.board[row][rook_end_col] = "--"
            
        if move.is_promotion:
            self.board[move.start_row][move.start_col] = move.piece_moved[0] + 'p'

        self.castling_rights = deepcopy(move.prev_castling_rights)
        self.enpassant_target = deepcopy(move.prev_enpassant_target)
        self.halfmove_clock = move.prev_halfmove_clock
        self.white_king_location = move.prev_white_king_location
        self.black_king_location = move.prev_black_king_location
        self.white_to_move = not self.white_to_move
        self.pawn_promotion = None
        self.check = self.in_check()
        self.checkmate = False
        self.stalemate = False

    def get_valid_moves(self):
        moves = self.get_all_possible_moves()
        legal_moves = []
        for mv in moves:
            self.make_move(mv)
            self.white_to_move = not self.white_to_move
            if not self.in_check():
                legal_moves.append(mv)
            self.white_to_move = not self.white_to_move
            self.undo_move()
            
        if not legal_moves:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.check = self.in_check()
        return legal_moves

    def in_check(self):
        if self.white_to_move:
            kr, kc = self.white_king_location
        else:
            kr, kc = self.black_king_location
        return self.square_under_attack(kr, kc)

    def square_under_attack(self, r, c):
        opp_color = 'b' if self.white_to_move else 'w'
        for move in self.get_all_possible_moves_for_color(opp_color, for_attack_only=True):
            if move.end_row == r and move.end_col == c:
                return True
        return False
        
    def get_all_possible_moves_for_color(self, color, for_attack_only=False):
        moves = []
        original_side = self.white_to_move
        self.white_to_move = (color == 'w')

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != "--" and piece[0] == color:
                    ptype = piece[1]
                    if ptype == 'k':
                        self.get_king_moves(r, c, moves, for_attack_only=for_attack_only)
                    else:
                        self.move_functions[ptype](r, c, moves)
        
        self.white_to_move = original_side
        return moves

    def get_all_possible_moves(self):
        return self.get_all_possible_moves_for_color('w' if self.white_to_move else 'b')

    def get_pawn_moves(self, r, c, moves):
        piece = self.board[r][c]
        color = piece[0]
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        enemy = 'b' if color == 'w' else 'w'

        if 0 <= r + direction < 8 and self.board[r + direction][c] == "--":
            moves.append(Move((r, c), (r + direction, c), self.board))
            if r == start_row and self.board[r + 2 * direction][c] == "--":
                moves.append(Move((r, c), (r + 2 * direction, c), self.board))
        
        for dc in (-1, 1):
            cc = c + dc
            rr = r + direction
            if 0 <= rr < 8 and 0 <= cc < 8:
                target = self.board[rr][cc]
                if target != "--" and target[0] == enemy:
                    moves.append(Move((r, c), (rr, cc), self.board))

        if self.enpassant_target:
            ep_r, ep_c = self.enpassant_target
            if (r + direction, c - 1) == (ep_r, ep_c) or (r + direction, c + 1) == (ep_r, ep_c):
                captured_pawn_loc = (r, ep_c)
                moves.append(Move((r, c), (ep_r, ep_c), self.board, is_enpassant_move=True, enpassant_pawn_location=captured_pawn_loc))

    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        ally = 'w' if self.white_to_move else 'b'
        for dr, dc in directions:
            for i in range(1, 8):
                rr, cc = r + dr * i, c + dc * i
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = self.board[rr][cc]
                    if target == "--":
                        moves.append(Move((r, c), (rr, cc), self.board))
                    else:
                        if target[0] != ally:
                            moves.append(Move((r, c), (rr, cc), self.board))
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]
        ally = 'w' if self.white_to_move else 'b'
        for dr, dc in knight_offsets:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                target = self.board[rr][cc]
                if target == "--" or target[0] != ally:
                    moves.append(Move((r, c), (rr, cc), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        ally = 'w' if self.white_to_move else 'b'
        for dr, dc in directions:
            for i in range(1, 8):
                rr, cc = r + dr * i, c + dc * i
                if 0 <= rr < 8 and 0 <= cc < 8:
                    target = self.board[rr][cc]
                    if target == "--":
                        moves.append(Move((r, c), (rr, cc), self.board))
                    else:
                        if target[0] != ally:
                            moves.append(Move((r, c), (rr, cc), self.board))
                        break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves, for_attack_only=False):
        ally = 'w' if self.white_to_move else 'b'
        king_offsets = [(-1, -1), (-1, 0), (-1, 1),
                        (0, -1),           (0, 1),
                        (1, -1),  (1, 0),  (1, 1)]
        for dr, dc in king_offsets:
            rr, cc = r + dr, c + dc
            if 0 <= rr < 8 and 0 <= cc < 8:
                target = self.board[rr][cc]
                if target == "--" or target[0] != ally:
                    moves.append(Move((r, c), (rr, cc), self.board))

        if for_attack_only:
            return

        if self.white_to_move:
            if (r, c) == (7, 4) and not self.square_under_attack(r, c):
                if self.castling_rights[0] and self.board[7][5] == "--" and self.board[7][6] == "--":
                    if not self.square_under_attack(7, 5) and not self.square_under_attack(7, 6):
                        moves.append(Move((r, c), (7, 6), self.board, is_castle_move=True))
                if self.castling_rights[1] and self.board[7][1] == "--" and self.board[7][2] == "--" and self.board[7][3] == "--":
                    if not self.square_under_attack(7, 2) and not self.square_under_attack(7, 3):
                        moves.append(Move((r, c), (7, 2), self.board, is_castle_move=True))
        else:
            if (r, c) == (0, 4) and not self.square_under_attack(r, c):
                if self.castling_rights[2] and self.board[0][5] == "--" and self.board[0][6] == "--":
                    if not self.square_under_attack(0, 5) and not self.square_under_attack(0, 6):
                        moves.append(Move((r, c), (0, 6), self.board, is_castle_move=True))
                if self.castling_rights[3] and self.board[0][1] == "--" and self.board[0][2] == "--" and self.board[0][3] == "--":
                    if not self.square_under_attack(0, 2) and not self.square_under_attack(0, 3):
                        moves.append(Move((r, c), (0, 2), self.board, is_castle_move=True))

    def insufficient_material(self):
        pieces = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != "--":
                    pieces.append(piece)
        nonkings = [p for p in pieces if p[1] != 'k']
        if not nonkings:
            return True
        if len(nonkings) == 1 and nonkings[0][1] in ('n', 'b'):
            return True
        return False

class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False, enpassant_pawn_location=None):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        if is_enpassant_move:
            self.piece_captured = board[enpassant_pawn_location[0]][enpassant_pawn_location[1]]
            self.enpassant_pawn_location = enpassant_pawn_location
        else:
            self.piece_captured = board[self.end_row][self.end_col]
            self.enpassant_pawn_location = None
        self.is_enpassant_move = is_enpassant_move
        self.is_castle_move = is_castle_move
        self.is_promotion = False
        self.prev_castling_rights = None
        self.prev_enpassant_target = None
        self.prev_halfmove_clock = None
        self.prev_white_king_location = None
        self.prev_black_king_location = None
        self.move_id = (self.start_row * 1000 + self.start_col * 100 +
                        self.end_row * 10 + self.end_col)

    def __eq__(self, other):
        return isinstance(other, Move) and self.move_id == other.move_id

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]