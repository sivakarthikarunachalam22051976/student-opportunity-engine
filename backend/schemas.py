from pydantic import BaseModel
from typing import Optional, List


class OpportunityData(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    year: List[str] = []
    branches: List[str] = []
    skills: List[str] = []
    location: Optional[str] = None
    remote: Optional[bool] = None
    deadline: Optional[str] = None
    stipend: Optional[float] = None
    documents: List[str] = []