from objects.flight import Flight


class Plane:
    '''Classe para representar aviao'''

    
    def __init__(self,id,state,company,type,flight:Flight):
        self.id = id
        self.state = state
        self.company = company
        self.type = type
        self.flight = flight
