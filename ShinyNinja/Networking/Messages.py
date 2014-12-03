MATCHMAKING_PORT = 3126

class Peer(object):
    def __init__(self, addr, sock):
        self.addr = addr
        self.sock = sock
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

class MatchmakingAccept(object):
    def __init__(self, port):
        self.port = port

class MatchmakingConnect(object):
    pass

class NinjaMove(object):
    def __init__(self, orientation, magnitude):
        self.orientation = orientation
        self.magnitude = magnitude

    def __repr__(self):
        return ("<NinjaMove Orientation=%s Magnitude=%s>"
            % (self.orientation, self.magnitude))

class NinjaPosition(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return ("<NinjaPosition x=%s y=%s>"
            % (self.x, self.y))

class NinjaDeath(object):
    pass

class SwordSwing(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return ("<SwordSwing x=%s y=%s>"
            % (self.x, self.y))

class Spotlights(object):
    def __init__(self, spotlights):
        self.spotlights = spotlights
