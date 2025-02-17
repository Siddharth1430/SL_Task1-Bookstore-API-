from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.connection import get_db
from app.models import Book
from app.schemas import BookCreate, BookResponse, BookUpdate
from sqlalchemy.exc import IntegrityError
from uuid import UUID

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

    def get_book(self, book_id: UUID) -> Book:
        '''
        Retrieves a specific book from the database by its ID.

        If the book with the given ID does not exist, raises an HTTPException.

        Parameters:
            book_id (UUID): The ID of the book to retrieve.

        Returns:
            Book: The book object retrieved from the database.
        '''
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    def update_book(self, book_id: UUID, book_data: BookUpdate) -> Book:
        '''
        Updates the data of an existing book in the database.

        If the book with the given ID does not exist, raises an HTTPException.
        Updates the book with the provided data and commits the changes.

        Parameters:
            book_id (UUID): The ID of the book to update.
            book_data (BookUpdate): The updated data for the book.

        Returns:
            Book: The updated book object.
        '''
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        for key, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, key, value)

        self.db.commit()
        self.db.refresh(book)
        return book

    def delete_book(self, book_id: UUID) -> None:
        '''
        Deletes a specific book from the database.

        If the book with the given ID does not exist, raises an HTTPException.
        Commits the deletion to the database.

        Parameters:
            book_id (UUID): The ID of the book to delete.
        '''
        book = self.db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        self.db.delete(book)
        self.db.commit()


@router.post("/books/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)) -> Book:
    return BookService(db).create_book(book)

@router.get("/books/", response_model=List[BookResponse])
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> List[Book]:
    return BookService(db).list_books(skip, limit)

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: UUID, db: Session = Depends(get_db)) -> Book:
    return BookService(db).get_book(book_id)

@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: UUID, book_data: BookUpdate, db: Session = Depends(get_db)) -> Book:
    return BookService(db).update_book(book_id, book_data)

@router.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: UUID, db: Session = Depends(get_db)) -> None:
    BookService(db).delete_book(book_id)
