from os import system

class Pieces:

    def __init__(self, type, colour: int, pos: tuple):

        self.type = type
        self.x, self.y = pos        # (x, y)
        self.colour = colour        # 1 → WHITE | (-1) → BLACK | 0 → NONE
        self.has_moved = False


    def move(self, pos: tuple) -> None:
        "moves an object to a cordinate pos incl. castling, queening"
        
        x, y  = pos

        if self.type == "king":
            castle_cords = ((7, 2), (7, 6), (0, 2), (0, 6))
            if (x, y) in castle_cords:
                for check_cord in castle_cords:
                    if result := self.check_castle_cord(check_cord):
                        result[1].move(result[0])

        elif self.type == "pawn" and (
            (self.colour == -1 and self.x == 6) or
            (self.colour == 1  and self.x == 1)):
            self.type = "queen"

        board[x][y] = self
        board[self.x][self.y] = Pieces(None, 0, (self.x, self.y))
        self.x, self.y = x, y
        
        self.has_moved = True


    def all_legal_moves(self, for_checks=False) -> set:
        "All legal moves for a piece, for_checks parameter includes friendlies as moves well"

        moves = set()
        for g in range(9):

            x_d, y_d = g//3 - 1, g%3 - 1
            x, y = self.x + x_d, self.y + y_d

            if x_d == y_d == 0: continue # to prevent recurssion

            def check_cardinal_directions(cords: tuple, x, y):
                if (x_d, y_d) in cords:
                    while x in range(8) and y in range(8):
                        if (board[x][y].type == "king" and for_checks) or board[x][y].type == None:
                            moves.add((x,y))
                            x += x_d
                            y += y_d
                        else:
                            if board[x][y].colour == self.colour * -1 or for_checks:
                                moves.add((x,y))
                            break

            if self.type == "king": #special case

                if x in range(8) and y in range(8):

                    if not self.is_check((x, y)):
                        if board[x][y].colour == self.colour: #check if same col
                            continue
                        moves.add((x, y))

                    castle = {
                        1  : ((7, 2), (7, 6)),      #white
                        -1 : ((0, 2), (0, 6))       #black
                    }
                    for i in castle[self.colour]:
                        if self.check_castle_cord(i):
                            moves.add(i)

            elif self.type == "knight": #special case

                x, y = self.x, self.y

                KNIGHT_MOVES = [
                    (x - 2, y + 1), (x - 2, y - 1),
                    (x - 1, y + 2), (x - 1, y - 2),
                    (x + 1, y + 2), (x + 1, y - 2),
                    (x + 2, y + 1), (x + 2, y - 1)
                ]

                for move in KNIGHT_MOVES:
                    if move[0] in range(8) and move[1] in range(8):
                        if self.colour == -board[move[0]][move[1]].colour: #check if same colour
                            continue
                        moves.add(move)

            elif self.type == "pawn": #special case
                heading = -self.colour      # 1 * -1 (WHITE) and -1 * -1 (BLACK)
                x, y = self.x, self.y

                if not for_checks: #normal moves
                    if board[x + heading][y].type == None:
                        moves.add((x + heading, y))
                        if not self.has_moved and board[x + 2*heading][y].type == None:
                            moves.add((x + 2*heading, y))

                for dir in [-1, 1]:
                    if (y + dir) in range(8):
                        if board[x + heading][y + dir].colour == -self.colour or for_checks:
                            moves.add((x + heading, y + dir))

            elif self.type == "queen":
                check_cardinal_directions((
                    (-1, -1), (-1, 0), (-1, 1), (0, -1),
                    (0, 1), (1, -1), (1, 0), (1, 1)
                    ), x, y)

            elif self.type == "bishop":
                check_cardinal_directions((
                    (1, 1), (-1, -1), (1, -1), (-1, 1),
                    ), x, y)

            elif self.type == "rook":
                check_cardinal_directions((
                    (1, 0), (0, 1), (-1, 0), (0, -1),
                    ), x, y)
        
        return moves


    def is_check(self, cord: tuple):
        "returns bool if not check or attacker obj if true"

        for obj in [i for j in board for i in j if i.colour == -self.colour]:
            if obj.type != "king" and cord in obj.all_legal_moves(True):
                return obj
        return False


    def check_castle_cord(self, cord: tuple): #check for rook at pos
        "To check if a cord for castling is legal {returns → rook_cord, rook_object or FALSE}"

        if not self.has_moved and (self.x, self.y) in [(7, 4), (0, 4)]:
            x, y = cord
            init_rook, final_rook = (0, 3) if y == 2 else (7, 5)
            range_i = range(5, 7) if init_rook == 7 else range(1, 4)
            
            if not board[x][init_rook].has_moved \
                and board[x][init_rook].type == "rook" \
                and not any([board[x][i].type for i in range_i]):
                return ((x, final_rook), board[x][init_rook])

        return False


    def check_moves(self, attacker) -> tuple:
        "takes attacker OBJECT as argument; returns bool"

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


def spawn():
    colours = {
        "king"   : ["♚", "♔"],
        "queen"  : ["♛", "♕"],
        "bishop" : ["♝", "♗"],
        "knight" : ["♞", "♘"],
        "rook"   : ["♜", "♖"],
        "pawn"   : ["♟", "♙"],
        None     : [" " , " " ],
        }

    repr_str = '  A B C D E F G H\n'
    for i, l in enumerate(board):
        repr_str += ' '.join([str(8-i), *[colours[k.type][0 if k.colour == 1 else 1] if k.type else "." for k in l], str(8-i)]) + '\n'
    repr_str += '  A B C D E F G H'

    print(repr_str)
    
def piece_moves(obj):
    moves = obj.all_legal_moves()
    for i in range(8):
        for j in range(8):
            if (i,j) == (obj.x, obj.y):
                print("0", end="|")
            elif (i,j) in moves:
                print("#", end="|")
            else:
                print(".", end="|")
        print()

board = [[Pieces(None, 0, (j, i)) for i in range(8)] for j in range(8)]

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

while True:

    system("cls")
    print("turn :", "WHITE" if turn else "BLACK")
    spawn()

    check_w = King_white.is_check((King_white.x, King_white.y))
    check_b = King_black.is_check((King_black.x, King_black.y))
    
    if check_w or check_b: #check for mates
        attacker = check_w if check_w else check_b
        team = King_white if turn else King_black

        if not team.check_moves(attacker)[1]:
            print(f"MATE\n{attacker.colour} WINS!!!")
            break
        
    
    a1, b1 = input("CORD: ").lower().split()
    a1, b1 = ord(a1) - 97, 8 - int(b1)
    obj = board[b1][a1]

    if check_w: moves = obj.check_moves(check_w)[0]
    if check_b: moves = obj.check_moves(check_b)[0]
    else:       moves = obj.all_legal_moves()

    if ((turn and obj.colour == 1) or (not turn and obj.colour == -1)) and moves:

        piece_moves(obj)
        while True:

            a2, b2 = input("TO CORD: ").lower().split()
            a2, b2 = ord(a2) - 97, 8 - int(b2)

            if (b2, a2) in moves:
                obj.move((b2, a2))
                turn = not turn
                break
