from clientconnection import ClientConnection
from psychicsdata import PsychicData
from iptools import unresolved_endpoint, resolve_to_canonical_endpoint
from socket import AddressFamily, SOL_UDP, SOCK_DGRAM
from socketcommon import create_ordinary_udp_socket

class PsychicClient:
    # Fields
    # ------
    # connection: ClientConnection | None
    # server: IP_endpoint | None
    # family: AddressFamily
    # socket: udp socket
    def __init__(self, family: AddressFamily):
        self.connection = None
        self.server = None
        self.family = family
        self.socket = create_ordinary_udp_socket(0, family)

    def connect(self, server: unresolved_endpoint) -> bool:
        resolved_server = resolve_to_canonical_endpoint(server, self.family)
        if resolved_server is None:
            return False
        

    def tick():
        # ticks the client forward. Ensure to run tick() before receiving or sending.
