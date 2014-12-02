import sys
import socket
import Messages
import pickle
import threading
import Queue


#code from http://stackoverflow.com/questions/12435211/python-threading-timer-repeat-function-every-n-seconds
def _setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop(): # executed in another thread
                while not stopped.wait(interval): # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator

comm_array = []
_peers = []
_avatars = []
_throttle = None
_in_messages = Queue.Queue()
_out_messages = Queue.Queue()
network_fps = 30.0
network_frame = 1.0/network_fps

def find_peers(server_name, n):

    for p in range(n-1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Created listen socket")
        sock.bind(('', 0))
        print("Listen socket bound")
        sock.listen(5)

        comm_array.append(sock)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_name, Messages.MATCHMAKING_PORT))
    print("Connecting to matchmaking server")
    sock.send(pickle.dumps(Messages.MatchmakingConfiguration(int(n), [s.getsockname()[1] for s in comm_array])))

    print("Waiting for players...")

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
            _peers.append(Messages.Peer(addr, conn))
            server_sock.close()
        elif isinstance(data, Messages.MatchmakingPeers):
            print("Connecting to %s peer(s)" % len(data.peers))
            for addr in data.peers:
                comm_array.pop().close()
                peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_sock.connect(addr)
                _peers.append(Messages.Peer(addr, peer_sock))
        else:
            print("Protocol breach: %s" % str(data))
            sys.exit(1)
    sock.close()
    #for peer in _peers:
        #peer.sock.setblocking(0)
    print("Connected to %s peer(s)" % (n-1))


def register_avatars(avatars):
    for i in range(len(_peers)):
        _peers[i].avatar = avatars[i]

    @_setInterval(network_frame)
    def blast():
        messages = []
        while not _out_messages.empty():
            message = _out_messages.get()
            messages.append(message)
        for peer in _peers:
            peer.sock.send(pickle.dumps(messages))

    def in_loop(peer):
        while True:
            data = peer.sock.recv(4096)
            _in_messages.put((peer, data))

    _blaster = blast()
    for peer in _peers:
        _throttle = threading.Thread(target=in_loop, args=(peer,))
        _throttle.daemon = True
        _throttle.start()

def send(message):
    _out_messages.put(message)

def recv():
    result = []
    while not _in_messages.empty():
        peer, messages = _in_messages.get()
        messages = pickle.loads(messages)
        for message in messages:
            peer.avatar.recv(message)
