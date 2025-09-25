from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from config_database import Base


# Vai criar a tabela dos livros que vem do scrapping (validação com dados do pydantic)
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    rating = Column(Integer, nullable=True) # rating será opicional
    availability = Column(String, nullable=True) # availability será opicional
    image_url = Column(String, nullable=True) # image_url  será opicional

class FailedBook(Base):
    __tablename__ = "failed_books"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)  # data/hora da falha


# Cria tabela de usuários, todos os campos são obrigatórios (password será hasheado depois)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

