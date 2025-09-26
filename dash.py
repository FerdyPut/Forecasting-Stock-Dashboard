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
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

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

with col1:
    with st.container(border=True):
            # --- Input: pilih skema warna ---
        st.write(f"### 🌐Heatmap Saham: Market Cap vs Daily Return")
        color_map = st.selectbox(
            "Pilih Skema Warna",
            ["RdYlGn", "Viridis", "Bluered", "Plasma", "Cividis"],
            index=3
        )
        daily_return = data_metric.pct_change().iloc[-1] * 100  # % terakhir
        daily_return = daily_return.round(2)

        # --- Ambil Market Cap ---
        market_caps = {}
        for t in tickers:
            info = yf.Ticker(t).info
            market_caps[t] = info.get("marketCap", None)

        # --- Buat DataFrame ringkasan ---
        df_heat = pd.DataFrame({
            "Saham": tickers,
            "Daily Return (%)": [daily_return[t] for t in tickers],
            "Market Cap": [market_caps[t] for t in tickers]
        })

        # --- Treemap Plotly ---
        fig = px.treemap(
            df_heat,
            path=["Saham"],
            values="Market Cap",
            color="Daily Return (%)",
            color_continuous_scale=color_map
        )

        # Geser colorbar ke atas
        fig.update_layout(
            coloraxis_colorbar=dict(
                orientation="h",
                y=1.05,
                x=0.5,
                xanchor="center",
                title="Daily Return (%)"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("📈 Forecasting Saham")

        # --- Pilih saham & metric ---
        saham_choice = st.selectbox("Pilih Saham untuk Forecasting", tickers)
        metric_choice = st.session_state.metric_choice
        st.write(f"📊 Forecasting untuk **{saham_choice} - {metric_choice}**")

        ts = data[metric_choice][saham_choice].dropna()

        # --- Train-test split ---
        train_size = int(len(ts) * 0.8)
        train, test = ts.iloc[:train_size], ts.iloc[train_size:]

        # --- Cek stasioneritas (ADF Test) ---
        adf_result = adfuller(train)
        st.write("ADF Statistic:", round(adf_result[0], 3))
        st.write("p-value:", round(adf_result[1], 3))
        if adf_result[1] > 0.05:
            st.warning("⚠️ Data tidak stasioner → dilakukan differencing untuk ARIMA")
            ts_diff = ts.diff().dropna()
            train, test = ts_diff.iloc[:train_size], ts_diff.iloc[train_size:]
        else:
            ts_diff = ts

        # =======================
        # 1. ARIMA (statsmodels)
        # =======================
        try:
            # order default (1,1,1), bisa dioptimasi manual/grid search
            model_arima = ARIMA(train, order=(1, 1, 1))
            model_fit = model_arima.fit()
            forecast_arima = model_fit.forecast(steps=len(test))
        except Exception as e:
            st.error(f"ARIMA error: {e}")
            forecast_arima = [np.nan] * len(test)

        # =======================
        # 2. Holt-Winters
        # =======================
        try:
            if len(train) > 20:  # minimal data
                model_hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=12)
                model_hw_fit = model_hw.fit()
            else:
                model_hw = SimpleExpSmoothing(train)
                model_hw_fit = model_hw.fit()
            forecast_hw = model_hw_fit.forecast(len(test))
        except Exception as e:
            st.error(f"Holt-Winters error: {e}")
            forecast_hw = [np.nan] * len(test)

        # =======================
        # 3. SVR
        # =======================
        try:
            scaler = MinMaxScaler()
            X_train = np.arange(len(train)).reshape(-1, 1)
            y_train = scaler.fit_transform(train.values.reshape(-1, 1)).ravel()

            svr = SVR(kernel="rbf", C=100, gamma=0.1, epsilon=0.1)
            svr.fit(X_train, y_train)

            X_test = np.arange(len(train), len(train) + len(test)).reshape(-1, 1)
            forecast_svr_scaled = svr.predict(X_test)
            forecast_svr = scaler.inverse_transform(forecast_svr_scaled.reshape(-1, 1)).ravel()
        except Exception as e:
            st.error(f"SVR error: {e}")
            forecast_svr = [np.nan] * len(test)

        # =======================
        # Evaluasi & Plot
        # =======================
        results = {
            "ARIMA": forecast_arima,
            "Holt-Winters": forecast_hw,
            "SVR": forecast_svr
        }

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(ts.index, ts.values, label="Actual", color="black")
        ax.plot(test.index, forecast_arima, label="ARIMA Forecast", linestyle="--")
        ax.plot(test.index, forecast_hw, label="Holt-Winters Forecast", linestyle="--")
        ax.plot(test.index, forecast_svr, label="SVR Forecast", linestyle="--")
        ax.legend()
        st.pyplot(fig)

        # --- RMSE ---
        for model_name, forecast in results.items():
            if not np.isnan(forecast).all():
                rmse = np.sqrt(mean_squared_error(test, forecast))
                st.write(f"✅ RMSE {model_name}: {rmse:.2f}")