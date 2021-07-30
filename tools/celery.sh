#!/usr/bin/env bash
source /home/sistemas/sican_docker/bin/activate
celery -A sican_2018 worker -l info -B