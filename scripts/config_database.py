from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./books_production.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}) # será usado para permitir as queries.  

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # cria uma base ORM para todos os modelos.