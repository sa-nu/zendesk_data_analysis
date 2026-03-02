import pandas as pd
import plotly.express as px
import streamlit as st


def render_ticket_trend_chart(df: pd.DataFrame, period: str) -> None:
    if df.empty:
        st.info("No data to display for the selected period.")
        return

    period_label = {"daily": "Day", "weekly": "Week", "monthly": "Month"}[period]

    fig = px.line(
        df,
        x="date",
        y="ticket_count",
        title=f"Ticket Count by {period_label}",
        labels={"date": "Date", "ticket_count": "Ticket Count"},
        markers=True,
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty:
        st.info("No data to display.")
        return

    fig = px.bar(
        df,
        x=y,
        y=x,
        orientation="h",
        title=title,
        labels={x: x.capitalize(), y: "Ticket Count"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def render_pie_chart(df: pd.DataFrame, names: str, values: str, title: str) -> None:
    if df.empty:
        st.info("No data to display.")
        return

    fig = px.pie(df, names=names, values=values, title=title, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)


def render_tag_trend_chart(df: pd.DataFrame, period: str) -> None:
    if df.empty:
        st.info("No tag trend data to display.")
        return

    period_label = {"daily": "Day", "weekly": "Week", "monthly": "Month"}[period]

    fig = px.line(
        df,
        x="date",
        y="ticket_count",
        color="tag",
        title=f"Tag Trends by {period_label}",
        labels={"date": "Date", "ticket_count": "Ticket Count", "tag": "Tag"},
        markers=True,
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
