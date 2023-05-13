from objects.position import Position

class Station():
    '''Classe representante de uma gare do aeroporto'''

    
    def __init__(self,id,type,x,y, base_value, airline_name=None):
        self.id = id
        self.plane = None
        self.type = type
        self.state = 0 # Não ocupado
        self.pos = Position(x,y)
        self.airline_name = airline_name
        self.base_value = base_value


    def get_pos_x(self):
        return self.pos.x
    
    def get_pos_y(self):
        return self.pos.y

    def __str__(self) -> str:
        str= f'''Station {self.id}:
        - type    : {self.type}
        - vacancy : {self.state}'''
        str+='''
        - plane   : ''' + f'{self.plane.id}' if self.plane else ''
        str +='''
        - pos     : ''' + f'{self.pos}'
        return str
    
    def isEqual(self, station):
        return self.id == station.id

    def get_copy(self):
        station = Station(self.id, self.type, self.pos.x, self.pos.y, self.base_value, self.airline_name)
        station.plane = self.plane
        station.state = self.state
        return station
    