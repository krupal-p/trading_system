from os import walk
import os
import time
from flask_restful import Resource
import pandas as pd
from datetime import datetime
from dateutil import tz

import logging

logging = logging.getLogger()

from utils import get_alpha_vantage_historical_data, get_realtime_quote


def load_data():
    data = dict()
    data_files = [file for file in list(walk("data/"))[0][2] if "_result.csv" in file]
    for file in data_files:
        symbol = file.split("_")[0]
        df = pd.read_csv("data/" + file, header=0)
        data[symbol] = df
    print(data)
    return data


def convert_utc_datetime(utc_datetime):
    """Convert UTC datetime to New York Time

    Args:
        utc_datetime (str): UTC datetime in str format YYYY-MM-DD-HH:MM

    Returns:
        str: New York datetime in str format YYYY-MM-DD-HH:MM
    """
    from_zone = from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("America/New_York")
    return (
        datetime.strptime(utc_datetime, "%Y-%m-%d-%H:%M")
        .replace(tzinfo=from_zone)
        .astimezone(to_zone)
        .strftime("%Y-%m-%d-%H:%M")
    )


def get_price(df, query_datetime):
    current_time = datetime.now().strftime("%Y-%m-%d-%H:%M")
    price = (
        df[(df["datetime"] < query_datetime) & (query_datetime <= current_time)]
        .tail(1)["price"]
        .values
    )
    if len(price) == 1:
        return price[0]
    elif len(price) == 0:
        return "No Data"


def get_signal(df, query_datetime):
    current_time = datetime.now().strftime("%Y-%m-%d-%H:%M")
    signal = (
        df[(df["datetime"] < query_datetime) & (query_datetime <= current_time)]
        .tail(1)["signal"]
        .values
    )
    if len(signal) == 1:
        return int(signal[0])
    elif len(signal) == 0:
        return "No Data"


data = load_data()


class HomePage(Resource):
    def get(self):
        return "Welcome to the trading server"


class Price(Resource):
    def get(self, query_datetime):
        if query_datetime.lower() == "now":
            query_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M")
        else:
            query_datetime = convert_utc_datetime(query_datetime)
        print(query_datetime)

        response = {}

        for symbol in data:
            response[symbol] = get_price(data[symbol], query_datetime=query_datetime)

        values = list(set(response.values()))
        if len(values) == 1 and values[0] == "No Data":
            return "Server has no data"
        else:
            return response


class Signal(Resource):
    def get(self, query_datetime):
        if query_datetime.lower() == "now":
            query_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M")
        else:
            query_datetime = convert_utc_datetime(query_datetime)
        print(query_datetime)

        response = {}

        for symbol in data:
            response[symbol] = get_signal(data[symbol], query_datetime=query_datetime)

        values = list(set(response.values()))
        if len(values) == 1 and values[0] == "No Data":
            return "Server has no data"
        else:
            return response


class DelTicker(Resource):
    def get(self, ticker):
        if ticker in data.keys():
            del data[ticker]
            data_files = [file for file in list(walk("data/"))[0][2] if ticker in file]
            for file in data_files:
                if os.path.exists(f"data/{file}"):
                    os.remove(f"data/{file}")
                else:
                    logging.error(
                        f"Historical data file not found on server for ticker: {ticker}"
                    )
            return 0
        elif ticker not in data.keys():
            return 2


class AddTicker(Resource):
    def get(self, ticker):
        print(ticker)


class Reset(Resource):
    pass
