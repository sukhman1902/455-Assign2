# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html
import copy
import random
import sys
import time
import cProfile

class CommandInterface:

    def __init__(self):
        # Define the string to function command mapping
        self.command_dict = {
            "help": self.help,
            "game": self.game,
            "show": self.show,
            "play": self.play,
            "legal": self.legal,
            "genmove": self.genmove,
            "winner": self.winner,
            "timelimit": self.timelimit,
            "solve": self.solve
        }
        self.board = [[None]]
        self.player = 1
        self.start_time = None
        self.time_limit = 1.0
        self.timed_out = False
        self.positions = {}
        self.row_number = 0
        self.column_number = 0
        self.half_row_number_threshold = 0
        self.half_column_number_threshold = 0
        self.number_of_calls = 0

    # ===============================================================================================
    # VVVVVVVVVV START of PREDEFINED FUNCTIONS. DO NOT MODIFY. VVVVVVVVVV
    # ===============================================================================================

    # Convert a raw string to a command and a list of arguments
    def process_command(self, str):
        str = str.lower().strip()
        command = str.split(" ")[0]
        args = [x for x in str.split(" ")[1:] if len(x) > 0]
        if command not in self.command_dict:
            print("? Uknown command.\nType 'help' to list known commands.", file=sys.stderr)
            print("= -1\n")
            return False
        try:
            return self.command_dict[command](args)
        except Exception as e:
            print("Command '" + str + "' failed with exception:", file=sys.stderr)
            print(e, file=sys.stderr)
            print("= -1\n")
            return False

    # Will continuously receive and execute commands
    # Commands should return True on success, and False on failure
    # Every command will print '= 1' or '= -1' at the end of execution to indicate success or failure respectively
    def main_loop(self):
        while True:
            str = input()
            if str.split(" ")[0] == "exit":
                print("= 1\n")
                return True
            if self.process_command(str):
                print("= 1\n")

    # Will make sure there are enough arguments, and that they are valid numbers
    # Not necessary for commands without arguments
    def arg_check(self, args, template):
        converted_args = []
        if len(args) < len(template.split(" ")):
            print("Not enough arguments.\nExpected arguments:", template, file=sys.stderr)
            print("Recieved arguments: ", end="", file=sys.stderr)
            for a in args:
                print(a, end=" ", file=sys.stderr)
            print(file=sys.stderr)
            return False
        for i, arg in enumerate(args):
            try:
                converted_args.append(int(arg))
            except ValueError:
                print("Argument '" + arg + "' cannot be interpreted as a number.\nExpected arguments:", template,
                      file=sys.stderr)
                return False
        args = converted_args
        return True

    # List available commands
    def help(self, args):
        for command in self.command_dict:
            if command != "help":
                print(command)
        print("exit")
        return True

    # ===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF PREDEFINED FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    # ===============================================================================================

    # ===============================================================================================
    # VVVVVVVVVV START OF ASSIGNMENT 2 FUNCTIONS. ADD/REMOVE/MODIFY AS NEEDED. VVVVVVVV
    # ===============================================================================================

    def game(self, args):
        if not self.arg_check(args, "n m"):
            return False
        n, m = [int(x) for x in args]
        if n < 0 or m < 0:
            print("Invalid board size:", n, m, file=sys.stderr)
            return False

        self.board = []
        for i in range(m):
            self.board.append([None] * n)
        self.player = 1

        # Set the default time limit to 1
        self.timelimit(["1"])

        # Set the row number, column number, half row number threshold and half column number threshold
        self.row_number = n
        self.column_number = m
        self.half_column_number_threshold = self.column_number // 2 + self.column_number % 2
        self.half_row_number_threshold = self.row_number // 2 + self.row_number % 2

        return True

    def show(self, args):
        for row in self.board:
            for x in row:
                if x is None:
                    print(".", end="")
                else:
                    print(x, end="")
            print()
        return True

    def is_legal_reason(self, x, y, num):
        if self.board[y][x] is not None:
            return False, "occupied"

        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(self.column_number):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if count > self.half_column_number_threshold:
            self.board[y][x] = None
            return False, "too many " + str(num)

        consecutive = 0
        count = 0
        for col in range(self.row_number):
            if self.board[y][col] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False, "three in a row"
            else:
                consecutive = 0
        if count > self.half_row_number_threshold:
            self.board[y][x] = None
            return False, "too many " + str(num)

        self.board[y][x] = None
        return True, ""

    def is_legal(self, x, y, num):

        # Check if the point is empty
        if self.board[y][x] is not None:
            return False

        # Simulate the move
        self.board[y][x] = num

        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(self.column_number):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > self.half_column_number_threshold:
            self.board[y][x] = None
            return False

        # Check for row
        consecutive = 0
        count = 0
        row = self.board[y]
        for point in row:
            if point == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > self.half_row_number_threshold:
            self.board[y][x] = None
            return False

        # Undo the move
        self.board[y][x] = None

        return True

    def valid_move(self, x, y, num):
        return x >= 0 and x < self.row_number and \
            y >= 0 and y < self.column_number and \
            (num == 0 or num == 1) and \
            self.is_legal(x, y, num)

    def play(self, args):
        err = ""
        if len(args) != 3:
            print("= illegal move: " + " ".join(args) + " wrong number of arguments\n")
            return False
        try:
            x = int(args[0])
            y = int(args[1])
        except ValueError:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if x < 0 or x >= self.row_number or y < 0 or y >= self.column_number:
            print("= illegal move: " + " ".join(args) + " wrong coordinate\n")
            return False
        if args[2] != '0' and args[2] != '1':
            print("= illegal move: " + " ".join(args) + " wrong number\n")
            return False
        num = int(args[2])
        legal, reason = self.is_legal_reason(x, y, num)
        if not legal:
            print("= illegal move: " + " ".join(args) + " " + reason + "\n")
            return False
        self.board[y][x] = num
        if self.player == 1:
            self.player = 2
        else:
            self.player = 1
        return True

    def legal(self, args):
        if not self.arg_check(args, "x y number"):
            return False
        x, y, num = [int(x) for x in args]
        if self.valid_move(x, y, num):
            print("yes")
        else:
            print("no")
        return True

    def get_legal_moves(self):
        moves = []
        for y in range(self.column_number):
            for x in range(self.row_number):
                if self.board[y][x] is None:
                    for num in range(2):
                        if self.is_legal(x, y, num):
                            moves.append([str(x), str(y), str(num)])
        return moves

    def genmove(self, args):
        moves = self.get_legal_moves()
        if len(moves) == 0:
            print("resign")
        else:
            rand_move = moves[random.randint(0, len(moves) - 1)]
            self.play(rand_move)
            print(" ".join(rand_move))
        return True

    def winner(self, args):
        if not self.get_legal_moves():
            if self.player == 1:
                print(2)
            else:
                print(1)
        else:
            print("unfinished")
        return True

    # new function to be implemented for assignment 2
    def timelimit(self, args):
        input = float(args[0])
        if 1 <= input <= 100:
            self.time_limit = input
            return True
        return False

    # Check if there is a timeout
    def time_out(self):
        return time.process_time() - self.start_time >= self.time_limit

    # Update the legal_moves after a move played
    def update_legal_moves(self, legal_moves, move_played):

        moves = []
        removed_moves = []
        played_x, played_y, played_digit = move_played[0], move_played[1], move_played[2]

        for legal_move in legal_moves:

            x, y, digit = legal_move[0], legal_move[1], legal_move[2]

            # Skip the move if it's the same point just played
            if played_x == x and played_y == y:
                removed_moves.append([x, y, digit])
                continue

            # Flag to indicate whether to remove this move
            remove_move = False

            # Check if the move is in the same row or column as the move just played
            if played_x == x or played_y == y:

                # If the digit is the same
                if played_digit == digit:

                    # Check balance constraint and triple constraint
                    # Simulate placing the digit on the board
                    self.board[y][x] = digit

                    # Check for balance constraint in the row or column
                    if played_x == x:  # Same column
                        column = [self.board[row_index][x] for row_index in range(self.column_number)]
                        if column.count(digit) > self.half_column_number_threshold:
                            remove_move = True
                    if played_y == y:  # Same row
                        row = self.board[y]
                        if row.count(digit) > self.half_row_number_threshold:
                            remove_move = True

                    # Check for triple constraint in the row
                    if played_y == y:
                        row = self.board[y]
                        consecutive = 0
                        for point in row:
                            if point == digit:
                                consecutive += 1
                                if consecutive >= 3:
                                    remove_move = True
                                    break
                            else:
                                consecutive = 0

                    # Check for triple constraint in the column
                    if played_x == x:
                        column = [self.board[row_index][x] for row_index in range(self.column_number)]
                        consecutive = 0
                        for point in column:
                            if point == digit:
                                consecutive += 1
                                if consecutive >= 3:
                                    remove_move = True
                                    break
                            else:
                                consecutive = 0

                    # Undo the simulated move
                    self.board[y][x] = None

                    if remove_move:
                        removed_moves.append([x, y, digit])
                        continue

            # If we reach here, the move is still legal
            moves.append([x, y, digit])

        return moves, removed_moves

    def another_is_legal(self, x, y, num):

        # Simulate the move
        self.board[y][x] = num

        consecutive = 0
        count = 0
        self.board[y][x] = num
        for row in range(self.column_number):
            if self.board[row][x] == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > self.half_column_number_threshold:
            self.board[y][x] = None
            return False

        # Check for row
        consecutive = 0
        count = 0
        row = self.board[y]
        for point in row:
            if point == num:
                count += 1
                consecutive += 1
                if consecutive >= 3:
                    self.board[y][x] = None
                    return False
            else:
                consecutive = 0
        if count > self.half_row_number_threshold:
            self.board[y][x] = None
            return False

        # Undo the move
        self.board[y][x] = None

        return True

    def another_get_legal_moves(self):
        moves = []
        for y in range(self.column_number):
            for x in range(self.row_number):
                if self.board[y][x] is None:
                    for num in range(2):
                        if self.another_is_legal(x, y, num):
                            moves.append([x, y, num])
        return moves

    # Recursively solve the board using negamax
    def recursive_solve(self, available_legal_moves):

        # Check if there are 2 moves to play
        if len(available_legal_moves) == 2:

            move_1, move_2 = available_legal_moves
            x_1, y_1, digit_1 = move_1[0], move_1[1], move_1[2]
            move_1_win = False
            x_2, y_2, digit_2 = move_2[0], move_2[1], move_2[2]
            move_2_win = False

            # Play each move and check if it wins
            self.board[y_1][x_1] = digit_1
            # Check if the other move is still legal
            move_1_win = not self.another_is_legal(x_2, y_2, digit_2)

            if move_1_win:
                self.positions[str(self.board)] = [True, move_1]
                self.board[y_1][x_1] = None
                return True, move_1

            self.board[y_1][x_1] = None

            self.board[y_2][x_2] = digit_2
            # Check if the other move is still legal
            move_2_win = not self.another_is_legal(x_1, y_1, digit_1)

            if move_2_win:
                self.positions[str(self.board)] = [True, move_2]
                self.board[y_2][x_2] = None
                return True, move_2

            self.board[y_2][x_2] = None

            self.positions[str(self.board)] = [False, None]
            return False, None

        # Check if there is only 1 move to play -> Winning
        elif len(available_legal_moves) == 1:

            only_move = available_legal_moves[0]
            self.positions[str(self.board)] = [True, only_move]
            return True, only_move

        # Check if there is no more move to play -> Losing
        elif not available_legal_moves:
            self.positions[str(self.board)] = [False, None]
            return False, None

        # Check for timeout to cancel all recursive calls
        if self.timed_out:
            return None, None

        self.number_of_calls += 1

        # Check if there is still time every 500 recursive calls
        if self.number_of_calls % (self.row_number + self.column_number) == 0:
            if self.time_out():
                self.timed_out = True
                return None, None

        # Search for a winning move
        for move in available_legal_moves:

            x, y, digit = move

            # Check if we encounter this position before to reuse calculations
            current_position = self.positions.get(str(self.board))
            if current_position is not None:
                return current_position[0], current_position[1]

            # Play the move
            self.board[y][x] = digit

            # Check legal moves to play
            moves, removed_moves = self.update_legal_moves(available_legal_moves, move)

            # Check if the move is a winning move or not
            winning, winning_move = self.recursive_solve(moves)

            # Undo the last move to play another move
            self.board[y][x] = None

            # If timeout
            if winning is None:
                return None, None

            # The move is a winning move, the opponent has no winning moves after that
            if not winning:
                self.positions[str(self.board)] = [True, move]
                return True, move

            if self.time_out():
                self.timed_out = True
                return None, None

        # If there are no winning moves for us, then we definitely lose
        self.positions[str(self.board)] = [False, None]
        return False, None

    # new function to be implemented for assignment 2
    def solve(self, args):

        # Start the timer
        self.start_time = time.process_time()

        winning, winning_move = self.recursive_solve(self.another_get_legal_moves())

        # There is a timeout event
        if winning is None:
            print("unknown")

        # The current player is going to win
        elif winning:
            print(f"{str(self.player)} {winning_move[0]} {winning_move[1]} {winning_move[2]}")

        # The current player is going to lose
        else:
            print(3 - self.player)

        return True

    # ===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    # ===============================================================================================

