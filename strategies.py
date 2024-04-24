import numpy as np
import time
from strategies import *
from helperfunctions import *

# The 7 methods solver is using
#########################################

# 0. Simple Elimination
# If a cell has only one candidate, put it there
###################################
def simple_elimination(sudoku):
    count = 0
    for group in all_houses:
        for cell in group:
            if len(sudoku[cell]) == 1:
                for cell2 in group:
                    if sudoku[cell][0] in sudoku[cell2] and cell2 != cell:
                        sudoku[cell2].remove(sudoku[cell][0])
                        count += 1
    return count


# 1. Hidden Single
# If there is only one cell in the house that can contain a number - put it there
###################################
def hidden_single(sudoku):

    def find_only_number_in_group():
        nonlocal group
        nonlocal number
        count = 0
        removed = 0
        cell_to_clean = (-1, -1)
        for cell in group:
            for n in sudoku[cell]:
                if n == number:
                    count += 1
                    cell_to_clean = cell
        if count == 1 and cell_to_clean != (-1, -1) \
           and len(sudoku[cell_to_clean]) > 1:
            removed = len(sudoku[cell_to_clean]) - 1
            sudoku[cell_to_clean] = [number]
        return removed

    count = 0
    for number in range(1, 10):
        for group in all_houses:
            count += find_only_number_in_group()
    return count


# 2. CSP
# brute force CSP solution for each cell:
# it covers hidden and naked pairs, triples, quads
################################################
def csp_list(inp):

    perm = []

    # get all permutations
    def append_permutations(sofar):
        nonlocal inp
        for n in inp[len(sofar)]:
            if len(sofar) == len(inp) - 1:
                perm.append(sofar + [n])
            else:
                append_permutations(sofar + [n])

    append_permutations([])

    # remove duplicates
    for i in range(len(perm))[::-1]:
        if len(perm[i]) != len(set(perm[i])):
            del perm[i]

    
    out = []
    for i in range(len(inp)):
        out.append([])
        for n in range(10):
            for p in perm:
                if p[i] == n and n not in out[i]:
                    out[i].append(n)
    return out


def csp(s):
    count = 0
    for group in all_houses:
        house = []
        for cell in group:
            house.append(s[cell])
        house_csp = csp_list(house)
        if house_csp != house:
            for i in range(len(group)):
                if s[group[i]] != house_csp[i]:
                    count += len(s[group[i]]) - len(house_csp[i])
                    s[group[i]] = house_csp[i]
    return count


# 3. Intersection
# If a number can only be in one line of a block - remove it from other cells in that line
#############################################
def n_from_cells(s, cells):
    numbers = []
    for cell in cells:
        numbers += s[cell]
    return list(set(numbers))

def remove_n_from_cells(s, n, cells):
    count = 0
    for cell in cells:
        if n in s[cell]:
            s[cell].remove(n)
            count += 1
    return count

def intersect(s):
    count = 0
    for block in all_blocks:
        for line in all_rows + all_columns:

            # get the block/line/intersection coords
            sblock = set(block)
            sline = set(line)
            both = sblock.intersection(line)
            if len(both) == 0:
                continue  # if no intersection - go to next
            only_b = sblock.difference(both)
            only_l = sline.difference(both)

            # get the numbers from those region
            n_only_b = n_from_cells(s, only_b)
            n_both = n_from_cells(s, both)
            n_only_l = n_from_cells(s, only_l)

            # go through all numbers
            for i in range(1, 10):
                if i in n_both and i in n_only_b and i not in n_only_l:
                    count += remove_n_from_cells(s, i, list(only_b))
                if i in n_both and i not in n_only_b and i in n_only_l:
                    count += remove_n_from_cells(s, i, list(only_l))
    return count


# 4. X-Wing
# If a number can only be in two lines of two blocks - remove it from other cells in those lines
##################################################
def n_from_cells_dup(s, cells):
    numbers = []
    for cell in cells:
        numbers += s[cell]
    return numbers


