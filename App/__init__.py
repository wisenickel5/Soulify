from flask import Flask
from flask_bootstrap import Bootstrap
# from extensions import bootstrap, scheduler
from App.scheduler import init_scheduler
from App.database import init_db
from App import config


def init_routes():
    from App import routes


app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['CLIENT_SECRET']

init_db()
init_scheduler()
init_routes()

bootstrap = Bootstrap(app)
