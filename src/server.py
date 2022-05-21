import logging
from datetime import datetime, tzinfo
import argparse
import sys
from os import walk

import pandas as pd
from flask import Flask
from flask_restful import Api
from flask_routes import HomePage, Price, Signal, DelTicker, AddTicker, Reset

from utils import (
    get_alpha_vantage_historical_data,
    calculate_signal_and_pnl,
    add_tickers,
)

logging.basicConfig(
    filename=f"logs/server_log_{datetime.utcnow().strftime('%Y-%m-%d-%H:%M')}",
    level=logging.INFO,
)

parser = argparse.ArgumentParser(description="Process arguments when server starts")
try:
    parser.add_argument(
        "-t",
        "--tickers",
        nargs="+",
        default=["AAPL"],
        help="If specified, download data for all the US tickers specified. If this option is not specified, the server will download data for ticker 'AAPL' (Max of 3 tickers)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="It specifies the network port for the server. This argument is optional, and default port is 8000.",
    )
    parser.add_argument(
        "-r",
        "--reload",
        type=str,
        help="If specified, the server will load historical data from the reload file instead of querying from Source 1",
    )
    parser.add_argument(
        "-m",
        "--minutes",
        type=int,
        default=5,
        choices=[5, 15, 30, 60],
        help="It specifies the sample data being downloaded. It only accepts (5,15,30,60) as inputs, and default value is 5.",
    )
except:
    print("Incorrect arguments passed")


def main(args, port=8000):
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HomePage, "/")
    api.add_resource(Price, "/price/<query_datetime>")
    api.add_resource(Signal, "/signal/<query_datetime>")
    api.add_resource(AddTicker, "/add_ticker/<ticker>")
    api.add_resource(DelTicker, "/del_ticker/<ticker>")
    api.add_resource(Reset, "/reset")

    logging.info("Starting trading server")
    app.run(debug=True, port=port)


def program_start(args, reload_symbol):
    add_tickers(
        tickers=[ticker for ticker in args.tickers if ticker != reload_symbol],
        interval=args.minutes,
    )


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    try:
        data_files = list(walk("data/"))[0][2]
        if args.reload in data_files:
            reload_symbol = args.reload.split("_")[0]
        else:
            reload_symbol = None

        program_start(args=args, reload_symbol=reload_symbol)

        main(args, port=args.port)
    except KeyboardInterrupt:
        logging.error("Server Terminated")
