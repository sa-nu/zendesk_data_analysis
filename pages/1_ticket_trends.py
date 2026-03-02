import requests
import streamlit as st

from components.charts import render_ticket_trend_chart
from components.sidebar import (
    render_date_range_filter,
    render_period_selector,
    render_ticket_filters,
)
from src.data_processor import aggregate_ticket_counts, tickets_to_dataframe
from src.zendesk_client import ZendeskClient

st.header("問い合わせ件数推移")

# --- Sidebar controls ---
start_date, end_date = render_date_range_filter()
filters = render_ticket_filters()
period = render_period_selector()


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

# --- Processing ---
df = tickets_to_dataframe(raw_tickets)

# Display summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Tickets", len(df))
col2.metric("Date Range", f"{start_date} - {end_date}")
col3.metric("Period", period.capitalize())

# --- Chart ---
trend_df = aggregate_ticket_counts(df, period=period)
render_ticket_trend_chart(trend_df, period)

# --- Raw data table (expandable) ---
with st.expander("View Raw Data"):
    st.dataframe(df, use_container_width=True)
