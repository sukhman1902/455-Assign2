# CMPUT 455 Assignment 2 starter code
# Implement the specified commands to complete the assignment
# Full assignment specification here: https://webdocs.cs.ualberta.ca/~mmueller/courses/cmput455/assignments/a2.html

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

        consecutive = 0
        count = 0
        for col in range(self.row_number):
            if self.board[y][col] == num:
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
        self.time_limit = float(args[0])
        return True

    # Check if there is a timeout
    def time_out(self):
        return time.time() - self.start_time >= self.time_limit

    # Get all the points in the same row of the board
    def get_row(self, row_index):
        return self.board[row_index]

    # Get all the points in the same column of the board
    def get_column(self, column_index):
        return [row[column_index] for row in self.board]

    def categorize_move_deep(self, legal_moves):
        moves = []
        for move in legal_moves:
            x, y, digit = int(move[0]), int(move[1]), int(move[2])
            if self.is_legal(x, y, digit):
                moves.append(move)

        return moves

    # Optimization: randomizing the choice of digit of a move
    # For a move in a row and a column with seemingly equal number of digits,
    # only 1 digit is randomly chosen for the move
    def categorize_move_root(self, legal_moves, depth):

        if depth <= 2 and (self.row_number >= 4 and self.column_number >= 4 or self.column_number >= 4 and self.row_number >= 4):

            moves = []
            categorized_moves = {}
            for move in legal_moves:
                x, y, digit = int(move[0]), int(move[1]), int(move[2])
                if self.is_legal(x, y, digit):
                    if (x, y) not in categorized_moves:
                        categorized_moves[(x, y)] = [digit]
                    else:
                        categorized_moves[(x, y)].append(digit)

            for coordinates, digits in categorized_moves.items():

                row = self.get_row(int(coordinates[0]))
                column = self.get_column(int(coordinates[0]))

                # If both digits can be chosen for this move
                if len(digits) == 2:

                    zero_row_count = row.count(0)
                    zero_column_count = column.count(0)
                    one_row_count = row.count(1)
                    one_column_count = column.count(1)

                    # If the digits are closely equal in number in a row and in a column
                    if (((zero_row_count - one_row_count <= 1 or
                          zero_row_count - one_row_count >= -1) and
                         zero_row_count + one_row_count < self.half_row_number_threshold) and
                            ((zero_column_count - one_column_count <= 1 or
                              zero_column_count - one_column_count >= -1) and
                             zero_column_count + one_column_count >= self.half_column_number_threshold)):
                        moves.append([coordinates[0], coordinates[1], digits[random.randint(0, 1)]])

                    # Add the move with distinct digit
                    else:
                        moves.append([coordinates[0], coordinates[1], digits[0]])

                # If only 1 digit can be chosen for this move
                else:
                    moves.append([coordinates[0], coordinates[1], digits[0]])

            return moves

        else:
            return self.categorize_move_deep(legal_moves)


    # Recursively solve the board using negamax
    def recursive_solve(self, move_sequence, depth, available_legal_moves):

        # print(f"Move sequence at depth {depth}: {move_sequence}")

        # Check if there is only 1 move to play -> Winning
        if len(available_legal_moves) == 1:
            return True, available_legal_moves[0]
        # Check if there is no more move to play -> Losing
        elif not available_legal_moves:
            self.positions[move_sequence] = [False, None]
            return False, None

        # Check for timeout to cancel all recursive calls
        if self.timed_out:
            return None, None

        # Check if there is still time every 5,000 recursive calls
        if self.number_of_calls % 5000 == 0:
            if self.time_out():
                self.timed_out = True
                return None, None

        # Search for a winning move
        for move in available_legal_moves:

            x = int(move[0])
            y = int(move[1])
            digit = int(move[2])

            # Check if we encounter this position before to reuse calculations
            current_position = self.positions.get(move_sequence)
            if current_position is not None:
                return current_position[0], current_position[1]

            # Play the move
            self.board[y][x] = digit

            # Check legal moves to play
            # sorted_categorized_moves = []
            moves = self.categorize_move_root(available_legal_moves, depth)

            # print(moves, number_of_multiple_digits)
            # sorted_categorized_moves.append((move, number_of_multiple_digits))
            # sorted_categorized_moves.sort(key=lambda item: item[1])
            # moves = []
            # for min_move in sorted_categorized_moves:
            #     moves.append(min_move[0])
            #
            # print(moves)

            # Check if the move is a winning move or not
            winning, winning_move = self.recursive_solve(move_sequence + f"-{x}.{y}.{digit}", depth + 1, moves)
            self.number_of_calls += 1
            # Undo the last move to play another move
            self.board[y][x] = None

            # If timeout
            if winning is None:
                return None, None

            # The move is a winning move, the opponent has no winning moves after that
            elif not winning:
                self.positions[move_sequence] = [True, move]
                return True, move

        # If there are no winning moves for us, then we definitely lose
        self.positions[move_sequence] = [False, None]
        return False, None

    # new function to be implemented for assignment 2
    def solve(self, args):

        # Start the timer
        self.start_time = time.time()

        # Begin searching for a winning from the current position
        # Notice that we are searching from the current position before playing any move
        # Therefore, there is no need to negate the result
        # Optimization: reusing the initial legal moves and then reduce it by each move
        # since the number of legal moves can only decrease without replacement
        winning, winning_move = self.recursive_solve("Start", 0, self.get_legal_moves())

        # There is a timeout event
        if winning is None:
            print("unknown")

        # The current player is going to win
        elif winning:
            print(f"{str(self.player)} {winning_move[0]} {winning_move[1]} {winning_move[2]}")

        # The current player is going to lose
        else:
            print(3 - self.player)

        # print(f"Time spent: {str(time.time() - self.start_time)}")
        # print(self.positions)
        return True

    # ===============================================================================================
    # ɅɅɅɅɅɅɅɅɅɅ END OF ASSIGNMENT 2 FUNCTIONS. ɅɅɅɅɅɅɅɅɅɅ
    # ===============================================================================================


if __name__ == "__main__":
    interface = CommandInterface()
    interface.main_loop()