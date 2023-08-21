from pydantic import BaseModel, constr, field_validator


class Message(BaseModel):
    text: constr(min_length=1)

    @field_validator("text", mode="before")
    @classmethod
    def validate_message(cls, v):
        if isinstance(v, str):
            v = v.replace("text=", "").replace("+", " ")
        return v
