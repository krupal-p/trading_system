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
        print(r.url)

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