def x_wing(s):
    count = 0
    for h1 in range(0, 9):
        for h2 in range(h1 + 1, 9):
            for v1 in range(0, 9):
                for v2 in range(v1 + 1, 9):
                    hline1 = all_rows[h1]
                    hline2 = all_rows[h2]
                    vline1 = all_columns[v1]
                    vline2 = all_columns[v2]

                    s_rows = set(hline1).union(set(hline2))
                    s_cols = set(vline1).union(set(vline2))
                    cross_4 = s_rows.intersection(s_cols)
                    if len(cross_4) != 4:
                        continue  # wrong cross-section
                    only_row = s_rows.difference(cross_4)
                    only_col = s_cols.difference(cross_4)

                    # get the numbers from those region
                    n_cross = n_from_cells_dup(s, cross_4)
                    n_only_row = n_from_cells(s, only_row)
                    n_only_col = n_from_cells(s, only_col)

                    # go through all numbers
                    for i in range(1, 10):
                        if n_cross.count(i) == 4:
                            if i in n_only_row and i not in n_only_col:
                                count += \
                                      remove_n_from_cells(s, i, list(only_row))
                            if i not in n_only_row and i in n_only_col:
                                count += \
                                      remove_n_from_cells(s, i, list(only_col))
    # print ("X:", time.time()-t)
    return count






# 5. 3D Medusa
# If a number can only be in two lines of two blocks - remove it from other cells in those lines
##############
def get_all_bicells(s):
    bicells = []
    for (i, j) in range2(9, 9):
        if len(s[i, j]) == 2:
            bicells.append([(i, j), s[i, j][0], s[i, j][1]])
    return bicells


# get all chains of links and bicells
def get_medusa_chains(links_original, bicells_original):
    links = links_original.copy()
    bicells = bicells_original.copy()
    groups = []
    while len(links):
        has_to_add = True
        groups.append([])
        groups[-1].append(links[0])
        del (links[0])
        while has_to_add:
            has_to_add = False
            for link in groups[-1]:
                if type(link[1]) == tuple:  # it's a link
                    for cell in link[0:2]:
                        # add other links
                        for i in range(len(links))[::-1]:
                            if (links[i][0] == cell or links[i][1] == cell) \
                                    and link[2] == links[i][2]:
                                groups[-1].append(links[i])
                                del (links[i])
                                has_to_add = True
                        # add other bicells
                        for i in range(len(bicells))[::-1]:
                            if bicells[i][0] == cell \
                                    and (link[2] == bicells[i][1] \
                                    or link[2] == bicells[i][2]):
                                groups[-1].append(bicells[i])
                                del (bicells[i])
                                has_to_add = True
                else:  # it's a bicell
                    # add other links
                    for i in range(len(links))[::-1]:
                        if (links[i][0] == link[0]
                                or links[i][1] == link[0]) \
                                and (links[i][2] == link[1]
                                or links[i][2] == link[2]):
                            groups[-1].append(links[i])
                            del (links[i])
                            has_to_add = True
    return groups


# get all chains of links and bicells
def cell_in_ab_medusa_chain(cell, chain, n):
    for link in chain:
        if link[0] == cell and n == link[1]:
                return True
    return False

