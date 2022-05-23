# H1 Stock trading system using client-server model. 

# H2 Built with:
Flask
Flask-restful
waitress
requests
pandas
finnhub-python

# H2 Getting Started

# H1 Setting up virtual environment
    `pip install virtualenv`
    `virtual .venv`
    `source .venv/bin/activate`
    `pip install -r requirements.txt`

# H1 Update values in CONFIG file
    Update gmail_username and gmail_password

# H1 Starting up server with no options
    `python src/server.py`

# H1 Starting up server with options
    `python src/server.py --tickers FB AMZN MSFT --port 5000 --reload filename.csv --minutes 15`

# H1 Running queries on client
    `python src/client.py --price YYYY-MM-DD-HH:MM`
    `python src/client.py --signal YYYY-MM-DD-HH:MM`
    `python src/client.py --server_address XXX.XXX.XXX.XXX:YYYY --price now`
    `python src/client.py --del_ticker TICKER`
    `python src/client.py --add_ticker TICKER`
    `python src/client.py --reset`
    `python src/client.py --price now --signal now --server_address XXX.XXX.XXX.XXX:YYYY --del_ticker TICKER --add_ticker TICKER --reset`



