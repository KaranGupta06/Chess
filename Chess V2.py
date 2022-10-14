from termcolor import colored       #>>> pip install termcolor
from os import system

class Pieces:
    
    def __init__(self, type, colour: int, pos: tuple):

        self.type = type
        self.x, self.y = pos        # (x, y)
        self.colour = colour                                    # 1 → WHITE | (-1) → BLACK | 0 → NONE
        self.has_moved = False
        self.en_passant = False
        

    def move(self, pos: tuple) -> None:
        "moves an object to a cordinate pos, includes castling and queening"
        x, y  = pos

        if self.type == "king":
            if x in [7, 0] and y in [2, 6]:                    #castle cords check
                castle_cord = self.castle_check((x, y))        #stores rook move info
                castle_cord[1].move(castle_cord[0])
                        
        elif self.type == "pawn":
            if cut_cord := self.en_passant:
                board[cut_cord[1][0]][cut_cord[1][1]] = Pieces(None, 0, (self.x, self.y))
                self.en_passant = False
            if pos[0] in [7, 0]:
                self.type = input("Queen | Rook | Bishop | Knight >>> ").lower()
        

        board[x][y] = self                                          #set "cord" as self object
        board[self.x][self.y] = Pieces(None, 0, (self.x, self.y))   #set previous cord as None
        self.x, self.y = x, y

        self.has_moved = True


    def all_legal_moves(self, for_checks=False) -> set:
        "All legal moves for a piece, for_checks parameter includes friendlies as well"

        moves = set()

        def check_cardinal_directions(cords: tuple):
            for x_d, y_d in cords:
                x, y = self.x + x_d, self.y + y_d

                while x in range(8) and y in range(8):
                    if (board[x][y].type == "king" and for_checks) or board[x][y].type == None:
                        moves.add((x,y))
                        x += x_d
                        y += y_d
                    else:
                        if board[x][y].colour == -self.colour or for_checks:
                            moves.add((x,y))
                        break
        
        if self.type == "king":
            for g in range(9):
                x_d, y_d = g//3 - 1, g%3 - 1
                x, y = self.x + x_d, self.y + y_d

                if for_checks:
                    moves.add((x, y))
                else:
                    if (x in range(8) and y in range(8) and not x_d == y_d == 0 and
                        not self.is_check((x, y)) and board[x][y].colour != self.colour):
                            moves.add((x, y))

            for i in (2, 6):
                if self.castle_check((self.x, i)):
                    moves.add((self.x, i))

        elif self.type == "knight":

            x, y = self.x, self.y

            KNIGHT_MOVES = [
                (x - 2, y + 1), (x - 2, y - 1),
                (x - 1, y + 2), (x - 1, y - 2),
                (x + 1, y + 2), (x + 1, y - 2),
                (x + 2, y + 1), (x + 2, y - 1)
            ]

            for move in KNIGHT_MOVES:
                if move[0] in range(8) and move[1] in range(8):
                    if self.colour == board[move[0]][move[1]].colour: #check if same colour
                        continue
                    moves.add(move)

        elif self.type == "pawn":
            heading = -self.colour
            x, y = self.x, self.y

            if not for_checks:                          #normal moves
                if board[x + heading][y].type == None:
                    moves.add((x + heading, y))

                    if not self.has_moved and board[x + 2*heading][y].type == None:
                        moves.add((x + 2*heading, y))

                        for dir in [-1, 1]:             #en passant
                            if y + dir not in range(8): continue
                            if (board[x + 2*heading][y + dir].type == "pawn" and
                                board[x + 2*heading][y + dir].colour == -self.colour):
                                board[x + 2*heading][y + dir].en_passant = ((x + heading, y), (x + 2*heading, y))

            if self.en_passant: moves.add(self.en_passant[0])

            for dir in [-1, 1]:                         #attack moves
                if (y + dir) in range(8):
                    if board[x + heading][y + dir].colour == -self.colour or for_checks:
                        moves.add((x + heading, y + dir))

        elif self.type == "queen":
            check_cardinal_directions((
                (-1, -1), (-1, 0), (-1, 1), (0, -1),
                (0, 1), (1, -1), (1, 0), (1, 1)
                ))

        elif self.type == "bishop":
            check_cardinal_directions((
                (1, 1), (-1, -1), (1, -1), (-1, 1),
                ))

        elif self.type == "rook":
            check_cardinal_directions((
                (1, 0), (0, 1), (-1, 0), (0, -1),
                ))
        
        return moves


    def is_check(self, cord: tuple):
        "returns bool if not check or attacker obj if true"

        for obj in [i for j in board for i in j if i.colour == -self.colour]:
            if cord in obj.all_legal_moves(True):
                return obj
        return False


    def castle_check(self, cord: tuple):
        "To check if a cord for castling is legal {returns → rook_cord, rook_object or FALSE}"

        if not self.has_moved and (self.x, self.y) in [(7, 4), (0, 4)]:
            x, y = cord
            init_rook, final_rook = (0, 3) if y == 2 else (7, 5)
            range_i = range(5, 7) if init_rook == 7 else range(1, 4)
            
            if (not board[x][init_rook].has_moved
                and board[x][init_rook].type == "rook"
                and not any([board[x][i].type for i in range_i])):
                return ((x, final_rook), board[x][init_rook])

        return False


    def check_moves(self, attacker) -> tuple:
        "takes attacker OBJECT as argument; → (self_moves {set}, team_moves {set})"

        if attacker.type != "knight":
            attack_cords = set()

            king = King_white if self.colour == 1 else King_black
            
            x_d, y_d = king.x - attacker.x, king.y - attacker.y
            x_s = 0 if x_d == 0 else int(abs(x_d)/x_d * -1)
            y_s = 0 if y_d == 0 else int(abs(y_d)/y_d * -1)

            for i in range(1, max(abs(x_d), abs(y_d))):
                attack_cords.add((king.x + i*x_s, king.y + i*y_s))

        attack_cords.add((attacker.x, attacker.y))

        moves = set()               #[0]
        for obj in [i for j in board for i in j if i.colour == self.colour]:
            moves |= (obj.all_legal_moves() & attack_cords)
        moves |= king.all_legal_moves()

        if self.type == "king":     #[1]
            self_moves = self.all_legal_moves()
        else:
            self_moves = self.all_legal_moves() & attack_cords

        return (self_moves, moves)


