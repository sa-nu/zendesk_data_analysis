import requests
import streamlit as st

from components.charts import (
    render_bar_chart,
    render_pie_chart,
    render_tag_trend_chart,
)
from components.sidebar import (
    render_date_range_filter,
    render_period_selector,
    render_ticket_filters,
)
from src.data_processor import (
    aggregate_by_field,
    aggregate_by_tags,
    aggregate_tags_over_time,
    tickets_to_dataframe,
)
from src.zendesk_client import ZendeskClient

st.header("カテゴリ・タグ別分析")

# --- Sidebar controls ---
start_date, end_date = render_date_range_filter()
filters = render_ticket_filters()
period = render_period_selector()

top_n = st.sidebar.slider("Top N Tags", min_value=5, max_value=50, value=15)


# --- Data fetching (cached) ---
@st.cache_data(ttl=300, show_spinner="Fetching tickets from Zendesk...")
def fetch_tickets(_config, start, end, **kwargs):
    client = ZendeskClient(_config)
    return client.fetch_tickets_by_date_chunks(start, end, **kwargs)


config = st.session_state.get("zendesk_config")
if not config:
    st.error("Configuration not loaded. Please return to the main page.")
    st.stop()

try:
    raw_tickets = fetch_tickets(config, start_date, end_date, **filters)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        st.error(
            "Authentication failed. Check your ZENDESK_EMAIL and ZENDESK_API_TOKEN."
        )
    else:
        st.error(f"Zendesk API error: {e}")
    st.stop()
except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to Zendesk. Check your ZENDESK_SUBDOMAIN and network connection."
    )
    st.stop()

df = tickets_to_dataframe(raw_tickets)

st.metric("Total Tickets", len(df))

# --- Status Distribution ---
st.subheader("Status Distribution")
col1, col2 = st.columns(2)
status_df = aggregate_by_field(df, "status")
with col1:
    render_bar_chart(status_df, "status", "ticket_count", "Tickets by Status")
with col2:
    render_pie_chart(status_df, "status", "ticket_count", "Status Proportion")

# --- Priority Distribution ---
st.subheader("Priority Distribution")
col1, col2 = st.columns(2)
priority_df = aggregate_by_field(df, "priority")
with col1:
    render_bar_chart(priority_df, "priority", "ticket_count", "Tickets by Priority")
with col2:
    render_pie_chart(priority_df, "priority", "ticket_count", "Priority Proportion")

# --- Tag Analysis ---
st.subheader("Tag Analysis")
tag_df = aggregate_by_tags(df, top_n=top_n)
render_bar_chart(tag_df, "tag", "ticket_count", f"Top {top_n} Tags")

# --- Tag Trends Over Time ---
st.subheader("Tag Trends Over Time")
tag_trend_df = aggregate_tags_over_time(df, period=period, top_n=min(top_n, 10))
render_tag_trend_chart(tag_trend_df, period)
