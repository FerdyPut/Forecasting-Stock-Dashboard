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
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from statsmodels.stats.diagnostic import acorr_ljungbox
from scipy.stats import shapiro, jarque_bera
import openpyxl

# --- Page Config ---

st.set_page_config(page_title="📊 Stock Dashboard", layout="wide")
st.title("🔮 STOCK INTELLIGENCE HUB")
st.badge("Selamat datang di STOCK INTELLIGENCE HUB 🚀", color="violet")
st.warning("Dashboard ini dibuat supaya stakeholders bisa melihat bagaimana harga saham bergerak, memprediksi arahnya, dan mengukur seberapa akurat model prediksi melalui MAPE. Dengan sentuhan chatbot interaktif, dashboard ini bukan hanya menampilkan angka—tapi juga memberikan rekomendasi strategi: kapan harus hold, buy, atau sell.")

# --- Ambil data saham dari Dropbox ---
url = "https://www.dropbox.com/scl/fi/c00v1ghuj6k06uirtdql4/Daftar-Saham-20250926.xlsx?rlkey=w2az4wpj6ti88yn2tmscdl6z5&st=alpxhyqt&dl=1"
df_saham = pd.read_excel(url)


tab1, tab2 = st.tabs(["Forecast", "List Saham"])

with tab1:
        # --- Layout 2 kolom ---
        col1, col2 = st.columns([1, 2])  # kiri: input, kanan: grafik

        # --- Kiri: Pilihan Input ---
        with col1:
            with st.container(border=True): # Streamlit tidak mendukung border=True secara default
                # --- Pilih ticker ---
                # Ambil list saham dari Excel (kolom A)
                tickers_list = df_saham.iloc[:, 1].dropna().tolist()

                # Multiselect pilihan saham
                selected_tickers = st.multiselect(
                    "Pilih Saham:", 
                    options=tickers_list,
                    default=["BBCA", "BBRI", "BMRI", "ASII", "TLKM", "UNVR"]  # tanpa .JK
                )

                # --- Tambahkan suffix .JK untuk yfinance ---
                tickers = [ticker + ".JK" for ticker in selected_tickers]

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
                        <strong>HISTORICAL STOCK OF PERFORMANCE</strong>
                    </div>
                    <p></p>
                    """, unsafe_allow_html=True
                )
                    
                    with st.container(border=True):
                        metric_choice = st.session_state.metric_choice
                        data_metric = data[metric_choice]

                        # --- Simpan data asli (untuk tabel/opsi lain) ---
                        data_nonnormal = data_metric.copy()

                        # --- Pilih tampilan data ---
                        scale_option = st.radio(
                            "Tipe Data",
                            ["Normalisasi", "Asli"],
                            horizontal=True
                        )

                        # --- Normalisasi (kecuali Volume) ---
                        if scale_option == "Normalisasi" and metric_choice != "Volume":
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
                        st.badge(f" Perbandingan Harga {metric_choice} Saham ({scale_option})", color="grey")
                        chart = (
                            alt.Chart(df_long)
                            .mark_line()
                            .encode(
                                x=alt.X("Date:T", title="Date"),
                                y=alt.Y(
                                    "Value:Q",
                                    title=(("Normalized " if scale_option == "Normalisasi" and metric_choice != "Volume" else "") + metric_choice),
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
                                delta="\u200B IDR (Rupiah)",
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
                            st.badge(f"Berdasarkan Rata-rata Harga {metric_choice}", color= "violet")

                    with col3_s:
                        with st.container(border=True):
                            st.metric(
                                label=f"Saham Terendah ({metric_choice})",
                                value=f"{lowest_stock} : {lowest_avg_value:.2f}",
                                delta=f"{lowest_pct:.2f}%"
                            )
                            st.badge(f"Berdasarkan Rata-rata Harga {metric_choice}", color= "violet")

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
                metric_choice = st.session_state.metric_choice

                # --- Pilih data sesuai metric ---
                if len(tickers) == 1:
                    data_metric = data[[metric_choice]].rename(columns={metric_choice: tickers[0]})
                    single_saham = True
                else:
                    data_metric = data[metric_choice]
                    single_saham = False

                # --- Pastikan selalu DataFrame ---
                if isinstance(data_metric, pd.Series):
                    data_metric = data_metric.to_frame(name=tickers[0])

                # --- Simpan data asli ---
                data_nonnormal = data_metric.copy()

                # --- Normalisasi (kecuali Volume) ---
                if metric_choice != "Volume":
                    data_metric = data_metric / data_metric.iloc[0]

                # --- Hitung MA (opsional) ---
                ma_options = [10, 20, 50, 100, 200]
                ma_period1 = st.selectbox("Pilih MA 1", ma_options, index=1, key="ma1")
                ma_period2 = st.selectbox("Pilih MA 2", ma_options, index=2, key="ma2")
                ma_method = st.selectbox("Metode MA", ["Exponential Smoothing"])


                ma1 = data_metric.ewm(span=ma_period1, adjust=False).mean()
                ma2 = data_metric.ewm(span=ma_period2, adjust=False).mean()
                    
                # --- Reshape ke long format untuk Altair ---
                if single_saham:
                    values = data_metric.iloc[:, 0].values  # pastikan 1D
                    df_long = pd.DataFrame({
                        "Date": data_metric.index,
                        "Saham": tickers[0],
                        "Value": values
                    })
                    df_ma1 = pd.DataFrame({
                        "Date": ma1.index,
                        "Saham": tickers[0],
                        f"MA{ma_period1}": ma1.iloc[:, 0].values
                    })
                    df_ma2 = pd.DataFrame({
                        "Date": ma2.index,
                        "Saham": tickers[0],
                        f"MA{ma_period2}": ma2.iloc[:, 0].values
                    })
                else:
                    df_long = data_metric.reset_index().melt(
                        id_vars="Date", var_name="Saham", value_name="Value"
                    )
                    df_ma1 = ma1.reset_index().melt(id_vars="Date", var_name="Saham", value_name=f"MA{ma_period1}")
                    df_ma2 = ma2.reset_index().melt(id_vars="Date", var_name="Saham", value_name=f"MA{ma_period2}")

                # --- Hitung quantile untuk default scale ---
                q_low, q_high = df_long["Value"].quantile([0.05, 0.95])

                # --- Slider manual untuk atur range Y ---
                ymin, ymax = st.slider(
                    "Atur Range Y-axis",
                    float(df_long["Value"].min()),
                    float(df_long["Value"].max()),
                    (float(q_low), float(q_high)), key="slider2"
                )

                # --- Line chart Altair ---
                base = alt.Chart(df_long).mark_line().encode(
                    x=alt.X("Date:T", title="Date"),
                    y=alt.Y(
                        "Value:Q",
                        title=("Normalized " if metric_choice != "Volume" else "") + metric_choice,
                        scale=alt.Scale(domain=[ymin, ymax])
                    ),
                    color=alt.Color("Saham:N", title="Saham"),
                    tooltip=["Saham", "Date:T", alt.Tooltip("Value:Q", format=",.2f")]
                )

                line_ma1 = alt.Chart(df_ma1).mark_line(strokeDash=[5, 5], color="#cd4d4d").encode(
                    x="Date:T",
                    y=f"MA{ma_period1}:Q",
                    tooltip=["Saham", "Date:T", alt.Tooltip(f"MA{ma_period1}:Q", format=",.2f")]
                )

                line_ma2 = alt.Chart(df_ma2).mark_line(strokeDash=[2, 2], color="#1a69e0").encode(
                    x="Date:T",
                    y=f"MA{ma_period2}:Q",
                    tooltip=["Saham", "Date:T", alt.Tooltip(f"MA{ma_period2}:Q", format=",.2f")]
                )

                final_chart = (base + line_ma1 + line_ma2).properties(
                    title=f"📊 Harga {metric_choice} + MA ({ma_period1} & {ma_period2})",
                    height=400
                ).configure_axis(
                    labelFont="Poppins",
                    titleFont="Poppins"
                ).configure_title(
                    font="Poppins",
                    fontSize=16
                ).configure_legend(
                    labelFont="Poppins",
                    titleFont="Poppins"
                )

                st.altair_chart(final_chart, use_container_width=True)

        # Fungsi
        def analyze_stock_full(ticker, start_date, end_date, metric):
            df = yf.download(
                ticker,
                start=start_date - timedelta(days=500),
                end=end_date,
                progress=False,
                auto_adjust=False
            )

            if df.empty:
                return None

            # Handle MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if metric not in df.columns:
                return None

            price = df[metric].dropna()
            if len(price) < 60:
                return None

            # ======================
            # Harga sekarang
            # ======================
            current_price = price.iloc[-1]

            last_date = price.index[-1]
            current_year = last_date.year

            # ======================
            # YTD
            # ======================
            ytd_data = price[price.index.year == current_year]
            ytd = (
                (ytd_data.iloc[-1] / ytd_data.iloc[0] - 1) * 100
                if len(ytd_data) > 1 else None
            )

            # ======================
            # MoM (~21 trading days)
            # ======================
            mom = (
                (price.iloc[-1] / price.iloc[-21] - 1) * 100
                if len(price) > 21 else None
            )

            # ======================
            # YoY ALL (TTM)
            # ======================
            yoy_all = (
                (price.iloc[-1] / price.iloc[-252] - 1) * 100
                if len(price) > 252 else None
            )

            # ======================
            # YoY Quarterly (Mean Based)
            # ======================
            yoy_q = {}
            for q in [1, 2, 3, 4]:
                curr_q = price[
                    (price.index.year == current_year) &
                    (price.index.quarter == q)
                ]
                prev_q = price[
                    (price.index.year == current_year - 1) &
                    (price.index.quarter == q)
                ]

                yoy_q[q] = (
                    (curr_q.mean() / prev_q.mean() - 1) * 100
                    if len(curr_q) > 5 and len(prev_q) > 5 else None
                )

            # ======================
            # When (MA Cross)
            # ======================
            if len(price) < 200:
                when = "Insufficient data"
            else:
                ma50 = price.rolling(50).mean()
                ma200 = price.rolling(200).mean()
                cross = (ma50 > ma200) & (ma50.shift(1) <= ma200.shift(1))
                when = cross[cross].index[-1].strftime("%b %Y") if cross.any() else "No clear trend"

            return {
                "Saham": ticker.replace(".JK", ""),
                "Harga Sekarang": round(current_price, 2),
                "YTD (%)": round(ytd, 2) if ytd is not None else None,
                "MoM (%)": round(mom, 2) if mom is not None else None,
                "YoY ALL (%)": round(yoy_all, 2) if yoy_all is not None else None,
                "YoY Q1 (%)": round(yoy_q[1], 2) if yoy_q[1] is not None else None,
                "YoY Q2 (%)": round(yoy_q[2], 2) if yoy_q[2] is not None else None,
                "YoY Q3 (%)": round(yoy_q[3], 2) if yoy_q[3] is not None else None,
                "YoY Q4 (%)": round(yoy_q[4], 2) if yoy_q[4] is not None else None,
                "When": when
            }
        with col1:
            with st.container(border=True):
                st.write("### 🌐 Advanced Analysis")

                results = []

                with st.spinner("📊 Running analysis..."):
                    for t in tickers:
                        res = analyze_stock_full(
                            t,
                            start_date,
                            end_date,
                            st.session_state.metric_choice
                        )
                        if res:
                            results.append(res)

                if not results:
                    st.warning("Tidak ada data yang bisa dianalisis.")
                    st.stop()

                df_table = pd.DataFrame(results)

                st.dataframe(
                    df_table,
                    use_container_width=True,
                    hide_index=True
                )

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
                <strong>FORECASTING SAHAM: MENDUKUNG STRATEGI INVESTASI & BISNIS</strong>
            </div>
            <p></p>
            """, unsafe_allow_html=True
        )
            with st.container(border=True):
                try:
                    # --- Pilih saham & metric ---
                    saham_choice = st.selectbox("Pilih 1 Saham untuk Forecasting diantara saham yang sudah dipilih di Atas!", tickers)
                    metric_choice = st.session_state.metric_choice
                    method_choice = st.selectbox("Pilih Metode Forecasting + Cek Asumsi", ["ARIMA", "Holt-Winters", "SVR"])
                    
                    
                    st.badge(f"Asumsi Lengkap untuk metode ARIMA! (Stasioner, Normal, dan Autokorelasi)")
                    st.markdown("Ketika, salah satu asumsi tidak terpenuhi, maka sudah ditransformasi!. Diharapkan, lebih bagus menggunakan metode SVR mengantisipasi cek Asumsi")

                    ts = data[metric_choice][saham_choice].dropna()
                
                    # --- Train-test split ---
                    train_size = int(len(ts) * 0.8)
                    train, test = ts.iloc[:train_size], ts.iloc[train_size:]

                    # =====================================================
                    # 1. CEK ASUMSI STASIONERITAS (ADF Test)
                    # =====================================================
                    adf_result = adfuller(train)
                    p_value = adf_result[1]

                    if p_value > 0.05:
                        ts = ts.diff().dropna()
                        train, test = ts.iloc[:train_size], ts.iloc[train_size:]
                        if method_choice == "ARIMA" or method_choice == "Holt-Winters":
                            st.warning(f"⚠️ Data tidak stasioner (p-value = {p_value:.4f}) → lakukan differencing.")
                    else:
                        if method_choice == "ARIMA" or method_choice == "Holt-Winters":
                            st.success(f"✅ Data stasioner (p-value = {p_value:.4f})")

                    # =====================================================
                    # 2. Cek ASUMSI RESIDUAL (WHITE NOISE, NORMALITAS)
                    # =====================================================
                    # Sementara kita cek untuk ARIMA saja
                    if method_choice == "ARIMA":
                        try:
                            model_arima = ARIMA(train, order=(1, 1, 1))
                            model_fit = model_arima.fit()

                            resid = model_fit.resid

                            # --- Ljung-Box test (cek autokorelasi residual) ---
                            lb_test = acorr_ljungbox(resid, lags=[10], return_df=True)
                            lb_pval = lb_test["lb_pvalue"].iloc[0]

                            if lb_pval > 0.05:
                                st.success(f"✅ Residual memenuhi asumsi white noise (Ljung-Box p = {lb_pval:.4f})")
                            else:
                                st.warning(f"⚠️ Residual masih ada autokorelasi (Ljung-Box p = {lb_pval:.4f})")

                            # --- Normalitas residual ---
                            jb_stat, jb_pval = jarque_bera(resid)
                            if jb_pval > 0.05:
                                st.success(f"✅ Residual berdistribusi normal (JB p = {jb_pval:.4f})")
                            else:
                                st.warning(f"⚠️ Residual tidak normal (JB p = {jb_pval:.4f})")

                        except Exception as e:
                            st.error(f"Gagal fitting ARIMA untuk uji asumsi: {e}")

                    # =====================================================
                    # 3. Forecasting sesuai pilihan
                    # =====================================================
                    st.write(f"📊 Forecasting **{saham_choice} - {metric_choice}** dengan metode **{method_choice}**")

                    forecast = None
                    try:
                        if method_choice == "ARIMA":
                            model_arima = ARIMA(train, order=(1, 1, 1))
                            model_fit = model_arima.fit()
                            forecast = model_fit.forecast(steps=len(test))

                        elif method_choice == "Holt-Winters":
                            if len(train) > 20:
                                model_hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=12)
                                model_hw_fit = model_hw.fit()
                            else:
                                model_hw = SimpleExpSmoothing(train)
                                model_hw_fit = model_hw.fit()
                            forecast = model_hw_fit.forecast(len(test))

                        elif method_choice == "SVR":
                            scaler = MinMaxScaler()
                            X_train = np.arange(len(train)).reshape(-1, 1)
                            y_train = scaler.fit_transform(train.values.reshape(-1, 1)).ravel()
                            svr = SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
                            svr.fit(X_train, y_train)

                            X_test = np.arange(len(train), len(train) + len(test)).reshape(-1, 1)
                            forecast_svr_scaled = svr.predict(X_test)
                            forecast = scaler.inverse_transform(forecast_svr_scaled.reshape(-1, 1)).ravel()
                    except Exception as e:
                        st.error(f"{method_choice} error: {e}")

                    # =====================================================
                    # 4. Visualisasi + MAPE
                    # =====================================================
                    if forecast is not None:
                        df_plot = pd.DataFrame({"Date": ts.index, "Actual": ts.values})
                        df_forecast = pd.DataFrame({"Date": test.index, "Forecast": forecast})
                        df_all = pd.merge(df_plot, df_forecast, on="Date", how="outer")

                        df_long = df_all.melt("Date", var_name="Type", value_name="Value")

                        line_chart = alt.Chart(df_long).mark_line().encode(
                            x="Date:T",
                            y="Value:Q",
                            color=alt.Color("Type:N",
                                            scale=alt.Scale(domain=["Actual", "Forecast"],
                                                            range=["#1a69e0", "#ee6525"])),
                            strokeDash=alt.StrokeDash("Type:N",
                                                    scale=alt.Scale(domain=["Actual", "Forecast"],
                                                                    range=[[1, 0], [4, 4]])),
                            tooltip=["Date:T", "Value:Q", "Type:N"]
                        )

                        st.altair_chart(line_chart, use_container_width=True)

                        # --- MAPE ---

                        # pastikan array
                        y_true = np.array(test)
                        y_pred = np.array(forecast)

                        # buang nilai nol atau NaN pada data aktual
                        mask = (y_true != 0) & ~np.isnan(y_true) & ~np.isnan(y_pred)

                        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
                        st.success(f"Nilai MAPE metode {method_choice}: {mape:.2f} %")
                        st.caption(f"✅ MAPE (Pengukuran yang menunjukkan semakin kecil nilai MAPE semakin baik dalam memprediksi)")
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}. Silakan ganti time horizon yang lebih panjang lagi atau jika masih error, maka pilih saham lainnya.")
        with col1:
            with st.container(border=True):
                try:
                    st.subheader("🤖 TRENDS ADVISOR WITH AI")
                
                    st.info(
                        f"Nilai MAPE metode {method_choice}: {mape:.2f}% → "
                        f"Semakin kecil MAPE, semakin akurat dalam meramalkan harga {metric_choice} di {saham_choice}."
                    )

                    # simpan riwayat percakapan
                    if "messages" not in st.session_state:
                        st.session_state.messages = []

                    # tampilkan riwayat
                    #for msg in st.session_state.messages:
                        #with st.chat_message(msg["role"]):
                            #st.write(msg["content"])

                    # input user
                    if prompt := st.chat_input("Tanyakan arah tren (ex: menurun, naik, stagnan)..."):
                        # tampilkan pesan user
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.write(prompt)
                        user_input = prompt.lower()

                        # respon chatbot
                        if "menurun" in user_input or "turun" in user_input:
                            reply = "📉 Prediksi harga menurun → disarankan **jual / hindari beli dulu**. Investor jangka panjang bisa tunggu momentum beli di bawah."
                        elif "naik" in user_input or "menaik" in user_input:
                            reply = "📈 Prediksi harga naik → rekomendasi **beli / hold** untuk memaksimalkan potensi keuntungan."
                        elif "stagnan" in user_input or "lurus" in user_input or "tetap" in user_input:
                            reply = "➖ Prediksi harga stagnan → sebaiknya **hold**, karena peluang profit terbatas."
                        else:
                            reply = "🤔 Saya hanya bisa menjawab tren: menurun, naik, atau stagnan."

                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        with st.chat_message("assistant"):
                            st.write(reply)
                except:
                    st.error("Terdapat Error pada Fiture Forecasting! Silahkan Cermati Errornya!")

with tab2:
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
                        <strong>DAFTAR SAHAM BEI</strong>
                    </div>
                    <p></p>
                    """, unsafe_allow_html=True
                )
    st.info("Adapun daftar saham-saham ini berdasarkan dari perusahaan saham yang terdaftar di Bursa Efek Indonesia per September 2025")

    # --- Styling biar tabel bagus ---
    styled_df = (
        df_saham.style
        .set_properties(**{"text-align": "center"})
        .set_table_styles(
            [
                {"selector": "th", "props": [
                    ("background-color", "#FAB12F"),
                    ("color", "black"),
                    ("font-weight", "bold"),
                    ("text-align", "center")
                ]}
            ]
        )
    )

    st.dataframe(styled_df, use_container_width=True, height=500)

with st.container(border=False):
    st.caption("Copyrights @2025 by Ferdyansyah P Putra")
    st.caption("Connect with me: [My LinkedIn](https://www.linkedin.com/in/ferdypput/)")
