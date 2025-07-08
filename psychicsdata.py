

class PsychicData:
    # Fields
    # ------
    # timestep : int - the timestep for this data
    # data : bytes - the data 
    def __init__(self, timestep: int, data: bytes):
        self.timestep = timestep
        self.data = data