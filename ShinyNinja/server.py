import socket
from Networking import Messages
import pickle

HOST = socket.gethostbyname(socket.gethostname())

def main():

    pool = {
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
        config = pickle.loads(conn.recv(512))
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
        pool[n].append((conn, address))

        if len(pool[n]) == n:
            print("Starting a %s-player game" % str(n))
            peers = [x[1][0] for x in pool[n]]
            for x in pool[n]:
                others = [p for p in peers if p != x[1][0]]
                x[0].send(pickle.dumps(Messages.MatchmakingPeers(others)))
                x[0].close()
                pool[n] = []

if __name__ == '__main__':
    main()

