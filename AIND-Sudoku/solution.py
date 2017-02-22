assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
            tKeys = [box for box in unit if len(values[box]) == 2]
            for key in tKeys:
                istwinsKeys = [box for box in tKeys if values[box] == values[key]]
                if len(istwinsKeys) == 2:
                    restKeys = [box for box in unit if values[box] != values[key]]                    
                    for box in restKeys:
                        for value in values[key]:                           
                            values = assign_value(values, box, values[box].replace(value, ''))
                            
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [i+j for i in A for j in B]
    
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_unit = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']]
unitlist = row_units + column_units + square_units + diagonal_unit
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    """grid_dict = dict()
    for idx,val in enumerate(boxes):
        grid_dict[val] = '123456789' if grid[idx] == '.' else grid[idx]
        
    return grid_dict"""
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    values = dict(zip(boxes, chars))
    assignments.append(values.copy())
    return values


def display(values):
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print (''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF':
            print (line)
    return

def eliminate(values):
    solvedboxes = [box for box in values.keys() if len(values[box]) == 1]
    for key in solvedboxes:
        dgit = values[key]
        for pkey in peers[key]:
            """values[pkey] = values[pkey].replace(dgit, '')"""
            assign_value(values,pkey, values[pkey].replace(dgit, '') )
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
                assign_value(values,dplaces[0], digit )
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        print(solved_values_before)
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)      
      
        #remove naked twins
        values = naked_twins(values)       

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
        return values

def search(values):
    
    values = reduce_puzzle(values)
   
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
        
    # Choose one of the unfilled squares with the fewest possibilities
    minimumkey =  min((len(values[box]),box) for box in boxes if len(values[box]) > 1)
    
    for value in values[minimumkey[1]]:
        childSudoku = dict(values)
        childSudoku[minimumkey[1]] = value
        result = search(childSudoku)
        if result:
            return result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    result = solve(diag_sudoku_grid)
  
    display(result)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
