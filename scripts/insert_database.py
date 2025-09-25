from config_database import SessionLocal, Base, engine
from models import Book,FailedBook
from schema_pydantic import Books
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
from sqlalchemy import text


# Criar tabelas se não existirem.
Base.metadata.create_all(bind=engine)

def save_to_database(books_list):
    session = SessionLocal()
    saved_books = []
    failures = []

    for book in books_list:
        try:
            # INSERT OR IGNORE: não adiciona se o ID já existir
            sql = text("""
                INSERT OR IGNORE INTO books (id, title, price, category, rating, availability, image_url)
                VALUES (:id, :title, :price, :category, :rating, :availability, :image_url)
            """)
            session.execute(sql, {
                "id": book["id"],
                "title": book["title"],
                "price": book["price"],
                "category": book["category"],
                "rating": book["rating"],
                "availability": book["availability"],
                "image_url": book["image_url"]
            })
            saved_books.append(book)
        except Exception as e:
            failures.append({"book": book, "error": str(e)})

    session.commit()
    session.close()

    return {
        "saved": saved_books,
        "failures": failures
    }