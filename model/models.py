from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union

class Metadata(BaseModel):
    summary: List[str] = Field(default_factory = list, description = "Summary of the document")
    Title: str
    Author: str
    DateCreated: str
    Published: str
    Language: str
    PageCount: Union[int, str]
    SentimentTone: str

class ChangeFormat(BaseModel):
    page: str
    changes: str

class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass