#!/usr/bin/env python 
from sys import argv
from apscheduler.schedulers.background import BackgroundScheduler
from custom_types import get_match, Card
from bs4 import BeautifulSoup
import requests

def formacion(soup, home_or_away):
    return soup.find('table', attrs={ 'id': f'formacion{home_or_away}'})


def team_name(formacion):
    return formacion.find('td', attrs={ 'class': 'nomequipo' }).string

def get_changes(url, match_data):
    document = requests.get(url).content
    soup = BeautifulSoup(document, 'lxml')
    
    new_data = get_match()

    new_data['home_team'].name = team_name(formacion(soup, 1))
    new_data['away_team'].name = team_name(formacion(soup, 2))
    print(new_data['home_team'].name)
    print(new_data['away_team'].name)


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


