#!/usr/bin/env python3

# Imports
from spade import agent, quit_spade
from agents.control_tower import ControlTowerAgent
from objects.airport_map import AirportMap
import time
import random
import json


# Main
if __name__ == "__main__":

    # openfire credentials file
    file = open('config/creds.json', 'r')
    creds = json.load(file)
    file.close()
    USER = creds['user']
    PASSWORD = creds['password']

    # airport map
    file = open('config/map.json', 'r')
    map = json.load(file)
    file.close()
    aiorport_map = AirportMap(map)

    
    # Criar torre de controlo
    control_tower = ControlTowerAgent(f'control_tower@{USER}',PASSWORD)
    control_tower.set('airport_map',aiorport_map)

    futureCT = control_tower.start()

    futureCT.result()

    print(control_tower.status())

    control_tower.stop()
    print("Control Tower stopped")

    quit_spade()