from flask import Flask
import config
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
import sqlalchemy
from App import routes
from App.user_operations import User

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['CLIENT_SECRET']

# connect to local instance of mysqlDB server
engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)

from sqlalchemy.orm import sessionmaker # create session and base declarative
Session = sessionmaker(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
Base.metadata.create_all(engine) # make sure user table is created

# schedule updates for the TopTracks playlists
from App.services import updatePlaylists
scheduler = BackgroundScheduler()
scheduler.add_job(updatePlaylists, trigger='interval', days=1)
scheduler.start()

bootstrap = Bootstrap(app)