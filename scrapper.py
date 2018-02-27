#!/usr/bin/env python 
from sys import argv
from bs4 import BeautifulSoup
from json import dumps
import requests


def translate(string):
    translations = {
        'goles': 'goals',
        'amarillas': 'yellow_cards',
        'rojas': 'red_cards',
        'cambios': 'subs'
    }
    return translations[string]


def formacion(soup, home_or_away):
    """
    Given a ficha soup, it will return either the formacion table of the home team, or the away one.
    """
    return soup.find('table', attrs={ 'id': f'formacion{home_or_away}' })


def team_name(formacion):
    """
    Given a formacion table, it will find and return the name of the team.
    """
    return formacion.find('td', attrs={ 'class': 'nomequipo' }).string


def incidencia(formacion, incidencia_type):
    """
    Given a formacion table, and an incidencia, that is a string that can be one of: \
    ['amarillas', 'cambios', 'rojas', 'goles'], it will return a string contained in a \
    td of class 'incidencias2'
    """
    # If its a 'gol' the previous tr has a td of class .incidencias1, otherwise it has
    # the same class as the parameter incidencia.
    td_class = 'incidencias1' if incidencia_type is 'goles' else incidencia_type
    prev_sibling_td = formacion.find('td', attrs={ 'class': td_class })
    if prev_sibling_td:
        prev_sibling_tr = prev_sibling_td.parent
        return prev_sibling_tr.next_sibling.find('td', attrs={ 'class': 'incidencias2' })


def parse_minute_and_player(string):
    """
    Given a string like '30\' Some. Player' it deconstructs it into minutes and player
    """
    minute_and_player = dict()
    for subs in string.split('\''):
        try:
            minute_and_player['minute'] = int(subs)
        except ValueError:
            minute_and_player['player'] = subs[1:]
    return minute_and_player


def parse_sub(string):
    """
    Given a string of like '30\' P. In ⇆ P. Out generates a sub dict
    """
    if string.endswith(';'):
        string = string [:-1]
    if string.startswith(' '):
        string = string [1:]
    # TODO: Maybe keep Lesion?
    if string.endswith(' (Lesion)') or string.endswith(' (Lesión)'):
        string = string[:-9]
    players = string.split('⇆')
    if players[0] is not '' and players[0] is not ' ':
        # players[0] should be of the form 'minutes\' player' and players[1]
        # of the form ' player'
        minute_and_player_in = parse_minute_and_player(players[0])
        sub = dict()
        sub['minute'] = minute_and_player_in['minute']
        sub['player_in'] = minute_and_player_in['player'].strip()
        player_out = players[1]
        sub['player_out'] = player_out[1:] if player_out.startswith(' ') else player_out
        return sub


def parse_incidencia(incidencia):
    """
    Given a incidencia (a td containing information about goals, subs and cards), parses the string, \
    returning a list of the events inside of it.
    """
    if incidencia:
        string = incidencia.string
        events = []
        if '⇆' in string:
            subs = []
            for s in string.split(';'):
                if s is not ' ':
                    subs.append(parse_sub(s))
            events.append(subs)
        else:
            for s in string.split(';'):
                if s is not ' ' and s is not '':
                    events.append(
                        parse_minute_and_player(s[1:] if s.startswith(' ') else s)
                    )
            # return [s for s in string.split(';') if s is not ' ' and s is not '62\' L. Fernandez']
        return events
        

def flatten(a_list):
    """
    Takes a list with sublists, returns a flat list:
    flatten :: [[a]] -> [a]
    """
    return [item for sublist in a_list for item in sublist]


def compare(old, new):
    """
    Goes over two dicts with the same keys, whose values contain lists. Returns a \
    list of the values present in the new list but not in the old one.
    """
    events = []
    for key, value in old.items():
        if isinstance(old[key], dict) and isinstance(new[key], dict):
            events.append(compare(old[key], new[key]))
        if old[key] != new[key]:
            events.append([x for x in new[key] if x not in old[key]])
    return flatten(events)


def get_changes(id, match_data):
    url = f'http://www.promiedos.com.ar/ficha.php?id={id}'
    document = requests.get(url).content
    soup = BeautifulSoup(document, 'lxml')
    
    new_match_data = dict()
    new_match_data['match_id'] = id
    for x in [1,2]:
        a_formacion = formacion(soup, x)
        team = dict()
        team['name'] = team_name(a_formacion)
        for i in ['goles', 'amarillas', 'rojas', 'cambios']:
            incidencias = parse_incidencia(incidencia(a_formacion, i))
            team[translate(i)] = incidencias if incidencias else []
        new_match_data[
            'home_team' if x is 1 else 'away_team'
        ] = team
    # return compare(match_data, new_match_data)


def main():
    if len(argv[1:]) != 1:
        print('A match id was not specified, exiting...')
        return 1
    match_id = argv[1:][0]

    # Will hold all match data information, when scrapping job is triggered, it'll
    # be compared with another similar dictionary, which has the information
    # currently in the DOM. When the two instances are different an Event will be
    # launched.
    match_data = dict()

    # get_changes(match_id, match_data)
    print(dumps(
        compare(
            {
                'match': 'ccvnfkpnf',
                'home_team': {
                    'goals': [
                        { 'minute': 3 }
                    ]
                },
                'away_team': {
                    'goals': [
                        { 'minute': 3 }
                    ],
                    'yellow_cards': []
                }
            },
            {
                'match': 'ccvnfkpnf',
                'home_team': {
                    'goals': [
                        { 'minute': 3 },
                        { 'minute': 10 }
                    ]
                },
                'away_team': {
                    'goals': [
                        { 'minute': 3 },
                        { 'minute': 15 }
                    ],
                    'yellow_cards': [
                        { 'minute': 25 }
                    ]
                }
            }
        )
    ))
    return 0


if __name__ == '__main__':
    main()
