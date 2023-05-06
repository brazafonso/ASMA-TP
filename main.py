#!/usr/bin/env python3

# Imports
from spade import agent, quit_spade
from agents.control_tower import ControlTowerAgent
from agents.station_manager import StationManagerAgent
from agents.dashboard_manager import Dashboard_Manager
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

    # Airport configurations
    ## airport map
    file = open('config/1.json', 'r')
    config = json.load(file)
    file.close()
    airport_map = AirportMap(config)
    airport_map.set_frame()
    airport_map.place_airstrips()
    airport_map.place_stations()
    airport_map.draw_map()

    ## airport config variables
    max_queue = config['max_queue']
    dash_board_period = config["dash_board_period"]
    plane_speed = config["plane_speed"]
    max_wait_in_station = config["max_wait_in_station"]
    max_wait_landing = config["max_wait_landing"]
    max_wait_take_off = config["max_wait_take_off"]
    
    # Criar torre de controlo
    control_tower = ControlTowerAgent(f'control_tower@{USER}',PASSWORD)
    control_tower.set('airport_map',airport_map)
    control_tower.set('max_queue',max_queue)
    control_tower.set('station_manager',f'station_manager@{USER}')


    futureCT = control_tower.start()

    # Criar station manager
    station_manager = StationManagerAgent(f'station_manager@{USER}',PASSWORD)
    station_manager.set('airport_map',airport_map)
    station_manager.set('control_tower',f'control_tower@{USER}')

    futureSM = station_manager.start()

    

    
    futureCT.result()
    futureSM.result()
    
    
    # Criar Gestor de Dashboards
    dashboard_manager = Dashboard_Manager(f'dashboard_manager@{USER}',PASSWORD,period=dash_board_period)
    dashboard_manager.set('airport_map',airport_map)
    dashboard_manager.set('control_tower',f'control_tower@{USER}')

    futureDM = dashboard_manager.start()
    futureDM.result()



    # Criar aviao
    plane1 = PlaneAgent(f'plane@{USER}',PASSWORD)
    plane1.set('id',1)
    plane1.set('control_tower',f'control_tower@{USER}')
    plane1.set('station_manager',f'station_manager@{USER}')
    futureP = plane1.start()




    
    futureP.result()

    while(control_tower.is_alive()):
        time.sleep(5)

    print(control_tower.status())
    control_tower.stop()
    print("Control Tower stopped")

    station_manager.stop()
    print("Station Manager stopped")

    dashboard_manager.stop()
    print("Dashboard Manager stopped")

    plane1.stop()

    quit_spade()