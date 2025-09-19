import yfinance as yf
import plotly.express as px
import pandas as pd

tickers = ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]
data = yf.download(tickers, start="2023-01-01", end="2023-09-01")["Adj Close"]

# Normalisasi harga
normalized = data / data.iloc[0]

# Ubah ke format long
df_long = normalized.reset_index().melt(id_vars="Date", var_name="Stock", value_name="Normalized Price")

# Line chart interaktif
fig = px.line(
    df_long, 
    x="Date", 
    y="Normalized Price", 
    color="Stock", 
    title="Stock Comparison (Normalized Price)"
)

fig.show()
