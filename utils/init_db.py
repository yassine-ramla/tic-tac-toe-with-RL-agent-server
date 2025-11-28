import pandas as pd
from sqlalchemy import create_engine

stats = pd.read_csv("../data/statistics.csv")
policy = pd.read_csv("../data/policy.csv", index_col='state')

engine = create_engine("sqlite:///tic-tac-toe.db")

stats.to_sql(name="statistics", con=engine, if_exists="replace", index=False)
policy.to_sql(name="policy", con=engine, if_exists="replace")