def spawn(turn, moves = None, obj = None):

    piece_symbols = {
        "king"   : [None, "♔ ", "\033[38;2;30;30;30m♚ "],
        "queen"  : [None, "♕ ", "\033[38;2;30;30;30m♛ "],
        "bishop" : [None, "♗ ", "\033[38;2;30;30;30m♝ "],
        "knight" : [None, "♘ ", "\033[38;2;30;30;30m♞ "],
        "rook"   : [None, "♖ ", "\033[38;2;30;30;30m♜ "],
        "pawn"   : [None, "♙ ", "\033[38;2;30;30;30m♟ "],
        None     : ["  "]
        }

    system("cls")
    print("Turn:", "White" if turn else "Black")

    for i in white_cut_pieces: print(piece_symbols[i.type][i.colour], end="")
    print()

    for i in range(8):
        print(8-i, end=" ")
        for j in range(8):

            fg = piece_symbols[board[i][j].type][board[i][j].colour]
            bg = "on_white" if (i + j)%2 else "on_green"

            if obj != None:
                if (i, j) in moves and abs(board[i][j].colour):
                    bg = "on_red"
                elif (i, j) in moves:
                    fg = "・"
                elif (i, j) == (obj.x, obj.y):
                    bg = "on_cyan"
            
            print(colored(fg, on_color=bg, attrs=["bold"]), end="")
        print()
    print("  A B C D E F G H")
    for i in black_cut_pieces: print(piece_symbols[i.type][i.colour], end="")


board = [[Pieces(None, 0, (j, i)) for i in range(8)] for j in range(8)]
white_cut_pieces = []
black_cut_pieces = []

CHESS_PIECES = [
    "rook", "knight", "bishop", "queen",
    "king", "bishop", "knight", "rook"
    ]

for i, piece in enumerate(CHESS_PIECES):
    board[7][i] = Pieces(piece, 1, (7, i))
    board[0][i] = Pieces(piece, -1, (0, i))
    board[6][i] = Pieces("pawn", 1, (6, i))
    board[1][i] = Pieces("pawn", -1, (1, i))

board[7][4] = King_white = Pieces("king", 1, (7, 4))
board[0][4] = King_black = Pieces("king", -1, (0, 4))
turn = True                                                 # TRUE → WHITE, FALSE → BLACK

if input("""
         ♔  CHESS ♚

A Two player game, Checkmate the
     opponent's king to win!

Select a piece by simply typing
its coordinate (ex A5, f7, etc)
and then to move it repeat this 
             process.

   Press enter to continue.""") == "carrot":
   raise SyntaxError("~Easter Egg~")

while True:
    spawn(turn)

    check_w = King_white.is_check((King_white.x, King_white.y))
    check_b = King_black.is_check((King_black.x, King_black.y))
    
    if check_w or check_b:                                  #check for mates
        attacker = check_w if check_w else check_b
        team = King_white if turn else King_black

        if not team.check_moves(attacker)[1]:               #no more moves remaining
            print("MATE!", ("White" if attacker.colour == 1 else "Black"), "wins!")
            break

    a1, b1 = input("\nCORD: ").lower()
    a1, b1 = ord(a1) - 97, 8 - int(b1)
    obj = board[b1][a1]

    if check_w: moves = obj.check_moves(check_w)[0]
    if check_b: moves = obj.check_moves(check_b)[0]
    else:       moves = obj.all_legal_moves()

    if ((turn and obj.colour == 1) or (not turn and obj.colour == -1)) and moves:

        spawn(turn, moves, obj)
    
        while True:

            a2, b2 = input("CORD: ").lower()
            a2, b2 = ord(a2) - 97, 8 - int(b2)

            if (b2, a2) in moves:
                if board[b2][a2].colour == -obj.colour:
                    if board[b2][a2].colour == 1:
                        white_cut_pieces.append(board[b2][a2])
                    else:
                        black_cut_pieces.append(board[b2][a2])

                obj.move((b2, a2))
                turn = not turn
                break

            elif (turn and board[b2][a2].colour == 1) or \
                (not turn and board[b2][a2].colour == -1):

                obj = board[b2][a2]

                if check_w: moves = obj.check_moves(check_w)[0]
                if check_b: moves = obj.check_moves(check_b)[0]
                else:       moves = obj.all_legal_moves()

                system("cls")
                spawn(turn, moves, obj)
