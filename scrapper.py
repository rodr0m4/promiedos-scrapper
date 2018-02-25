#!/usr/bin/env python 

from sys import argv
from apscheduler.schedulers.background import BackgroundScheduler
from custom_types import get_match, Card
from bs4 import BeautifulSoup
import requests


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
    # If its a 'gol' the previous tr has a td of class .incidencias1, otherwise it has \
    # the same class as the parameter incidencia.
    td_class = 'incidencias1' if incidencia_type is 'goles' else incidencia_type
    prev_sibling_tr = formacion.find('td', attrs={ 'class': td_class }).parent
    return prev_sibling_tr.next_sibling.find('td', attrs={ 'class': 'incidencias2' })


def get_changes(url, match_data):
    return 0


def main():
    if len(argv[1:]) != 1:
        print('A match id was not specified, exiting...')
        return 1
    match_id = argv[1:][0]
    
    url = f'http://www.promiedos.com.ar/ficha.php?id={match_id}'

    # Will hold all match data information, when scrapping job is triggered, it'll
    # be compared with another similar dictionary, which has the information
    # currently in the DOM. When the two instances are different an Event will be
    # launched.
    match_data = get_match()

    get_changes(url, match_data)
    return 1


if __name__ == '__main__':
    main()
