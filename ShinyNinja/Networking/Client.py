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

    connections = 0
    while connections != n-1:
        data = pickle.loads(sock.recv(4096))
        if isinstance(data, Messages.MatchmakingError):
            print("Matchmaking Error")
            sys.exit(1)
        if isinstance(data, Messages.MatchmakingAccept):
            print("Connecting to 1 peer")
            sock = [s for s in comm_array if s.getsockname()[1] == data.port][0]
            comm_array.remove(sock)
            conn, addr = sock.accept()
            peers.append(Messages.Peer((addr, conn)))
            connections += 1
        if isinstance(data, Messages.MatchmakingPeers):
            print("Connecting to %s peer(s)" % len(data.peers))
            for addr in data.peers:
                sock = comm_array.pop()
                sock.close()
                sock.connect(addr)
                _peers.append(Messages.Peer(addr, sock))
                connections += 1
        else:
            print("Protocol breach: %s" % str(data))
            sys.exit(1)
    sock.close()
    print("Connected to %s peer(s)" % (n-1))


def register_avatars(avatars):
    for i in range(len(_peers)):
        _peers[i].avatar = avatars[i]

    @_setInterval(network_frame)
    def blast():
        messages = []
        while not _out_messages.empty():
            messages.append(_out_messages.get())

        for peer in _peers:
            for message in messages:
                peer.sock.send(pickle.dumps(message))
            try:
                while True:
                    data = pickle.loads(peer.sock.recv(4096))
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
