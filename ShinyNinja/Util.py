class Event(object):
    def __init__(self):
        self._subscribers = []

    def subscribe(self, f):
        self._subscribers.append(f)

    def unsubscribe(self, f):
        self._subscribers.remove(f)

    def fire(self, event_args):
        for subscriber in self._subscribers:
            subscriber(event_args)
            