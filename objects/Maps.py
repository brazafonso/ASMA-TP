class Map:

    def __init__(self):
        self.pistas = []
        self.gares = []
        self.avioes = []
        self.size_x = 145
        self.size_y = 37
        self.map = [[' ' for _ in range(self.size_x)] for _ in range(self.size_y)]

    def getPistas(self):
        return self.pistas
    
    def getGares(self):
        return self.gares
    
    def getAvioes(self):
        return self.avioes
    
    def getSize_x(self):
        return self.size_x
    
    def getSize_y(self):
        return self.size_y
    
    def getMap(self):
        return self.map
    
    def setPistas(self,pistas):
        self.pistas = pistas
    
    def setGares(self,gares):
        self.gares = gares

    def setAvioes(self,avioes):
        self.avioes = avioes

    def setSize_x(self,size_x):
        self.size_x = size_x
    
    def setSize_y(self,size_y):
        self.size_y = size_y

    def setMap(self,map):
        self.map = map


    #def initMap(self):
    #    self.map = [[' ' for _ in range(self.size_y)] for _ in range(self.size_x)]

    def replacer(self,line,index,newstring):
        
        charline = list(self.map[line])

        for i in range(index,index+len(newstring)):
            charline[i] = newstring[i-index]

        self.map[line] = ''.join(charline)


    #Moldura que vai envolver o aeroporto
    def setFrame(self,airport_name):

        #Definir o Header com o nome do aeroporto

        border_lenght = self.size_x - len(airport_name)

        if (border_lenght % 2) == 0:
            border_left = int(border_lenght / 2)
            border_right = int(border_lenght / 2)

        else:
            border_left = int(border_lenght / 2)
            border_right = int(border_left + 1)

        self.map[0] = '+'+'−'*(border_left-1)+airport_name+'−'*(border_right-1)+'+'

        #Definir as bordas dos lados

        for i in range(1,self.size_y-1):
            self.map[i] = '|'+' '*(self.size_x-2)+'|'

        #Definir o footer

        self.map[-1] = '+'+'−'*(self.size_x-2)+'+'

        #Replace de teste

        #Map.replacer(self,17,70,'teste')


    def placeGares(self):
        topline = '+−−+'

        bottomline = '|−−|'

        for i in self.gares:
            x = i.getPosicaoX()
            y = i.getPosicaoY()
            Map.replacer(self,y-1,x,topline)
            Map.replacer(self,y,x,bottomline)

    def placePistas(self):
        topline = '_'*(self.size_x-2)

        resto = (self.size_x-2) % 10

        repeticoes = int((self.size_x-2) / 10)

        if resto == 0:

            midline = (' '*5+'−'*5)*(repeticoes)

        elif resto <= 5: 

            midline = (' '*5+'−'*5)*(repeticoes)+' '*resto

        elif resto <= 10:

            midline = (' '*5+'−'*5)*(repeticoes)+' '*5+'−'*(resto-5)

        bottomline = '‾'*(self.size_x-2)

        for i in self.pistas:
            x = i.getPosicaoX()
            y = i.getPosicaoY()
            Map.replacer(self,y,x,topline)
            Map.replacer(self,y+2,x,midline)
            Map.replacer(self,y+4,x,bottomline)


    def drawMap(self):
        for i in range(0,self.size_y):
            print(self.map[i])
      