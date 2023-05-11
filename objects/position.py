class Position():
    '''Classe representante de uma posição num espaço 2D'''
    
    def __init__(self,x,y):
        self.x = x
        self.y = y


    def __str__(self) -> str:
        return f'({self.x},{self.y})'
    
    def distance(self,other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)**(1/2)

    def get_copy(self):
        return Position(self.x,self.y)
    