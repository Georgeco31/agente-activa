from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard import current_ecuador_date, get_dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview_endpoint(
    db: DbSession,
    selected_date: Annotated[date | None, Query(alias="date")] = None,
    year: Annotated[int | None, Query(ge=2000, le=2100)] = None,
    month: Annotated[int | None, Query(ge=1, le=12)] = None,
):
    reference_date = selected_date or current_ecuador_date()
    return get_dashboard_overview(
        db,
        selected_date=reference_date,
        year=year or reference_date.year,
        month=month or reference_date.month,
    )
