from objects.position import Position

class Station():
    '''Classe representante de uma gare do aeroporto'''

    
    def __init__(self,id,type,x,y):
        self.id = id
        self.plane = None
        self.type = type
        self.state = 0 # Não ocupado
        self.pos = Position(x,y)


    def __str__(self) -> str:
        return f'''Station {self.id}:
        - type    : {self.type}
        - vacancy : {self.state}
        - plane   : {self.plane}
        - pos     : {self.pos}'''



    