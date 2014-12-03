import sys
import socket
import Messages
import pickle
import threading
import Queue
import sha

class _Protocol(object):
    NAIVE = 0
    LOCKSTEP = 1
    AS = 2

PROTOCOL = _Protocol.NAIVE
if len(sys.argv) > 3:
    protocol = sys.argv[3]
    if protocol == "naive":
        pass
    elif protocol == "lockstep":
        PROTOCOL = _Protocol.LOCKSTEP
    elif protocol == "as":
        PROTOCOL = _Protocol.AS
        print("AS not implemented")
        sys.exit(1)
    else:
        print("protocol not recognized")
        sys.exit(1)

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
_me = Messages.Peer("127.0.0.1", 0)
_avatars = []
_spotlights = []
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

    messages = pickle.loads(sock.recv(4096))
    print("Found players!")
    for message in messages:
        if isinstance(message, Messages.Spotlights):
            _spotlights.extend(message.spotlights)
        elif isinstance(message, Messages.MatchmakingError):
            print("Matchmaking Error")
            sys.exit(1)
        elif isinstance(message, Messages.MatchmakingAccept):
            print("Connecting to 1 peer")
            server_sock = [s for s in comm_array if s.getsockname()[1] == message.port][0]
            comm_array.remove(server_sock)
            conn, addr = server_sock.accept()
            _peers.append(Messages.Peer(addr, conn))
            #conn.send(pickle.dumps(Messages.PeerConnected()))
            print("Connected to %s on port %s" % (addr, conn.getsockname()[1]))
            server_sock.close()
        elif isinstance(message, Messages.MatchmakingPeers):
            print("Connecting to %s peer(s)" % len(message.peers))
            for addr in message.peers:
                comm_array.pop().close()
                peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_sock.connect(addr)
                _peers.append(Messages.Peer(addr, peer_sock))
                #message = pickle.loads(peer_sock.recv(4096))
                #if not isinstance(message, Messages.PeerConnected):
                    #print("Expected PeerConnected message; got %s" % str(message))
                print("Connected to %s on port %s" % (addr, peer_sock.getsockname()[1]))
        else:
            print("Protocol breach: %s" % str(message))
            sys.exit(1)
    #for peer in _peers:
        #peer.sock.setblocking(0)
    print("Connected to %s peer(s)" % (n-1))

def get_spotlights():
    return _spotlights

def register_local_avatar(avatar):
    _me.avatar = avatar

if (PROTOCOL == _Protocol.NAIVE):
    def register_remote_avatars(avatars):
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
            while peer.active:
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
            try:
                messages = pickle.loads(messages)
            except EOFError:
                print("Peer quit the game")
                peer.active = False
            for message in messages:
                if isinstance(message, Messages.SwordSwing):
                    _me.avatar.recv(message)
                else:
                    peer.avatar.recv(message)
elif (PROTOCOL == _Protocol.LOCKSTEP):
    hashes = Queue.Queue(len(_peers))

    def register_remote_avatars(avatars):
        for i in range(len(_peers)):
            _peers[i].avatar = avatars[i]

        @_setInterval(network_frame)
        def blast():
            messages = []
            while not _out_messages.empty():
                message = _out_messages.get()
                messages.append(message)
            s = pickle.dumps(messages)
            h = sha.new(s).digest()
            for peer in _peers:
                peer.sock.send(h)
            ct = 0
            while ct < len(_peers):
                hashes.get()
                ct += 1
            for peer in _peers:
                peer.sock.send(s)

        def in_loop(peer):
            while peer.active:
                data = peer.sock.recv(4096)
                h = data[:20]
                hashes.put(h)
                data = data[20:]
                if len(data) == 0:
                    data = peer.sock.recv(4096)
                _in_messages.put((peer, data, h))

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
            peer, s, h = _in_messages.get()
            check = sha.new(s).digest()
            if not check == h:
                print("CHEATER! (%s : %s)" % (check, h))
            messages = []
            try:
                messages = pickle.loads(s)
            except EOFError:
                print("Peer quit the game")
                peer.active = False
            for message in messages:
                if isinstance(message, Messages.SwordSwing):
                    _me.avatar.recv(message)
                else:
                    peer.avatar.recv(message)
else:
    pass
