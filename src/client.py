import logging
import re
from datetime import datetime

from client_argument_parser import parser
import requests


logging.basicConfig(
    filename=f"logs/client_log_{datetime.utcnow().strftime('%Y-%m-%d-%H:%M')}",
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M',
    level=logging.INFO,
)


def get_base_url(ip_address="127.0.0.1", port=8000):
    return f"http://{ip_address}:{port}"


def is_valid_server_address(server_address):
    is_valid = re.fullmatch("^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}$", server_address)
    return True if is_valid else False


def is_valid_datetime(datetime_input):
    date_format = "%Y-%m-%d-%H:%M"
    try:
        datetime.strptime(datetime_input, date_format)
        return True
    except ValueError:
        logging.error("Incorrect datetime format, should be YYYY-MM-DD-HH:MM or now")
        return False


def get_price(datetime_input):
    url = f"{base_url}/price/{datetime_input}"
    r = requests.get(url=url, timeout=30)
    print(r.text)
    try:
        return r.json()
    except:
        return r.text


def get_signal(datetime_input):
    url = f"{base_url}/signal/{datetime_input}"
    r = requests.get(url=url, timeout=30)
    print(r.text)
    try:
        return r.json()
    except:
        return r.text


def del_ticker(ticker):
    url = f"{base_url}/del_ticker/{ticker}"
    r = requests.get(url=url, timeout=30)
    print(r.text)


def add_ticker(ticker):
    url = f"{base_url}/add_ticker/{ticker}"
    r = requests.get(url=url, timeout=30)
    print(r.text)


def reset():
    url = f"{base_url}/reset"
    r = requests.get(url=url, timeout=30)
    print(r.text)


def main():
    if args.price and (args.price.lower() == "now" or is_valid_datetime(args.price)):
        price_response = get_price(args.price)
    if args.signal and (args.signal.lower() == "now" or is_valid_datetime(args.signal)):
        signal_response = get_signal(args.signal)
    if args.del_ticker:
        del_ticker_response = del_ticker(args.del_ticker)
    if args.add_ticker:
        add_ticker_response = add_ticker(args.add_ticker)
    if args.reset:
        reset_response = reset()


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    if args.server_address and is_valid_server_address(args.server_address):
        ip_address, port = args.server_address.split(":")
        base_url = get_base_url(ip_address=ip_address, port=port)
        r = requests.get(url=base_url + "/", timeout=30)
        print(r.text)
    else:
        base_url = get_base_url()
    main()
