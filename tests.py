from unittest import TestCase, main
from unittest.mock import MagicMock
import scrapper
import copy
from bs4 import BeautifulSoup
from json import dumps

class ScrapperTests(TestCase):

    def setUp(self):
        with open('test.html', 'r') as f:
            self.html = f.read()
        self.soup = BeautifulSoup(self.html, 'lxml')
        self.data = dict()
        self.data['home_team'] = dict()
        self.data['home_team']['team_name'] = 'Velez'
        self.data['home_team']['goals'] = "70' L. Robertone; "
        self.data['home_team']['yellow_cards'] = "12' L. Robertone; 62' F. Cubero; 89' J. Mendez; "
        self.data['home_team']['red_cards'] = ""
        self.data['home_team']['subs'] = "53' J. Mendez ⇆ N. Dominguez (Lesion); 74' R. Caseres ⇆ L. Robertone; 91' M. Torsiglieri ⇆ A. Bouzat; "
        self.data['away_team'] = dict()
        self.data['away_team']['team_name'] = 'River Plate'
        self.data['away_team']['goals'] = ""
        self.data['away_team']['yellow_cards'] = "12' B. Zuculini; 23' I. Scocco; 52' E. Perez; 56' N.D.La Cruz; 85' R. Mora; "
        self.data['away_team']['red_cards'] = "65' E. Perez; "
        self.data['away_team']['subs'] = "45' L. Ponzio ⇆ B. Zuculini; 53' R. Mora ⇆ I. Scocco; 73' J. Quintero ⇆ E. Palacios; "
        self.maxDiff = None

    def test_file_is_loading(self):
        self.assertIsInstance(self.soup, BeautifulSoup)

    def test_team_name_should_be_Velez(self):
        self.assertEqual(
            'Velez',
            scrapper.team_name(scrapper.formacion(self.soup, 1))
        )

    def test_translation_works(self):
        self.assertEqual(
            ['goals', 'yellow_cards', 'red_cards', 'subs'],
            [scrapper.translate(x) for x in ['goles', 'amarillas', 'rojas', 'cambios']]
        )

    def test_incidencia_works(self):
        formacion = scrapper.formacion(self.soup, 2)
        self.assertEqual(
            "45' L. Ponzio ⇆ B. Zuculini; 53' R. Mora ⇆ I. Scocco; 73' J. Quintero ⇆ E. Palacios; ",
            scrapper.incidencia(formacion, 'cambios')
        )

    def test_match_data_as_string_works(self):
        self.assertEqual(
            self.data,
            scrapper.match_data_as_string(self.soup)
        )

    def test_changes_as_string(self):
        old_data = copy.deepcopy(self.data)
        old_data['home_team']['yellow_cards'] = ""
        self.assertNotEqual(
            old_data,
            scrapper.changes_as_string(old_data, self.soup)
        )
        

if __name__ == '__main__':
    main()