from io import StringIO
import logging
from dateutil import tz
from datetime import datetime
import pandas as pd
import requests
import finnhub
from configparser import ConfigParser

logging = logging.getLogger()
config = ConfigParser()
config.read('src/config_file.txt')

def get_alpha_vantage_historical_data(ticker, interval):
    """Get historical intraday data from Alpha Vantage API. Saves price series to {ticker}_price.csv

    Args:
        ticker (str): Stock symbol
        interval (int): Time interval for intraday prices in minutes

    Returns:
        pandas DF: DataFrame with datetime, price or empty DataFrame with no data/error
    """
    logging.info("Getting historical data from Alpha Vantage API for %s", ticker)

    try:
        ALPHA_VANTAGE_API_KEY = config['API_KEYS']['ALPHA_VANTAGE_API_KEY']
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
        if r.status_code == 200 and "Invalid API call" in r.text:
            return pd.DataFrame()
        csvStringIO = StringIO(r.content.decode("utf-8"))

        df = pd.read_csv(
            csvStringIO, sep=",", header=0, parse_dates={"datetime": ["timestamp"]}
        ).rename(columns={"close": "price"})[["datetime", "price"]]
        df["price"] = df["price"].apply(lambda x: round(x, 2))
        df = df.sort_values(
            "datetime",
            ascending=True,
        ).reset_index(drop=True)
        return df
    except Exception as e:
        logging.error(e)
        return pd.DataFrame()


def get_realtime_quote(ticker):
    FINNHUB_API_KEY =config['API_KEYS']['FINNHUB_API_KEY']
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    quote = finnhub_client.quote(ticker.upper())
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


def calculate_avg_and_sigma(df, interval):
    window = 24 * 60 // interval
    df["S_avg"] = df["price"].rolling(window=window).mean().apply(lambda x: round(x, 2))
    df["sigma"] = df["price"].rolling(window=window).std()
    return df


def add_ticker(ticker, interval):
    df = get_alpha_vantage_historical_data(ticker, interval=interval)
    if df.shape[0] == 0:
        return "Invalid ticker"
    df = calculate_avg_and_sigma(df, interval=interval)
    df = calculate_signal_and_pnl(df)

    # Saving to csv file
    df[["datetime", "price", "signal", "pnl"]].to_csv(
        f"data/{ticker}_result.csv", index=False
    )
    df[["datetime", "price"]].to_csv(f"data/{ticker}_price.csv", index=False)


def convert_utc_datetime(utc_datetime):
    """Convert UTC datetime to New York Time

    Args:
        utc_datetime (str): UTC datetime in str format YYYY-MM-DD-HH:MM

    Returns:
        str: New York datetime in str format YYYY-MM-DD-HH:MM
    """
    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("America/New_York")
    return (
        datetime.strptime(utc_datetime, "%Y-%m-%d-%H:%M")
        .replace(tzinfo=from_zone)
        .astimezone(to_zone)
        .strftime("%Y-%m-%d-%H:%M")
    )


def get_price(df, query_datetime):
    price = (
        df.loc[(df['datetime'] <= query_datetime)].tail(1)["price"].values
    )
    if len(price) == 1:
        return int(price[0])
    elif len(price) == 0:
        return "No Data"


def get_signal(df, query_datetime):
    signal = (
        df.loc[(df['datetime'] <= query_datetime)].tail(1)["signal"].values
    )
    if len(signal) == 1:
        return int(signal[0])
    elif len(signal) == 0:
        return "No Data"
