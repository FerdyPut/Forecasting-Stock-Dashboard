import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date, timedelta

st.set_page_config(page_title="📊 Stock Dashboard", layout="wide")

st.title("📈 Stock Dashboard - Yahoo Finance")

# --- Layout 2 kolom ---
col1, col2 = st.columns([1, 2])  # kiri kecil (input), kanan besar (grafik)

with col1:
    # --- Pilih ticker ---
    tickers_list = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK"
    ]
    tickers = st.multiselect(
        "Pilih saham:", 
        tickers_list, 
        default=["AAPL", "MSFT", "GOOGL"]
    )

    # --- Pilih mode date ---
    date_mode = st.radio("Pilih Mode Waktu:", ["Time Horizon Cepat", "Custom Date Range"])

    if date_mode == "Time Horizon Cepat":
        horizon_options = {
            "1 Minggu": 7,
            "1 Bulan": 30,
            "3 Bulan": 90,
            "6 Bulan": 180,
            "1 Tahun": 365,
            "5 Tahun": 365*5,
        }
        time_choice = st.selectbox("Pilih Time Horizon:", list(horizon_options.keys()))
        days_back = horizon_options[time_choice]
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

    else:
        start_date = st.date_input("Start Date", date(2020, 1, 1))
        end_date = st.date_input("End Date", date.today())

with col2:
    # --- Ambil data ---
    if tickers:
        data = yf.download(tickers, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ Data tidak ditemukan untuk range ini.")
        else:
            # --- Handle single vs multi ticker ---
            if len(tickers) == 1:
                # Kalau hanya 1 ticker, ubah jadi DataFrame dengan nama kolom = ticker
                data = data[["Close"]].rename(columns={"Close": tickers[0]})
            else:
                # Kalau multi ticker, ambil level Close
                data = data["Close"]

            # --- Normalisasi harga biar bisa dibandingkan ---
            data = data / data.iloc[0]

            # --- Plot interaktif ---
            fig = go.Figure()
            for col in data.columns:
                col_name = str(col)  # pastikan selalu string
                fig.add_trace(go.Scatter(
                    x=data.index, y=data[col], mode="lines", name=col_name,
                    hovertemplate=col_name + "<br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>"
                ))

            fig.update_layout(
                title="📊 Perbandingan Harga Saham (Normalized)",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                hovermode="x unified",
                template="plotly_dark",
            )

            st.plotly_chart(fig, use_container_width=True)

            # --- Tabel return ---
            returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
            st.subheader("📋 Persentase Return (%)")
            st.dataframe(returns.sort_values(ascending=False).round(2))

            # --- Tombol download ---
            csv = data.to_csv().encode("utf-8")
            st.download_button(
                "⬇️ Download Data CSV",
                data=csv,
                file_name="stock_data.csv",
                mime="text/csv"
            )
    else:
        st.warning("Silakan pilih minimal satu saham.")
