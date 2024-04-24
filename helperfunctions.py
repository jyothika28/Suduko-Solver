import numpy as np
import time
from strategies import *

# Some helper lists to iterate through houses
#################################################

# return columns' lists of cells
all_columns = [[(i, j) for j in range(9)] for i in range(9)]

# same for rows
all_rows = [[(i, j) for i in range(9)] for j in range(9)]

# same for blocks
# this list comprehension is unreadable, but quite cool!
all_blocks = [[((i//3) * 3 + j//3, (i % 3)*3+j % 3)
               for j in range(9)] for i in range(9)]

# combine three
all_houses = all_columns+all_rows+all_blocks


# Some helper functions
#################################################
# returns list [(0,0), (0,1) .. (a-1,b-1)]
# kind of like "range" but for 2d array
def range2(a, b):
    permutations = []
    for j in range(b):
        for i in range(a):
            permutations.append((i, j))
    return permutations


# Adding candidates instead of zeros
def pencil_in_numbers(puzzle):
    sudoku = np.empty((9, 9), dtype=object)
    for (j, i) in range2(9, 9):
        if puzzle[i, j] != 0:
            sudoku[i][j] = [puzzle[i, j], ]
        else:
            sudoku[i][j] = [i for i in range(1, 10)]
    return sudoku


# Count solved cells
def n_solved(sudoku):
    solved = 0
    for (i, j) in range2(9, 9):
        if len(sudoku[i, j]) == 1:
            solved += 1
    return solved


# Count remaining unsolved candidates to remove
def n_to_remove(sudoku):
    to_remove = 0
    for (i, j) in range2(9, 9):
        to_remove += len(sudoku[i, j])-1
    return to_remove


# Print full sudoku, with all candidates (rather messy)
def print_sudoku(sudoku):
    for j in range(9):
        out_string = "|"
        out_string2 = " " * 10 + "|"
        for i in range(9):
            if len(sudoku[i, j]) == 1:
                out_string2 += str(sudoku[i, j][0])+" "
            else:
                out_string2 += "  "

            for k in range(len(sudoku[i, j])):
                out_string += str(sudoku[i, j][k])
            for k in range(10 - len(sudoku[i, j])):
                out_string += " "
            if (i + 1) % 3 == 0:
                out_string += " | "
                out_string2 += "|"

        if (j) % 3 == 0:
            print ("-" * 99, " " * 10, "-" * 22)
        print (out_string, out_string2)
    print ("-" * 99,  " " * 10, "-" * 22)
