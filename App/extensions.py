from flask_bootstrap import Bootstrap
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

bootstrap = Bootstrap()
scheduler = AsyncIOScheduler()
