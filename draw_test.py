import datetime
import random
from objects import Maps,Pista,Gare


#offset = random.randint(45,75)
#data_agora = datetime.datetime.now()
#data_descolagem = data_agora + datetime.timedelta(seconds = offset)
#
#print(data_agora)
#print(data_descolagem)


# Tamanho da mapa para caber na minha consola 143 x 35(espaço útil), 145 x 37(espaço total) 
                                                         
#print('+'+'−'*61+'Aeroporto Sá Carneiro'+'−'*61+'+') # 1 + 61 + 21 + 61 + 1 = 145 chars
#print(('|'+' '*143+'|\n')*34+('|'+' '*143+'|'))
#print('+'+'−'*143+'+') # 1 + 143 + 1 = 145
#
##print(' /\\')
#print('+−−+')
#print('|AC|')
#print('1000\n')
#
#print('+−−+')
#print('|AM|')
#print('9999\n')
#
#print('+−−+')
#print('|−−|\n')
#
#print('_'*141)
#print(' '*135+'AM100')
#print((' '*5+'−'*5)*14)
#print(' AC100')
#print('‾'*141)

map1 = Maps.Map()
map2 = Maps.Map()

map1.setFrame('Aeroporto Francisco Sá Carneiro')
map2.setFrame('Aeroporto Humberto Delgado')

pistas1 = []

pistas1.append(Pista.Pista(1,10))

pistas1.append(Pista.Pista(1,25))

map1.setPistas(pistas1)

map1.placePistas()

gares1 = []

#Primeira linha

gares1.append(Gare.Gare(5,7))

gares1.append(Gare.Gare(15,7))

gares1.append(Gare.Gare(25,7))

gares1.append(Gare.Gare(35,7))

gares1.append(Gare.Gare(45,7))

gares1.append(Gare.Gare(55,7))

gares1.append(Gare.Gare(65,7))

gares1.append(Gare.Gare(75,7))

gares1.append(Gare.Gare(85,7))

gares1.append(Gare.Gare(95,7))

gares1.append(Gare.Gare(105,7))

gares1.append(Gare.Gare(115,7))

gares1.append(Gare.Gare(125,7))

gares1.append(Gare.Gare(135,7))

#Segunda linha

gares1.append(Gare.Gare(5,18))

gares1.append(Gare.Gare(15,18))

gares1.append(Gare.Gare(25,18))

gares1.append(Gare.Gare(35,18))

gares1.append(Gare.Gare(45,18))

gares1.append(Gare.Gare(55,18))

gares1.append(Gare.Gare(65,18))

gares1.append(Gare.Gare(75,18))

gares1.append(Gare.Gare(85,18))

gares1.append(Gare.Gare(95,18))

gares1.append(Gare.Gare(105,18))

gares1.append(Gare.Gare(115,18))

gares1.append(Gare.Gare(125,18))

gares1.append(Gare.Gare(135,18))

#Terceira linha

gares1.append(Gare.Gare(5,22))

gares1.append(Gare.Gare(15,22))

gares1.append(Gare.Gare(25,22))

gares1.append(Gare.Gare(35,22))

gares1.append(Gare.Gare(45,22))

gares1.append(Gare.Gare(55,22))

gares1.append(Gare.Gare(65,22))

gares1.append(Gare.Gare(75,22))

gares1.append(Gare.Gare(85,22))

gares1.append(Gare.Gare(95,22))

gares1.append(Gare.Gare(105,22))

gares1.append(Gare.Gare(115,22))

gares1.append(Gare.Gare(125,22))

gares1.append(Gare.Gare(135,22))

#Quarta Linha 

gares1.append(Gare.Gare(5,33))

gares1.append(Gare.Gare(15,33))

gares1.append(Gare.Gare(25,33))

gares1.append(Gare.Gare(35,33))

gares1.append(Gare.Gare(45,33))

gares1.append(Gare.Gare(55,33))

gares1.append(Gare.Gare(65,33))

gares1.append(Gare.Gare(75,33))

gares1.append(Gare.Gare(85,33))

gares1.append(Gare.Gare(95,33))

gares1.append(Gare.Gare(105,33))

gares1.append(Gare.Gare(115,33))

gares1.append(Gare.Gare(125,33))

gares1.append(Gare.Gare(135,33))

map1.setGares(gares1)

map1.placeGares()

map1.drawMap()

pistas2 = []

pistas2.append((Pista.Pista(1,10)))

pistas2.append((Pista.Pista(1,21)))

map2.setPistas(pistas2)

map2.placePistas()

gares2 = []

#Primeira linha

gares2.append(Gare.Gare(5,7))

gares2.append(Gare.Gare(15,7))

gares2.append(Gare.Gare(25,7))

gares2.append(Gare.Gare(35,7))

gares2.append(Gare.Gare(45,7))

gares2.append(Gare.Gare(55,7))

gares2.append(Gare.Gare(65,7))

gares2.append(Gare.Gare(75,7))

gares2.append(Gare.Gare(85,7))

gares2.append(Gare.Gare(95,7))

gares2.append(Gare.Gare(105,7))

gares2.append(Gare.Gare(115,7))

gares2.append(Gare.Gare(125,7))

gares2.append(Gare.Gare(135,7))

#Segunda linha

gares2.append(Gare.Gare(5,18))

gares2.append(Gare.Gare(15,18))

gares2.append(Gare.Gare(25,18))

gares2.append(Gare.Gare(35,18))

gares2.append(Gare.Gare(45,18))

gares2.append(Gare.Gare(55,18))

gares2.append(Gare.Gare(65,18))

gares2.append(Gare.Gare(75,18))

gares2.append(Gare.Gare(85,18))

gares2.append(Gare.Gare(95,18))

gares2.append(Gare.Gare(105,18))

gares2.append(Gare.Gare(115,18))

gares2.append(Gare.Gare(125,18))

gares2.append(Gare.Gare(135,18))

#Terceira linha

gares2.append(Gare.Gare(5,29))

gares2.append(Gare.Gare(15,29))

gares2.append(Gare.Gare(25,29))

gares2.append(Gare.Gare(35,29))

gares2.append(Gare.Gare(45,29))

gares2.append(Gare.Gare(55,29))

gares2.append(Gare.Gare(65,29))

gares2.append(Gare.Gare(75,29))

gares2.append(Gare.Gare(85,29))

gares2.append(Gare.Gare(95,29))

gares2.append(Gare.Gare(105,29))

gares2.append(Gare.Gare(115,29))

gares2.append(Gare.Gare(125,29))

gares2.append(Gare.Gare(135,29))

map2.setGares(gares2)

map2.placeGares()

map2.drawMap()