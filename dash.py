import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date, timedelta

st.set_page_config(page_title="📊 Stock Dashboard", layout="wide")

# ==== CSS untuk bikin tombol pill (segmented style) ====
st.markdown("""
    <style>
    div[data-baseweb="radio"] > div {
        display: flex;
        gap: 6px;
    }
    div[data-baseweb="radio"] label {
        background-color: #1e1e2f;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid #4a4a5c;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    div[data-baseweb="radio"] label:hover {
        background-color: #2c2c3e;
        border-color: #6a6a8a;
    }
    div[data-baseweb="radio"] input:checked + div {
        background-color: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

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
        default=["AAPL", "MSFT"]
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
            "10 Tahun": 365*10,
            "20 Tahun": 365*20,
        }

        # tombol pill horizontal
        time_choice = st.radio(
            "Time Horizon",
            list(horizon_options.keys()),
            horizontal=True
        )

        days_back = horizon_options[time_choice]
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

    else:
        start_date = st.date_input("Start Date", date(2010, 1, 1))
        end_date = st.date_input("End Date", date.today())

    # --- Pilih metrik ---
    metrics = ["Close", "Open", "High", "Low", "Volume"]
    metric_choice = st.radio("Pilih Metrik:", metrics)

with col2:
    # --- Ambil data ---
    if tickers:
        data = yf.download(tickers, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ Data tidak ditemukan untuk range ini.")
        else:
            fig = go.Figure()

            # --- Handle single vs multi ticker untuk line chart ---
            if len(tickers) == 1:
                data_metric = data[[metric_choice]].rename(columns={metric_choice: tickers[0]})
            else:
                data_metric = data[metric_choice]

            # Normalisasi harga (kecuali volume, biar lebih fair)
            if metric_choice != "Volume":
                data_metric = data_metric / data_metric.iloc[0]

            for col in data_metric.columns:
                col_name = str(col)
                fig.add_trace(go.Scatter(
                    x=data_metric.index, y=data_metric[col], mode="lines", name=col_name,
                    hovertemplate=col_name + "<br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>"
                ))

            fig.update_layout(
                title=f"📊 Perbandingan {metric_choice} Saham",
                xaxis_title="Date",
                yaxis_title=("Normalized " if metric_choice != "Volume" else "") + metric_choice,
                hovermode="x unified",
                template="plotly_dark",
            )

            st.plotly_chart(fig, use_container_width=True)

            # --- Tabel return (hanya untuk harga, bukan volume) ---
            if metric_choice != "Volume":
                returns = (data_metric.iloc[-1] / data_metric.iloc[0] - 1) * 100
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
