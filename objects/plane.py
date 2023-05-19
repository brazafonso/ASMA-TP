from objects.flight import Flight


class Plane:
    '''Classe para representar aviao'''

    
    def __init__(self,id,state,airline_name,type,flight:Flight):
        self.id = id
        self.state = state
        self.airline_name = airline_name
        self.type = type
        self.flight = flight

    def __str__(self) -> str:
        return f'''
    plane : {self.id}        
        state : {self.state}
        airline : {self.airline_name}
        type : {self.type}
        destination : {self.flight.destination}
        origin : {self.flight.start}
'''

    def get_copy(self):
        return Plane(self.id,self.state,self.airline_name,self.type,self.flight.get_copy())