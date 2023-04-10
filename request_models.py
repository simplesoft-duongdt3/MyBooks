from pydantic import BaseModel

class GetDraftBookDetailRequest(BaseModel):
    draft_book_id: int

class CreateNewBookRequest(BaseModel):
    draft_book_id: int
    name: str | None = None
    author: str | None = None
    published_by: str | None = None
    published_year: int | None = None

