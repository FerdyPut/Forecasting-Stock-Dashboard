import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date, timedelta
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns

# --- Page Config ---
st.set_page_config(page_title="📊 Stock Dashboard", layout="wide")
st.title("📈 Dynamic Stock Dashboard")

# --- Layout 2 kolom ---
col1, col2 = st.columns([1, 2])  # kiri: input, kanan: grafik

# --- Kiri: Pilihan Input ---
with col1:
    with st.container(border=True): # Streamlit tidak mendukung border=True secara default
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

            st.write("⏳ Time Horizon")

            # --- tombol grid 3 kolom ---
            options = list(horizon_options.keys())
            for i in range(0, len(options), 3):
                cols = st.columns([1,1,1,0.2])
                for j, option in enumerate(options[i:i+3]):
                    if cols[j].button(option, use_container_width=True):
                        st.session_state.time_choice = option

            days_back = horizon_options[st.session_state.time_choice]
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)

            st.caption(f"📌 Dipilih: **{st.session_state.time_choice}**")

        else:  # Custom Date Range
            start_date = st.date_input("Start Date", date(2010,1,1))
            end_date = st.date_input("End Date", date.today())

    # --- Pilih Metric ---
    with st.container(border=True):
        metrics = ["Close", "Open", "High", "Low", "Volume"]
        if "metric_choice" not in st.session_state:
            st.session_state.metric_choice = "Close"

        st.write("📊 Pilih Metrik")

        for i in range(0, len(metrics), 3):
            cols = st.columns([1,1,1,0.2])
            for j, m in enumerate(metrics[i:i+3]):
                if cols[j].button(m, use_container_width=True):
                    st.session_state.metric_choice = m

        st.caption(f"📌 Metrik aktif: **{st.session_state.metric_choice}**")

# --- Kanan: Grafik & Data ---
with col2:
    if tickers:
        data = yf.download(tickers, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ Data tidak ditemukan untuk range ini.")
        else:
            fig = go.Figure()
            metric_choice = st.session_state.metric_choice

            if len(tickers) == 1:
                data_metric = data[[metric_choice]].rename(columns={metric_choice: tickers[0]})
            else:
                data_metric = data[metric_choice]

            # Normalisasi kecuali Volume
            data_nonnormal = data_metric.copy()

            if metric_choice != "Volume":
                data_metric = data_metric / data_metric.iloc[0]

            for col in data_metric.columns:
                fig.add_trace(go.Scatter(
                    x=data_metric.index, y=data_metric[col], mode="lines", name=str(col),
                    hovertemplate=str(col)+"<br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.2f}<extra></extra>"
                ))

            fig.update_layout(
                title=f"📊 Perbandingan Harga {metric_choice} Saham",
                xaxis_title="Date",
                yaxis_title=("Normalized " if metric_choice != "Volume" else "") + metric_choice,
                hovermode="x unified",
                template="plotly_dark"
            )
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)

            # --- Download CSV dengan Hover Box ---
            csv_string = data.to_csv(index=True)
            csv_uri = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

            st.markdown(
                f"""
                <style>
                .hover-box {{
                    border: 1px solid #151f33;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    background-color: #151f33;
                    color: white;
                    transition: 0.3s;
                    position: relative;
                    margin-top: 15px;
                }}
                .hover-box:hover {{
                    background-color: #151f33;
                }}
                .download-btn {{
                    display: none;
                    margin-top: 10px;
                }}
                .hover-box:hover .download-btn {{
                    display: block;
                }}
                a.download-link {{
                    color: white;
                    text-decoration: none;
                    padding: 5px 10px;
                    background-color: #615fff;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                </style>

                <div class="hover-box">
                    <strong>Download Data Saham</strong>
                    <div class="download-btn">
                        <a class="download-link" href="{csv_uri}" download="stock_data.csv">⬇️ Download CSV</a>
                    </div>
                </div>
                <p></p>
                """, unsafe_allow_html=True
            )
            # --- Scorecard Summary ---

            # Hitung rata-rata per saham

            avg_prices = data_nonnormal.mean()

            # Persentase perubahan dari awal ke akhir
            pct_change = ((data_nonnormal.iloc[-1] - data_nonnormal.iloc[0]) / data_nonnormal.iloc[0]) * 100

            # Saham tertinggi
            highest_stock = avg_prices.idxmax()
            highest_avg_value = avg_prices[highest_stock]
            highest_pct = pct_change[highest_stock]

            # Saham terendah
            lowest_stock = avg_prices.idxmin()
            lowest_avg_value = avg_prices[lowest_stock]
            lowest_pct = pct_change[lowest_stock]


            col1_s, col2_s, col3_s = st.columns(3)

            with col1_s:
                with st.container(border=True):
                    st.metric(
                        label=f"Rata-rata Harga Saham ({metric_choice})",
                        value=f"{avg_prices.mean():.2f}"
                    )
                    st.caption("Nilai dalam satuan Mata Uang terkait")

            with col2_s:
                with st.container(border=True):
                    st.metric(
                        label=f"Saham Tertinggi ({metric_choice})",
                        value=f"{highest_stock} : {highest_avg_value:.2f}",
                        delta=f"{highest_pct:.2f}%"
                    )

            with col3_s:
                with st.container(border=True):
                    st.metric(
                        label=f"Saham Terendah ({metric_choice})",
                        value=f"{lowest_stock} : {lowest_avg_value:.2f}",
                        delta=f"{lowest_pct:.2f}%"
                    )

    else:
        st.warning("Silakan pilih minimal satu saham.")

col1, col2 = st.columns([1, 2])  # kiri: input, kanan: grafik
with col1:
    # --- Horizontal Bar Chart Top 5 Saham ---
    top5_stocks = avg_prices.sort_values(ascending=False).head(5)

    fig_barh = go.Figure(go.Bar(
        x=top5_stocks.values,      # sumbu X = nilai
        y=top5_stocks.index,       # sumbu Y = nama saham
        text=[f"{v:.2f}" for v in top5_stocks.values],
        textposition='auto',
        orientation='h',           # ini bikin horizontal
        marker=dict(color='#091a30')
    ))

    fig_barh.update_layout(
        xaxis_title=metric_choice,
        yaxis_title="Saham",
        template="plotly_dark"
    )


    st.plotly_chart(fig_barh, use_container_width=True)

