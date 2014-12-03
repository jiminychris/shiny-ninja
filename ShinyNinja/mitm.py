from Networking import Messages
import socket
import pickle
import sys
import threading
import Queue

HOST = socket.gethostbyname(socket.gethostname())

def main():
    peers = []
    me = {}

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
    serversocket.close()
    print("Connected to address %s" % str(address))
    print("Connecting to real matchmaking server...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_name, Messages.MATCHMAKING_PORT))
    print("Connected!")

    config = pickle.loads(conn.recv(4096))

    n = config.number_of_players
    comm_array = []

    for p in range(n-1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Created listen socket")
        s.bind(('', 0))
        print("Listen socket bound")
        s.listen(5)

        comm_array.append(s)
    
    config.ports = [s.getsockname()[1] for s in comm_array]
    sock.send(pickle.dumps(config))


    spotlight = sock.recv(4096)
    conn.send(spotlight)
    conn.send(pickle.dumps(Messages.MatchmakingPeers([s.getsockname() for s in comm_array])))
    for s in comm_array:
        c, a = s.accept()
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

    me["queue"] = Queue.Queue()
    me["x"] = me["y"] = 0

    def incoming(peer):
        while True:
            message = peer["remote_socket"].recv(4096)
            peer["local_socket"].send(message)
            peer["queue"].put(message)

    def outgoing(peer):
        while True:
            peer["remote_socket"].send(peer["local_socket"].recv(4096))

    def outgoing_special(peer):
        while True:
            message = peer["local_socket"].recv(4096)
            peer["remote_socket"].send(message)
            me["queue"].put(message)

    for peer in peers:
        peer["queue"] = Queue.Queue()
        peer["x"] = peer["y"] = 0

        thread = threading.Thread(target=incoming, args=(peer,))
        thread.daemon = True
        thread.start()

        target = outgoing
        if peer == peers[0]:
            target = outgoing_special
        thread = threading.Thread(target=target, args=(peer,))
        thread.daemon = True
        thread.start()

    j = 0
    while True:
        print(j)
        j += 1
        while not me["queue"].empty():
            messages = pickle.loads(me["queue"].get())
            for message in messages:
                if isinstance(message, Messages.NinjaPosition):
                    me["x"], me["y"] = message.x, message.y
                elif isinstance(message, Messages.NinjaMove):
                    if message.orientation == Messages.Orientation.Horizontal:
                        me["x"] += message.magnitude
                    else:
                        me["y"] += message.magnitude
        for peer in peers:
            while not peer["queue"].empty():
                messages = pickle.loads(peer["queue"].get())
                for message in messages:
                    if isinstance(message, Messages.NinjaPosition):
                        peer["x"], peer["y"] = message.x, message.y
                    elif isinstance(message, Messages.NinjaMove):
                        if message.orientation == Messages.Orientation.Horizontal:
                            peer["x"] += message.magnitude
                        else:
                            peer["y"] += message.magnitude
        print("Local: x=%s y=%s" % (me["x"], me["y"]))
        for i in range(len(peers)):
            print("Remote %s: x=%s y=%s" % (i, peers[i]["x"], peers[i]["y"]))

if __name__ == '__main__':
    main()

