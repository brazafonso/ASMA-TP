#!/usr/bin/env python3

# Imports
from spade import agent, quit_spade
from agents.control_tower import ControlTowerAgent
from agents.plane import PlaneAgent
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
    file = open('config/airport.json', 'r')
    config = json.load(file)
    file.close()
    airport_map = AirportMap(config)
    airport_map.set_frame()
    airport_map.place_airstrips()
    airport_map.place_stations()
    airport_map.draw_map()

    
    # Criar torre de controlo
    control_tower = ControlTowerAgent(f'control_tower@{USER}',PASSWORD)
    control_tower.set('airport_map',airport_map)
    control_tower.set('station_manager',f'station_manager@{USER}')


    futureCT = control_tower.start()


    # Criar aviao

    plane1 = PlaneAgent(f'plane@{USER}',PASSWORD)
    plane1.set('id',1)
    plane1.set('control_tower',f'control_tower@{USER}')

    futureP = plane1.start()

    
    
    futureCT.result()
    futureP.result()


    time.sleep(5)

    print(control_tower.status())
    control_tower.stop()
    print("Control Tower stopped")

    plane1.stop()

    quit_spade()