from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    service: str


class DatabaseHealthStatus(BaseModel):
    status: str
    database: str
