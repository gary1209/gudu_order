#!/bin/bash

cd "$(dirname "$0")"
screen -d -m -S GuduOrder bash -c "python3 gudu/server.py"
