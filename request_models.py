from pydantic import BaseModel, Field

from response_models import ThumbImageItem

class GetDraftBookDetailRequest(BaseModel):
    draft_book_id: int

class CreateNewBookRequest(BaseModel):
    draft_book_id: int
    name: str | None = None
    author: str | None = None
    published_by: str | None = None
    published_year: int | None = None


class BookRequestToDb(BaseModel):
    Name: str | None = None
    Authors: str | None = None
    PublishedYear: str | None = Field(alias='Published Year', default=None)
    PublishedBy: str | None = Field(alias='Published By', default=None)
    ThumbImage: list[ThumbImageItem] | None = None
    Thumb_Image_Feature_Vector: str | None = Field(alias='Thumb Image Feature Vector', default=None)