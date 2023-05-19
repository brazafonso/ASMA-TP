import json

map_config = {}

def addAirstrips(poslist):
    '''Aceita como argumento uma lista de tuplos de posições (x,y).'''

    for pos_x,pos_y in poslist:

        map_config['map'][pos_y][pos_x] = {"type":"airstrip"}


def addStations(stationlist):
    '''Aceita como argumento uma lista de tuplos de posições (x,y), número de gares 
    nessa linha y, o espaçamento em x entre elas e o tipo de aviões que podem estacionar na gare 
    (comercial,goods). O elemento vai ter o seguite aspeto (pos_x, pos_y, 10, 4, 'comercial').'''

    for pos_x,pos_y,number,spacing,station_type,airline,value in stationlist:

        for i in range(number):

            map_config['map'][pos_y][pos_x+i*spacing] = {"type":"station","base_value":value,"airline_name":airline,"purpose":station_type}


def createAirportconfig1(filename,name,width,height):

    mid_width = int(width/2)

    #airstrip_list = [(1,10),(1,25)]
    airstrip_list = [(mid_width,12),(mid_width,27)]

    station_list = [(5,7,14,10,'comercial'),(5,18,14,10,'goods'),(5,22,14,10,'comercial'),(5,33,14,10,'goods')]

    map_config['name'] = name
    map_config['max_queue'] = 5
    map_config['max_planes'] = 2
    map_config['dash_board_period'] = 2
    map_config['plane_speed'] = 10
    map_config['max_wait_in_station'] = 2
    map_config['max_wait_landing'] = 60
    map_config['max_wait_take_off'] = 60
    map_config['origin'] = "Porto"
    map_config['destination'] = "Lisboa" 
    map_config['width'] = width
    map_config['height'] = height
    map_config['airlines'] = {}
    
    map_config['map'] = [[{"type":"empty"} for _ in range(width)] for _ in range(height)]

    addAirstrips(airstrip_list)

    addStations(station_list)

    json_object = json.dumps(map_config, ensure_ascii=False, indent=4, separators=(',',':'))

    with open(filename,"w") as outfile:
        outfile.write(json_object)

#createAirportconfig1('config/1.json','Aeroporto Francisco Sá Carneiro',145,37)

def createAirportconfig2(filename,name,width,height):

    mid_width = int(width/2)

    #airstrip_list = [(1,10),(1,25)]
    airstrip_list = [(mid_width,12),(mid_width,27)]

    station_list = [(5,7,2,10,'comercial','TAP',500),(5,18,2,10,'goods','FedEx',1500),(5,22,2,10,'comercial','easyJet',1000),(5,33,2,10,'goods','UPS',2000)]

    map_config['name'] = name
    map_config['max_queue'] = 5
    map_config['max_planes'] = 2
    map_config['dash_board_period'] = 2
    map_config['plane_speed'] = 10
    map_config['max_wait_in_station'] = 2
    map_config['max_wait_landing'] = 60
    map_config['max_wait_take_off'] = 60
    map_config['origin'] = "Porto"
    map_config['destination'] = "Lisboa" 
    map_config['width'] = width
    map_config['height'] = height
    map_config['airlines'] = {}
    
    map_config['map'] = [[{"type":"empty"} for _ in range(width)] for _ in range(height)]

    addAirstrips(airstrip_list)

    addStations(station_list)

    json_object = json.dumps(map_config, ensure_ascii=False, indent=4, separators=(',',':'))

    with open(filename,"w") as outfile:
        outfile.write(json_object)

createAirportconfig2('config/t.json','Aeroporto de Teste',45,37)




