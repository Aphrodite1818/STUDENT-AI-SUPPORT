from pydantic import BaseModel, ConfigDict


class OutputBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TenantSearchResult(OutputBase):
    label: str
    role: str
    metadata: str | None = None
    admission_number: str | None = None
    staff_id: str | None = None
    class_name: str | None = None
    subject_name: str | None = None
    email: str | None = None
    href: str


class TenantSearchResponse(OutputBase):
    items: list[TenantSearchResult]
    total: int
