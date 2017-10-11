#!/bin/bash
npm install
bower install
polymer build
export PYTHONPATH=`pwd`
python snapyelp/aws/publish.py
python snapyelp/aws/invalidate.py