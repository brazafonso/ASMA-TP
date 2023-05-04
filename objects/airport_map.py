from objects.airstrip import Airstrip
from objects.station import Station

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
        topline = '_'*4

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

        print(f"Lista das possicoes das pistas:\n{pos_roads}")

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

                            topline += '|  |'

                        else:

                            between_space = (pos_gares[key][ind+1] - elem) - 4

                            topline += '|  |'+'_'*between_space

                    midline = '|'+'_'*(int(road_width/2) - 1)+' '*4+'_'*(int(road_width/2) - 1)+'|'

                    bottomline = '|  |'

                elif (key - posr[1] == 4):

                    bottomline = ''

                    for ind,elem in enumerate(pos_gares[key]):

                        between_space = (pos_gares[key][ind+1][0] - elem[0]) - 4

                        bottomline += '|  |'+'_'*between_space

                    midline = '|'+'_'*(int(road_width/2) - 1)+' '*4+'_'*(int(road_width/2) - 1)+'|'

                    topline = '|  |'

                bottomline_x = int(self.width/2) - 2

                self.replacer(key+1,pos_gares[key][0],topline)
                self.replacer(key+2,pos_gares[key][0],midline)
                self.replacer(key+3,bottomline_x,bottomline)

        print(f"Dicionario das posicoes das gares:\n{pos_gares}") 


    def draw_map(self):
        for i in range(0,self.height):
            print(self.map_draw[i])
        

        
