import sys
import socket
import Messages
import pickle

SELF = socket.gethostbyname(socket.gethostname())

def main():
    if len(sys.argv) != 3:
        print("Expected name of matchmaking server and number of players")
        sys.exit(1)

    server_name, n = sys.argv[1:]

    peers = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Created socket")
    sock.connect((server_name, Messages.MATCHMAKING_PORT))
    sock.send(pickle.dumps(Messages.MatchmakingConfiguration(int(n))))

    data = pickle.loads(sock.recv(512))
    sock.close()
    if isinstance(data, Messages.MatchmakingError):
        print("Matchmaking Error")
        sys.exit(1)
    if not isinstance(data, Messages.MatchmakingPeers):
        sys.exit(1)

    peers = [p for p in data.peers if p != SELF]

    for peer in peers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer, Messages.PEER_PORT))
        peers.append(sock)

    listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Created listen socket")
    listensocket.bind((SELF, Messages.PEER_PORT))
    print("Listen socket bound")
    listensocket.listen(5)
    for peer in peers:
        listensocket.accept()
    print("Connected to %s peers" % len(data.peers))


if __name__ == '__main__':
    main()