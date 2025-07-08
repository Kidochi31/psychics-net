from psychicsnetclient import *
from socketcommon import *
from socket import AF_INET
from select import select

def main():
    client_socket = create_ordinary_udp_socket(2000, AF_INET)
    client = PsychicClient(5, client_socket, "BOB")

    server_socket = create_ordinary_udp_socket(2010, AF_INET)
    server_socket_address = get_loopback_endpoint(AF_INET, get_canonical_local_endpoint(server_socket))
    if server_socket_address is None:
        return

    client.connect(server_socket_address)


    while client.is_connecting():
        rl, _, _ = select([server_socket], [], [], 0)
        if len(rl) > 0:
            data = server_socket.recv(2000)
            result = interpret_packet_safe(data)
            print(result)
        tick_result = client.tick(None)
        if tick_result == False:
            print("No longer connecting")


if __name__ == "__main__":
    main()