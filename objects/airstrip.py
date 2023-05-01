from objects.position import Position

class Airstrip():
    '''Classe representante de uma pista do aeroporto'''

    
    def __init__(self,id,x,y):
        self.id = id
        self.plane = None
        self.state = 0 # Não ocupada
        self.pos = Position(x,y)


    def get_pos_x(self):
        return self.pos.x
    
    def get_pos_y(self):
        return self.pos.y

    def __str__(self) -> str:
        return f'''Strip {self.id}:
        - vacancy : {self.state}
        - plane   : {self.plane}
        - pos     : {self.pos}'''



    