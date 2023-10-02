from App.extensions import scheduler
from App.spotify.api_handler import SpotifyAPIHandler

def init_scheduler():
    scheduler.add_job(SpotifyAPIHandler.update_playlists, trigger='interval', days=1)
    scheduler.start()