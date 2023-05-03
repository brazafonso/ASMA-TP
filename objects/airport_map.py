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

        bottomline = '|−−|'

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

    def placeRoads(self):

        mid = int((self.size_x-2) / 2)

        # Lista de tuplos (posicao_x,posicao_y) das pistas do aeroporto
        pos_roads = []

        for i in self.pistas:
            pos_roads.append((i.getPosicaoX(),i.getPosicaoY()))

        print(f"Lista das possicoes das pistas:\n{pos_roads}")

        # Dicionario onde as chaves são a posicao_y das gares e o valor será uma lista com a posicao_x
        # das gares com essa coordenada y 
        pos_gares = {}

        posxlist = []
        
        for i in range(len(self.gares)):
            if (i == 0):
                lasty = self.gares[0].getPosicaoY()
                posxlist.append(self.gares[0].getPosicaoX())
            elif (i == (len(self.gares) - 1)):
                lasty = self.gares[i-1].getPosicaoY()
                y = self.gares[i].getPosicaoY()
                if(lasty == y):
                    posxlist.append(self.gares[i].getPosicaoX())
                    pos_gares[lasty] = posxlist
                else:
                    pos_gares[lasty] = posxlist
                    posxlist = []
                    posxlist.append(self.gares[i].getPosicaoX())
                    pos_gares[y] = posxlist
            else:
                lasty = self.gares[i-1].getPosicaoY()
                y = self.gares[i].getPosicaoY()
                if(lasty == y):
                    posxlist.append(self.gares[i].getPosicaoX())
                else:
                    pos_gares[lasty] = posxlist
                    posxlist = []
                    posxlist.append(self.gares[i].getPosicaoX())

        print(f"Dicionario das posicoes das gares:\n{pos_gares}") 


    def draw_map(self):
        for i in range(0,self.height):
            print(self.map_draw[i])
        

        
