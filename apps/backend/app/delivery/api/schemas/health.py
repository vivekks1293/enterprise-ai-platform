from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class DatabaseDiagnosticResponse(BaseModel):
    current_database: str | None
    current_schema: str | None
    current_user: str | None
    inet_server_addr: str | None
    inet_server_port: int | None
    search_path: str | None
    table_exists: bool