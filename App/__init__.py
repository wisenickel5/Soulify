from flask import Flask
from flask_bootstrap import Bootstrap
import config
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from apscheduler.schedulers.background import BackgroundScheduler

template_dir = os.path.abspath('../Soulify/App/UI/templates/')
static_dir = os.path.abspath('../Soulify/App/UI/static/')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(config)
app.secret_key = app.config['CLIENT_SECRET']

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
# Create User Table
from App.DbMs.user_operations import User
Base.metadata.create_all(engine)

# schedule updates for the TopTracks playlists
from App.services import updatePlaylists
scheduler = BackgroundScheduler()
scheduler.add_job(updatePlaylists, trigger='interval', days=1)
scheduler.start()

from App import routes
bootstrap = Bootstrap(app)