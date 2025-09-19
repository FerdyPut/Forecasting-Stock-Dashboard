import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 IDX Stock Dashboard", layout="wide")

# ===== Daftar saham Indonesia (contoh, bisa ditambah sendiri) =====
tickers_id = {
    "BBCA": "BBCA.JK",
    "BBRI": "BBRI.JK",
    "BMRI": "BMRI.JK",
    "ASII": "ASII.JK",
    "TLKM": "TLKM.JK",
    "ICBP": "ICBP.JK",
    "UNVR": "UNVR.JK",
    "ANTM": "ANTM.JK",
    "INDF": "INDF.JK",
    "ADRO": "ADRO.JK",
    "PGAS": "PGAS.JK",
    "KLBF": "KLBF.JK",
}

# ===== Sidebar =====
st.sidebar.header("⚙️ Filter")

# Multi select tickers
selected_names = st.sidebar.multiselect(
    "Pilih Saham (IDX)", list(tickers_id.keys()), default=["BBCA", "BBRI", "BMRI"]
)
selected = [tickers_id[name] for name in selected_names]

# Time horizon
horizon = st.sidebar.radio(
    "Time Horizon",
    ["1W", "1M", "3M", "6M", "1Y", "5Y", "Max", "Custom Date"],
    index=2,
    horizontal=False
)

end_date = datetime.today()
if horizon == "1W":
    start_date = end_date - timedelta(weeks=1)
elif horizon == "1M":
    start_date = end_date - timedelta(days=30)
elif horizon == "3M":
    start_date = end_date - timedelta(days=90)
elif horizon == "6M":
    start_date = end_date - timedelta(days=180)
elif horizon == "1Y":
    start_date = end_date - timedelta(days=365)
elif horizon == "5Y":
    start_date = end_date - timedelta(days=5*365)
elif horizon == "Max":
    start_date = "2000-01-01"
else:  # Custom Date
    start_date = st.sidebar.date_input("Start Date", datetime(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.today())

# ===== Ambil Data =====
if selected:
    data = yf.download(selected, start=start_date, end=end_date)

    if data.empty:
        st.warning("⚠️ Tidak ada data untuk saham & periode ini.")
    else:
        # Handle multi ticker
        if isinstance(data.columns, pd.MultiIndex):
            if "Adj Close" in data.columns.levels[0]:
                data = data.xs("Adj Close", axis=1, level=0)
            elif "Close" in data.columns.levels[0]:
                data = data.xs("Close", axis=1, level=0)
            else:
                st.error("⚠️ Data harga tidak ditemukan.")
                st.stop()
        else:
            if "Adj Close" in data.columns:
                data = data[["Adj Close"]]
                data.columns = selected
            elif "Close" in data.columns:
                data = data[["Close"]]
                data.columns = selected
            else:
                st.error("⚠️ Data harga tidak ditemukan.")
                st.stop()

        # ===== Plotly Chart =====
        fig = go.Figure()
        for col in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data[col], mode="lines", name=col,
                hovertemplate=f"{col}<br>Date: %{x|%Y-%m-%d}<br>Price: %{y:.2f}<extra></extra>"
            ))

        fig.update_layout(
            title="📊 IDX Stock Prices",
            xaxis_title="Date",
            yaxis_title="Price (IDR)",
            template="plotly_dark",
            hovermode="x unified",
            legend_title="Stock",
            height=600
        )

        # ===== Show Chart =====
        st.plotly_chart(fig, use_container_width=True)

        # ===== Download Data =====
        csv = data.to_csv().encode("utf-8")
        st.download_button("⬇️ Download Data (CSV)", data=csv, file_name="stocks.csv", mime="text/csv")

else:
    st.info("👉 Pilih minimal 1 saham dari sidebar.")
