#!/bin/sh

uvicorn fmedia.main:app --host 0.0.0.0 --port $PORT
