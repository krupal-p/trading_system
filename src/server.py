import logging
from datetime import datetime, timedelta
import sys, os
from os import walk
import atexit

import pandas as pd
from flask import Flask
from flask_restful import Api, Resource
from waitress import serve

from server_argument_parser import parser

from utils import (
    add_ticker,
    get_realtime_quote,
    calculate_signal_and_pnl,
    calculate_avg_and_sigma,
    convert_utc_datetime,
    get_price,
    get_signal,
)
import threading, time, requests

# Create Data and logs folder if they don't already exist
if not os.path.exists("data/"):
    os.makedirs("data/")
if not os.path.exists("logs/"):
    os.makedirs("logs/")

# Logger configuration
logging.basicConfig(
    filename=f"logs/server_log_{datetime.utcnow().strftime('%Y-%m-%d-%H:%M')}",
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M',
    level=logging.INFO,
)

# Classes for Flask-restful routes/endpoints
class HomePage(Resource):
    def get(self):
        return "Connected to trading server"


class Price(Resource):
    def get(self, query_datetime):
        if query_datetime.lower() == "now":
            query_datetime = datetime.now().strftime("%Y-%m-%d-%H:%M")
        elif (datetime.strptime(convert_utc_datetime(query_datetime), '%Y-%m-%d-%H:%M') > datetime.now()):
            return "Server has no data"
        else:
            query_datetime = convert_utc_datetime(query_datetime)

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
        elif (datetime.strptime(convert_utc_datetime(query_datetime), '%Y-%m-%d-%H:%M') > datetime.now()):
            return "Server has no data"
        else:
            query_datetime = convert_utc_datetime(query_datetime)

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
        ticker = ticker.lower()
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
        else:
            return 1


class AddTicker(Resource):
    def get(self, ticker):
        ticker = ticker.lower()
        try:
            add_ticker_status = add_ticker(ticker, args.minutes)
            if add_ticker_status == "Invalid ticker":
                return 2
            data[ticker] = pd.read_csv(f"data/{ticker}_result.csv", header=0)
            return 0
        except Exception as e:
            logging.error("Error while adding ticker")
            return 1


class Reset(Resource):
    def get(self):
        global data
        data = dict()
        try:
            data_files = list(walk("data/"))[0][2]
            for file in data_files:
                if os.path.exists(f"data/{file}"):
                    os.remove(f"data/{file}")
                else:
                    logging.error(f"Error resetting server data")
            return 0
        except Exception as e:
            logging.error("Error while resetting server data")
            return 1


def load_data():
    """Function to load historical data on server startup

    Returns:
        dict: dictionary with keys are symbol and DataFrame as values
    """    
    data = dict()
    data_files = [file for file in list(walk("data/"))[0][2] if "_result.csv" in file]
    for file in data_files:
        symbol = file.split("_")[0]
        df = pd.read_csv("data/" + file, header=0)
        data[symbol] = df
    return data


def update_data():
    """Function to get realtime data every X minutes from Finnhub for every symbol and append to internal data structure. 
       Returns None
    """    
    for symbol in data:
        logging.info("Getting realtime data for: %s", symbol)
        try:
            realtime_quote = get_realtime_quote(symbol)
        except Exception as e:
            logging.error(e)
            continue 
        try:
            df = data[symbol]
        except KeyError as e:
            logging.error(e)
            continue 
        # appends realtime quote to existing interal data structure
        df.at[df.shape[0] + 1, ("datetime", "price")] = (
            realtime_quote["datetime"],
            realtime_quote["price"],
        )
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = calculate_avg_and_sigma(df, interval=args.minutes)
        df = calculate_signal_and_pnl(df)
        data[symbol] = df


def main():
    """ Creates and runs Flask app through waitress.
    Runs a loop on a separate thread to continously update data every X minutes after server startup 
    """    
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HomePage, "/")
    api.add_resource(Price, "/price/<query_datetime>")
    api.add_resource(Signal, "/signal/<query_datetime>")
    api.add_resource(AddTicker, "/add_ticker/<ticker>")
    api.add_resource(DelTicker, "/del_ticker/<ticker>")
    api.add_resource(Reset, "/reset")

    @app.before_first_request
    def activate_job():
        def run_job():
            """Task to update realtime data every X minutes 
            """            
            last_data_update = datetime.now()
            while True:
                next_data_update = last_data_update + timedelta(
                    seconds=args.minutes * 60
                )
                if last_data_update < next_data_update:
                    update_data()
                    logging.info("Updated realtime data for subscribed tickers")
                    last_data_update = datetime.now()
                    time.sleep(args.minutes * 60)

        thread = threading.Thread(target=run_job)
        thread.start()


    def start_runner():
        """Function to get the @app.before_first_request job started when server starts up.
        Server makes a request to itself to get the task started. 
        """        
        def start_loop():
            not_started = True
            while not_started:
                try:
                    r = requests.get(url=f"http://127.0.0.1:{args.port}/")
                    if r.status_code == 200:
                        not_started = False
                except:
                    time.sleep(2)

        thread = threading.Thread(target=start_loop)
        thread.start()

    start_runner()

    logging.info("Starting trading server")
    serve(app, listen=f'*:{args.port}')


def server_start_up_tasks():
    """ Startup tasks to run when the server starts. 
    Tasks:
    - add historical data from list of tickers provided
    - if reload file provided and that symbol is in tickers provided, it loads from reload file
    """    
    tickers = [ticker for ticker in args.tickers if ticker != reload_symbol]
    for ticker in tickers:
        add_ticker(
            ticker=ticker,
            interval=args.minutes,
        )

def at_keyboard_interrupt():
    sys.exit(0)

atexit.register(at_keyboard_interrupt)

if __name__ == "__main__":
    # parses initial arguments, lower case all tickers and file names
    args = parser.parse_args()
    logging.info(args)
    args.reload = args.reload.lower()
    args.tickers = [args.tickers[i].lower() for i in range(3)] if len(args.tickers) > 3 else [ticker.lower() for ticker in args.tickers]

    
    try:
        # If reload file on server, it will load from there otherwise does nothing
        data_files = list(walk("data/"))[0][2]
        if args.reload in data_files:
            reload_symbol = args.reload.split("_")[0]
        else:
            reload_symbol = None

        server_start_up_tasks()
        data = load_data()
        main()
    except KeyboardInterrupt:
        logging.error("Server Terminated")
        sys.exit(0)