# get all chains of links and bicells
def ab_group_medusa(chain):
    a = [(chain[0][0], chain[0][2]),]
    b = [(chain[0][1], chain[0][2]),]
    keep_going = True
    while keep_going:
        keep_going = False
        for link in chain:
            if type(link[1]) == tuple:  # it's a link
                if cell_in_ab_medusa_chain(link[0], a, link[2]) and not cell_in_ab_medusa_chain(link[1], b, link[2]):
                    b.append((link[1], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[0], b, link[2]) and not cell_in_ab_medusa_chain(link[1], a, link[2]):
                    a.append((link[1], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[1], a, link[2]) and not cell_in_ab_medusa_chain(link[0], b, link[2]):
                    b.append((link[0], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[1], b, link[2]) and not cell_in_ab_medusa_chain(link[0], a, link[2]):
                    a.append((link[0], link[2]))
                    keep_going = True
            else: # it's a bicell
                if cell_in_ab_medusa_chain(link[0], a, link[1]) and not cell_in_ab_medusa_chain(link[0], b, link[2]):
                    b.append((link[0], link[2]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], b, link[1]) and not cell_in_ab_medusa_chain(link[0], a, link[2]):
                    a.append((link[0], link[2]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], a, link[2]) and not cell_in_ab_medusa_chain(link[0], b, link[1]):
                    b.append((link[0], link[1]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], b, link[2]) and not cell_in_ab_medusa_chain(link[0], a, link[1]):
                    a.append((link[0], link[1]))
                    keep_going = True                    
    return  (a, b)

#
def same_color_twice_in_cell(s, a):
    count = 0 
    for cell1 in a:
        for cell2 in a:
            if cell1[0] == cell2[0] and cell1[1] != cell2[1]:
                for cell in a:
                    count += remove_n_from_cells(s, cell[1], (cell[0],))
    return count

def twice_in_a_house_medusa(s, a):
    count = 0
    for house in all_houses:
        n_count = [0] * 9
        for cell in a:
            if cell[0] in house:
                n_count[cell[1] - 1] += 1
        if n_count.count(2) > 0:
            pass
            # this one is not finished, cause I haven't found any examples in my set
    return count
        
def two_colors_in_a_cell(s, a, b):
    count = 0
    for (i, j) in range2(9, 9):
        found_colors = []
        if len(s[i,j])>2:
            for cell in a+b:
                if cell[0] == (i, j):
                    found_colors.append(cell[1])
        if len(found_colors) > 1:
            for n in s[i, j]:
                if n not in found_colors:
                    s[i, j].remove(n)
                    count += 1
    return count


def cell_in_chain(cell, chain):
    for link in chain:
        if link[0] == cell:
                return True
    return False


def two_colors_elsewhere_medusa(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):
        if not cell_in_chain((i, j), all_a) and not cell_in_chain((i,j), all_b):
            for n in s[i, j]:
                spotted_a, spotted_b = False, False
                for house in all_houses:
                    if (i, j) in house:
                        for a in all_a:
                            if a[0] in house and a[1] == n:
                                spotted_a = True
                        for b in all_b:
                            if b[0] in house and b[1] == n:
                                spotted_b = True
                if spotted_a and spotted_b:
                    s[i, j].remove(n)
                    count += 1
    return count

# get the number from the chain
def get_n_cell_in_chain(needle_cell, chain):
    for cell in chain:
        if cell[0] == needle_cell:
            return cell[1]
    return None


def two_colors_unit_cell(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):  # go through all cells
        for (a, b) in [(all_a, all_b), (all_b, all_a)]:  # A-cell, B-house; then the other way round
            if len(s[i, j])>1 and cell_in_chain((i, j), a) and not cell_in_chain((i, j), b): # 2+ numbers in cell, from one chain, but not from the other
                in_cell = get_n_cell_in_chain((i, j), a)  # The number that is from the chain
                for n in s[(i, j)]: # Go through all numbers in the cell
                    if n != in_cell:  # Except for the one from the chain
                        for house in all_houses:  # Look at all houses
                            if (i, j) in house:  # That the cell can see
                                for cell in house:  # and then look through house's cells
                                    if cell_in_chain(cell, b) and get_n_cell_in_chain(cell, b) == n: # Is there an item from another chain
                                        if n in s[i, j]:  # In case we've done it already
                                            s[i, j].remove(n)
                                            count += 1
    return count

def empty_by_color(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):
        for (a, b) in [(all_a, all_b), (all_b, all_a)]:
            if len(s[i, j])>1 and not cell_in_chain((i, j), a) and not cell_in_chain((i, j), b):
                found = []
                for n in s[i, j]:
                    for house in all_houses:
                        if (i, j) in house:
                            for cell in house:
                                if cell_in_chain(cell, a) and get_n_cell_in_chain(cell, a) == n:
                                    found.append( get_n_cell_in_chain(cell, a) )
                if set(found) == set(s[i, j]):
                    for cell in a: 
                        if cell[1] in s[cell[0]]:
                            s[cell[0]].remove(cell[1])
                            count += 1
                    return count
    return count

def get_a_hard_link(s, n, group, add_n=False):
    links = []
    for cell in group:
        if n in s[cell]:
            links.append(cell)
    if len(links) == 2:
        if add_n:
            links.append(n)
        return links
    return []


def get_all_hard_links(s, n, add_n=False):
    hard_links = []
    for group in all_houses:
        new_link = get_a_hard_link(s, n, group, add_n)
        if new_link != [] and new_link not in hard_links:
            hard_links.append(new_link)
    return hard_links
def medusa_3d(s):
    count = 0
    hard_links = []
    for n in range(1, 10):
        hard_links += get_all_hard_links(s, n, add_n=True)
    bicells = get_all_bicells(s)
    chains = get_medusa_chains(hard_links, bicells)
    for chain in chains:
        if len(chain) > 1:
            a, b = ab_group_medusa(chain)
            count += same_color_twice_in_cell(s, a)
            count += same_color_twice_in_cell(s, b)
            count += twice_in_a_house_medusa(s, a)
            count += twice_in_a_house_medusa(s, b)
            count += two_colors_in_a_cell(s, a, b)
            count += two_colors_elsewhere_medusa(s, a, b)
            count += two_colors_unit_cell(s, a, b)
            count += empty_by_color(s, a, b)
    return count


# 6. Backtracking
# If all else fails, try all possible combinations
#####################

def cellInHouse():
    out = {(-1, -1):[]}
    for (i, j) in range2(9, 9):
        out[(i,j)] = []
        for h in all_houses:
            if (i, j) in h:
                out[(i, j)].append(h)
    return out

def get_next_cell_to_force(s):
    for (i, j) in range2(9, 9):
        if len(s[i, j])>1:
            return (i, j)


def brute_force(s, verbose):
    solution = []
    t = time.time()
    iter_counter = 0

    cellHouse = cellInHouse()
    
    def is_broken(s, last_cell):
        for house in cellHouse[last_cell]:
            house_data = []
            for cell in house:
                if len(s[cell]) == 1:
                    house_data.append(s[cell][0])
            if len(house_data) != len(set(house_data)):
                return True
        return False

    def iteration(s, last_cell=(-1,-1)):
        nonlocal solution
        nonlocal iter_counter

        iter_counter += 1
        if iter_counter%200000 == 0 and verbose:
            print ("Iteration", iter_counter)

        # is broken - return fail
        if is_broken(s, last_cell):
            return -1

        # is solved - return success
        if n_to_remove(s) == 0:
            #print ("Solved")
            solution = s
            return 1

        
        next_cell = get_next_cell_to_force(s)

        # go through all candidates
        for n in s[next_cell]:
            scopy = s.copy()
            scopy[next_cell] = [n]
            result = iteration(scopy, next_cell)
            if result == 1:
                return

    iteration(s)

    if len(solution)>0:
        if verbose:
            print ("Time taken by Backtracking strategy is :", time.time()-t, "seconds, with", iter_counter, "attempts made")
        return solution

    
    print ("The puzzle appears to be broken")
    return s


# Main Solver
#############
report_list=[]
def solve(original_puzzle, verbose):

    report = [0]*7

    puzzle = pencil_in_numbers(original_puzzle)
    solved = n_solved(puzzle)
    to_remove = n_to_remove(puzzle)
    if verbose:
        print ("Initial puzzle")
        print("-"*15)
        print("Number of pre-filled cells: ", solved, "/81.")
        print("Candidates to remove:", to_remove)

    t = time.time()

    # Control how solver goes through the methods:
    # False - go back to previous method if the next one yeild results
    # True - try all methods one by one and then go back
    all_at_once = False

    while to_remove != 0:
        r_step = 0
        r0 = simple_elimination(puzzle)
        report[0] += r0
        r_step += r0
        
        if all_at_once or r_step == 0:
            r1 = hidden_single(puzzle)
            report[1] += r1
            r_step += r1

        if all_at_once or r_step == 0:
            r2 = csp(puzzle)
            report[2] += r2
            r_step += r2

        if all_at_once or r_step == 0:
            r3 = intersect(puzzle)
            report[3] += r3
            r_step += r3

        if all_at_once or r_step == 0:
            r4 = x_wing(puzzle)
            report[4] += r4
            r_step += r4
            
        if all_at_once or r_step == 0:
            r5 = medusa_3d(puzzle)
            report[5] += r5
            r_step += r5

        # check state
        solved = n_solved(puzzle)
        to_remove = n_to_remove(puzzle)

        # Nothing helped, logic failed
        if r_step == 0:
            break

    #print_sudoku(puzzle)
    if verbose:
        print()
        print("Solved with logic: number of complete cells", solved,"/81. Candidates to remove:", to_remove)
        print("Time taken by strategies except backtracking is ", time.time() - t)

    if to_remove > 0:
        for_brute = n_to_remove(puzzle)
        puzzle = brute_force(puzzle, verbose)
        report[6] += for_brute

    #Strategies used
    legend = [
            'Simple elimination',
            'Hidden single',
            'CSP',
            'Intersection',
            'X-Wing',
            '3D Medusa',
            'Backtracking']
    if verbose:
        print ("These are the methods used to solve the Puzzle:")
        #print("report list",report)
        index=1
        report_list.append(report)
        for i in range(len(legend)):
            if(report[i] > 0):
                print ("\t", index, legend[i], ":", report[i])
                index+=1
    return puzzle,report_list

# Print Sudoku board
def print_board(board):
    """Prints the Sudoku board."""
    print()
    print("Solved Puzzle")
    print("="*45)
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            print("- "*23)
        for j, cell in enumerate(row):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")
            if j == 8:
                print(cell)
            else:
                print(str(cell) + " ", end="")
    
def solve_from_line(line, verbose=False):
    s_str = ""
    raw_s = line[0:81]
    for ch in raw_s:
        s_str += ch + " "
    s_np1 = np.fromstring(s_str, dtype=int, count=-1, sep=' ')
    s_np = np.reshape(s_np1, (9, 9))
    puzzle,report_list=solve(s_np, verbose)
    return print_board(puzzle),report_list
          