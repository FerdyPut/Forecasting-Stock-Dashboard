import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("📈 Stock Dashboard")

# --- Tickers Indonesia (IDX)
tickers_dict = {
    "BBCA": "Bank Central Asia",
    "BBRI": "Bank Rakyat Indonesia",
    "BMRI": "Bank Mandiri",
    "TLKM": "Telkom Indonesia",
    "ASII": "Astra International",
}
tickers = list(tickers_dict.keys())

# --- Input Saham
selected_stocks = st.multiselect("Pilih Saham:", tickers, format_func=lambda x: f"{x} - {tickers_dict[x]}")

# --- Time Horizon Options
time_options = {
    "1M": timedelta(days=30),
    "3M": timedelta(days=90),
    "6M": timedelta(days=180),
    "1Y": timedelta(days=365),
    "5Y": timedelta(days=1825),
    "10Y": timedelta(days=3650),
}

st.subheader("⏳ Time Horizon")
time_col1, time_col2, time_col3 = st.columns(3)

selected_horizon = None
for i, (label, delta) in enumerate(time_options.items()):
    col = [time_col1, time_col2, time_col3][i % 3]
    if col.button(label, use_container_width=True):
        selected_horizon = delta

# Default kalau belum dipilih
if selected_horizon is None:
    selected_horizon = timedelta(days=365)

# --- Metrik Options
metric_options = ["Close", "Open", "High", "Low", "Volume"]

st.subheader("📊 Pilih Metrik")
met_col1, met_col2, met_col3 = st.columns(3)

selected_metric = None
for i, metric in enumerate(metric_options):
    col = [met_col1, met_col2, met_col3][i % 3]
    if col.button(metric, use_container_width=True):
        selected_metric = metric

# Default metrik kalau belum dipilih
if selected_metric is None:
    selected_metric = "Close"

# --- Ambil Data
if selected_stocks:
    end = datetime.today()
    start = end - selected_horizon
    data = yf.download(selected_stocks, start=start, end=end)

    st.subheader(f"📉 Grafik {selected_metric}")

    fig = go.Figure()
    if len(selected_stocks) == 1:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[selected_metric],
            mode="lines",
            name=selected_stocks[0],
            hovertemplate="Date: %{x}<br>Value: %{y:.2f}<extra></extra>"
        ))
    else:
        for stock in selected_stocks:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data[selected_metric][stock],
                mode="lines",
                name=stock,
                hovertemplate="Date: %{x}<br>Value: %{y:.2f}<extra></extra>"
            ))

    fig.update_layout(
        xaxis_title="Tanggal",
        yaxis_title=selected_metric,
        hovermode="x unified",
        template="plotly_dark",
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
