import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")
st.title("📊 Stock Comparison Dashboard (Yahoo Finance)")

# Daftar contoh saham (bisa ditambah sesuai kebutuhan)
available_tickers = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA", "BBRI.JK", "BBCA.JK", "BMRI.JK"]

# Input multi select
selected_tickers = st.multiselect("Pilih saham:", available_tickers, default=["AAPL", "TSLA", "BBRI.JK"])

# Pilih mode time horizon
horizon_mode = st.radio("Pilih Time Horizon:", ["Custom Date", "Preset"])

if horizon_mode == "Custom Date":
    start_date = st.date_input("Start Date", date(2022, 1, 1))
    end_date = st.date_input("End Date", date.today())
else:
    preset = st.selectbox("Pilih periode:", ["1W", "1M", "3M", "1Y", "5Y"])
    end_date = date.today()
    if preset == "1W":
        start_date = end_date - timedelta(weeks=1)
    elif preset == "1M":
        start_date = end_date - timedelta(days=30)
    elif preset == "3M":
        start_date = end_date - timedelta(days=90)
    elif preset == "1Y":
        start_date = end_date - timedelta(days=365)
    elif preset == "5Y":
        start_date = end_date - timedelta(days=5*365)

# Download data
if st.button("📥 Ambil Data"):
    data = yf.download(selected_tickers, start=start_date, end=end_date)

    if data.empty:
        st.warning("⚠️ Data tidak ditemukan.")
    else:
        # Kalau multi ticker → ambil level "Adj Close"
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs("Adj Close", axis=1, level=0)
        else:  # single ticker
            data = data[["Adj Close"]]
            data.columns = selected_tickers  # rename biar konsisten

        # Normalisasi harga biar start = 1
        normalized = data / data.iloc[0]

        # Ubah ke format long untuk plotly
        df_long = normalized.reset_index().melt(
            id_vars="Date", var_name="Stock", value_name="Normalized Price"
        )

        # Grafik interaktif
        fig = px.line(
            df_long,
            x="Date",
            y="Normalized Price",
            color="Stock",
            title="📈 Normalized Stock Price Comparison"
        )
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="Date",
            yaxis_title="Normalized Price"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabel harga terakhir
        st.subheader("📊 Harga Terakhir")
        st.dataframe(data.tail())

        # Download tombol CSV
        csv = data.to_csv().encode("utf-8")
        st.download_button(
            "⬇️ Download Data CSV",
            csv,
            f"stock_data_{start_date}_{end_date}.csv",
            "text/csv"
        )
