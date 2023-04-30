class Voo:

    def __init__(self,origem,destino,data_descolagem):
        self.origem = origem  
        self.destino = destino 
        self.data_descolagem = data_descolagem

    def getOrigem(self):
        return self.origem
    
    def getDestino(self):
        return self.destino
    
    def getData_descolagem(self):
        return self.data_descolagem
    
    def setOrigem(self,origem):
        self.origem = origem

    def setDestino(self,destino):
        self.destino = destino

    def setData_descolagem(self,data_descolagem):
        self.data_descolagem = data_descolagem