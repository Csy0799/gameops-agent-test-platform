from typing import List, Optional

from pydantic import BaseModel, Field


class ProbabilityValidateRequest(BaseModel):
    probability: float
    sample_size: int = 100000
    tolerance: float = 0.01
    seed: int = 42
    pity_threshold: Optional[int] = None


class ProbabilityValidateResponse(BaseModel):
    expected_probability: float
    actual_probability: float
    deviation: float
    sample_size: int
    tolerance: float
    pass_: bool = Field(alias="pass")
    warnings: List[str]
