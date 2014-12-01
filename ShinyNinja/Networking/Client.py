import sys
import socket
import Messages as Messages
import pickle

class Peer(object):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.avatar = 0

_listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_peers = []
_avatars = []

def find_peers(server_name, n):

    print("Created listen socket")
    _listensocket.bind(('', Messages.PEER_PORT))
    print("Listen socket bound")
    _listensocket.listen(5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_name, Messages.MATCHMAKING_PORT))
    print("Connecting to matchmaking server")
    sock.send(pickle.dumps(Messages.MatchmakingConfiguration(int(n))))

    print("Waiting for players...")
    data = pickle.loads(sock.recv(512))
    sock.close()
    print("Found players!")
    if isinstance(data, Messages.MatchmakingError):
        print("Matchmaking Error")
        sys.exit(1)
    if not isinstance(data, Messages.MatchmakingPeers):
        print("Protocol breach: %s" % str(data))
        sys.exit(1)

    for peer in data.peers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (peer, Messages.PEER_PORT)
        print("Connecting to %s..." % str(addr))
        sock.connect(addr)
        print("Connection succeeded!")
        _peers.append(Peer(sock, peer))

    for peer in data.peers:
        _listensocket.accept()

    print("Connected to %s peers" % len(data.peers))

def register_avatars(avatars):
    for i in range(len(_peers)):
        _peers[i].avatar = avatars[i]
