import random

import pygame

pygame.mixer.init()

from copy import deepcopy

from src.pieces import *

class Chessboard:

    def __init__(self, game):

        self.game = game
        self.win = self.game.win

        self.move_sound = pygame.mixer.Sound("./res/sounds/move.mp3")

        self.take_sound = pygame.mixer.Sound("./res/sounds/take.mp3")

        self.pieces = Pieces()

        self.BOARD = [
            ["R", "H", "B", "Q", "K", "B", "H", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0"],
            ["0", "0", "0", "0", "0", "0", "0", "0"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "h", "b", "q", "k", "b", "h", "r"],
        ]


        self.turn = 1

        # - 1 White, 2 Black
        self.king_pos = [(4, 7), (4, 0)]
        self.KingsHasMoved = [False, False]

        # - 1, King, 2 Queen
        self.RooksHasMoved = [False, False, False, False]
        self.EnPassantSquere = []

        self.all_pseudo = self.get_moves(self.BOARD)
        self.all_legal_for_piece = []

        self.move = []
        self.piece_moved = []
        self.highlight_moved_piece = [(-500, -500), (-500, -500)]


        self.highlighter = pygame.image.load("./res/other/empty.png")
        self.piecehighlighter = pygame.image.load("./res/other/!empty.png")
        self.green_tile = pygame.image.load("./res/other/moved.png")

        self.drag = False

        self.setup()

    # _ Gui Fucntions

    def setup(self):

        path = "./res/pieces/"

        # Black
        self.BP = pygame.image.load(path + "BP.png")
        self.BR = pygame.image.load(path + "BR.png")
        self.BH = pygame.image.load(path + "BH.png")
        self.BB = pygame.image.load(path + "BB.png")
        self.BQ = pygame.image.load(path + "BQ.png")
        self.BK = pygame.image.load(path + "BK.png")

        # White
        self.WP = pygame.image.load(path + "WP.png")
        self.WR = pygame.image.load(path + "WR.png")
        self.WH = pygame.image.load(path + "WH.png")
        self.WB = pygame.image.load(path + "WB.png")
        self.WQ = pygame.image.load(path + "WQ.png")
        self.WK = pygame.image.load(path + "WK.png")

        # Dictionary used so the "DrawPieces" function knows what piece to draw
        self.PieceDict = {
            "R": self.BR, "H": self.BH, "B": self.BB, "Q": self.BQ, "K": self.BK, "P": self.BP,
            "r": self.WR, "h": self.WH, "b": self.WB, "q": self.WQ, "k": self.WK, "p": self.WP,
            "0": pygame.Surface([0, 0], pygame.SRCALPHA, 32).convert_alpha()
        }

        self.Black = (108,140,76)
        self.White = (228,228,200)

        self.Black = (164,128,95)
        self.White = (236,218,185)
        
        
    def draw_board(self):

        # Creates the squares of the chessboard

        for COL in range(0, 8 + 1):
            for ROW in range(0, 8 + 1):
                if (ROW + COL) % 2 == 0:
                    pygame.draw.rect(self.win, self.White, (100 * ROW, 100 * COL, 100, 100))
                else:
                    pygame.draw.rect(self.win, self.Black, (100 * ROW, 100 * COL, 100, 100))

    def draw_pieces(self):

        # Draws the pieces based on current board state

        for COL in range(0, 8):
            for ROW in range(0, 8):
                if self.BOARD[COL][ROW] != "0":
                    self.win.blit(self.PieceDict[self.BOARD[COL][ROW]], (100 * ROW, 100 * COL))

    def highlight_squares(self):

        # Higlights all legal squares a selected piece can go

        for move in self.all_legal_for_piece:
            if self.BOARD[move[1]][move[0]] != "0":
                self.win.blit(self.piecehighlighter, (move[0] * 100, move[1] * 100))
            else:
                self.win.blit(self.highlighter, (move[0] * 100, move[1] * 100))

    def highlight_move(self):

        # highlights the recent move made

        self.win.blit(self.green_tile, (self.highlight_moved_piece[0][0] * 100,
                                        self.highlight_moved_piece[0][1] * 100))
        self.win.blit(self.green_tile, (self.highlight_moved_piece[1][0] * 100,
                                        self.highlight_moved_piece[1][1] * 100))

    def dragger(self):

        if self.drag:
            pos = pygame.mouse.get_pos()
            mot = pygame.mouse.get_pressed()
            if mot[0]:
                move = self.move[0]
                piece = self.BOARD[move[1]][move[0]]

                if (self.move[0][0] + 1 + self.move[0][1] + 1) % 2 == 0:
                    pygame.draw.rect(self.win, self.White, (100 * move[0], 100 * move[1], 100, 100))
                else:
                    pygame.draw.rect(self.win, self.Black, (100 * move[0], 100 * move[1], 100, 100))
                self.win.blit(self.PieceDict[piece], (pos[0] - 50, pos[1] - 50))

            elif not mot[0]:

                self.move.append(self.mouse_pos())
                self.drag = False

                self.handle_movement()
                self.draw_board()
                self.draw_pieces()

    def mouse_pos(self):

        # Returns a coordinate for the mouse position

        pos = pygame.mouse.get_pos()
        col = pos[0] // 100
        row = pos[1] // 100

        return (col, row)

    def move_pieces(self, board, FromTile, ToTile, pront=False):

        # Changes the board list so that the position changes

        board[ToTile[1]][ToTile[0]] = board[FromTile[1]][FromTile[0]]
        board[FromTile[1]][FromTile[0]] = "0"

        return board

    # _ Logic Functions

    def get_moves(self, board):

        # Gets all pseudo-legal moves for each piece on the board for white or black
        # Outputs a list like this [ ( piece position, (all the positions the piece can move to) ) ]

        moves = []

        row_count = -1

        for r in board:
            row_count += 1
            col_count = -1

            for c in r:
                col_count += 1

                if (c.isupper() and self.turn == 1) or (c.islower() and self.turn == -1):
                    continue

                elif c == "0":
                    continue

                moves.append(((col_count, row_count), self.pieces.generate_legal_moves(
                    col_count,
                    row_count,
                    self.turn,
                    c, self.BOARD,
                    self.EnPassantSquere,
                    self.KingsHasMoved,
                    self.RooksHasMoved)))

        return moves
    
    def is_draw(self, board):

        for r in board:
            for c in r:

                if c not in  ("0", "k", "K"):
                    print(c)
                    return True
                
        return False

    def check_for_mate_or_stale(self):

        # Will check for a end condition, either check- or stalemate
        # Go's through all pseudo-legal moves and deletes moves that makes the player go in check

        if not self.is_draw(self.BOARD):
            #Checks if there are only kings on the baord
            
            pygame.display.set_caption("Draw")
            self.game_over = True
            return True
        

        all_legal = []

        self.all_pseudo = self.get_moves(self.BOARD)

        for node in self.all_pseudo:
            fake_piece = self.BOARD[node[0][1]][node[0][0]]

            all_legal.append(self.delete_illegal_moves(
                fake_piece, node[1], node[0]
            ))

        for m in all_legal:
            if m != []:
                return False
            

        if self.is_attacked((self.king_pos[0] if self.turn == 1 else self.king_pos[1]), self.BOARD):

            pygame.display.set_caption("Chessmate: " + ("White wins!" if self.turn == -1 else "Black wins!"))

        else:

            pygame.display.set_caption("Moldmate: its a draw")

        self.game_over = True

    def after_castle(self, piece, fromTile, toTile, board):
        # Checks if the last move was a castle, if it was then it will change the board

        if piece == "k":
            if fromTile[0] + 2 == toTile[0]:
                board[7][7] = "0"
                board[7][5] = "r"
            elif fromTile[0] - 2 == toTile[0]:
                board[7][0] = "0"
                board[7][3] = "r"
        if piece == "K":
            if fromTile[0] + 2 == toTile[0]:
                board[0][7] = "0"
                board[0][5] = "R"
            elif fromTile[0] - 2 == toTile[0]:
                board[0][0] = "0"
                board[0][3] = "R"

        return board

    def after_enpassant(self, piece, tomove, enpassant):
        # Removes the pawn in a case of enpassant

        if tomove == enpassant:
            if piece == "p":
                self.BOARD[enpassant[1] + 1][enpassant[0]] = "0"
            if piece == "P":
                self.BOARD[enpassant[1] - 1][enpassant[0]] = "0"

        return self.BOARD

    def get_enpassant_square(self, piece, fromTile, toTile):

        # Return the square where a pawn can attack if there is a enpassant

        if piece == "p":
            if toTile[1] == fromTile[1] - 2:
                return (toTile[0], toTile[1] + 1)
        if piece == "P":
            if toTile[1] == fromTile[1] + 2:
                return (toTile[0], toTile[1] - 1)

    def is_attacked(self, square, board):

        # Takes in a position and checks if the piece is attacked.
        # This is used to check if the king is in check.

        list_of_pieces = ["h", "r", "b", "q", "p", "k"]

        for i in list_of_pieces:

            # Generates all the positions i has to be in in order for it to attack

            checks = self.pieces.generate_legal_moves(square[0], square[1], self.turn, i, board,
                                                      self.EnPassantSquere, self.KingsHasMoved, self.RooksHasMoved)

            for n in checks:

                # Checks if i (the piece) is in the positions they have to

                if board[n[1]][n[0]] == (i.upper() if self.turn == 1 else i):
                    return True

    def delete_illegal_moves(self, piece, moves, from_location):

        # Deletes all illeagal moves form a pseudo-legal moves list

        new_moves = deepcopy(moves)

        # Goas through all the moves in the list given

        for m in moves:

            if piece in ("k", "K"):

                king_pos = m

                # Here we remove castle rights if any file in the king path is attacked

                # Kingside castle for both black and white

                if (from_location[0] + 2, from_location[1]) == m and self.KingsHasMoved[
                    (0 if piece == "k" else 1)] == False:

                    if self.is_attacked(self.king_pos[(0 if piece == "k" else 1)], self.BOARD):
                        new_moves.remove(m)

                    else:

                        for p in range(4, 6 + 1):

                            if self.is_attacked((p, (7 if piece == "k" else 0)), self.BOARD):
                                new_moves.remove(m)
                                break

                # Queenside castle for both black and white

                elif (from_location[0] - 2, from_location[1]) == m and self.KingsHasMoved[
                    (0 if piece == "k" else 1)] == False:

                    if self.is_attacked(self.king_pos[(0 if piece == "k" else 1)], self.BOARD):
                        new_moves.remove(m)

                    else:

                        for p in range(2, 4 + 1):

                            if self.is_attacked((p, (7 if piece == "k" else 0)), self.BOARD):
                                new_moves.remove(m)
                                break

            else:

                king_pos = (self.king_pos[0] if self.turn == 1 else self.king_pos[1])

            new_board = deepcopy(self.BOARD)
            new_board = self.move_pieces(new_board, from_location, m, True)

            if m == self.EnPassantSquere:
                # If the move a player can go is a enpassant, it removes the pawn killed from the board it will check  if the king is attacked in.
                # This prevents being able to break a pin with enpassant

                new_board[((self.EnPassantSquere[1] + 1) if self.turn == 1 else (self.EnPassantSquere[1] - 1))][
                    self.EnPassantSquere[0]] = "0"

            if self.is_attacked(king_pos, new_board) == True:
                # Checks if the board copy will result in the king being in check, if that is the result, the move will be removed from legal moves

                new_moves.remove(m)

        return new_moves

    def promote(self):

        hasPicked = False
        pygame.display.set_caption("Q: for Queen, H: for Horse, R: for Rock, B: for Bishop")

        while hasPicked == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        return "q" if self.turn == 1 else "Q"
                    if event.key == pygame.K_h:
                        return "h" if self.turn == 1 else "H"
                    if event.key == pygame.K_r:
                        return "r" if self.turn == 1 else "R"
                    if event.key == pygame.K_b:
                        return "b" if self.turn == 1 else "B"

    def handle_movement(self):

        # Handles movement and calls functions for generating legal moves, its also responsable for reacting to castle en enpassant moves

        if len(self.move) == 0:
            self.move.append(self.mouse_pos())

        if len(self.move) == 1:

            move = self.move[0]
            self.piece_moved = self.BOARD[move[1]][move[0]]

            for node in self.all_pseudo:

                # Checks all pseudo-legal moves and deletes the one that are illegal

                if node[0] == move:
                    self.all_legal_for_piece = node[1]

                    self.all_legal_for_piece = self.delete_illegal_moves(self.piece_moved, self.all_legal_for_piece,
                                                                         move)

            self.drag = True

        if len(self.move) == 2:

            if self.move[1] in self.all_legal_for_piece:

                self.BOARD = self.move_pieces(self.BOARD, self.move[0], self.move[1])

                if self.piece_moved in ("k", "K"):

                    self.KingsHasMoved[0 if self.turn == 1 else 1] = True
                    self.king_pos[0 if self.turn == 1 else 1] = self.move[1]
                    self.BOARD = self.after_castle(self.piece_moved, self.move[0], self.move[1], self.BOARD)

                if "p" or "P" in self.piece_moved:

                    if self.move[1][1] == 0 and self.piece_moved == "p":
                        self.BOARD[self.move[1][1]][self.move[1][0]] = self.promote()
                    elif self.move[1][1] == 7 and self.piece_moved == "P":
                        self.BOARD[self.move[1][1]][self.move[1][0]] = self.promote()

                    self.BOARD = self.after_enpassant(self.piece_moved, self.move[1], self.EnPassantSquere)

                    self.EnPassantSquere = self.get_enpassant_square(self.piece_moved, self.move[0], self.move[1])

                if "r" or "R" in self.piece_moved:

                    if self.BOARD[0][0] != "R":
                        self.RooksHasMoved[1] = True
                    if self.BOARD[0][7] != "R":
                        self.RooksHasMoved[0] = True

                    if self.BOARD[7][0] != "r":
                        self.RooksHasMoved[3] = True
                    if self.BOARD[7][7] != "r":
                        self.RooksHasMoved[2] = True

                self.turn *= -1

                self.highlight_moved_piece = self.move

                pygame.display.set_caption(("White to move" if self.turn == 1 else "Black to move"))

                self.move_sound.play()

                self.check_for_mate_or_stale()




            self.drag = False

            self.all_legal_for_piece = []

            self.move = []



