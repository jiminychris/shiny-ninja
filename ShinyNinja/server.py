import socket
from Networking import Messages
import pickle
import random
import os

# Code from http://stackoverflow.com/questions/11735821/python-get-localhost-ip
if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip
###

HOST = get_lan_ip()

def main():
    random.seed()

    pool = {
        1: [],
        2: [],
        3: [],
        4: []
    }

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
            spotlights = [(random.random(), random.random()) for i in range()]
            peers = pool[n]
            for peer in peers:
                peer[0].send(pickle.dumps(Messages.Spotlights(spotlights)))
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

