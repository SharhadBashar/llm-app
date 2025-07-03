'''
    Base database configuration and setup.
'''
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import (
    DB_USER, DB_PASSWORD, DB_HOST, 
    DB_PORT, DB
)

load_dotenv()

DATABASE_URL = (
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}'
)

'''
    Database Configuration Parameters:

    pool_pre_ping=True:
    - Tests connections before using them, detecting stale or disconnected connections
    - Prevents 'connection has been closed' errors after idle periods

    autoflush=False:
    - Prevents automatic flushing of changes to the database before every query
    - Gives explicit control over when changes are persisted

    autocommit=False:
    - Forces us to use explicit transactions (this means changes are only commited when you call db.commit())
    - Also allows for rolling back changes if errors occur during processing
'''

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
