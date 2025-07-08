from clientconnection import ClientConnection
from iptools import *
from socket import socket
from packet import *
from time import time_ns

VERS = 0
VERSION = 0
init_request_timeout_ns = 100_000_000

class PsychicClient:
    # Fields
    # ------
    # connection_info: ClientConnection | None
    # server: tuple[IP_endpoint] | None
    # family: AddressFamily
    # socket: udp socket
    def __init__(self, max_timeouts: int, socket: socket, name: str):
        self.connection_info:  ClientConnection | None= None
        self.server: IP_endpoint | None = None
        self.time_request_sent: int = 0
        self.max_timeouts = max_timeouts
        self.num_timeouts = 0
        self.socket = socket
        self.name = name

    def is_connected(self) -> bool:
        return self.connection_info is not None

    def is_connecting(self) -> bool:
        return self.connection_info is None and self.server is not None

    def connect(self, server: IP_endpoint) -> bool:
        if self.server is not None:
            return False
        self.server = server
        if not self._send_request_to_server(self.server):
            self._cancel_connect()
            return False
        return True
        
    def tick(self, data: bytes | None) -> ClientConnection | bool:
        # ticks the client forward. Ensure to run tick() before receiving or sending.
        # returns true if currently connecting, false if not connecting
        if self.connection_info is None:
            if self.server is None:
                return False # nothing to do
            else: #currently waiting for server response
                if data is not None:
                    info = interpret_packet_safe(data)
                    if info is not None and info[0] == PacketType.ACCEPT:
                        manage_result = self._manage_accept_packet(info[1], self.server)
                        if manage_result is None:
                            return False
                        return manage_result
                    # ignore packet
                # check timeout
                if time_ns() >= self.time_request_sent + init_request_timeout_ns:
                    self.num_timeouts += 1
                    if self.num_timeouts >= self.max_timeouts:
                        # timeout
                        self._cancel_connect()
                        return False
                    self._send_request_to_server(self.server)
                return True
        # if it gets here, then sef.connection_info is not None
        return self.connection_info

                    
    def _manage_accept_packet(self, data: dict[str, Any], server: IP_endpoint) -> ClientConnection | None:
        #[("vers", ("version", ("timestep0", ("lentimestep", ("timestamp", ("data",
        if data["vers"] != VERS:
            self._cancel_connect()
            return None
        if data["version"] != VERSION:
            self._cancel_connect()
            return None
        self.connection_info = ClientConnection(server)
        return self.connection_info
                
    def _cancel_connect(self):
        self.num_timeouts = 0
        self.server = None 
    
    def _send_request_to_server(self, server: IP_endpoint) -> bool:
        try:
            request = create_request_packet(VERS, VERSION, self.name, b'hello')
            if request is not None:
                self.socket.sendto(request, server)
                self.time_request_sent = time_ns()
                return True
        except:
            pass
        return False