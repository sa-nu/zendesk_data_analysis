from typing import Dict, List

import pandas as pd


def tickets_to_dataframe(tickets: List[Dict]) -> pd.DataFrame:
    if not tickets:
        return pd.DataFrame()

    df = pd.DataFrame(tickets)

    columns_map = {
        "id": "ticket_id",
        "subject": "subject",
        "status": "status",
        "priority": "priority",
        "type": "ticket_type",
        "tags": "tags",
        "group_id": "group_id",
        "created_at": "created_at",
        "updated_at": "updated_at",
        "solved_at": "solved_at",
    }

    available = {k: v for k, v in columns_map.items() if k in df.columns}
    df = df[list(available.keys())].rename(columns=available)

    for col in ["created_at", "updated_at", "solved_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)

    if "created_at" in df.columns:
        df["created_date"] = df["created_at"].dt.date
        df["created_week"] = (
            df["created_at"].dt.to_period("W").dt.start_time.dt.date
        )
        df["created_month"] = (
            df["created_at"].dt.to_period("M").dt.start_time.dt.date
        )

    return df


def aggregate_ticket_counts(df: pd.DataFrame, period: str = "daily") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "ticket_count"])

    period_col_map = {
        "daily": "created_date",
        "weekly": "created_week",
        "monthly": "created_month",
    }
    col = period_col_map[period]
    result = df.groupby(col).size().reset_index(name="ticket_count")
    result.columns = ["date", "ticket_count"]
    result = result.sort_values("date")
    return result


def aggregate_by_field(df: pd.DataFrame, field: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[field, "ticket_count"])

    result = df.groupby(field).size().reset_index(name="ticket_count")
    result = result.sort_values("ticket_count", ascending=False)
    return result


def explode_tags(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "tags" not in df.columns:
        return pd.DataFrame(columns=["ticket_id", "tag"])

    exploded = df[["ticket_id", "tags"]].explode("tags")
    exploded = exploded.rename(columns={"tags": "tag"})
    exploded = exploded.dropna(subset=["tag"])
    return exploded


def aggregate_by_tags(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    exploded = explode_tags(df)
    if exploded.empty:
        return pd.DataFrame(columns=["tag", "ticket_count"])

    result = exploded.groupby("tag").size().reset_index(name="ticket_count")
    result = result.sort_values("ticket_count", ascending=False).head(top_n)
    return result


def aggregate_tags_over_time(
    df: pd.DataFrame, period: str = "monthly", top_n: int = 10
) -> pd.DataFrame:
    if df.empty or "tags" not in df.columns:
        return pd.DataFrame(columns=["date", "tag", "ticket_count"])

    period_col_map = {
        "daily": "created_date",
        "weekly": "created_week",
        "monthly": "created_month",
    }
    date_col = period_col_map[period]

    top_tags = aggregate_by_tags(df, top_n=top_n)["tag"].tolist()

    exploded = df[["ticket_id", "tags", date_col]].explode("tags")
    exploded = exploded.rename(columns={"tags": "tag", date_col: "date"})
    exploded = exploded[exploded["tag"].isin(top_tags)]

    result = exploded.groupby(["date", "tag"]).size().reset_index(name="ticket_count")
    result = result.sort_values("date")
    return result
