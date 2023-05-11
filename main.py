#!/usr/bin/env python3

# Imports
import os
import sys
from spade import agent, quit_spade
from agents.airline import AirlineAgent
from agents.control_tower import ControlTowerAgent
from agents.station_manager import StationManagerAgent
from agents.dashboard_manager import Dashboard_Manager
from agents.plane import PlaneAgent
from agents.auction_manager import AuctionManagerAgent
from objects.airport_map import AirportMap
from objects.airline import Airline
import time
import random
import json
import argparse

# Default config
max_queue = 5
max_planes = 5
spawn_time = 2
dash_board_period = 2
plane_speed = 10
max_wait_in_station = 60
max_wait_landing = 60
max_wait_take_off = 60
origin='Porto'
destination='Lisboa'
airlines_list = []

def parse_arguments()->argparse.Namespace:
    """Process arguments from stdin"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=f'''
    --------------------------------------------------------------------
                                **ASM Airport**
    --------------------------------------------------------------------'''
    )
    parser.add_argument('-c','--creds'           ,type=str                                      ,default='config/creds.json'                                ,help='Open fire credentials file.')
    parser.add_argument('-ac','--airport_config' ,type=str                                      ,default='config/ac.json'                                   ,help='Airport Configuration file.')
    parser.add_argument('-l','--logs'                                                                                           ,action='store_true'        ,help='Activating logging.')
    parser.add_argument('-lf','--logs_file'      ,type=argparse.FileType('w',encoding='utf-8')  ,default=sys.stdout                                         ,help='File for logging.')
    return parser.parse_args()

def get_airline_name():
    '''Escolhe aleatoriamente uma empresa da lista de empresas'''
    global airlines_list

    airline_name = None
    if airlines_list:
        airline_name = airlines_list[random.randint(0,len(airlines_list)-1)]
    return airline_name

def get_plane_type():
    '''Escolhe aleatoriamente um tipo de aviao'''
    type = None
    types = ['comercial','goods']
    type = types[random.randint(0,len(types)-1)]
    return type

def create_plane_agents(n_planes,control_tower,station_manager,airport_map:AirportMap,logs,logs_file):
    '''Cria a lista de agentes aviao, alguns em gares e outros no ar e atualiza mapa do aeroporto'''
    planes_ground = []
    planes_air = []
    plane_id = 0
    stations_dic = airport_map.get_divided_stations()
    n_stations = airport_map.get_num_stations()
    n_types = len(stations_dic)
    max_ground_planes = random.randint(0,min(n_planes,n_stations))
    # Criar avioes em gares
    if max_ground_planes:
        for type,dict in stations_dic.items():
            max = int(max_ground_planes/n_types)
            assigned = 0
            for station in dict:
                airline_name = station.airline_name
                plane_agent = PlaneAgent(f'plane{plane_id}@{USER}',PASSWORD,state=False,airline_name=airline_name,
                                   type=type,plane_speed=plane_speed,max_wait_in_station=max_wait_in_station,
                                   max_wait_landing=max_wait_landing,max_wait_take_off=max_wait_take_off,
                                   origin=origin,destination=destination)
                plane_agent.set('id',plane_id)
                plane_agent.set('control_tower',control_tower)
                plane_agent.set('station_manager',station_manager)
                plane_agent.set('logs',logs)
                plane_agent.set('logs_file',logs_file)
                airport_map.reserve_station(station.id,plane_agent.plane)
                assigned += 1
                plane_id += 1
                planes_ground.append(plane_agent)
                if assigned >= max:
                    break
            if len(planes_ground) == max_ground_planes:
                break

    # Criar avioes no ar
    n_planes -= len(planes_ground)
    for _ in range(0,n_planes):
        airline_name = get_airline_name()
        type = get_plane_type()
        plane_agent = PlaneAgent(f'plane{plane_id}@{USER}',PASSWORD,state=True,airline_name=airline_name,
                                   type=type,plane_speed=plane_speed,max_wait_in_station=max_wait_in_station,
                                   max_wait_landing=max_wait_landing,max_wait_take_off=max_wait_take_off,
                                   origin=origin,destination=destination)
        plane_agent.set('id',plane_id)
        plane_agent.set('control_tower',control_tower)
        plane_agent.set('station_manager',station_manager)
        plane_agent.set('logs',logs)
        plane_agent.set('logs_file',logs_file)
        plane_id += 1
        planes_air.append(plane_agent)

    return (planes_ground,planes_air,airport_map)

# Main
if __name__ == "__main__":

    args = parse_arguments()

    if os.path.exists(args.creds):
        # openfire credentials file
        file = open(args.creds, 'r')
        creds = json.load(file)
        file.close()
        USER = creds['user']
        PASSWORD = creds['password']

        if os.path.exists(args.airport_config):
            # Airport configurations
            ## airport map
            file = open(args.airport_config, 'r')
            config = json.load(file)
            file.close()
            


            if 'map' in config:
                CT = f'control_tower@{USER}'
                SM = f'station_manager@{USER}'
                AM = f'auction_manager@{USER}'

                ## airport map
                airport_map = AirportMap(config)

                ## airport config variables
                if 'max_queue' in config:
                    max_queue = config['max_queue']
                if 'max_planes' in config:
                    max_planes = config['max_planes']
                if 'spawn_time' in config:
                    spawn_time = config['spawn_time']
                if 'dash_board_period' in config:
                    dash_board_period = config["dash_board_period"]
                if 'plane_speed' in config:
                    plane_speed = config["plane_speed"]
                if 'max_wait_in_station' in config:
                    max_wait_in_station = config["max_wait_in_station"]
                if 'max_wait_landing' in config:
                    max_wait_landing = config["max_wait_landing"]
                if 'max_wait_take_off' in config:
                    max_wait_take_off = config["max_wait_take_off"]
                if 'origin' in config:
                    origin = config["origin"]
                if 'destination' in config:
                    destination = config["destination"]
                if 'airlines' in config:
                    airlines_conf = config["airlines"]
                    airlines_list = list(airlines_conf.keys())

                # Criar avioes (devido aos que começam nas gares)
                n_planes = random.randint(1,max_planes-1)
                ground_plane_agents,air_plane_agents,airport_map = create_plane_agents(n_planes,CT,SM,airport_map,args.logs,args.logs_file)
                print('Info:',len(ground_plane_agents),len(air_plane_agents))

                # Desenha aeroporto
                airport_map.set_frame()
                airport_map.place_airstrips()
                airport_map.place_stations()
                airport_map.place_roads()
                airport_map.map_update_stations(airport_map.get_stations())
                airport_map.draw_map()
                
                # Criar torre de controlo
                control_tower = ControlTowerAgent(CT,PASSWORD)
                control_tower.set('airport_map',airport_map)
                control_tower.set('max_queue',max_queue)
                control_tower.set('n_planes',n_planes)
                control_tower.set('station_manager',SM)
                control_tower.set('logs',args.logs)
                control_tower.set('logs_file',args.logs_file)

                futureCT = control_tower.start()

                # Criar station manager
                station_manager = StationManagerAgent(SM,PASSWORD)
                station_manager.set('airport_map',airport_map)
                station_manager.set('control_tower',CT)
                station_manager.set('logs',args.logs)
                station_manager.set('logs_file',args.logs_file)

                futureSM = station_manager.start()

                time.sleep(0.1) # TODO: Testing delays...

                # Start auction manager
                auction_manager = AuctionManagerAgent(AM,PASSWORD)
                auction_manager.set('airport_map',airport_map)
                auction_manager.set('logs',args.logs)
                auction_manager.set('logs_file',args.logs_file)
                
                futureAM = auction_manager.start()

                time.sleep(0.1) # TODO: Testing delays...

                # Start airline agents
                future_airlines = []
                for airline_name in airlines_list:
                    airline_jid = ('airline_'+str(airline_name)+'@'+USER).lower()
                    type = airlines_conf[airline_name]["type"]
                    budget = airlines_conf[airline_name]["budget"]
                    costs = airlines_conf[airline_name]["costs"]
                    strategy = airlines_conf[airline_name]["strategy"]
                    airline_obj = Airline(airline_jid, airline_name, type, budget, costs, strategy)
                    
                    airline_agent = AirlineAgent(airline_jid, PASSWORD, airline=airline_obj)
                    airline_agent.set('auction_manager',AM)
                    airline_agent.set('logs',args.logs)
                    airline_agent.set('logs_file',args.logs_file)

                    future_airlines.append(airline_agent.start())

                    break # TODO: Test only one airline

                # TODO: Add delays between airline/auction manager...subscribe is not captured
                #       Actually, this is not the only message to be dropped..maybe add delays between all agents

                            
                futureCT.result()
                futureSM.result()
                futureAM.result()

                for future in future_airlines:
                    future.result()
                
                # Criar Gestor de Dashboards
                dashboard_manager = Dashboard_Manager(f'dashboard_manager@{USER}',PASSWORD,period=dash_board_period)
                dashboard_manager.set('airport_map',airport_map)
                dashboard_manager.set('control_tower',CT)
                dashboard_manager.set('logs',args.logs)
                dashboard_manager.set('logs_file',args.logs_file)

                futureDM = dashboard_manager.start()
                futureDM.result()

                futureP = []
                # Iniciar agentes aviao no chao
                for plane in ground_plane_agents:
                    futureP.append(plane.start())

                # Iniciar agentes aviao no ar (delay de spawn)
                for plane in air_plane_agents:
                    futureP.append(plane.start())
                    time.sleep(spawn_time)

                for future in futureP:
                    future.result()


                # Esperar ate torre desligar
                while(control_tower.is_alive()):
                    time.sleep(5)

                control_tower.stop()
                print("Control Tower stopped")

                station_manager.stop()
                print("Station Manager stopped")

                dashboard_manager.stop()
                print("Dashboard Manager stopped")

                quit_spade()

            else:
                print('Please provide a airport map in the config file.')
        else:
            print('Please provide a airport config file.')
    else:
        print('Please provide a credentials file.')

    