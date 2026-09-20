"""Book catalogue operations."""

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BookPage, BookQueryParams, BookUpdate


def create_book(db: Session, data: BookCreate) -> Book:
    """Add a book to the catalogue.

    Rules: the (already normalized) ISBN must be unique -> 409 otherwise.
    """
    existing = db.scalar(select(Book).where(Book.isbn == data.isbn))
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="A book with this ISBN already exists"
        )

    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> Book:
    """Return a book by id, or raise 404."""
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book:
    """Apply a partial update. Only fields present in the request are changed; 404 if missing."""
    book = get_book(db, book_id)
    updates = data.model_dump(exclude_unset=True)
    updates.pop("isbn", None)
    for field, value in updates.items():
        if hasattr(book, field):
            setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def list_books(db: Session, params: BookQueryParams) -> BookPage:
    """Search the catalogue.

    Rules:
    - ``q`` matches title OR author, case-insensitive substring.
    - ``restricted`` filters exactly; ``min_price``/``max_price`` are inclusive.
    - Sorted by ``sort`` (title / price, ``-`` for descending) with ties broken by id;
      default order is id ascending.
    - ``total`` counts all matches before ``limit``/``offset`` are applied.
    """
    query = select(Book)
    if params.q:
        escaped_q = params.q
        query = query.where(
            or_(
                Book.title.icontains(escaped_q, autoescape=True),
                Book.author.icontains(escaped_q, autoescape=True),
            )
        )
    if params.restricted is not None:
        query = query.where(Book.restricted == params.restricted)
    if params.min_price is not None:
        query = query.where(Book.price_cents >= params.min_price)
    if params.max_price is not None:
        query = query.where(Book.price_cents <= params.max_price)

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    if params.sort == "title":
        query = query.order_by(Book.title.asc(), Book.id.asc())
    elif params.sort == "-title":
        query = query.order_by(Book.title.desc(), Book.id.asc())
    elif params.sort == "price":
        query = query.order_by(Book.price_cents.asc(), Book.id.asc())
    elif params.sort == "-price":
        query = query.order_by(Book.price_cents.desc(), Book.id.asc())
    else:
        query = query.order_by(Book.id.asc())

    books = list(db.scalars(query.limit(params.limit).offset(params.offset)).all())
    return BookPage(items=books, total=total, limit=params.limit, offset=params.offset)
