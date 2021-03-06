import celery
import celery.beat


class Service(celery.Celery):

    def __init__(self, flask_app):
        super(Service, self).__init__(__package__, loader='default')
        self.config_from_object(flask_app.config)
        self.periodic_tasks = {}

    def init_cli(self, manager):

        @manager.command
        def taskbeat():
            beat = self.Beat()
            beat.scheduler_cls = Scheduler
            beat.run()

        @manager.command
        def taskworker():
            self.Worker().run()

    def init_sentry(self, sentry):
        from raven.contrib.celery import register_signal
        register_signal(sentry)

    def periodic_task(self, *args, **kwargs):
        crontab = kwargs.pop('crontab')
        task = self.task(*args, **kwargs)
        self.periodic_tasks[task.name] = {'task': task, 'schedule': crontab}
        return task


class Scheduler(celery.beat.PersistentScheduler):

    def setup_schedule(self):
        super(Scheduler, self).setup_schedule()
        self.merge_inplace(self.app.periodic_tasks)
