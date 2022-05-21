import argparse
import logging

logging = logging.getLogger()
parser = argparse.ArgumentParser(description="Process client command line arguments")

try:
    parser.add_argument(
        "-p",
        "--price",
        type=str,
        help="If specified, queries server for latest price available as of the time specified. The time queried is expected to be in UTC Time.",
    )
    parser.add_argument(
        "-s",
        "--signal",
        type=str,
        help="If specified, queries server for latest trading signal available as of the time specified. The time queried is expected to be in UTC Time.",
    )
    parser.add_argument(
        "-sa",
        "--server_address",
        type=str,
        default="127.0.0.1:8000",
        help="If specified, connect to server running on the IP address, and use specified port number. If this option is not specified, client assumes that the server is running on 127.0.0.1:8000",
    )
    parser.add_argument(
        "-d",
        "--del_ticker",
        type=str,
        help="Instruct the server to del a ticker from the server database. Returns 0=success, 1=server error, 2=ticker not found",
    )
    parser.add_argument(
        "-a",
        "--add_ticker",
        type=str,
        help="Instruct the server to add a new ticker to the server database. Server must download historical data for said ticker, and start appending on the next pull. Returns 0=success, 1=server error, 2=invalid ticker",
    )
    parser.add_argument(
        "-r",
        "--reset",
        action="store_const",
        const=True,
        help="If specified, instructs the server to reset all the data. Server must re-download data and tell client that it was successful. Client exits with return code: 0=success, 1=failure",
    )
except:
    logging.error("Incorrect arguments passed")
