import streamlit as st

from src.config import load_config

st.set_page_config(
    page_title="Zendesk Ticket Analysis",
    page_icon="\ud83d\udcca",
    layout="wide",
)

st.title("Zendesk Ticket Analysis Dashboard")
st.markdown("Select a page from the sidebar to view ticket trends or category analysis.")

try:
    config = load_config()
    st.success(f"Connected to Zendesk: {config.subdomain}.zendesk.com")
    st.session_state["zendesk_config"] = config
except ValueError as e:
    st.error(str(e))
    st.stop()
