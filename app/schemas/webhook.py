from pydantic import BaseModel, Field
from typing import Any, Literal

class WebhookPayload(BaseModel):
    event_id: str = Field(min_length=1)
    event_type: str
    payment_id: str
    provider_payment_id: str = Field(min_length=1)
    status: Literal["SUCCESS", "FAILED"]

class WebhookResponse(BaseModel):
    status: str
