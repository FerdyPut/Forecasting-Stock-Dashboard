import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objs as go
from datetime import date

st.title("📈 Stock Forecasting App (Yahoo Finance)")

# Input multi ticker
tickers = st.text_input("Masukkan kode saham (pisahkan dengan koma, contoh: AAPL, TSLA, BBNI.JK):", "AAPL, TSLA")

# Range tanggal
start_date = st.date_input("Start Date", date(2020, 1, 1))
end_date = st.date_input("End Date", date.today())

# Periode ramalan
n_days = st.slider("Ramalkan berapa hari ke depan:", 7, 90, 30)

# Proses tiap ticker
for ticker in [t.strip() for t in tickers.split(",")]:
    st.subheader(f"📊 {ticker} Stock")

    # Ambil data dari Yahoo Finance
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.warning(f"Data untuk {ticker} tidak ditemukan.")
        continue

    # Plot harga close historis
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price'))
    fig.update_layout(title=f"{ticker} Closing Price", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    # Prophet Forecasting
    df_train = data.reset_index()[['Date','Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    model = Prophet(daily_seasonality=True)
    model.fit(df_train)

    future = model.make_future_dataframe(periods=n_days)
    forecast = model.predict(future)

    # Plot forecast
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
    fig2.add_trace(go.Scatter(x=df_train['ds'], y=df_train['y'], name='Actual'))
    fig2.update_layout(title=f"Forecast {ticker} {n_days} Hari ke Depan", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig2)

    # Tampilkan tabel prediksi
    st.write(forecast[['ds','yhat','yhat_lower','yhat_upper']].tail(n_days))
