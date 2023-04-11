from pydantic import BaseModel, Field

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
    Thumb_Image_Feature_Vector: str | None = Field(alias='Thumb Image Feature Vector', default=None)

class DraftBookListResponse(BaseModel):
    draftBooks: list[DraftBook] | None

class DraftBookListResponseFromDb(BaseModel):
    list: list[DraftBookFromDb] | None

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
    PublishedYear: str | None = Field(alias='Published Year', default=None)
    PublishedBy: str | None = Field(alias='Published By', default=None)
    Status: str
    ThumbImage: list[ThumbImageItem] | None = None

class BookFromDb(Book):
    Thumb_Image_Feature_Vector: str | None = Field(alias='Thumb Image Feature Vector', default=None)

class BookListResponse(BaseModel):
    books: list[Book] | None

class BookListResponseFromDb(BaseModel):
    list: list[BookFromDb] | None

class BookSimilarItem(Book):
    distance: float

class ListBookSimilarResponse(BaseModel):
    listBookSimilar: list[BookSimilarItem]

class CreateDraftBookResponse(BaseModel):
    draftBook: DraftBook
    listBookSimilar: list[BookSimilarItem]