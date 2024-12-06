import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from service.calculation import EfficiencyService
import pytz

class BaseScheduler:
    def __init__(self, job_func, cron_trigger):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Jakarta"))
        self.job_func = job_func
        self.cron_trigger = cron_trigger
        self.job = None

    def begin(self):
        if self.job is None:
            self.job = self.scheduler.add_job(self.job_func, trigger=self.cron_trigger, replace_existing=True)

    def start(self):
        self.begin()
        if not self.scheduler.running:
            self.scheduler.start()

    def close(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

class CycleEfficiencyScheduler(BaseScheduler):
    def __init__(self):
        cycle_schedule = os.getenv("CYCLE_SCHEDULE")
        cron_trigger = CronTrigger(hour=cycle_schedule, minute=0)
        super().__init__(EfficiencyService.cycle_efficiency, cron_trigger)

class HourEfficiencyScheduler(BaseScheduler):
    def __init__(self):
        hour_schedule = int(os.getenv("HOUR_SCHEDULE"))
        cron_trigger = CronTrigger(hour=hour_schedule, minute=0)
        super().__init__(EfficiencyService.hour_efficiency, cron_trigger)
