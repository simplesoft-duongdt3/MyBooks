from pydantic import BaseModel

class Paging(BaseModel):
    isFirstPage: bool
    isLastPage: bool
    totalRows: int
    page: int
    pageSize: int

class ThumbImageItem(BaseModel):
    mimetype: str
    size: int
    title: str
    path: str

class DraftBook(BaseModel):
    Id: int
    ThumbImage: list[ThumbImageItem] | None = None
    CreatedAt: str
    UpdatedAt: str
    Status: str

class DraftBookFromDb(DraftBook):
    ThumbImageFeatureVector: str | None

class DraftBookListResponse(BaseModel):
    draftBooks: list[DraftBook] | None
    paging: Paging

class DraftBookListResponseFromDb(BaseModel):
    list: list[DraftBookFromDb] | None
    pageInfo: Paging

class BookCollectionsListItem(BaseModel):
    Id: int
    Name: str | None = None
    CreatedAt: str
    UpdatedAt: str

class Book(BaseModel):
    Id: int
    Name: str | None = None
    CreatedAt: str
    UpdatedAt: str
    Authors: str | None = None
    PublishedYear: str | None
    PublishedBy: str | None
    Status: str
    ThumbImage: list[ThumbImageItem] | None = None

class BookFromDb(Book):
    ThumbImageFeatureVector: str | None

class BookListResponse(BaseModel):
    books: list[Book] | None
    paging: Paging

class BookListResponseFromDb(BaseModel):
    list: list[BookFromDb] | None
    pageInfo: Paging

class BookSimilarItem(Book):
    distance: float

class ListBookSimilarResponse(BaseModel):
    listBookSimilar: list[BookSimilarItem]

class CreateDraftBookResponse(BaseModel):
    draftBook: DraftBook
    listBookSimilar: list[BookSimilarItem]