from objects.airstrip import Airstrip
from objects.station import Station

class AirportMap():
    '''Classe representante do mapa do aeroporto'''
    
    def __init__(self,map_json):
        self.width = map_json['width']
        self.height = map_json['height']
        self.map = map_json['map']
        self.scrape_airport_map()



    def scrape_airport_map(self):
        '''Obtém informação mais detalhada a partir do mapa (como as pistas e gares)'''
        self.airstrips = []
        self.stations = []
        airstrip_id = 0
        station_id = 0

        for x,line in enumerate(self.map):
            for y,space in enumerate(line):
                if space['type'] == 'airstrip':
                    self.airstrips.append(Airstrip(id=airstrip_id,x=x,y=y))
                    airstrip_id += 1
                elif space['type'] == 'station':
                    type=space['purpose']
                    self.stations.append(Station(id=station_id,type=type,x=x,y=y))
                    station_id += 1
        

        
