MATCHMAKING_PORT = 3126
PEER_PORT = 3092

class MatchmakingError:
    pass

class MatchmakingConfiguration:
    def __init__(self, number_of_players):
        self.number_of_players = number_of_players

class MatchmakingPeers:
    def __init__(self, peers):
        self.peers = peers

class MatchmakingConnect:
    pass

class Direction:
    Left = 0
    Right = 1
    Up = 2
    Down = 3

class Orientation:
    Vertical = 0
    Horizontal = 0

class NinjaMove:
    def __init__(self, orientation, magnitude):
        self.orientation = orientation
        self.magnitude = magnitude