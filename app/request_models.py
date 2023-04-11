from pydantic import BaseModel

from response_models import ThumbImageItem

class CreateNewBookRequest(BaseModel):
    DraftBookId: int
    Name: str | None = None
    Authors: str | None = None
    PublishedBy: str | None = None
    PublishedYear: int | None = None


class BookRequestToDb(BaseModel):
    Name: str | None = None
    Authors: str | None = None
    PublishedYear: int | None
    PublishedBy: str | None
    ThumbImage: list[ThumbImageItem] | None = None
    ThumbImageFeatureVector: str | None
