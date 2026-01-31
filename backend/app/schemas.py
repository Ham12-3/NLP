from pydantic import BaseModel, field_validator
from typing import Literal


class CorrectionRequest(BaseModel):
    text: str
    variant: Literal["uk", "us"]

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Input text must not be empty.")
        return v


class Change(BaseModel):
    type: Literal["spelling", "grammar", "punctuation"]
    original: str
    replacement: str


class CorrectionResponse(BaseModel):
    corrected: str
    variant: Literal["uk", "us"]
    changes: list[Change]
