import socket
from Networking import Messages
import pickle

HOST = socket.gethostbyname(socket.gethostname())

def main():

    pool = {
        1: [],
        2: [],
        3: [],
        4: []
    }

    print(HOST)
    #create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Created socket")
    # bind the socket to a public host,
    # and an unassigned port
    serversocket.bind(('', Messages.MATCHMAKING_PORT))
    print("Socket bound")
    #become a server socket
    serversocket.listen(5)
    print("Matchmaking server listening")

    while True:
        conn, address = serversocket.accept()
        print("Connected to address %s" % str(address))
        config = pickle.loads(conn.recv(4096))
        if not isinstance(config, Messages.MatchmakingConfiguration):
            print("Breach of protocol; dropping connection to %s" % str(address))
            conn.send(pickle.dumps(Messages.MatchmakingError()))
            conn.close()
            continue
        n = config.number_of_players
        print("%s requests a %s-player game" % (str(address), str(n)))
        if n not in pool.keys():
            print("Cannot fulfill request for %s-player game; dropping connection to %s" % (str(n), str(address)))
            conn.send(pickle.dumps(Messages.MatchmakingError()))
            conn.close()
            continue
        pool[n].append((conn, address, config.ports))

        if len(pool[n]) == n:
            print("Starting a %s-player game" % str(n))
            peers = pool[n]
            for i in range(n-1):
                x = peers[i]

                others = []
                for o in peers[i+1:]:
                    addr = o[1][0], o[2].pop()
                    others.append((o[0], addr))
                x[0].send(pickle.dumps(Messages.MatchmakingPeers([addr for conn, addr in others])))
                x[0].close()

                for o in others:
                    o[0].send(pickle.dumps(Messages.MatchmakingAccept(o[1][1])))
            pool[n] = []

if __name__ == '__main__':
    main()

