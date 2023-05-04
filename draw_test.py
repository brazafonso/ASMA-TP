import datetime
import random
import json 
from objects import airport_map,airstrip,station


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

f = open('config/1.json')

ap_map = json.load(f)

map1 = airport_map.AirportMap(ap_map)
map1.set_frame()
map1.place_airstrips()
map1.place_stations()
map1.place_roads()
map1.draw_map()

map2 = airport_map.AirportMap(ap_map)

map2.set_frame()

pistas1 = []

pistas1.append(airstrip.Airstrip(1,1,10))

pistas1.append(airstrip.Airstrip(2,1,25))

map1.airstrips = pistas1

map1.place_airstrips()

gares1 = []

#Primeira linha

gares1.append(station.Station(1,'tipo',5,7))

gares1.append(station.Station(2,'tipo',15,7))

gares1.append(station.Station(3,'tipo',25,7))

gares1.append(station.Station(4,'tipo',35,7))

gares1.append(station.Station(5,'tipo',45,7))

gares1.append(station.Station(6,'tipo',55,7))

gares1.append(station.Station(7,'tipo',65,7))

gares1.append(station.Station(8,'tipo',75,7))

gares1.append(station.Station(9,'tipo',85,7))

gares1.append(station.Station(10,'tipo',95,7))

gares1.append(station.Station(11,'tipo',105,7))

gares1.append(station.Station(12,'tipo',115,7))

gares1.append(station.Station(13,'tipo',125,7))

gares1.append(station.Station(14,'tipo',135,7))

#Segunda linha

gares1.append(station.Station(15,'tipo',5,18))

gares1.append(station.Station(16,'tipo',15,18))

gares1.append(station.Station(17,'tipo',25,18))

gares1.append(station.Station(18,'tipo',35,18))

gares1.append(station.Station(19,'tipo',45,18))

gares1.append(station.Station(20,'tipo',55,18))

gares1.append(station.Station(21,'tipo',65,18))

gares1.append(station.Station(22,'tipo',75,18))

gares1.append(station.Station(23,'tipo',85,18))

gares1.append(station.Station(24,'tipo',95,18))

gares1.append(station.Station(25,'tipo',105,18))

gares1.append(station.Station(26,'tipo',115,18))

gares1.append(station.Station(27,'tipo',125,18))

gares1.append(station.Station(28,'tipo',135,18))

#Terceira linha

gares1.append(station.Station(29,'tipo',5,22))

gares1.append(station.Station(30,'tipo',15,22))

gares1.append(station.Station(31,'tipo',25,22))

gares1.append(station.Station(32,'tipo',35,22))

gares1.append(station.Station(33,'tipo',45,22))

gares1.append(station.Station(34,'tipo',55,22))

gares1.append(station.Station(35,'tipo',65,22))

gares1.append(station.Station(36,'tipo',75,22))

gares1.append(station.Station(37,'tipo',85,22))

gares1.append(station.Station(38,'tipo',95,22))

gares1.append(station.Station(39,'tipo',105,22))

gares1.append(station.Station(40,'tipo',115,22))

gares1.append(station.Station(41,'tipo',125,22))

gares1.append(station.Station(42,'tipo',135,22))

#Quarta Linha 

gares1.append(station.Station(43,'tipo',5,33))

gares1.append(station.Station(44,'tipo',15,33))

gares1.append(station.Station(45,'tipo',25,33))

gares1.append(station.Station(46,'tipo',35,33))

gares1.append(station.Station(47,'tipo',45,33))

gares1.append(station.Station(48,'tipo',55,33))

gares1.append(station.Station(49,'tipo',65,33))

gares1.append(station.Station(50,'tipo',75,33))

gares1.append(station.Station(51,'tipo',85,33))

gares1.append(station.Station(52,'tipo',95,33))

gares1.append(station.Station(53,'tipo',105,33))

gares1.append(station.Station(54,'tipo',115,33))

gares1.append(station.Station(55,'tipo',125,33))

gares1.append(station.Station(56,'tipo',135,33))

map1.stations = gares1

map1.place_stations()

map1.place_roads()

map1.draw_map()

pistas2 = []

pistas2.append((airstrip.Airstrip(1,10)))

pistas2.append((airstrip.Airstrip(1,21)))

map2.setPistas(pistas2)

map2.placePistas()

gares2 = []

#Primeira linha

gares2.append(station.Station(5,7))

gares2.append(station.Station(15,7))

gares2.append(station.Station(25,7))

gares2.append(station.Station(35,7))

gares2.append(station.Station(45,7))

gares2.append(station.Station(55,7))

gares2.append(station.Station(65,7))

gares2.append(station.Station(75,7))

gares2.append(station.Station(85,7))

gares2.append(station.Station(95,7))

gares2.append(station.Station(105,7))

gares2.append(station.Station(115,7))

gares2.append(station.Station(125,7))

gares2.append(station.Station(135,7))

#Segunda linha

gares2.append(station.Station(5,18))

gares2.append(station.Station(15,18))

gares2.append(station.Station(25,18))

gares2.append(station.Station(35,18))

gares2.append(station.Station(45,18))

gares2.append(station.Station(55,18))

gares2.append(station.Station(65,18))

gares2.append(station.Station(75,18))

gares2.append(station.Station(85,18))

gares2.append(station.Station(95,18))

gares2.append(station.Station(105,18))

gares2.append(station.Station(115,18))

gares2.append(station.Station(125,18))

gares2.append(station.Station(135,18))

#Terceira linha

gares2.append(station.Station(5,29))

gares2.append(station.Station(15,29))

gares2.append(station.Station(25,29))

gares2.append(station.Station(35,29))

gares2.append(station.Station(45,29))

gares2.append(station.Station(55,29))

gares2.append(station.Station(65,29))

gares2.append(station.Station(75,29))

gares2.append(station.Station(85,29))

gares2.append(station.Station(95,29))

gares2.append(station.Station(105,29))

gares2.append(station.Station(115,29))

gares2.append(station.Station(125,29))

gares2.append(station.Station(135,29))

map2.setGares(gares2)

map2.placeGares()

map2.drawMap()