class Position():
    '''Classe representante de uma posição num espaço 2D'''
    
    def __init__(self,x,y):
        self.x = x
        self.y = y


    def __str__(self) -> str:
        return f'({self.x},{self.y})'

    
    