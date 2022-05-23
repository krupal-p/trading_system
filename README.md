# Stock trading system using client-server model. 

### Built with:
- Flask
- Flask-restful
- waitress
- requests
- pandas
- finnhub-python

## Getting Started

### Setting up virtual environment
    pip3 install virtualenv
    virtual .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

### Update values in CONFIG file

    Update gmail_username and gmail_password

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
