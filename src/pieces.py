
class Pieces:

    def in_bounds(self, new_x, new_y):

        # Used to check if the cordinates are in bounds for the chessboard, prevents the game from crashing

        return 0 <= new_x < 8 and 0 <= new_y < 8


    def generate_legal_moves(self, x, y, turn, piece, board, enpassant = None, kinghasmoved = None, rookshasmoved = None):

        moves = []

        if piece in ("p", "P"):
            moves = self.generate_pawn_moves(x, y, turn, board, enpassant)
        elif piece in ("h", "H"):
            moves = self.generate_knight_moves(x, y, turn, board)
        elif piece in ("r", "R", "q", "Q", "b", "B"):
            moves = self.generate_sliding_moves(x, y, turn, piece, board)
        elif piece in ("k", "K"):
            moves = self.generate_king_moves(x, y, turn, board, kinghasmoved, rookshasmoved)

        return moves

    def generate_sliding_moves(self, x, y, turn, piece, board):

        # Generates moves for both rooks, bishops and queens

        moves = []
        directions = []

        if piece in ("b", "B"):
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        elif piece in ("r", "R"):
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        elif piece in ("q", "Q"):
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

        for direction in directions:
            for i in range(1, 8):
                new_x, new_y = x + direction[0] * i, y + direction[1] * i
                if self.in_bounds(new_x, new_y) == True:
                    if turn == 1:
                        if not board[new_y][new_x].islower():
                
                            moves.append((new_x, new_y))
                            if board[new_y][new_x].isupper():
                                break
                        else:
                            break
                    if turn == -1:
                        if not board[new_y][new_x].isupper():
                            moves.append((new_x, new_y))
                            if board[new_y][new_x].islower():
                                break
                        else:
                            break
        return moves

    def generate_knight_moves(self, x, y, turn, board):

        # Generates all pseudo-legal moves a knight can make

        moves = []
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for direction in directions:
            
            new_x, new_y = x + direction[0], y + direction[1]

            if self.in_bounds(new_x, new_y) == True:

                if not board[new_y][new_x].islower() and turn == 1:
                    moves.append((new_x, new_y))
                if not board[new_y][new_x].isupper() and turn == -1:
                    moves.append((new_x, new_y))
            
        return moves
  
    def generate_pawn_moves(self, x, y, turn, board, enpassant, only_diag = False):

        # Generates all pseudo-legal moves a pawn can make

        directions = []
        moves = []

        attack = []
        attack_moves = []

        if (y-1*turn) < 8 and board[y - 1*turn][x] == "0":
            directions.append((0, -1*turn))

        if turn == 1:
            
            if y == 6:
                if board[y-1][x] == "0" and board[y-2][x] == "0":
                    directions.append((0, - 2))

                
            if enpassant == (x-1, y-1):
                directions.append((-1, -1))
            elif enpassant == (x+1, y-1):
                directions.append((1, -1))

            if (x - 1 < 8) and (y - 1 > -1) and board[y - 1][x - 1].isupper():
                directions.append((-1, -1))
                attack.append((-1, -1))
            if (x + 1 < 8) and (y - 1 > -1) and board[y - 1][x + 1].isupper():
                directions.append((1, -1))
                attack.append((1, -1))

        if turn == -1:

            if y == 1:
                if board[y+1][x] == "0" and board[y+2][x] == "0":
                    directions.append((0, + 2))

            if enpassant == (x+1, y+1):
                directions.append((1, 1))
            elif enpassant == (x-1, y+1):
                directions.append((-1, 1))
   
            if (x + 1 < 8) and (y + 1 < 8) and board[y + 1][x + 1].islower():
                directions.append((1, 1))
                attack.append((1, 1))
            if (x - 1 > -1) and (y + 1 < 8) and board[y + 1][x - 1].islower():
                directions.append((-1, 1))
                attack.append((-1, 1))


        if only_diag == True:

            # This is just used when checking if king is in check, cause a pawn can only attack diagonally

            for dir in attack:
                new_x, new_y = x + dir[0], y + dir[1]
                attack_moves.append((new_x, new_y))

            return attack_moves

        for direction in directions:
            new_x, new_y = x + direction[0], y + direction[1]
            moves.append((new_x, new_y))

        return moves

    def generate_king_moves(self, x, y, turn, board, kinghasmoved, rookshasmoved):

        # Generates all pseudo-legal moves the king can make

        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        moves = []

        if kinghasmoved[0] == False and turn == 1:
            if rookshasmoved[2] == False and board[7][5] == "0" and board[7][6] == "0":
                directions.append((2, 0))
            if rookshasmoved[3] == False and board[7][1] == "0" and board[7][2] == "0" and board[7][3] == "0":
                directions.append((-2, 0))
        
        if kinghasmoved[1] == False and turn == -1:
            if rookshasmoved[0] == False and board[0][6] == "0" and board[0][5] == "0":
                directions.append((2, 0))
            if rookshasmoved[1] == False and board[0][1] == "0" and board[0][2] == "0" and board[0][3] == "0":
                directions.append((-2, 0))

        for direction in directions:
            new_x, new_y = x + direction[0], y + direction[1]
            if self.in_bounds(new_x, new_y) == True:
                if (not board[new_y][new_x].islower() and turn == 1) or (not board[new_y][new_x].isupper() and turn == -1):
                    moves.append((new_x, new_y))
            
        return moves

