#!/usr/bin/env bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
cd /ScaaS
export FLASK_APP=myapp.py
python3 -m flask run --host 0.0.0.0
