from pydantic import BaseModel

class GetDraftBookDetailRequest(BaseModel):
    draft_book_id: int