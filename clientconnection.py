from psychicsdata import PsychicData
from iptools import *

class ClientConnection:
    def __init__(self, server: IP_endpoint):
        self.server = server

    def receive(self) -> list[PsychicData]:
        # Receives new data from the other endpoint
        return []
    
    def send(self, data: PsychicData):
        # Sends data to the other endpoint
        pass