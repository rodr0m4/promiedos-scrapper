from unittest import TestCase
from unittest.mock import MagicMock
import scrapper
from bs4 import BeautifulSoup


class ScrapperTests(TestCase):

    def setUp(self):
        self.soup = BeautifulSoup(
        """
        <html>
            <head>
            </head>
            <body>
                <table id="formacion1">
                
                </table>
                <table id="formacion2">I'm formation 2</table>
            <body>
        </html>
        """, 'lxml')
    
    def formation2_should_be_found(self):
        self.assertEqual(
            'I\'m formation 2',
            scrapper.formacion(self.soup, 2).string
        )

    def name_should_be_independiente(self):
        scrapper.formacion = MagicMock(
                return_value = """
                <table id="formacion1">
                    <tbody>
                        <tr>
                             <td class="nomequipo">Independiente</td>
                        </tr>
                    </tbody>
                </table>
                """
        )
        self.assertEqual(
            'Independiente',
            scrapper.team_name(scrapper.formacion())
        )