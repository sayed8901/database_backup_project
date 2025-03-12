from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from django.core.management import call_command



# creating method to auto database backup
def backup_every_interval():
    print("Database Backed Up")

    # automatically call the backup method
    call_command("dbbackup", clean=True)
    # it calls: "python manage.py dbbackup --clean"




# creating cleanup method to remove old backup records from (Django job executions এই model থেকে)
@util.close_old_connections
def delete_old_job_executions(max_age=2): 
  # deletes the jobs that have expired for more than 2 seconds
  DjangoJobExecution.objects.delete_old_job_executions(max_age)




def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # set job to create database backup
    # in every 5 seconds
    scheduler.add_job(
        backup_every_interval,
        'interval', seconds=5,
        jobstore='default',
        id="backup_every_interval",
        replace_existing=True,
    )

    # for clean up every 10 seconds
    scheduler.add_job(
        delete_old_job_executions,
        'interval', seconds=10,
        jobstore='default',
        id="delete_old_job_executions",
        replace_existing=True,
    )


    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()

