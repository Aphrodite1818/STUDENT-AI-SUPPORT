from pydantic import BaseModel, ConfigDict, Field


class MetricsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class ChartPoint(MetricsBase):
    label: str
    value: int


class DashboardMetricsResponse(MetricsBase):
    stats: dict[str, int] = Field(default_factory=dict)
    charts: dict[str, list[ChartPoint]] = Field(default_factory=dict)
