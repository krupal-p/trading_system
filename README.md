# Stock trading system

### Built with:
- Flask
- Flask-restful
- waitress
- requests
- pandas
- finnhub-python

## Getting Started


  
### Installation
    git clone https://github.com/krupal-p/trading_system.git
    cd trading_system
    pip3 install -r requirements.txt

### Enter gmail credentials in config_file.txt
    gmail_username = ******@gmail.com
    gmail_password = **********

## Usage
### Starting up server with no options
    python3 src/server.py

### Starting up server with options
    python3 src/server.py --tickers FB AMZN MSFT --port 5000 --reload filename.csv --minutes 15

### Running queries on client
    python3 src/client.py --price YYYY-MM-DD-HH:MM
    python3 src/client.py --signal YYYY-MM-DD-HH:MM
    python3 src/client.py --server_address XXX.XXX.XXX.XXX:YYYY --price now
    python3 src/client.py --del_ticker TICKER
    python3 src/client.py --add_ticker TICKER
    python3 src/client.py --reset
    python3 src/client.py --price now --signal now --server_address XXX.XXX.XXX.XXX:YYYY --del_ticker TICKER --add_ticker TICKER --reset
