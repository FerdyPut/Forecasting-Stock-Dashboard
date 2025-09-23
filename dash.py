import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date, timedelta
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import altair as alt
from bokeh.plotting import figure, column
import talib
import numpy as np
from bokeh.models import ColumnDataSource, DataRange1d
from bokeh.layouts import column
from streamlit_bokeh import streamlit_bokeh

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
            "BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK",
            "ICBP.JK", "INDF.JK", "SMGR.JK", "KLBF.JK", "BBNI.JK", "BRIS.JK",
            "ADRO.JK", "ANTM.JK", "MEDC.JK", "PGAS.JK", "EXCL.JK", "JSMR.JK",
            "TBIG.JK", "SIDO.JK", "WIKA.JK", "WSKT.JK", "MYOR.JK", "MNCN.JK",
            "PWON.JK", "AKRA.JK", "UNTR.JK", "SMRA.JK", "TINS.JK", "BSDE.JK",
            "CPIN.JK", "HMSP.JK", "MAPA.JK", "MAPI.JK", "INCO.JK", "ADHI.JK",
            "INKP.JK", "TBLA.JK", "BUMI.JK", "ERAA.JK", "BTPS.JK", "BBTN.JK",
            "BBKP.JK", "PNBN.JK", "BNGA.JK", "NISP.JK", "BMTR.JK", "SCMA.JK",
            "TOTL.JK", "WTON.JK", "LPKR.JK", "LPCK.JK", "MLPL.JK", "IMAS.JK",
            "GGRM.JK", "DVLA.JK", "CMPP.JK", "KAEF.JK", "KRAS.JK", "PANI.JK",
            "TOWR.JK", "MTDL.JK", "ELSA.JK", "INDY.JK", "RAJA.JK", "SGRO.JK",
            "AALI.JK", "LSIP.JK", "SSMS.JK", "BISI.JK", "BWPT.JK", "HRUM.JK",
            "DOID.JK", "PTBA.JK", "ITMG.JK", "MBAP.JK", "GEMS.JK", "PSAB.JK",
            "DKFT.JK", "CITA.JK", "MDKA.JK", "BRMS.JK", "ZINC.JK", "GGRP.JK",
            "NCKL.JK", "FREN.JK", "ISAT.JK", "TPIA.JK", "INDY.JK", "ARTO.JK"
        ]
        tickers = st.multiselect(
            "Pilih Saham:", 
            tickers_list, 
            default=["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK", "TLKM.JK", "UNVR.JK",
            "ICBP.JK", "INDF.JK", "SMGR.JK", "KLBF.JK", "BBNI.JK", "BRIS.JK"]
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

            st.badge(f"📌 Dipilih: **{st.session_state.time_choice}**", color="blue")

        else:  # Custom Date Range
            start_date = st.date_input("Start Date", date(2010,1,1))
            end_date = st.date_input("End Date", date.today())

    # --- Pilih Metric ---
    with st.container(border=True):
        metrics = ["Close", "Open", "High", "Low", "Volume"]
        if "metric_choice" not in st.session_state:
            st.session_state.metric_choice = "Close"

        st.write("📊 Pilih Metrik")
        st.markdown(
            """
            <style>
            .custom-text {
                text-align: justify;
                font-family: 'Poppins', sans-serif;
                font-size: 15px;
                color: #ffffff;
                transition: 0.3s ease-in-out;
            }
            .custom-text:hover {
                color: #B0A5E6;
                transform: scale(1.01);
            }
            </style>
            <div class="custom-text">
                Pemilihan metrik menentukan sudut pandang analisis, apakah harga pembukaan, 
                tertinggi, terendah, penutupan, maupun volume. Dengan memilih metrik yang sesuai, 
                dinamika pasar dapat dipahami secara lebih jelas.
            </div>
            <p></p>
            """,
            unsafe_allow_html=True
        )
        for i in range(0, len(metrics), 3):
            cols = st.columns([1,1,1,0.2])
            for j, m in enumerate(metrics[i:i+3]):
                if cols[j].button(m, use_container_width=True):
                    st.session_state.metric_choice = m

        st.badge(f"📌 Metrik aktif: **{st.session_state.metric_choice}**", color="blue")

# --- Kanan: Grafik & Data ---
with col2:
    if tickers:
        data = yf.download(tickers, start=start_date, end=end_date)

        if data.empty:
            st.error("⚠️ Data tidak ditemukan untuk range ini.")
        else:
            with st.container(border=True):
                metric_choice = st.session_state.metric_choice
                data_metric = data[metric_choice]

                # --- Simpan data asli (untuk tabel/opsi lain) ---
                data_nonnormal = data_metric.copy()

                # --- Normalisasi (kecuali Volume) ---
                if metric_choice != "Volume":
                    data_metric = data_metric / data_metric.iloc[0]

                # --- Reshape ke long format untuk Altair ---
                df_long = data_metric.reset_index().melt(
                    id_vars="Date", var_name="Saham", value_name="Value"
                )

                # --- Hitung quantile untuk default scale ---
                q_low, q_high = df_long["Value"].quantile([0.05, 0.95])

                # --- Slider manual untuk atur range Y ---
                ymin, ymax = st.slider(
                    "Atur Range Y-axis",
                    float(df_long["Value"].min()),
                    float(df_long["Value"].max()),
                    (float(q_low), float(q_high))
                )

                # --- Line chart Altair ---
                st.write(f"### 📊 Perbandingan Harga {metric_choice} Saham")
                chart = (
                    alt.Chart(df_long)
                    .mark_line()
                    .encode(
                        x=alt.X("Date:T", title="Date"),
                        y=alt.Y(
                            "Value:Q",
                            title=("Normalized " if metric_choice != "Volume" else "") + metric_choice,
                            scale=alt.Scale(domain=[ymin, ymax])
                        ),
                        color=alt.Color("Saham:N", title="Saham"),
                        tooltip=["Saham", "Date:T", alt.Tooltip("Value:Q", format=",.2f")]
                    )
                    .configure_axis(
                        labelFont="Poppins",
                        titleFont="Poppins"
                    )
                    .configure_title(
                        font="Poppins",
                        fontSize=16
                    )
                    .configure_legend(
                        labelFont="Poppins",
                        titleFont="Poppins"
                    )
                )

                st.altair_chart(chart, use_container_width=True)



            # --- Download CSV dengan Hover Box ---
            csv_string = data.to_csv(index=True)
            csv_uri = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

            st.markdown(
                f"""
                <style>
                .hover-box {{
                    border: 1px solid #5b4699;
                    border-radius: 10px;
                    padding: 5px;
                    text-align: center;
                    background-color: #5b4699;
                    color: white;
                    transition: 0.3s;
                    position: relative;
                    margin-top: 1px;
                    font-size: 18px;
                    font-family: 'Poppins', sans-serif;
                }}
                .hover-box:hover {{
                    background-color: #5b4699;
                    transform: scale(1.01);
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
                    <strong>Analytics (Based on Statistics)</strong>
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
                        value=f"{avg_prices.mean():.2f}",
                        delta="\u200B IDR, USD, etc.",
                        delta_color = "off"
                    )
                    st.badge(f"Nilai dalam satuan Mata Uang terkait", color= "violet")

            with col2_s:
                with st.container(border=True):
                    st.metric(
                        label=f"Saham Tertinggi ({metric_choice})",
                        value=f"{highest_stock} : {highest_avg_value:.2f}",
                        delta=f"{highest_pct:.2f}%"
                    )
                    st.badge(f"Berdasarkan Harga {metric_choice}", color= "violet")

            with col3_s:
                with st.container(border=True):
                    st.metric(
                        label=f"Saham Terendah ({metric_choice})",
                        value=f"{lowest_stock} : {lowest_avg_value:.2f}",
                        delta=f"{lowest_pct:.2f}%"
                    )
                    st.badge(f"Berdasarkan Harga {metric_choice}", color= "violet")

    else:
        st.warning("Silakan pilih minimal satu saham.")


# --- Load Google Fonts: Poppins ---

with col1:
    with st.container(border=True):
        st.markdown(
            """<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">""",
            unsafe_allow_html=True
        )
        st.write(f"### 🔝 Top 10 Saham dengan Harga {st.session_state.metric_choice} Tertinggi")

        # --- Ambil Top 10 ---
        value_col = f"Harga {metric_choice}"
        top10_stocks = avg_prices.sort_values(ascending=False).head(10)
        df_bar = top10_stocks.reset_index()
        df_bar.columns = ["Saham", value_col]

        # --- pastikan numeric
        df_bar[value_col] = pd.to_numeric(df_bar[value_col], errors="coerce")

        # --- urutin descending berdasarkan value
        y_order = df_bar.sort_values(by=value_col, ascending=False)["Saham"].tolist()

        # --- Base Chart ---
        bar = (
            alt.Chart(df_bar)
            .mark_bar(color="#cd4d4d")
            .encode(
                x=alt.X(f"{value_col}:Q", title=value_col),
                y=alt.Y("Saham:N", sort=y_order, title="Saham"),
                tooltip=["Saham", alt.Tooltip(f"{value_col}:Q", format=",.2f")]
            )
        )

        # --- Label di bar ---
        text = (
            alt.Chart(df_bar)
            .mark_text(
                align="left",
                baseline="middle",
                dx=3,
                color="white",
                font="Poppins",
                fontSize=12
            )
            .encode(
                x=f"{value_col}:Q",
                y=alt.Y("Saham:N", sort=y_order),
                text=alt.Text(f"{value_col}:Q", format=",.2f")
            )
        )

        # --- Combine ---
        chart = (bar + text).properties(height=400)

        # --- Global Font Config ---
        chart = chart.configure_axis(
            labelFont="Poppins",
            titleFont="Poppins",
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            font="Poppins",
            fontSize=16
        ).configure_legend(
            labelFont="Poppins",
            titleFont="Poppins",
            labelFontSize=12,
            titleFontSize=14
        )

        st.altair_chart(chart, use_container_width=True)

with col2:
    st.markdown(
        f"""
        <style>
        .hover-box {{
            border: 1px solid #5b4699;
            border-radius: 10px;
            padding: 5px;
            text-align: center;
            background-color: #5b4699;
            color: white;
            transition: 0.3s;
            position: relative;
            margin-top: 1px;
            font-size: 18px;
            font-family: 'Poppins', sans-serif;
        }}
        .hover-box:hover {{
            background-color: #5b4699;
            transform: scale(1.01);
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
            <strong>SMOOTHING - MOVING AVERAGE</strong>
        </div>
        <p></p>
        """, unsafe_allow_html=True
    )

    with st.container(border=True):     

        # Fungsi untuk membuat chart
        def create_chart(df, indicators):
            source = ColumnDataSource(df)
            
            # Candlestick chart setup
            candle = figure(x_axis_type="datetime", height=500, 
                            tooltips=[("Date", "@Date_str"), ("Open", "@Open"), ("High", "@High"), 
                                    ("Low", "@Low"), ("Close", "@Close")])

            # Candlestick segments
            candle.segment("Date", "Low", "Date", "High", color="black", line_width=0.5, source=source)
            candle.vbar("Date", top="Open", bottom="Close", width=0.5, color="green", source=source, legend_label="Up")
            candle.vbar("Date", top="Close", bottom="Open", width=0.5, color="red", source=source, legend_label="Down")
            
            # Apply selected indicators
            for indicator in indicators:
                if indicator == "SMA":
                    sma = talib.SMA(df['Close'].values, timeperiod=14)  # 'Close' column is used for SMA
                    candle.line(df['Date'], sma, color="orange", line_width=2, source=source, legend_label="SMA")

                # Add more indicator conditions here (e.g., EMA, RSI)
                elif indicator == "EMA":
                    ema = talib.EMA(df['Close'].values, timeperiod=14)
                    candle.line(df['Date'], ema, color="blue", line_width=2, source=source, legend_label="EMA")

            return candle

        # Pilih indikator
        indicators = st.multiselect("Pilih Indikator", ["SMA", "EMA", "RSI", "WMA", "MOM", "DEMA", "TEMA"])

        # Menampilkan chart
        if indicators:
            st.bokeh_chart(create_chart(data_metric, indicators=indicators), use_container_width=True)
