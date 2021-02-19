#!/usr/bin/env bash
## start enterprise-gateway server
export FLASK_ENV=development
cd tmp
FLASK_APP=api-server/app/routes.py flask run --host=0.0.0.0 --with-threads 

