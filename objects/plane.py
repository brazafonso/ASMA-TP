from objects.flight import Flight


class Plane:
    '''Classe para representar aviao'''

    
    def __init__(self,id,state,airline_name,type,flight:Flight):
        self.id = id
        self.state = state
        self.airline_name = airline_name
        self.type = type
        self.flight = flight
