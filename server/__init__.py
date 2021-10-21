from os import system

from server.routes.api import register_api_routes
from flask import Flask

app = Flask(__name__)

register_api_routes(app)

system('cls')
