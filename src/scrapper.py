#!/usr/bin/env python 

import time
from sys import argv
from bs4 import BeautifulSoup
from json import dumps
from apscheduler.schedulers.background import BackgroundScheduler
import requests

events = []
old_match_data = dict()


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

    Args:
        soup (BeautifulSoup): Soup of the current match
        home_or_away (int): Either a 1(home team) or 0(away team)
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
        return prev_sibling_tr.next_sibling.find('td', attrs={ 'class': 'incidencias2' }).string
    else:
        return ''

def parse_minute_and_player(string):
    if string.endswith('; '):
        substrings = string[:-2].split("'")
    else:
        substrings = string.split("'")
    if len(substrings) < 2 or substrings[1] is '' or substrings[1] is ' ':
        return None
    minutes_and_player = dict()
    minutes_and_player['minute'] = int(substrings[0])
    minutes_and_player['player'] = substrings[1].strip()
    return minutes_and_player

def parse_sub(string):
    if string.endswith('; '):
        substrings = string[:-2].split('⇆')
    else:
        substrings = string.split('⇆')
    minute_and_player_in = parse_minute_and_player(substrings[0].strip())
    sub = dict()
    sub['minute'] = minute_and_player_in['minute']
    sub['player_in'] = minute_and_player_in['player']
    sub['player_out'] = substrings[1].strip()
    return sub


def prepare_message(team_name, event_type_with_s, string):
    message = dict()
    message['event_type'] = event_type_with_s[:-1].upper()
    message['team'] = team_name
    if event_type_with_s is not 'subs':
        parsed = parse_minute_and_player(string)
    else:
        parsed = parse_sub(string)
    for k, v in parsed.items():
        message[k] = v
    return dumps(message)


def match_data_as_string(soup):
    match_data = dict()
    for x in [1,2]:
        team = 'home_team' if x is 1 else 'away_team'
        match_data[team] = dict()
        the_formacion = formacion(soup, x)
        match_data[team]['team_name'] = team_name(the_formacion)
        for i in ['goles', 'amarillas', 'rojas', 'cambios']:
            match_data[team][translate(i)] = incidencia(the_formacion, i)
    return match_data


def changes_as_string(old_data, soup):
    new_data = match_data_as_string(soup)
    events = []
    for team in ['home_team', 'away_team']:
        for k, v in new_data[team].items():
            if v > old_data[team][k]:
                team_name = new_data[team]['team_name']
                prefix = old_data[team][k]
                events.append(prepare_message(team_name, k, v[len(prefix):]))
    return (new_data, events)

match_data = 0

def job(url):
    global match_data

    document = requests.get(url).content
    soup = BeautifulSoup(document, 'lxml')

    changes = changes_as_string(match_data, soup)
    match_data = changes[0]

    for event in changes[1]:
        print(event)


def main():
    if len(argv[1:]) != 1:
        print('A match id was not specified, exiting...')
        return 1
    match_id = argv[1:][0]
    
    # Will hold all match data information, when scrapping job is triggered, it'll
    # be compared with another similar dictionary, which has the information
    # currently in the DOM. When the two instances are different an Event will be
    # launched.
    url = f'http://www.promiedos.com.ar/ficha.php?id={match_id}'
    document = requests.get(url).content
    soup = BeautifulSoup(document, 'lxml')

    global match_data
    match_data = match_data_as_string(soup)

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        (lambda: job(url)),
        'interval',
        seconds=30,
    )
    
    scheduler.start()

    try:
        while True:
           time.sleep(5) 
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

    return 0


if __name__ == '__main__':
    main()
