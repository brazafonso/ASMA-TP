class Pista:

    def __init__(self):
        self.posicao_x = 0
        self.posicao_y = 0 

    def __init__(self,x,y):
        self.posicao_x = x
        self.posicao_y = y 

    def getPosicaoX(self):
        return self.posicao_x
    
    def getPosicaoY(self):
        return self.posicao_y
    
    def setPosicaoX(self,posicao_x):
        self.posicao_x = posicao_x
    
    def setPosicaoY(self,posicao_y):
        self.posicao_y = posicao_y