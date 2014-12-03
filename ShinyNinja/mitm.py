from Networking import Messages
import socket
import pickle
import sys
import threading

HOST = socket.gethostbyname(socket.gethostname())

def main():
    peers = []

    if len(sys.argv) != 2:
        print("Expected name of matchmaking server")
        sys.exit(1)

    server_name = sys.argv[1]

    print(HOST)
    #create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Created socket")
    # bind the socket to a public host,
    # and an unassigned port
    serversocket.bind(('', Messages.MATCHMAKING_PORT))
    print("Socket bound")
    #become a server socket
    serversocket.listen(5)
    print("Man-in-the-middle listening >:)")

    conn, address = serversocket.accept()
    print("Connected to address %s" % str(address))
    print("Connecting to real matchmaking server...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_name, Messages.MATCHMAKING_PORT))
    print("Connected!")

    raw_config = conn.recv(4096)
    config = pickle.loads(raw_config)
    sock.send(raw_config)

    n = raw_config.number_of_players
    comm_array = []

    for p in range(n-1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Created listen socket")
        sock.bind(('', 0))
        print("Listen socket bound")
        sock.listen(5)

        comm_array.append(sock)

    conn.send(sock.recv(4096))
    conn.send(pickle.dumps(Messages.MatchmakingPeers([sock.getsockname() for sock in comm_array])))
    for sock in comm_array:
        c, a = sock.accept()
        peers.append({"local_socket": c})
    conn.close()


    while len(comm_array) > 0:
        data = pickle.loads(sock.recv(4096))
        if isinstance(data, Messages.MatchmakingError):
            print("Matchmaking Error")
            sys.exit(1)
        elif isinstance(data, Messages.MatchmakingAccept):
            print("Connecting to 1 peer")
            server_sock = [s for s in comm_array if s.getsockname()[1] == data.port][0]
            comm_array.remove(server_sock)
            conn, addr = server_sock.accept()
            peers[len(comm_array)]["remote_socket"] = conn
            print("Connected to %s on port %s" % (addr, conn.getsockname()[1]))
            server_sock.close()
        elif isinstance(data, Messages.MatchmakingPeers):
            print("Connecting to %s peer(s)" % len(data.peers))
            for addr in data.peers:
                comm_array.pop().close()
                peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_sock.connect(addr)
                peers[len(comm_array)]["remote_socket"] = peer_sock
                print("Connected to %s on port %s" % (addr, peer_sock.getsockname()[1]))
        else:
            print("Protocol breach: %s" % str(data))
            sys.exit(1)
    sock.close()

    def incoming(peer):
        while True:
            peer["local_socket"].send(peer["remote_socket"].recv(4096))
            
    def outgoing(peer):
        while True:
            peer["remote_socket"].send(peer["local_socket"].recv(4096))

    for peer in peers:
        threading.Thread(target=incoming, args=(peer,))
        threading.Thread(target=outgoing, args=(peer,))

if __name__ == '__main__':
    main()

