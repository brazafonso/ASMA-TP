from objects.airstrip import Airstrip
from objects.station import Station
from objects.position import Position

class AirportMap():
    '''Classe representante do mapa do aeroporto'''
    
    def __init__(self,map_json):
        self.airstrips = []
        self.stations = []
        self.name = map_json['name']
        self.width = map_json['width']
        self.height = map_json['height']
        self.map = map_json['map']
        self.map_draw = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.scrape_airport_map()


    def available_airstrips(self):
        '''Devolve a lista das pistas disponiveis'''
        available = []
        for airstrip in self.airstrips:
            if airstrip.state == 0:
                available.append(airstrip)
        return available
    
    def available_airstrip(self,id):
        '''Devolve se uma pista esta disponivel'''
        available = False
        for airstrip in self.airstrips:
            if airstrip.id == id:
                available = airstrip.state == 0
        return available
    
    def closest_available_airstrip(self,pos:Position):
        '''Devolve a pista mais proxima disponivel'''
        closest = None
        distance = None
        for airstrip in self.airstrips:
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
        if id:
            for airstrip in self.airstrips:
                if airstrip.id == id:
                    airstrip.state = 0
                    airstrip.plane = None
                    break

        elif plane_id:
            for airstrip in self.airstrips:
                if airstrip.state == 1:
                    if airstrip.plane.id == plane_id:
                        airstrip.state = 0
                        airstrip.plane = None
                        break

    def reserve_airstrip(self,id,plane):
        '''Torna uma pista ocupada'''
        for airstrip in self.airstrips:
            if airstrip.id == id:
                airstrip.state = 1
                airstrip.plane = plane
                break

    
    def free_station(self,id=None,plane_id=None):
        '''Torna uma gare livre'''
        if id:
            for station in self.stations:
                if station.id == id:
                    station.state = 0
                    station.plane = None
                    break

        elif plane_id:
            for station in self.stations:
                if station.state == 1:
                    if station.plane.id == plane_id:
                        station.state = 0
                        station.plane = None
                        break


    def reserve_station(self,id,plane):
        '''Torna uma gare ocupada'''
        reserved = False
        for station in self.stations:
            if station.id == id:
                station.state = 1
                station.plane = plane
                reserved = True
                break
        return reserved


    def scrape_airport_map(self):
        '''Obtém informação mais detalhada a partir do mapa (como as pistas e gares)'''
        airstrip_id = 0
        station_id = 0

        for y,line in enumerate(self.map):
            for x,space in enumerate(line):
                if space['type'] == 'airstrip':
                    self.airstrips.append(Airstrip(id=airstrip_id,x=x,y=y))
                    airstrip_id += 1
                elif space['type'] == 'station':
                    type=space['purpose']
                    self.stations.append(Station(id=station_id,type=type,x=x,y=y))
                    station_id += 1


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

        for i in self.stations:
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

        for i in self.airstrips:
            x = i.get_pos_x()
            y = i.get_pos_y()
            self.replacer(y,x,topline)
            self.replacer(y+2,x,midline)
            self.replacer(y+4,x,bottomline)

    def place_roads(self):

        # Lista de tuplos (posicao_x,posicao_y) das pistas do aeroporto
        pos_roads = []

        for i in self.airstrips:
            pos_roads.append((i.get_pos_x(),i.get_pos_y()))

        # Dicionario onde as chaves são a posicao_y das gares e o valor será uma lista com a posicao_x
        # das gares com essa coordenada y 
        pos_gares = {}

        posxlist = []
        
        for i in range(len(self.stations)):
            if (i == 0):
                lasty = self.stations[0].get_pos_y()
                posxlist.append(self.stations[0].get_pos_x())
            elif (i == (len(self.stations) - 1)):
                lasty = self.stations[i-1].get_pos_y()
                y = self.stations[i].get_pos_y()
                if(lasty == y):
                    posxlist.append(self.stations[i].get_pos_x())
                    pos_gares[lasty] = posxlist
                else:
                    pos_gares[lasty] = posxlist
                    posxlist = []
                    posxlist.append(self.stations[i].get_pos_x())
                    pos_gares[y] = posxlist
            else:
                lasty = self.stations[i-1].get_pos_y()
                y = self.stations[i].get_pos_y()
                if(lasty == y):
                    posxlist.append(self.stations[i].get_pos_x())
                else:
                    pos_gares[lasty] = posxlist
                    posxlist = []
                    posxlist.append(self.stations[i].get_pos_x())

        for i,key in enumerate(pos_gares):

            road_width = pos_gares[key][-1] - pos_gares[key][0]

            for posr in pos_roads:

                if (posr[1] - key == 3):

                    topline = ''

                    for ind,elem in enumerate(pos_gares[key]):

                        if ind == len(pos_gares[key])-1: 

                            topline += '/  \\'

                        else:

                            between_space = (pos_gares[key][ind+1] - elem) - 4

                            topline += '/  \\'+'_'*between_space

                    midline = '\\'+'_'*(int(road_width/2) - 1)+' '*4+'_'*(int(road_width/2) - 1)+'/'

                    bottomline = '\  /'

                    mid_diff = int(self.width/2) - int(road_width/2)

                    bottomline_x = int(road_width/2) + mid_diff - 2

                    self.replacer(key+1,pos_gares[key][0],topline)
                    self.replacer(key+2,pos_gares[key][0],midline)
                    self.replacer(key+3,bottomline_x,bottomline)

                elif (key - posr[1] == 8):

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

    def update_landing_queue(self):
        
        avioes_aterrar = ['AC1','AM2','AC3','AC4','AM5']

        fila_de_aterragem = 'Fila de Aterragem:'

        for aviao in avioes_aterrar:

            fila_de_aterragem += ' '+aviao

        self.replacer(1,1,fila_de_aterragem)

    def update_take_off_queue(self):

        avioes_descolar = ['AC1','AM2','AC3','AC4','AM5']

        fila_de_descolagem = 'Fila de Descolagem:'
        
        for aviao in avioes_descolar:

            fila_de_descolagem += ' '+aviao

        self.replacer(self.height-2,1,fila_de_descolagem)

    def update_airstrips(self,airstrips):

        for airstrip in airstrips:
            pos = airstrip.pos

            if airstrip.state == 1:
                plane = airstrip.plane

                if (plane.type == 'goods'):

                    plane_str = 'AM'+plane.id

                else:

                    plane_str = 'AC'+plane.id

                self.replacer(pos.y+1,pos.x,plane_str)

            else:
                self.replacer(pos.y+1,pos.x,''*6)



    def update_stations(self,stations):
        
        for station in stations:
            pos = station.pos

            if station.state == 1:

                plane = station.plane

                if (plane.type == 'goods'):

                    plane_str = '|AM|'+plane.id

                else:

                    plane_str = '|AC|'+plane.id

                self.replacer(pos.y,pos.x,plane_str)

            else:

                self.replacer(pos.y,pos.x,'|xx|'+' '*3)

    def draw_map(self):
        for i in range(0,self.height):
            print(self.map_draw[i])
        

        
