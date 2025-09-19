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
    with st.container(border=True):
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

        if "time_choice" not in st.session_state:
            st.session_state.time_choice = "1 Bulan"
        else:
            start_date = st.date_input("Start Date", date(2010, 1, 1))
            end_date = st.date_input("End Date", date.today())

        st.write("##### ⏳ Time Horizon")

        # --- bikin tombol dalam grid 3 kolom (rapat) ---
        options = list(horizon_options.keys())
        for i in range(0, len(options), 3):
            cols = st.columns([1, 1, 1, 0.2])  # extra kolom kecil buat buffer
            for j, option in enumerate(options[i:i+3]):
                if cols[j].button(option, use_container_width=True):
                    st.session_state.time_choice = option

        days_back = horizon_options[st.session_state.time_choice]
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)

        st.caption(f"📌 Dipilih: **{st.session_state.time_choice}**")

    # --- Pilih metrik ---
    metrics = ["Close", "Open", "High", "Low", "Volume"]
    if "metric_choice" not in st.session_state:
        st.session_state.metric_choice = "Close"

    st.write("##### 📊 Pilih Metrik")

    # --- bikin tombol metrik dalam grid 3 kolom (rapat) ---
    for i in range(0, len(metrics), 3):
        cols = st.columns([1, 1, 1, 0.2])
        for j, m in enumerate(metrics[i:i+3]):
            if cols[j].button(m, use_container_width=True):
                st.session_state.metric_choice = m

    st.caption(f"📌 Metrik aktif: **{st.session_state.metric_choice}**")

with col2:
    # --- Ambil data ---
    if tickers:
        data = yf.download(tickers, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ Data tidak ditemukan untuk range ini.")
        else:
            fig = go.Figure()

            metric_choice = st.session_state.metric_choice

            # --- Handle single vs multi ticker ---
            if len(tickers) == 1:
                data_metric = data[[metric_choice]].rename(columns={metric_choice: tickers[0]})
            else:
                data_metric = data[metric_choice]

            # Normalisasi (kecuali volume)
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

            # --- Return (hanya harga) ---
            if metric_choice != "Volume":
                returns = (data_metric.iloc[-1] / data_metric.iloc[0] - 1) * 100
                st.subheader("📋 Persentase Return (%)")
                st.dataframe(returns.sort_values(ascending=False).round(2))

            # --- Download ---
            csv = data.to_csv().encode("utf-8")
            st.download_button(
                "⬇️ Download Data CSV",
                data=csv,
                file_name="stock_data.csv",
                mime="text/csv"
            )
    else:
        st.warning("Silakan pilih minimal satu saham.")
