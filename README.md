# Documentation on - <br> Django Database Backup Implementation

## Overview

Database backup and restore operations is an important feature of any project. If database is not properly backed up, we will have nothing to do in case of any inconvenience or data loss.

This guide will help you to implement database automated periodical backup system of your django project. You can also restore the backup anytime you want.

To implement the feature, please see the documentation and follow the steps mentioned below.

---

<br>

## Technology Stack

In this project we are simply using -
- **Backend Framework**: `Django`
- **Database**: `PostgreSQL`

---

<br>

### Packages used:

```bash
    APScheduler==3.11.0
    asgiref==3.8.1
    dj-database-url==2.3.0
    Django==4.2.4
    django-apscheduler==0.7.0
    django-dbbackup==4.2.1
    psycopg2-binary==2.9.10
    pytz==2025.1
    sqlparse==0.5.3
    typing_extensions==4.12.2
    tzdata==2025.1
    tzlocal==5.3.1
```

<br>

---

# Implementation Steps

## 1. Initial Setup

1. Create a `virtual` environment and `activate` it:
   ```bash
    python -m venv venv
   ```

2. Create a Django `project` and also create an app named `record`.

3. Run the following commands:

   ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
   ```

4. Run all the installation packages needed:
   ```bash
    pip install -r requirements.txt
   ```

<br>

---

## 2. Installing and Configuring `django-dbbackup`

1. Install the package (already installed earlier):

   ```bash
    pip install django-dbbackup
   ```

2. Add `dbbackup` to INSTALLED_APPS in `settings.py`:

   ```py
    INSTALLED_APPS = [
        ...
        'record',
        'dbbackup',  # django-dbbackup
    ]
   ```

3. Create a folder named `dbbackup` in the **root project directory**. All the backup files will be saved in this folder.

4. Define storage settings in `settings.py`:

   ```py
    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
    DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'dbbackup'}
    DBBACKUP_CLEANUP_KEEP = 7  # Retain only the last 7 backups
   ```

   N.B.: Please be noted that, in the `DBBACKUP_STORAGE_OPTIONS` we need to specify the location. in this case, it will be our 'dbbackup' directory.

<br>

---

## 3. Manual Backup and Restore testing

1. To create a manual backup by running the following command:

   ```bash
    python manage.py dbbackup
   ```

2. To create a manual backup, also to clean old backups **(This command will be more efficient then the previous one)**:

   ```bash
    python manage.py dbbackup --clean
   ```

3. To restore the backup:

   ```bash
    python manage.py dbrestore
   ```

<br>

---

## 4. Automating Backups with `APScheduler`

1. Install APScheduler (already installed earlier):

   ```bash
    pip install django-apscheduler
   ```

2. Add dbbackup to INSTALLED_APPS in `settings.py`:

   ```py
    INSTALLED_APPS = [
        ...
        'django_apscheduler',
    ]
   ```

3. Create a folder named `scheduler` in the root directory and inside it again create 2 files: `__init__.py` and `scheduler.py`.


4. at `scheduler.py`:

   ```py
    from apscheduler.schedulers.background import BackgroundScheduler
    from django_apscheduler.jobstores import DjangoJobStore
    from django_apscheduler.models import DjangoJobExecution
    from django_apscheduler import util
    from django.core.management import call_command


    # creating method to auto database backup
    def backup_every_interval():
        print("Database Backed Up")

        call_command("dbbackup", clean=True)
        # it calls: "python manage.py dbbackup --clean"


    # creating cleanup method to remove old backup records
    @util.close_old_connections
    def delete_old_job_executions(max_age=604800):
        DjangoJobExecution.objects.delete_old_job_executions(max_age)


    def start():
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # set job to create database backup
        scheduler.add_job(
            backup_every_interval,
            'interval', days=1,    # setting up the interval period
            jobstore='default',
            id="backup_every_interval",
            replace_existing=True,
            coalesce=True, # prevents multiple overlapping job executions.
            max_instances=3, # voids skipping jobs when the previous job hasn't finished.
            misfire_grace_time=10, # ensures that slight delays don’t result in missed jobs
        )

        # for clean up
        scheduler.add_job(
            delete_old_job_executions,
            'interval', days=7,         # interval period
            jobstore='default',
            id="cleanup_old_backups",
            replace_existing=True,
            misfire_grace_time=10,
        )


        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
   ```


    ### Explanation of the codes of the `scheduler.py`:

    * **`backup_every_interval` Function:** This function calls `call_command("dbbackup", clean=True)` to back up the database. The `clean=True` flag ensures that old backups are removed before creating a new one.

    * **`start()` Function:** In this function, we add different jobs. For example, the `backup_every_interval` function is scheduled to run every day `('interval', days=1)`, meaning it will run once every day.

    * **Handling Scheduler with Try-Except:** The `start()` function is wrapped in a `try-except` block to gracefully handle any interruptions when starting the scheduler.
    
    ---
    <br >

    * **Job Execution Records:** Every time the scheduler runs, the execution records are stored in the `DjangoJobExecution` model. This can result in many records piling up.

    * **Automatic Cleanup of Old Records:** We can automatically remove old job execution records, similar to how the `DBBACKUP_CLEANUP_KEEP` setting works in `settings.py`. This can be done by creating a custom function named `delete_old_job_executions` in the `scheduler.py` file.

    * **Adding Cleanup Job:** The cleanup function can be added as another job inside the `start()` method to periodically remove old records.

    ---

    <br >


5. Updating `urls.py`:

    * To run the scheduler automatically in the background, we need to run the `start()` method somewhere. So, we are going to call it from the projects root `url.py` file.

   ```py
    from django.contrib import admin
    from django.urls import path
    from scheduler import scheduler  # Import the scheduler module

    urlpatterns = [
        path('admin/', admin.site.urls),
    ]

    # Start the scheduler automatically when the Django server is started
    scheduler.start()
   ```

6. Run migrations to set up `APScheduler tables`:

   ```bash
    python manage.py makemigrations
    python manage.py migrate
   ```

7. To save dependencies:

   ```bash
    pip freeze > requirements.txt
   ```


8. To check if this set-up is working or not or to browse `admin panel` to view the `APScheduler` data, run the server:

   ```bash
    py manage.py runserver
   ```

<br>

---


### Notes:

1. Its better to use `.env` file for the sensitive environment data such as "`databe name`", "`password`" etc. 

2. When switching to PostgreSQL, comment out `scheduler.start()` line in the `urls.py` before running `makemigrations` and `migrate` to avoid any further errors."

3. "`onRender`'s free PostgreSQL database, so `dbrestore` command may fail due to `permission issues`."


---

<br>

## Resources

* [django-dbbackup Documentation](https://django-dbbackup.readthedocs.io/en/master/installation.html)
* [django-apscheduler PyPI](https://pypi.org/project/django-apscheduler/)
* [APScheduler Documentation](https://apscheduler.readthedocs.io/en/3.x/userguide.html)
* [YouTube Tutorial](https://www.youtube.com/watch?v=tXwcTg43uxc)

---

<br>


## Conclusion

I hope, this comprehensive guide will help you to automate database backups and restoring system in your application. This setup provides both manual and automated database backup mechanisms for Django projects, ensuring data safety and recovery options.
