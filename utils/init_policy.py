import pandas as pd

lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]              # diagonals
        ]

with open('../data/tictactoe_states.txt') as f:
  all_states = [state.replace('\n', '') for state in list(f)]

policy = pd.DataFrame({
  "state": all_states,
  "value": [0 if any(state[a] == state[b] == state[c] == 'X' for [a, b, c] in lines) else 1 if any(state[a] == state[b] == state[c] == 'O' for [a, b, c] in lines) else 0.5 for state in all_states]
}).set_index('state', drop=True)

# ! warning: this line will reinitialize the policy entirely
# policy.to_csv('make_sure_you_want_to_reinitialize_the_policy/../data/policy.csv')