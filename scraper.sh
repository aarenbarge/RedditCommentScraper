#!bin/bash

while true; do
  if [ ! -e "./tmp/pidfiles/mydaemon2.pid" ]
    then
    echo "running"
    python test2.py uva_cs_dev wah00wa
  else
    rm ./tmp/pidfiles/mydaemon2.pid
  fi
done
