from flask import Flask
import config
from flask_bootstrap import Bootstrap
from apscheduler.schedulers.background import BackgroundScheduler
import sqlalchemy

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['CLIENT_SECRET']


# connect to local instance of mysqlDB server
engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)

# create session and base declarative
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# make sure user table is created
from App.user_operations import User
Base.metadata.create_all(engine)

# schedule updates for the TopTracks playlists
from App.services import updatePlaylists
scheduler = BackgroundScheduler()
scheduler.add_job(updatePlaylists, trigger='interval', days=1)
scheduler.start()

import App.routes
bootstrap = Bootstrap(app)

if __name__ == "__main__":
    app.run(debug=True)