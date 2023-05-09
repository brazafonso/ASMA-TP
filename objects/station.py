from objects.position import Position

class Station():
    '''Classe representante de uma gare do aeroporto'''

    
    def __init__(self,id,type,x,y,airline_name=None):
        self.id = id
        self.plane = None
        self.type = type
        self.state = 0 # Não ocupado
        self.pos = Position(x,y)
        self.airline_name = airline_name

        # TODO: Add base value in config file.
        self.base_value = 0


    def get_pos_x(self):
        return self.pos.x
    
    def get_pos_y(self):
        return self.pos.y

    def __str__(self) -> str:
        str= f'''Station {self.id}:
        - type    : {self.type}
        - vacancy : {self.state}'''
        str+='''
        - plane   : + ''' + f'{self.plane.id}' if self.plane else ''
        str +='''
        - pos     : {self.pos}'''
        return str
    
    def isEqual(self, station):
        return self.id == station.id

    