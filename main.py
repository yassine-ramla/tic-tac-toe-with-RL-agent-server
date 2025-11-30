from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from starlette.middleware.cors import CORSMiddleware
from utils.helper import *
import numpy as np
import threading
from contextlib import asynccontextmanager
# db
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Policy(Base):
    __tablename__ = "policy"
    state = Column(String(9), nullable=False, primary_key=True)
    value = Column(Float(), nullable=False)

class Statistics(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, nullable=False, primary_key=True)
    games = Column(Integer, nullable=False)
    loses = Column(Integer, nullable=False)
    draws = Column(Integer, nullable=False)

# Session-per-request DI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ## ensure data dir exists etc
    app_state["lock"] = threading.Lock()
    app_state["epsilon"] = 0.05
    app_state["decay"] = 0.9
    app_state["learning_rate"] = 0.3
    
    # database
    Base.metadata.create_all(bind=engine)
    
    yield
    app_state.clear()
    engine.dispose()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://tic-tac-toe-with-rl-agent.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # do not use ["*"] if allow_credentials=True
    allow_credentials=True,       # set True if you send cookies/auth headers
    allow_methods=["*"],
    allow_headers=["*"],
)

# pydantic models
class StateInput(BaseModel):
    previous_state: str
    current_state: str

class StateOutput(BaseModel):
    next_state: Optional[str]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/next-state", response_model=StateOutput)
async def compute_next_state(payload: StateInput, db: Session = Depends(get_db)):
    previous_state, current_state = (payload.previous_state, payload.current_state)
    
    lr = app_state["learning_rate"]
    eps = app_state["epsilon"]
    lock = app_state["lock"]

    with lock:
        try:
            # update the policy value of the previous state according to the next state
            db_previous_state = db.query(Policy).filter(Policy.state == previous_state).first()
            db_current_state = db.query(Policy).filter(Policy.state == current_state).first()

            if not db_previous_state or not db_current_state:
                raise HTTPException(status_code=404, detail="previous or current state not found")

            setattr(db_previous_state, "value", db_previous_state.value + lr * (db_current_state.value - db_previous_state.value))

            # select the possible next states

            # Check for wins
            stats = db.query(Statistics).first()

            if player_won(current_state, 'X'):
                setattr(stats, "loses", stats.loses + 1)
                setattr(stats, "games", stats.games + 1)
                next_state = None
            elif draw(current_state):
                setattr(stats, "draws", stats.draws + 1)
                setattr(stats, "games", stats.games + 1)
                next_state = None
            else:
                next_states = []
                for i, c in enumerate(db_current_state.state):
                    if c == "#":
                        next_states.append(db_current_state.state[:i] + "O" + db_current_state.state[i + 1:])

                db_next_states = db.query(Policy).filter(Policy.state.in_(next_states)).all()
                
                # group moves according to their value
                win_moves = [state for state in db_next_states if state.value <= 1 - 1e-4]
                good_moves = [state for state in db_next_states if 0.5 <= state.value < 1 - 1e-4]
                lose_moves = [state for state in db_next_states if state.value < 0.5]
                
                # choose the next state among the possible states
                if (np.random.rand() > eps):
                    if win_moves:
                        next_state=np.random.choice(win_moves)
                    elif good_moves:
                        next_state=np.random.choice([move for move in good_moves], p=np.array([move.value for move in good_moves]) / sum([move.value for move in good_moves]))
                    else:
                        next_state=np.random.choice(lose_moves)
                else:
                    next_state = np.random.choice(db_next_states)
                
                # update the policy value of the previous state according to the choosing next state
                setattr(db_current_state, "value", db_current_state.value + lr * (next_state.value - db_current_state.value))
                print(db_current_state)
                if player_won(next_state.state, "O"):
                    setattr(stats, "games", stats.games + 1)

                # save changes
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        app_state["epsilon"] = np.max(0.001, app_state["decay"] * app_state["epsilon"])
    return StateOutput(next_state=next_state.state if next_state else next_state)