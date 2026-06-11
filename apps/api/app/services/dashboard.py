import calendar
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.repositories import dashboard as dashboard_repository
from app.schemas.dashboard import (
    DashboardAlertResponse,
    DashboardDailySalesResponse,
    DashboardOverviewResponse,
    DashboardStatusCountResponse,
    DashboardSummaryResponse,
)

ECUADOR_TIMEZONE = ZoneInfo("America/Guayaquil")
ZERO_AMOUNT = Decimal("0.00")
AMOUNT_PRECISION = Decimal("0.01")

STATUS_SUMMARY_FIELDS = {
    "pendiente": "pending_orders",
    "asignado": "assigned_orders",
    "en_camino": "en_route_orders",
    "entregado": "delivered_orders",
    "no_entregado": "not_delivered_orders",
    "cancelado": "cancelled_orders",
}

ALERT_DEFINITIONS = {
    "pendiente": ("pending_orders", "Pedidos pendientes", "warning"),
    "en_camino": ("en_route_orders", "Pedidos en camino", "info"),
    "no_entregado": ("not_delivered_orders", "Pedidos no entregados", "danger"),
    "cancelado": ("cancelled_orders", "Pedidos cancelados", "warning"),
}


def current_ecuador_date() -> date:
    return datetime.now(ECUADOR_TIMEZONE).date()


def _amount(value: Decimal) -> Decimal:
    return Decimal(value).quantize(AMOUNT_PRECISION)


def _utc_day_range(selected_date: date) -> tuple[datetime, datetime]:
    start_local = datetime.combine(selected_date, time.min, tzinfo=ECUADOR_TIMEZONE)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def _utc_month_range(year: int, month: int) -> tuple[datetime, datetime]:
    start_local = datetime(year, month, 1, tzinfo=ECUADOR_TIMEZONE)
    if month == 12:
        end_local = datetime(year + 1, 1, 1, tzinfo=ECUADOR_TIMEZONE)
    else:
        end_local = datetime(year, month + 1, 1, tzinfo=ECUADOR_TIMEZONE)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)


def get_dashboard_overview(
    db: Session,
    *,
    selected_date: date,
    year: int,
    month: int,
) -> DashboardOverviewResponse:
    day_start, day_end = _utc_day_range(selected_date)
    month_start, month_end = _utc_month_range(year, month)

    status_metrics = dashboard_repository.get_daily_status_metrics(
        db,
        start_at=day_start,
        end_at=day_end,
    )
    monthly_metrics = dashboard_repository.get_monthly_sales(
        db,
        start_at=month_start,
        end_at=month_end,
    )
    catalog_metrics = dashboard_repository.get_catalog_metrics(db)
    recent_orders = dashboard_repository.get_recent_orders(db)

    status_counts = {code: 0 for code in STATUS_SUMMARY_FIELDS}
    sales_total_today = ZERO_AMOUNT
    orders_by_status: list[DashboardStatusCountResponse] = []
    for metric in status_metrics:
        status_counts[metric.code] = metric.count
        if metric.code == "entregado":
            sales_total_today = _amount(metric.total)
        orders_by_status.append(
            DashboardStatusCountResponse(
                code=metric.code,
                name=metric.name,
                count=metric.count,
            )
        )

    monthly_by_date = {metric.sale_date: metric for metric in monthly_metrics}
    monthly_sales: list[DashboardDailySalesResponse] = []
    sales_total_month = ZERO_AMOUNT
    for day_number in range(1, calendar.monthrange(year, month)[1] + 1):
        sale_date = date(year, month, day_number)
        metric = monthly_by_date.get(sale_date)
        sales_total = _amount(metric.sales_total) if metric else ZERO_AMOUNT
        delivered_orders_count = metric.delivered_orders_count if metric else 0
        sales_total_month += sales_total
        monthly_sales.append(
            DashboardDailySalesResponse(
                day=day_number,
                date=sale_date,
                sales_total=sales_total,
                delivered_orders_count=delivered_orders_count,
            )
        )

    summary_values = {
        field_name: status_counts[code] for code, field_name in STATUS_SUMMARY_FIELDS.items()
    }
    summary = DashboardSummaryResponse(
        orders_today=sum(status_counts.values()),
        sales_total_today=sales_total_today,
        sales_total_month=sales_total_month,
        active_products=catalog_metrics.active_products,
        total_customers=catalog_metrics.total_customers,
        **summary_values,
    )

    alerts = [
        DashboardAlertResponse(
            code=summary_field,
            label=label,
            count=getattr(summary, summary_field),
            severity=severity,
            status_code=status_code,
        )
        for status_code, (summary_field, label, severity) in ALERT_DEFINITIONS.items()
        if getattr(summary, summary_field) > 0
    ]

    return DashboardOverviewResponse(
        selected_date=selected_date,
        month=month,
        year=year,
        summary=summary,
        orders_by_status=orders_by_status,
        monthly_sales=monthly_sales,
        recent_orders=recent_orders,
        alerts=alerts,
    )
