from pydantic import BaseModel

from app.schemas.email import EmailCreate


class SendEmailResponse(BaseModel):
    status_code: int
    email: EmailCreate
    message : str
    class Config:
        allow_population_by_field_name = True


class FetchEmailsResponse(BaseModel):
    status_code: int
    count: int

    class Config:
        allow_population_by_field_name = True
