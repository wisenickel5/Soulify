from flask import Flask
from flask_bootstrap import Bootstrap
#from extensions import bootstrap, scheduler
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['CLIENT_SECRET']
"""
# Initialize the Soulify DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
# Creating User Table:
# The User Model needs to be imported before
# the .create_all() function is called
from App.database_management.user_operations import User
Base.metadata.create_all(engine)"""

# Schedule updates for the TopTracks playlists
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from App.services import update_playlists

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
scheduler = AsyncIOScheduler()
scheduler.add_job(update_playlists, trigger='interval', days=1)
scheduler.start()

from App import routes
bootstrap = Bootstrap(app)