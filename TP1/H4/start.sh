#!/bin/sh
python3 Serv_Cli.py 0.0.0.0 8080 127.0.0.1 8081 >> /logsA.txt &
sleep 5  # Añadir un pequeño retraso
python3 Serv_Cli.py 0.0.0.0 8081 127.0.0.1 8080
