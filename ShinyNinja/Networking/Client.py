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
        sock.setblocking(0)
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
    data = pickle.loads(sock.recv(4096))
    sock.close()
    print("Found players!")
    if isinstance(data, Messages.MatchmakingError):
        print("Matchmaking Error")
        sys.exit(1)
    if not isinstance(data, Messages.MatchmakingPeers):
        print("Protocol breach: %s" % str(data))
        sys.exit(1)
    for ip, port in data.peers:
        addr = (ip, port)
        _peers.append(Messages.Peer(addr, comm_array.pop()))

    print("Connected to %s peers" % len(data.peers))

def register_avatars(avatars):
    for i in range(len(_peers)):
        _peers[i].avatar = avatars[i]

    @_setInterval(network_frame)
    def blast():
        while not _out_messages.empty():
            message = _out_messages.get()
            print("Sending %s!" % (message))
            for peer in _peers:
                peer.out_sock.send(pickle.dumps(message))

        for peer in _peers:
            try:
                while True:
                    data = pickle.loads(peer.in_sock.recv(4096))
                    _in_messages.put((peer, data))
            except socket.error:
                pass
    _throttle = blast()

def send(message):
    _out_messages.put(message)

def recv():
    result = []
    while not _in_messages.empty():
        peer, message = _in_messages.get()
        peer.avatar.recv(message)
