import json

from flask import Flask
import pandas as pd
import os

from flask import Response


def register_api_routes(app: Flask):
    """
    Registers all app API routes
    :param Flask app: The Flask app to prep
    :return: Nothing
    """
    app.route('/api/v1/data', methods=['GET'])(fetch_data)

def fetch_data():
    """
    TODO: This is hacky now, @nugentb7 can hook up to SQL instead of just loading and returning the CSV
    Should feature pagination and stuff, but honestly thats not important atm
    :param page:
    :return:
    """

    data = json.load(open('server/data/waterway-readings.json', encoding='iso-8859-1'))
    return Response(json.dumps(data), content_type='application/json')


