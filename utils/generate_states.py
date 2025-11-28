def generate_all_states():
    """Generate all possible tic-tac-toe board states."""
    states = []
    
    def generate(board, pos):
        if pos == 9:
            states.append(''.join(board))
            return
        
        # Try empty space
        board[pos] = '#'
        generate(board, pos + 1)
        
        # Try X
        board[pos] = 'X'
        generate(board, pos + 1)
        
        # Try O
        board[pos] = 'O'
        generate(board, pos + 1)
    
    generate(['#'] * 9, 0)
    return states

def is_valid_state(state):
    """Check if a state is valid (respects turn order and win conditions)."""
    x_count = state.count('X')
    o_count = state.count('O')
    
    # X goes first, so X count should be equal to O count or one more
    if x_count < o_count or x_count > o_count + 1:
        return False
    
    # Check for wins
    def has_won(player):
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]
        for line in lines:
            if all(state[i] == player for i in line):
                return True
        return False
    
    x_won = has_won('X')
    o_won = has_won('O')
    
    # Both players can't win
    if x_won and o_won:
        return False
    
    # If X won, O shouldn't have played after
    if x_won and x_count == o_count:
        return False
    
    # If O won, X shouldn't have played after
    if o_won and x_count > o_count:
        return False
    
    return True

# Generate all states
print("Generating all possible states...")
all_states = generate_all_states()
print(f"Total possible states: {len(all_states)}")

# Filter for valid states
print("\nFiltering for valid game states...")
valid_states = [s for s in all_states if is_valid_state(s)]
print(f"Valid game states: {len(valid_states)}")

# Display some examples
print("\nFirst 20 valid states:")
for i, state in enumerate(valid_states[:20], 1):
    print(f"{i:3d}. {state}")

# Optional: Save all valid states to a file
save_to_file = input("\nSave all valid states to file? (y/n): ").lower()
if save_to_file == 'y':
    with open('tictactoe_states.txt', 'w') as f:
        for state in valid_states:
            f.write(state + '\n')
    print(f"Saved {len(valid_states)} states to tictactoe_states.txt")