def t_9(interface):
    profiler = cProfile.Profile()
    interface.game(['2', '2'])
    interface.timelimit(['1'])
    profiler.enable()
    interface.solve([])
    profiler.disable()
    profiler.print_stats()

def t_26(interface):
    profiler = cProfile.Profile()
    interface.game(['8', '4'])
    interface.play(['5', '1', '0'])
    interface.play(['0', '1', '0'])
    interface.play(['7', '1', '0'])
    interface.play(['4', '2', '0'])
    interface.play(['4', '0', '0'])
    interface.play(['2', '3', '1'])
    interface.play(['4', '1', '1'])
    interface.play(['3', '1', '0'])
    interface.play(['1', '3', '1'])
    interface.play(['5', '0', '0'])
    interface.play(['2', '0', '1'])
    interface.timelimit(['15'])
    profiler.enable()
    interface.solve([])
    profiler.disable()
    profiler.print_stats()

def t_41(interface):
    profiler = cProfile.Profile()
    interface.game(['6', '5'])
    interface.play(['4', '4', '1'])
    interface.play(['4', '0', '1'])
    interface.play(['3', '2', '0'])
    interface.play(['0', '4', '1'])
    interface.play(['2', '1', '1'])
    interface.play(['1', '2', '0'])
    interface.play(['3', '1', '0'])
    interface.play(['2', '0', '1'])
    interface.play(['5', '1', '0'])
    interface.play(['0', '3', '1'])
    interface.play(['5', '2', '1'])
    interface.play(['5', '3', '1'])
    interface.timelimit(['20'])
    profiler.enable()
    interface.solve([])
    profiler.disable()
    profiler.print_stats()

def t_57(interface):
    profiler = cProfile.Profile()
    interface.game(['4', '5'])
    interface.play(['1', '3', '0'])
    interface.play(['1', '2', '0'])
    interface.play(['1', '1', '1'])
    interface.play(['3', '1', '1'])
    interface.timelimit(['40'])
    profiler.enable()
    interface.solve([])
    profiler.disable()
    profiler.print_stats()

def t_68(interface):
    profiler = cProfile.Profile()
    interface.game(['5', '5'])
    interface.play(['0', '0', '1'])
    interface.play(['4', '4', '0'])
    interface.play(['4', '0', '0'])
    interface.play(['4', '3', '1'])
    interface.play(['4', '1', '0'])
    interface.play(['3', '4', '1'])
    interface.play(['0', '4', '1'])
    interface.play(['3', '3', '0'])
    interface.play(['3', '1', '0'])
    interface.timelimit(['80'])
    profiler.enable()
    interface.solve([])
    profiler.disable()
    profiler.print_stats()

if __name__ == "__main__":
    interface = CommandInterface()
    # t_9(interface)
    # t_26(interface)
    # t_41(interface)
    # t_57(interface)
    # t_68(interface)
    interface.main_loop()