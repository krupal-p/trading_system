import logging
from datetime import datetime, tzinfo
from flask import Flask
from flask_restful import Resource, Api
from flask_api import HomePage


logging.basicConfig(
    filename=f"logs/server_log_{datetime.utcnow().strftime('%Y-%m-%d-%H:%M')}",
    level=logging.INFO,
)


def main(port=8000):
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(HomePage, "/")

    logging.info("Starting trading server")
    app.run(debug=True, port=port)


if __name__ == "__main__":
    main()
