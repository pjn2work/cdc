#!/bin/bash

cd /home/cdc/apps/cdc || exit 1

git pull

source .venv/bin/activate

uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-config app/log.ini --reload --header App:CDC
