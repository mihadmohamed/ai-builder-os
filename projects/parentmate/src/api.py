from fastapi import FastAPI
from pydantic import BaseModel

from projects.parentmate.src.extractor import extract_email
from projects.parentmate.src.storage import save_event

app = FastAPI()


class EmailInput(BaseModel):
    subject: str
    body: str


@app.post("/ingest")
def ingest_email(email: EmailInput):
    result = extract_email(email.subject, email.body)

    save_event(result.model_dump())

    return result
