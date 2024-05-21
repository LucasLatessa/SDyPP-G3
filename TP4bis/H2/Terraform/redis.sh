#!/bin/bash
sudo apt-get update
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server