import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

st.set_page_config(page_title="📈 Stock Dashboard", layout="wide")

st.markdown("## 📊 Stock Performance Dashboard")
st.caption("Easily compare stocks against others in their peer group.")

# Sidebar / Left Panel
col1, col2 = st.columns([1, 3])

with col1:
    # Multi select tickers
    available_tickers = ["AAPL","AMZN","GOOGL","META","MSFT","NVDA","TSLA","BBRI.JK","BBCA.JK","BMRI.JK"]
    selected = st.multiselect("Stock tickers", available_tickers, default=["AAPL","MSFT","GOOGL","NVDA"])

    # Time horizon buttons
    horizon = st.radio("Time horizon", ["1M","3M","6M","1Y","5Y","10Y"], index=2)

    # Hitung start_date dari horizon
    end_date = date.today()
    if horizon == "1M": start_date = end_date - timedelta(days=30)
    elif horizon == "3M": start_date = end_date - timedelta(days=90)
    elif horizon == "6M": start_date = end_date - timedelta(days=180)
    elif horizon == "1Y": start_date = end_date - timedelta(days=365)
    elif horizon == "5Y": start_date = end_date - timedelta(days=1825)
    elif horizon == "10Y": start_date = end_date - timedelta(days=3650)

# Get stock data
if selected:
    data = yf.download(selected, start=start_date, end=end_date)

    if not data.empty:
        # Handle multi ticker vs single
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs("Adj Close", axis=1, level=0)
        else:
            data = data[["Adj Close"]]
            data.columns = selected

        normalized = data / data.iloc[0]
        df_long = normalized.reset_index().melt(id_vars="Date", var_name="Stock", value_name="Normalized Price")

        # Grafik interaktif
        with col2:
            fig = px.line(df_long, x="Date", y="Normalized Price", color="Stock")
            fig.update_layout(
                hovermode="x unified",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                legend_title="Stock"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Hitung performance terakhir
        returns = (normalized.iloc[-1] - 1) * 100
        best_stock = returns.idxmax()
        worst_stock = returns.idxmin()

        with col1:
            st.success(f"📈 Best stock: {best_stock} (+{returns[best_stock]:.2f}%)")
            st.error(f"📉 Worst stock: {worst_stock} ({returns[worst_stock]:.2f}%)")

        # Data download
        csv = data.to_csv().encode("utf-8")
        st.download_button("⬇️ Download CSV", csv, f"stocks_{horizon}.csv", "text/csv")
