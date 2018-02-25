class Event():
    def __init__(self, minute: int):
        self.minute = minute


class Goal(Event):
    def __init__(self, minute: int, player: str):
        super(Event, self).__init__(minute)
        self.player = player


class Card(Event):
    def __init__(self, minute: int, player: str, color: str):
        super(Event, self).__init__(minute)
        self.player = player
        self.color = color


class Sub(Event):
    def __init__(self, minute: int, player_in: str, player_out: str):
        super(Event, self).__init__(minute)
        self.player_in = player_in
        self.player_out = player_out


class Team():
    def __init__(self):
        self.name = ''
        self.score = 0
        self.cards = dict()
        self.cards['red'] = []
        self.cards['yellow'] = []
        self.goals = []
        self.subs = []


def get_match():
    match = dict()
    match['home_team'] = Team()
    match['away_team'] = Team()
    return match