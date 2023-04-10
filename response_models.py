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

class DraftBookListResponse(BaseModel):
    list: list[DraftBook] | None

class BookCollectionsList(BaseModel):
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
    Published_Year: str | None = Field(alias='Published Year', default=None)
    Published_By: str | None = Field(alias='Published By', default=None)
    Status: str
    ThumbImage: list[ThumbImageItem] | None = None
    BookCollections_List: list[BookCollectionsList] | None = Field(alias='BookCollections List', default=None)


class BookListResponse(BaseModel):
    list: list[Book] | None
    