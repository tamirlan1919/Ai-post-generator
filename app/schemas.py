from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    source_type: Literal['rss', 'telegram']
    url: str = Field(..., min_length=1, max_length=500)
    enabled: bool = Field(default=True)


class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    enabled: Optional[bool] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    url: str
    enabled: bool
    created_at: datetime
    updated_at: datetime
    model_config = {'from_attributes': True}


class KeywordCreate(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    pattern: Optional[str] = Field(None, max_length=200)
    enabled: bool = Field(default=True)

    @field_validator('word')
    @classmethod
    def lowercase_word(cls, v: str) -> str:
        return v.lower().strip()


class KeywordResponse(BaseModel):
    id: int
    word: str
    pattern: Optional[str]
    enabled: bool
    created_at: datetime
    model_config = {'from_attributes': True}


class Post(BaseModel):
    id: int
    news_id: str
    generated_text: str
    status: str
    published_at: Optional[datetime]
    created_at: datetime
    model_config = {'from_attributes': True}


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class MessageResponse(BaseModel):
    message: str