from datetime import date, timedelta

import streamlit as st


def render_date_range_filter() -> tuple[date, date]:
    st.sidebar.header("Date Range")

    default_start = date.today() - timedelta(days=90)
    default_end = date.today()

    start_date = st.sidebar.date_input(
        "Start Date", value=default_start, max_value=default_end
    )
    end_date = st.sidebar.date_input(
        "End Date", value=default_end, max_value=date.today()
    )

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        st.stop()

    return start_date, end_date


def render_ticket_filters() -> dict:
    st.sidebar.header("Filters")

    filters = {}

    status = st.sidebar.multiselect(
        "Status",
        options=["new", "open", "pending", "hold", "solved", "closed"],
        default=[],
    )
    if status:
        filters["status"] = status

    priority = st.sidebar.selectbox(
        "Priority",
        options=["All", "urgent", "high", "normal", "low"],
        index=0,
    )
    if priority != "All":
        filters["priority"] = priority

    return filters


def render_period_selector() -> str:
    period_labels = {"Daily": "daily", "Weekly": "weekly", "Monthly": "monthly"}
    selected = st.sidebar.radio(
        "Aggregation Period",
        options=list(period_labels.keys()),
        index=2,
    )
    return period_labels[selected]
