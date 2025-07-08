from psychicsnetclient import *
from socketcommon import *
from socket import AF_INET
from select import select

def test_connecting_to_nothing():
    print('connecting to silent server')
    client_socket = create_ordinary_udp_socket(2000, AF_INET)
    client = PsychicClient(5, client_socket, "BOB")

    server_socket = create_ordinary_udp_socket(2010, AF_INET)
    server_socket_address = get_loopback_endpoint(AF_INET, get_canonical_local_endpoint(server_socket))
    if server_socket_address is None:
        return

    print(f"connection worked: {client.connect(server_socket_address)}")

    while client.is_connecting():
        rl, _, _ = select([server_socket], [], [], 0)
        if len(rl) > 0:
            data = server_socket.recv(2000)
            result = interpret_packet_safe(data)
            print(result)
        tick_result = client.tick(None)
        if tick_result == False:
            print("No longer connecting")
    
    print("connecting to invalid address")
    print(f"connection worked: {client.connect(('', 0))}")
    print(f"is connecting: {client.is_connecting()}")
    while client.is_connecting():
        tick_result = client.tick(None)
        if tick_result == False:
            print("No longer connecting")
    
    print("connecting to valid address")
    print(f"connection worked: {client.connect(server_socket_address)}")

    while client.is_connecting():
        rl, _, _ = select([server_socket], [], [], 0)
        if len(rl) > 0:
            data = server_socket.recv(2000)
            result = interpret_packet_safe(data)
            print(result)
        tick_result = client.tick(None)
        if tick_result == False:
            print("No longer connecting")


def main():
    print("----------Starting Client Connection Tests----------")
    test_connecting_to_nothing()
    print("----------Finished Client Connection Tests----------")

if __name__ == "__main__":
    main()