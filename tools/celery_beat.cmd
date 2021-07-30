@echo off
C:\Users\SISTEMAS\PycharmProjects\sican_docker\venv\Scripts\celery.exe -A sican_2018 beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler