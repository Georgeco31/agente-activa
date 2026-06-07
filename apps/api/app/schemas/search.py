from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DuplicateDetectionRequest(BaseModel):
    phone: str | None = None
    name: str | None = None
    alias: str | None = None
    address: str | None = None
    reference: str | None = None


class DuplicateCandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID
    display_name: str
    reasons: list[str]
    score: int
    confidence: str
