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

class TestPicsFunctions(unittest.TestCase):
    ''' Test all pics functions '''
    def test_pic_correct_extension(self):
        pic_name = 'coucoute.png'
        correct_pic_name = recup_img.pic_correct_name(pic_name)
        self.assertEqual(correct_pic_name, pic_name)
    def test_correct_pic_name(self):
        pic_name = "71757710_481082935825164_7112786787258754684_n.jpg?_nc_ht=scontent-cdt1-1.cdninstagram.com&_nc_cat=100&oh=b8c5fe9f96fc1f5eed3038e77ebb4b80&oe=5E78CAD7"
        correct_pic_name = recup_img.pic_correct_name(pic_name)
        self.assertEqual(correct_pic_name, "71757710_481082935825164_7112786787258754684_n.jpg")
    def test_boolean_return_to_pic_extension(self):
        pic_name = 'picture.GiF'
        is_a_pic = recup_img.valide_extension(pic_name)
        self.assertTrue(is_a_pic)
    def test_boolean_return_to_nonpic_extension(self):
        pic_name = 'virus.exe'
        is_a_pic = not recup_img.valide_extension(pic_name)
        self.assertTrue(is_a_pic)
    def test_simple_number_pic(self):
        pic_name = '5.jpeg'
        correct_pic_name = recup_img.numerotation_image(pic_name)
        self.assertEqual(correct_pic_name, '05.jpeg')

if __name__ == '__main__':
    unittest.main()
