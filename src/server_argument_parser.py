import argparse

parser = argparse.ArgumentParser(description="Process arguments when server starts")
 
parser.add_argument(
    "-t",
    "--tickers",
    nargs="+",
    default=["aapl"],
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
    default="",
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
 
