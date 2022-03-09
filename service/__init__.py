from flask import Flask

app = Flask(__name__)

# Import the routes After the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import
from service import routes, models,error_handlers