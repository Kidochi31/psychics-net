from psychicsnetclient import *
from socketcommon import *
from socket import AF_INET
from select import select

def complete_client_connection(client: PsychicClient, server: socket, server_response: bytes | None, response_delay_ns: int):
    start_time = time_ns()

    while client.is_connecting():
        rl, _, _ = select([server], [], [], 0)
        if len(rl) > 0:
            data = server.recv(2000)
            result = interpret_packet_safe(data)
            print(result)
        
        response = None
        if time_ns() >= start_time + response_delay_ns:
            response = server_response
        
        tick_result = client.tick(response)

        if tick_result == False:
            print("No longer connecting")
        if isinstance(tick_result, ClientConnection):
            print("new connection made")

def test_connecting_to_nothing():
    print('connecting to silent server')
    client_socket = create_ordinary_udp_socket(2000, AF_INET)
    client = PsychicClient(5, client_socket, "BOB")

    server_socket = create_ordinary_udp_socket(2010, AF_INET)
    server_socket_address = get_loopback_endpoint(AF_INET, get_canonical_local_endpoint(server_socket))
    if server_socket_address is None:
        return

    print(f"connection worked: {client.connect(server_socket_address)}")

    complete_client_connection(client, server_socket, None, 999999999999999999999)
    
    print("connecting to invalid address")
    print(f"connection worked: {client.connect(('', 0))}")
    print(f"is connecting: {client.is_connecting()}")
    complete_client_connection(client, server_socket, None, 999999999999999999999)
    
    print("connecting to valid address")
    print(f"connection worked: {client.connect(server_socket_address)}")

    complete_client_connection(client, server_socket, None, 999999999999999999999)


def test_receiving_accept():
    print('connecting to server that will respond with accept')
    client_socket = create_ordinary_udp_socket(2000, AF_INET)
    client = PsychicClient(5, client_socket, "ALICE")

    server_socket = create_ordinary_udp_socket(2010, AF_INET)
    server_socket_address = get_loopback_endpoint(AF_INET, get_canonical_local_endpoint(server_socket))
    if server_socket_address is None:
        return

    print(f"connection worked: {client.connect(server_socket_address)}")


    complete_client_connection(client, server_socket, create_accept_packet(VERS, VERSION, 100, 10, 1, b'HIIIII FROM SERVER'), 50_000_000)
    
    print(f"connected: {client.is_connected()}")
    print(f"connecting: {client.is_connecting()}")

    print(f"second connection attempt: {client.connect(server_socket_address)}")

def test_receiving_accept_wrong_version():
    print('connecting to server that will respond with an accept with the wrong version')
    client_socket = create_ordinary_udp_socket(2000, AF_INET)
    client = PsychicClient(5, client_socket, "ALICE")

    server_socket = create_ordinary_udp_socket(2010, AF_INET)
    server_socket_address = get_loopback_endpoint(AF_INET, get_canonical_local_endpoint(server_socket))
    if server_socket_address is None:
        return

    print(f"connection worked: {client.connect(server_socket_address)}")
    complete_client_connection(client, server_socket, create_accept_packet(VERS + 1, VERSION, 100, 10, 1, b'HIIIII FROM SERVER'), 50_000_000)
    print(f"connected: {client.is_connected()}")
    print(f"connecting: {client.is_connecting()}")

    print(f"connection worked: {client.connect(server_socket_address)}")
    complete_client_connection(client, server_socket, create_accept_packet(VERS, VERSION + 1, 100, 10, 1, b'HIIIII FROM SERVER'), 50_000_000)
    print(f"connected: {client.is_connected()}")
    print(f"connecting: {client.is_connecting()}")

    print(f"connection worked: {client.connect(server_socket_address)}")
    complete_client_connection(client, server_socket, create_accept_packet(VERS + 1, VERSION + 1, 100, 10, 1, b'HIIIII FROM SERVER'), 50_000_000)
    print(f"connected: {client.is_connected()}")
    print(f"connecting: {client.is_connecting()}")

    print(f"connection worked: {client.connect(server_socket_address)}")
    complete_client_connection(client, server_socket, create_accept_packet(VERS, VERSION, 100, 10, 1, b'HIIIII FROM SERVER'), 50_000_000)
    print(f"connected: {client.is_connected()}")
    print(f"connecting: {client.is_connecting()}")

def main():
    print("----------Starting Client Connection Tests----------")
    test_connecting_to_nothing()
    test_receiving_accept()
    test_receiving_accept_wrong_version()
    print("----------Finished Client Connection Tests----------")

if __name__ == "__main__":
    main()
    