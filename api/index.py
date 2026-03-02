import sys
from pathlib import Path

# Vercel serverless functions run from the api/ directory.
# Add the project root to sys.path so that `src` package is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.config import load_config
from src.data_processor import (
    aggregate_by_field,
    aggregate_by_tags,
    aggregate_tags_over_time,
    aggregate_ticket_counts,
    tickets_to_dataframe,
)
from src.zendesk_client import ZendeskClient

app = FastAPI()


def _get_client() -> ZendeskClient:
    config = load_config()
    return ZendeskClient(config)


@app.get("/api/health")
def health():
    try:
        load_config()
        return {"status": "ok"}
    except ValueError as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})


@app.get("/api/tickets/trends")
def ticket_trends(
    start_date: date = Query(...),
    end_date: date = Query(...),
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    status: list[str] | None = Query(None),
    priority: str | None = Query(None),
):
    client = _get_client()
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority

    raw = client.fetch_tickets_by_date_chunks(start_date, end_date, **filters)
    df = tickets_to_dataframe(raw)
    trend = aggregate_ticket_counts(df, period=period)

    return {
        "total": len(df),
        "trend": trend.to_dict(orient="records"),
    }


@app.get("/api/tickets/categories")
def ticket_categories(
    start_date: date = Query(...),
    end_date: date = Query(...),
    top_n: int = Query(15, ge=1, le=50),
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    status: list[str] | None = Query(None),
    priority: str | None = Query(None),
):
    client = _get_client()
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority

    raw = client.fetch_tickets_by_date_chunks(start_date, end_date, **filters)
    df = tickets_to_dataframe(raw)

    status_dist = aggregate_by_field(df, "status") if "status" in df.columns else []
    priority_dist = aggregate_by_field(df, "priority") if "priority" in df.columns else []
    tags = aggregate_by_tags(df, top_n=top_n)
    tag_trends = aggregate_tags_over_time(df, period=period, top_n=min(top_n, 10))

    def to_records(data):
        if hasattr(data, "to_dict"):
            return data.to_dict(orient="records")
        return []

    return {
        "total": len(df),
        "status_distribution": to_records(status_dist),
        "priority_distribution": to_records(priority_dist),
        "top_tags": to_records(tags),
        "tag_trends": to_records(tag_trends),
    }
