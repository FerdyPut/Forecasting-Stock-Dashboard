import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("📈 Stock Dashboard")

# ===============================
# Sidebar - Pilih saham
# ===============================
tickers = ["BBRI.JK", "BBCA.JK", "TLKM.JK", "BMRI.JK", "ASII.JK", "ICBP.JK", "UNVR.JK"]
selected_tickers = st.sidebar.multiselect("Pilih Saham", tickers, default=["BBRI.JK"])

# ===============================
# Time Horizon (Tombol dalam 3 kolom, rapat)
# ===============================
st.subheader("⏳ Time Horizon")

time_options = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "5Y": "5y",
    "10Y": "10y",
    "20Y": "20y"
}

cols = st.columns(3)
selected_horizon = None
i = 0
for label, period in time_options.items():
    if cols[i % 3].button(label):
        selected_horizon = period
    i += 1

if not selected_horizon:
    selected_horizon = "6mo"  # default

# ===============================
# Pilihan custom date
# ===============================
st.subheader("📅 Custom Date Range")
col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", datetime.today() - timedelta(days=365))
end_date = col2.date_input("End Date", datetime.today())

# ===============================
# Metric Pilihan (dengan button 3 kolom)
# ===============================
st.subheader("📊 Pilih Metrik")

metric_options = ["Open", "High", "Low", "Close", "Volume"]
metric_cols = st.columns(3)
selected_metric = None
for i, m in enumerate(metric_options):
    if metric_cols[i % 3].button(m):
        selected_metric = m

if not selected_metric:
    selected_metric = "Close"

# ===============================
# Download data saham
# ===============================
df = yf.download(selected_tickers, period=selected_horizon, start=start_date, end=end_date, group_by='ticker')

# ===============================
# Plot Chart
# ===============================
fig = go.Figure()

for ticker in selected_tickers:
    if len(selected_tickers) == 1:
        data = df
    else:
        data = df[ticker]

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data[selected_metric],
        mode="lines",
        name=ticker
    ))

fig.update_layout(
    title=f"{selected_metric} Price",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
