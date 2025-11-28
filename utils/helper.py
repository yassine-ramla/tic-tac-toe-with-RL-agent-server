def player_won(state, player):
  lines = [
              [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
              [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
              [0, 4, 8], [2, 4, 6]              # diagonals
          ]
  return any(all(state[i] == player for i in line) for line in lines)

def draw(state):
  return all(c != "#" for c in state)