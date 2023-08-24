from pydantic import BaseModel, constr, field_validator


class Message(BaseModel):
    text: constr(min_length=1)

    @field_validator("text", mode="before")
    @classmethod
    def validate_message(cls, v):
        if isinstance(v, str):
            v = v.replace("text=", "").replace("+", " ")
        return v


class Mailing(BaseModel):
    timestamp: float
    SMSText: constr(min_length=1)
    mailingId: str
    totalSMSAmount: int
    deliveredSMSAmount: int
    failedSMSAmount: int

    @field_validator("mailingId", mode="before")
    @classmethod
    def validate_mailing_id(cls, v):
        if isinstance(v, int):
            v = str(v)
        return v
