#!/bin/bash
screen -S GuduOrder -X kill

cd "$(dirname "$0")"
FILE=./db/gudu.db
if test -f "$FILE"; then
    rm "$FILE"
fi
python3 ./gudu/init_db.py
./start.sh
