#from services import update_playlists
from App.extensions import scheduler

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from App.services import update_playlists

def init_scheduler():
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    #scheduler = AsyncIOScheduler()
    scheduler.add_job(update_playlists, trigger='interval', days=1)
    scheduler.start()