import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")
st.title("📊 Stock Comparison Dashboard (Yahoo Finance)")

# Input tickers
tickers = st.text_input(
    "Masukkan kode saham (pisahkan dengan koma, contoh: AAPL, TSLA, BBNI.JK):",
    "AAPL, AMZN, GOOGL, META, MSFT, NVDA, TSLA"
)

# Range tanggal
start_date = st.date_input("Start Date", date(2023, 1, 1))
end_date = st.date_input("End Date", date.today())

# Download data saham
tickers_list = [t.strip() for t in tickers.split(",") if t.strip()]

if st.button("📥 Ambil Data"):
    data = yf.download(tickers_list, start=start_date, end=end_date)

    if data.empty:
        st.warning("⚠️ Data tidak ditemukan. Coba ticker lain atau ubah tanggal.")
    else:
        # Ambil hanya kolom 'Adj Close' (tangani MultiIndex jika multi ticker)
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs("Adj Close", axis=1, level=0)
        else:
            data = data[["Adj Close"]]

        # Normalisasi harga biar start = 1
        normalized = data / data.iloc[0]

        # Ubah ke format long untuk plotly
        df_long = normalized.reset_index().melt(
            id_vars="Date", var_name="Stock", value_name="Normalized Price"
        )

        # Line chart interaktif
        fig = px.line(
            df_long,
            x="Date",
            y="Normalized Price",
            color="Stock",
            title="📈 Normalized Stock Price Comparison"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tampilkan tabel harga terakhir
        st.subheader("📊 Harga Terakhir")
        st.write(data.tail())
