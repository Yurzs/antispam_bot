from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from antispam_userbot.config import MONGO_DATABASE_NAME, mongo_client

jobstores = {
    'default': MongoDBJobStore(MONGO_DATABASE_NAME, client=mongo_client.delegate),
}

executors = {
    'default': AsyncIOExecutor(),
}


job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

scheduler = AsyncIOScheduler(jobstores=jobstores,
                             executors=executors,
                             job_defaults=job_defaults,
                             timezone=utc)
