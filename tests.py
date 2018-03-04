from unittest import TestCase, main
from unittest.mock import MagicMock
import requests
from bs4 import BeautifulSoup
from json import dumps
import scrapper
import copy

class ScrapperTests(TestCase):

    def setUp(self):
        with open('test-before.html', 'r') as f:
            self.html = f.read()
        self.soup_before = BeautifulSoup(self.html, 'lxml')
        with open('test-after.html', 'r') as f:
            self.html = f.read()
        self.soup_after = BeautifulSoup(self.html, 'lxml')
        self.maxDiff = None

    def test_team_name_should_be_Velez(self):
        self.assertEqual(
            'Velez',
            scrapper.team_name(scrapper.formacion(self.soup_before, 1))
        )

    def test_translation_works(self):
        self.assertEqual(
            ['goals', 'yellow_cards', 'red_cards', 'subs'],
            [scrapper.translate(x) for x in ['goles', 'amarillas', 'rojas', 'cambios']]
        )

    def test_incidencia_works(self):
        formacion = scrapper.formacion(self.soup_after, 2)
        self.assertEqual(
            "45' L. Ponzio ⇆ B. Zuculini; 53' R. Mora ⇆ I. Scocco; 73' J. Quintero ⇆ E. Palacios; ",
            scrapper.incidencia(formacion, 'cambios')
        )

    def test_match_data_as_string_works(self):
        data = dict()
        data['home_team'] = dict()
        data['home_team']['team_name'] = 'Velez'
        data['home_team']['goals'] = "70' L. Robertone; "
        data['home_team']['yellow_cards'] = "12' L. Robertone; 62' F. Cubero; 89' J. Mendez; "
        data['home_team']['red_cards'] = ""
        data['home_team']['subs'] = "53' J. Mendez ⇆ N. Dominguez (Lesion); 74' R. Caseres ⇆ L. Robertone; 91' M. Torsiglieri ⇆ A. Bouzat; "
        data['away_team'] = dict()
        data['away_team']['team_name'] = 'River Plate'
        data['away_team']['goals'] = ""
        data['away_team']['yellow_cards'] = "12' B. Zuculini; 23' I. Scocco; 52' E. Perez; 56' N.D.La Cruz; 85' R. Mora; "
        data['away_team']['red_cards'] = "65' E. Perez; "
        data['away_team']['subs'] = "45' L. Ponzio ⇆ B. Zuculini; 53' R. Mora ⇆ I. Scocco; 73' J. Quintero ⇆ E. Palacios; "
        self.assertEqual(
            data,
            scrapper.match_data_as_string(self.soup_after)
        )

    def test_changes_as_string(self):
        old_data = scrapper.match_data_as_string(self.soup_before)
        self.assertNotEqual(
            old_data,
            scrapper.changes_as_string(old_data, self.soup_after)
        )

    def test_prepare_message_makes_valid_json_with_yellow(self):
        data = "45' L. Ponzio; "
        message = scrapper.prepare_message('River Plate', 'yellow_cards', data)
        self.assertEqual(
            '{"event_type": "YELLOW_CARD", "team": "River Plate", "minute": 45, "player": "L. Ponzio"}',
            message
        )

    def test_prepare_message_makes_valid_json_with_red(self):
        data = "45' L. Ponzio; "
        message = scrapper.prepare_message('River Plate', 'red_cards', data)
        self.assertEqual(
            '{"event_type": "RED_CARD", "team": "River Plate", "minute": 45, "player": "L. Ponzio"}',
            message
        )
    
    def test_prepare_message_makes_valid_json_with_goal(self):
        data = "45' L. Ponzio; "
        message = scrapper.prepare_message('River Plate', 'goals', data)
        self.assertEqual(
            '{"event_type": "GOAL", "team": "River Plate", "minute": 45, "player": "L. Ponzio"}',
            message
        )

    def test_prepare_message_makes_valid_json_with_sub(self):
        data = "45' L. Ponzio ⇆ B. Zuculini; "
        message = scrapper.prepare_message('River Plate', 'subs', data)
        self.assertEqual(
            '{"event_type": "SUB", "team": "River Plate", "minute": 45, "player_in": "L. Ponzio", "player_out": "B. Zuculini"}',
            message
        )

    def test_before_after_with_change(self):
        old_data = scrapper.match_data_as_string(self.soup_before)
        (new_data, events) = scrapper.changes_as_string(old_data, self.soup_after)
        self.assertEqual(
            '{"event_type": "SUB", "team": "River Plate", "minute": 73, "player_in": "J. Quintero", "player_out": "E. Palacios"}',
            events[0]
        )


if __name__ == '__main__':
    main()