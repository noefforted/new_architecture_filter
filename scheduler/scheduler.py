from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from service.calculation import EfficiencyService
import os


class BaseScheduler:
    def __init__(self, interval_env:str, job_func):
        self.scheduler = AsyncIOScheduler()
        self.interval_ev = int(os.getenv(interval_env))
        self.job_func = job_func
        self.job = None

    def begin(self):
        if self.job is None:
            self.job = self.scheduler.add_job(self.job_func, trigger=IntervalTrigger(hours=self.interval), 
                              replace_existing=True)
            
    def start(self):
        self.begin()
        if not self.scheduler.running:
            self.scheduler.start()

    def close(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

class CycleEfficiencyScheduler:
    def __init__(self):
        super().__init__("CYCLE_INTERVAL", EfficiencyService.cycle_efficiency)

class HourEfficiencyScheduler:
    def __init__(self):
        super().__init__("HOUR_INTERVAL", EfficiencyService.hour_efficiency)