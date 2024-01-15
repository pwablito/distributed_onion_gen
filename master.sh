#!/bin/bash

tor &

python3 server.py

kill %1
