from os import system

from server.routes.api import register_api_routes
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# We'll use server side sessions only
# SECRET_KEY = "h5t4h-G^DTkHdyx&_xJP@uB%UdE3sbhnC-6#bjubekx&jt2zFxg$kzcGea%8EtyQ" \
#              "pFd+u#FczG7=mWN7^n*G*gvTZQhd=nv!Ga9vcr6XD%zr6PNsQ?$h&!8D%Nw5G+C!" \
#              "_G4gThMxD9gtrYmz-m%UrTs9^vB+r95XJzaT4cUb@NMZCqJ73u4Rs?BGB*UWsTzN" \
#              "&vuwNVSq-XYR_xmXvR9Dek=?_v%%E8VXHgN#w@%#2su*R=9m2B_A3_#rqx9gaX&=" \
#              "?8RNNes^E_9*pynAL*Q49%EmK4FKJaqZ$ZqPE52aF+W^-+u_*=dKa=BVWEHsDX$S" \
#              "-TCN&7DHn4s7wHRc?PV=W!Tub9Au%8b!qzqBE&GNVNZZPd#tnWJ%NDfy@j$@3V+s" \
#              "3TQN_a!EaaKULvy#tca_r*q3zpHn%6MDwfSg4QkVwGCnnEgv7ZEv3GV=!8ER?PuP" \
#              "mHVUbjVJN@Ze@N7UQxFVznYcD9=gzWmYX!fVh&se$aqhzpr2u7nwy%ph^YUXCfj8"
# app.config.from_object(__name__)

# app.secret_key = SECRET_KEY
# app.session_cookie_name = "session"

# Session(app)
CORS(app, supports_credentials=True)

register_api_routes(app)

system('cls')
