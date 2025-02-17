from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.connection import get_db
from typing import List
from app.models import Book
from app.schemas import BookCreate, BookResponse
from sqlalchemy.exc import IntegrityError

router = APIRouter()

class BookService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_book(self, book: BookCreate) -> Book:
        '''
        Creates a new book in the database.

        Checks if a book with the same ISBN already exists in the database. If so, raises an HTTPException.
        Commits the new book to the database and handles integrity errors related to unique ISBN.

        Parameters:
            book (BookCreate): The book data to be added to the database.

        Returns:
            Book: The newly created book object.
        '''
        
        existing_book = self.db.query(Book).filter(Book.isbn == book.isbn).first()
        if existing_book:
            raise HTTPException(status_code=400, detail="Book with this ISBN already exists.")
        
        new_book = Book(**book.model_dump())
        self.db.add(new_book)
        try:
            self.db.commit()
            self.db.refresh(new_book)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to add book. ISBN must be unique.")
        
        return new_book

    def list_books(self, skip: int = 0, limit: int = 10) -> List[Book]:
        '''
        Retrieves a list of books from the database with pagination.

        Parameters:
            skip (int, optional): The number of books to skip for pagination. Defaults to 0.
            limit (int, optional): The number of books to retrieve. Defaults to 10.

        Returns:
            List[Book]: A list of books retrieved from the database.
        '''
        return self.db.query(Book).offset(skip).limit(limit).all()


class BookController:
    @staticmethod
    @router.post("/books/", response_model=BookResponse)
    def create_book(book: BookCreate, db: Session = Depends(get_db)) -> Book:
        return BookService(db).create_book(book)

    @staticmethod
    @router.get("/books/", response_model=List[BookResponse])
    def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[Book]:
        books = BookService(db).list_books(skip, limit)
        return books
