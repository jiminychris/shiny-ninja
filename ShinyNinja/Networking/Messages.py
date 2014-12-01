MATCHMAKING_PORT = 3126

class Peer(object):
    def __init__(self, addr, in_sock, out_sock):
        self.addr = addr
        self.in_sock = in_sock
        self.out_sock = out_sock
        self.avatar = None

class Direction(object):
    Left = "L"
    Right = "R"
    Up = "U"
    Down = "D"

class Orientation(object):
    Vertical = "V"
    Horizontal = "H"

class MatchmakingError(object):
    pass

class MatchmakingConfiguration(object):
    def __init__(self, number_of_players, ports):
        self.number_of_players = number_of_players
        self.ports = ports

class MatchmakingPeers(object):
    def __init__(self, peers):
        self.peers = peers

class MatchmakingConnect(object):
    pass

class NinjaMove(object):
    def __init__(self, orientation, magnitude):
        self.orientation = orientation
        self.magnitude = magnitude

    def __repr__(self):
        return ("<NinjaMove Orientation=%s Magnitude=%s>"
            % (self.orientation, self.magnitude))