import unittest
import recup_img

class TestUrlFunctions(unittest.TestCase):
    ''' Test all url functions '''
    def test_correct_point_position(self):
        ''' check the correct point position '''
        point_position = recup_img.point_position("image2.jpeg")
        self.assertEqual(point_position, 6)
    def test_no_last_slash_position(self):
        ''' check when there is no /'''
        last_slash_position = recup_img.last_slash_position('toto')
        self.assertEqual(last_slash_position, -1)
    def test_last_slash_position(self):
        ''' check the correct position'''
        last_slash_position = recup_img.last_slash_position('http://')
        self.assertEqual(last_slash_position, 6)
    def test_complicated_last_slash_position(self):
        ''' check the correct position'''
        last_slash_position = recup_img.last_slash_position('http://azerty')
        self.assertEqual(last_slash_position, 6)
    def test_racine_du_site_with_http(self):
        ''' check the correct root '''
        url="http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-2/"
        racine_du_site = recup_img.racine_du_site(url)
        self.assertEqual(racine_du_site, 'http://sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-2/')
    def test_racine_du_site_without_http_and_lastslash(self):
        ''' check the correct root '''
        url="sametmax.com/un-gros-guide-bien-gras-sur-les-tests-unitaires-en-python-partie-2"
        racine_du_site = recup_img.racine_du_site(url)
        self.assertEqual(racine_du_site, 'sametmax.com/')
    def test_racine_du_site_without_http_and_slash(self):
        ''' check the correct root '''
        url="sametmax.com"
        racine_du_site = recup_img.racine_du_site(url)
        self.assertEqual(racine_du_site, 'sametmax.com')

if __name__ == '__main__':
    unittest.main()
