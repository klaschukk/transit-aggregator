#!/bin/bash
echo "$(date '+%Y-%m-%d %H:%M:%S') Stopping transit service..."
sudo systemctl stop transit
echo "Running enrich_stops_coords.py..."
cd /home/klaschuk/transit
source venv/bin/activate
python -u data/pipelines/enrich_stops_coords.py
echo "Starting transit service..."
sudo systemctl start transit
echo "$(date '+%Y-%m-%d %H:%M:%S') Done!"
