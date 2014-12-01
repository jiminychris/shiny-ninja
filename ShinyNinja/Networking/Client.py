import sys
import socket
import Messages as Messages
import pickle
import threading
import Queue

class _Peer(object):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.avatar = None

_listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_peers = []
_avatars = []
_throttle = None
_in_messages = Queue.Queue()
_out_messages = Queue.Queue()
network_fps = 30.0
network_frame = 1.0/network_fps

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
    data = pickle.loads(sock.recv(4096))
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
        _peers.append(_Peer(sock, peer))

    for peer in data.peers:
        _listensocket.accept()
    _listensocket.setblocking(0)

    print("Connected to %s peers" % len(data.peers))

def register_avatars(avatars):
    for i in range(len(_peers)):
        _peers[i].avatar = avatars[i]
    def blast():
        for peer in _peers:
            for message in _out_messages:
                peer.sock.send(pickle.dumps(message))
        try:
            while True:
                data = pickle.loads(_listensocket.recv(4096))
                _in_messages.put(data)
        except socket.error:
            pass
    _throttle = Timer(network_frame, blast)
    _throttle.start()

def send(message):
    _out_messages.put(message)

def recv():
    result = []
    while not _in_messages.empty():
        result.append(_in_messages.get())
    return result
