import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date
import requests
import os

# --- Ambil daftar ticker IDX (auto-generate jika belum ada) ---
@st.cache_data
def get_tickers_master():
    file_path = "tickers_master.csv"

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        url = "https://www.idx.co.id/umbraco/Surface/ListedCompany/GetCompanyProfiles"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)[["KodeEmiten", "NamaEmiten"]]
        df.to_csv(file_path, index=False, encoding="utf-8-sig")

    return df

tickers_df = get_tickers_master()
tickers_master = tickers_df["KodeEmiten"].tolist()

# --- Streamlit App ---
st.title("📈 Stock Dashboard IDX (Yahoo Finance)")

# Multi input ticker dari master list
tickers = st.multiselect(
    "Pilih Saham (Ticker IDX):",
    tickers_master,
    default=["BBCA", "BBRI", "TLKM"]
)

# Periode tanggal
start_date = st.date_input("Start Date", date(2020, 1, 1))
end_date = st.date_input("End Date", date.today())

# Time horizon (opsi sederhana)
horizon = st.selectbox(
    "Pilih Time Horizon:",
    ["1 Hari", "1 Minggu", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun"]
)

# --- Ambil data dan tampilkan chart ---
if tickers:
    # Format ticker ke Yahoo Finance (tambah .JK untuk saham Indonesia)
    tickers_yf = [t + ".JK" for t in tickers]

    data = yf.download(tickers_yf, start=start_date, end=end_date)["Close"]

    if isinstance(data, pd.Series):  # kalau cuma 1 ticker
        data = data.to_frame()

    st.subheader("Data Historis (Closing Price)")

    # Plot pakai seaborn
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(data=data, ax=ax)
    ax.set_title(f"Closing Price - {', '.join(tickers)}")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Harga (IDR)")
    st.pyplot(fig)

    st.write("📊 Preview Data")
    st.write(data.tail())
