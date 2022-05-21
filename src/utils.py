from io import StringIO
import logging
from datetime import datetime
from operator import index
import pandas as pd
import requests
import finnhub

logging = logging.getLogger()


def get_alpha_vantage_historical_data(ticker, interval):
    """Get historical intraday data from Alpha Vantage API. Saves price series to {ticker}_price.csv

    Args:
        ticker (str): Stock symbol
        interval (int): Time interval for intraday prices in minutes

    Returns:
        pandas DF: DataFrame with datetime, price
    """
    try:
        ALPHA_VANTAGE_API_KEY = "6ZHQHNVQUR40SSMF"
        CSV_URL = "https://www.alphavantage.co/query?"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": ticker,
            "interval": f"{interval}min",
            "datatype": "csv",
            "outputsize": "full",
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        r = requests.get(CSV_URL, params=params)

        csvStringIO = StringIO(r.content.decode("utf-8"))

        df = pd.read_csv(
            csvStringIO, sep=",", header=0, parse_dates={"datetime": ["timestamp"]}
        ).rename(columns={"close": "price"})[["datetime", "price"]]
        df["price"] = df["price"].apply(lambda x: round(x, 2))
        # df.to_csv(f"../data/{ticker}_price.csv", index=False)
        df = df.sort_values(
            "datetime",
            ascending=True,
        ).reset_index(drop=True)

        return df
    except Exception as e:
        logging.error(e)


def get_realtime_quote(ticker):
    FINNHUB_API_KEY = "ca3sllqad3ia58rfhmjg"
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    quote = finnhub_client.quote(ticker)
    result = {
        "datetime": datetime.fromtimestamp(quote["t"]),
        "price": quote["c"],
    }
    return result


def calculate_signal_and_pnl(df):
    df["signal"] = 0
    df["pnl"] = 0
    df["position"] = 0
    position = 0
    for i in range(1, len(df) - 1):
        current_price = df.iloc[i]["price"]
        avg_price = df.iloc[i]["S_avg"]
        sigma = df.iloc[i]["sigma"]

        if current_price > (avg_price + sigma):
            df.at[i, "signal"] = 1
            position += 1
            df.at[i + 1, "position"] = position
        elif current_price < (avg_price - sigma):
            df.at[i, "signal"] = -1
            position -= 1
            df.at[i + 1, "position"] = position
        else:
            df.at[i, "signal"] = 0
            df.at[i + 1, "position"] = position

    for i in range(1, len(df)):
        previous_position = df.iloc[i - 1]["position"]
        current_price = df.iloc[i]["price"]
        previous_price = df.iloc[i - 1]["price"]
        pnl = previous_position * ((current_price / previous_price) - 1)
        df.at[i, "pnl"] = round(pnl, 2)

    return df


def add_tickers(tickers, interval):
    logging.info("Getting historical data from Alpha Vantage API...")
    for symbol in tickers:
        window = 24 * 60 // interval
        df = get_alpha_vantage_historical_data(symbol, interval=interval)
        df["S_avg"] = (
            df["price"].rolling(window=window).mean().apply(lambda x: round(x, 2))
        )
        df["sigma"] = df["price"].rolling(window=window).std()
        df = calculate_signal_and_pnl(df)

        # Saving to csv file
        df[["datetime", "price", "signal", "pnl"]].to_csv(
            f"data/{symbol}_result.csv", index=False
        )
        df[["datetime", "price"]].to_csv(f"data/{symbol}_price.csv", index=False)
