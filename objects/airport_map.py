import re
from objects.airstrip import Airstrip
from objects.station import Station
from objects.position import Position

import threading
import os

class AirportMap():
    '''Classe representante do mapa do aeroporto'''
    
    def __init__(self,map_json):
        self.map_json = map_json
        self.name = map_json['name']
        self.width = map_json['width']
        self.height = map_json['height']
        self.max_queue = map_json['max_queue']
        self.map = map_json['map']
        self.map_draw = [[' ' for _ in range(self.width)] for _ in range(self.height)]

        self.__landing_queue = []
        self.__landing_queue_lock = threading.Lock()
        
        self.__take_off_queue = []
        self.__take_off_queue_lock = threading.Lock()
        
        self.__airstrips = {}
        self.__airstrips_lock = threading.Lock()

        self.__stations = {}
        self.__stations_lock = threading.Lock()
        
        self.scrape_airport_map()
    
    def get_copy(self):
        '''Construtor a partir de uma copia'''
        new_airport_map = AirportMap(self.get_json())

        new_airport_map.__landing_queue = self.get_landing_queue()
        new_airport_map.__take_off_queue = self.get_take_off_queue()
        new_airport_map.__airstrips = self.get_airstrips()
        new_airport_map.__stations = self.get_stations()
        
        return new_airport_map

    def get_json(self):
        new_map_json = {}
        for key in self.map_json:
            new_map_json[key] = self.map_json[key]
        return new_map_json

    def get_landing_queue(self):
        with self.__landing_queue_lock:
            new_landing_queue = []
            for plane, timestamp in self.__landing_queue:
                new_landing_queue.append((plane.get_copy(), timestamp))
            return new_landing_queue
    
    def get_take_off_queue(self):
        with self.__take_off_queue_lock:
            new_take_off_queue = []
            for pos, plane, timestamp in self.__take_off_queue:
                new_take_off_queue.append((pos, plane.get_copy(), timestamp))
            return new_take_off_queue
        
    def get_stations(self):
        stations = {}
        with self.__stations_lock:
            for id,station in self.__stations.items():
                stations[id] = station.get_copy()
        return stations
    
    def get_airstrips(self):
        with self.__airstrips_lock:
            airstrips = {}
            for id,airstrip in self.__airstrips.items():
                airstrips[id] = airstrip.get_copy()
            return airstrips
    
    def get_num_stations(self):
        with self.__stations_lock:
            return len(self.__stations)

    def get_divided_stations(self):
        '''Retorna as gares divididas por tipo'''
        stations_ret = {}

        # Deep copy list of stations
        stations_copy = self.get_stations()
        for key,station in stations_copy.items():
            type = station.type
            if type not in stations_ret:
                stations_ret[type] = {}
            stations_ret[type][key] = station

        return stations_ret

    def available_airstrips(self):
        '''Devolve a lista das pistas disponiveis'''
        available = {}
        with self.__airstrips_lock:
            for key,airstrip in self.__airstrips.items():
                if airstrip.state == 0:
                    available[key]=airstrip.get_copy()
            return available
    
    def available_airstrip(self,id):
        '''Devolve se uma pista esta disponivel'''
        available = False
        with self.__airstrips_lock:
            if id in self.__airstrips:
                available = self.__airstrips[id].state == 0
        return available
    
    def closest_available_airstrip(self,pos:Position):
        '''Devolve a pista mais proxima disponivel'''
        closest = None
        distance = None
        with self.__airstrips_lock:
            for airstrip in self.__airstrips.values():
                if airstrip.state == 0:
                    if closest:
                        if pos.distance(airstrip.pos) < distance:
                            closest = airstrip
                            distance = pos.distance(airstrip.pos) 
                    else:
                        closest = airstrip
                        distance = pos.distance(airstrip.pos)
            return closest
    
    def free_airstrip(self,id=None,plane_id=None):
        '''Torna uma pista livre'''
        with self.__airstrips_lock:
            if id:
                self.__airstrips[id].state = 0
                self.__airstrips[id].plane = None
                return self.__airstrips[id].get_copy()

            elif plane_id:
                for airstrip in self.__airstrips.values():
                    if airstrip.plane:
                        if airstrip.plane.id == plane_id:
                            airstrip.state = 0
                            airstrip.plane = None
                            return airstrip.get_copy()

    def reserve_airstrip(self,id,plane):
        '''Torna uma pista ocupada'''
        with self.__airstrips_lock:
            self.__airstrips[id].state = 1
            self.__airstrips[id].plane = plane

    
    def isPlaneInStation(self, plane_jid):
        with self.__stations_lock:
            for station in self.__stations.values():
                if station.plane:
                    if station.plane.id == plane_jid:
                        return station.get_copy()
            return None

    def free_station(self,id=None,plane_id=None):
        '''Torna uma gare livre'''
        with self.__stations_lock:
            if id:
                self.__stations[id].state = 0
                self.__stations[id].plane = None
                return self.__stations[id].get_copy

            elif plane_id:
                for station in self.__stations.values():
                    if station.state == 1:
                        if station.plane.id == plane_id:
                            station.state = 0
                            station.plane = None
                            return station.get_copy()


    def reserve_station(self,id,plane):
        '''Torna uma gare ocupada'''
        reserved = False
        with self.__stations_lock:
            if id in self.__stations:
                reserved = True
                self.__stations[id].state = 1
                self.__stations[id].plane = plane
        return reserved
    

    def update_stations(self,stations):
        '''Atualizar estado das gares'''
        with self.__stations_lock:
            self.__stations = stations


    def scrape_airport_map(self):
        '''Obtém informação mais detalhada a partir do mapa (como as pistas e gares)'''
        airstrip_id = 0
        station_id = 0

        stations_to_append = {}
        airstrips_to_append = {}
        for y,line in enumerate(self.map):
            for x,space in enumerate(line):
                if space['type'] == 'airstrip':
                    # TODO: meter x como metade da largura do mapa, para usar sempre o ponto medio da pista
                    airstrips_to_append[airstrip_id] = Airstrip(id=airstrip_id,x=x,y=y)
                    airstrip_id += 1
                elif space['type'] == 'station':
                    type=space['purpose']
                    airline_name=space['airline_name']
                    base_value=space['base_value']
                    stations_to_append[station_id]= Station(station_id, type, x, y, base_value, airline_name)
                    station_id += 1

        with self.__stations_lock:
            self.__stations.update(stations_to_append)
        with self.__airstrips_lock:
            self.__airstrips.update(airstrips_to_append)


    def replacer(self,line,index,newstring):
        charline = list(self.map_draw[line])

        for i in range(index,index+len(newstring)):
            charline[i] = newstring[i-index]

        self.map_draw[line] = ''.join(charline)


    #Moldura que vai envolver o aeroporto
    def set_frame(self):

        #Definir o Header com o nome do aeroporto

        border_lenght = self.width - len(self.name)

        if (border_lenght % 2) == 0:
            border_left = int(border_lenght / 2)
            border_right = int(border_lenght / 2)

        else:
            border_left = int(border_lenght / 2)
            border_right = int(border_left + 1)

        self.map_draw[0] = '+'+'−'*(border_left-1)+self.name+'−'*(border_right-1)+'+'

        #Definir as bordas dos lados

        for i in range(1,self.height-1):
            self.map_draw[i] = '|'+' '*(self.width-2)+'|'

        #Definir o footer

        self.map_draw[-1] = '+'+'−'*(self.width-2)+'+'


    def place_stations(self):
        topline = '_/\_'

        bottomline = '|xx|'
        
        with self.__stations_lock:
            for i in self.__stations:
                x = i.get_pos_x()
                y = i.get_pos_y()
                self.replacer(y-1,x,topline)
                self.replacer(y,x,bottomline)

    def place_airstrips(self):
        topline = '_'*(self.width-2)

        resto = (self.width-2) % 10

        repeticoes = int((self.width-2) / 10)

        if resto == 0:

            midline = (' '*5+'−'*5)*(repeticoes)

        elif resto <= 5: 

            midline = (' '*5+'−'*5)*(repeticoes)+' '*resto

        elif resto <= 10:

            midline = (' '*5+'−'*5)*(repeticoes)+' '*5+'−'*(resto-5)

        bottomline = '‾'*(self.width-2)

        with self.__airstrips_lock:
            for i in self.__airstrips:
                x = 1 #i.get_pos_x()
                y = i.get_pos_y()-2
                self.replacer(y,x,topline)
                self.replacer(y+2,x,midline)
                self.replacer(y+4,x,bottomline)

    def place_roads(self):

        # Lista de tuplos (posicao_x,posicao_y) das pistas do aeroporto
        pos_roads = []

        with self.__airstrips_lock:
            for i in self.__airstrips:
                pos_roads.append((i.get_pos_x(),i.get_pos_y()))

        # Dicionario onde as chaves são a posicao_y das gares e o valor será uma lista com a posicao_x
        # das gares com essa coordenada y 
        pos_gares = {}

        posxlist = []
        
        with self.__stations_lock:
            for i,station in self.__stations.items():
                if (i == 0):
                    lasty = self.__stations[0].get_pos_y()
                    posxlist.append(self.__stations[0].get_pos_x())
                elif (i == (len(self.__stations) - 1)):
                    lasty = self.__stations[i-1].get_pos_y()
                    y = self.__stations[i].get_pos_y()
                    if(lasty == y):
                        posxlist.append(self.__stations[i].get_pos_x())
                        pos_gares[lasty] = posxlist
                    else:
                        pos_gares[lasty] = posxlist
                        posxlist = []
                        posxlist.append(self.__stations[i].get_pos_x())
                        pos_gares[y] = posxlist
                else:
                    lasty = self.__stations[i-1].get_pos_y()
                    y = self.__stations[i].get_pos_y()
                    if(lasty == y):
                        posxlist.append(self.__stations[i].get_pos_x())
                    else:
                        pos_gares[lasty] = posxlist
                        posxlist = []
                        posxlist.append(self.__stations[i].get_pos_x())

        for i,key in enumerate(pos_gares):

            road_width = pos_gares[key][-1] - pos_gares[key][0]

            for posr in pos_roads:

                if (posr[1] - key == 5):

                    topline = ''

                    for ind,elem in enumerate(pos_gares[key]):

                        if ind == len(pos_gares[key])-1: 

                            topline += '|  |' #'/  \\'

                        else:

                            between_space = (pos_gares[key][ind+1] - elem) - 4

                            topline += '|  |'+'_'*between_space #'/  \\'+'_'*between_space

                    midline = '|'+'_'*(int(road_width/2) - 1)+' '*4+'_'*(int(road_width/2) - 1)+'|'#'\\'+'_'*(int(road_width/2) - 1)+' '*4+'_'*(int(road_width/2) - 1)+'/'

                    bottomline = '|  |' #'\  /'

                    mid_diff = int(self.width/2) - int(road_width/2)

                    bottomline_x = int(road_width/2) + mid_diff - 2

                    self.replacer(key+1,pos_gares[key][0],topline)
                    self.replacer(key+2,pos_gares[key][0],midline)
                    self.replacer(key+3,bottomline_x,bottomline)

                elif (key - posr[1] == 6):

                    bottomline = ''

                    for ind,elem in enumerate(pos_gares[key]):

                        if ind == len(pos_gares[key])-1: 

                            bottomline += '|  |'

                        else:

                            between_space = (pos_gares[key][ind+1] - elem) - 4

                            bottomline += '|  |'+'‾'*between_space

                    midline = '|'+'‾'*(int(road_width/2) - 1)+' '*4+'‾'*(int(road_width/2) - 1)+'|'

                    topline = '|  |'

                    mid_diff = int(self.width/2) - int(road_width/2)

                    topline_x = int(road_width/2) + mid_diff - 2

                    self.replacer(key-2,pos_gares[key][0],bottomline)
                    self.replacer(key-3,pos_gares[key][0],midline)
                    self.replacer(key-4,topline_x,topline)

    def update_landing_queue(self,landing_queue):

        with self.__landing_queue_lock:
            self.__landing_queue = landing_queue

            self.replacer(1,1,' '*(self.width-2))

            fila_de_aterragem = 'Fila de Aterragem:'

            for plane,_ in self.__landing_queue:
            
                plane_id_match = re.findall(r'(\d+)',str(plane.id))

                plane_id = plane_id_match[0]        

                if (plane.type == 'goods'):

                    plane_str = 'AM'+str(plane_id)

                else:

                    plane_str = 'AC'+str(plane_id)

                fila_de_aterragem += ' '+plane_str

            self.replacer(1,1,fila_de_aterragem)

    def update_take_off_queue(self,take_off_queue):

        with self.__take_off_queue_lock:
            self.__take_off_queue = take_off_queue

            self.replacer(self.height-2,1,' '*(self.width-2))

            fila_de_descolagem = 'Fila de Descolagem:'

            for _,plane,_ in self.__take_off_queue:

                plane_id_match = re.findall(r'(\d+)',str(plane.id))

                plane_id = plane_id_match[0]


                if (plane.type == 'goods'):

                    plane_str = 'AM'+str(plane_id)

                else:

                    plane_str = 'AC'+str(plane_id)

                fila_de_descolagem += ' '+plane_str

            self.replacer(self.height-2,1,fila_de_descolagem)

    def update_airstrips(self, airstrips):
        with self.__airstrips_lock:
            self.__airstrips = airstrips

    def map_update_airstrips(self,airstrips):

        self.update_airstrips(airstrips)
        airstrips = self.get_airstrips()

        for airstrip in airstrips:
            pos = airstrip.pos

            if airstrip.state == 1:
                print(airstrip)

                plane = airstrip.plane

                plane_id_match = re.findall(r'(\d+)',str(plane.id))

                plane_id = plane_id_match[0]

                if (plane.type == 'goods'):

                    plane_str = 'AM'+str(plane_id)

                else:

                    plane_str = 'AC'+str(plane_id)

                self.replacer(pos.y-1,self.width-7,plane_str)

            else:
                self.replacer(pos.y-1,self.width-7,' '*6)



    def map_update_stations(self,stations):

        self.update_stations(stations)

        stations = self.get_stations()
        
        for station in stations:
            
            pos = station.pos

            if station.state == 1:

                print(station)

                plane = station.plane

                plane_id_match = re.findall(r'(\d+)',str(plane.id))
                plane_id = plane_id_match[0]

                if (plane.type == 'goods'):

                    plane_str = '|AM|'+str(plane_id)

                else:

                    plane_str = '|AC|'+str(plane_id)

                self.replacer(pos.y,pos.x,plane_str)

            else:

                self.replacer(pos.y,pos.x,'|xx|'+' '*3)

    def draw_map(self):
        # Clear screen before drawing
        # os.system('cls' if os.name == 'nt' else 'clear')
        for i in range(0,self.height):
            print(self.map_draw[i])