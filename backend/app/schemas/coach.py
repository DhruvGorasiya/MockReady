from pydantic import BaseModel


class CoachScoreRequest(BaseModel):
    scores: dict[str, int]
    justification: str | None = None
