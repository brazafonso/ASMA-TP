class Flight:

    def __init__(self,start,destination,take_off_date):
        self.start = start  
        self.destination = destination 
        self.take_off_date = take_off_date

    def get_start(self):
        return self.start
    
    def get_destination(self):
        return self.destination
    
    def get_take_off_date(self):
        return self.take_off_date
    \
    def set_start(self,start):
        self.start = start

    def set_destination(self,destination):
        self.destination = destination

    def set_take_off_date(self,take_off_date):
        self.take_off_date = take_off_date