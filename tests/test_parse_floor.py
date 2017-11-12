from unittest import TestCase

from lxml import etree

from tieba_to_epub.parsers import parse_floor


class TestParseFloor(TestCase):
    def test_simple_floor(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)

        self.assertEqual(
            floor.texts,
            ['asdf']
        )

    def test_floor_with_a_tag(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <a href="#">bcde</a>
              xyz
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)

        self.assertEqual(
            floor.texts,
            ['asdfbcdexyz']
        )

    def test_floor_with_p_tag(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <p>bcde</p>
              xyz
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)

        self.assertEqual(
            floor.texts,
            ['asdf', 'bcde', 'xyz']
        )

    def test_floor_with_img_tag(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <img src="bcde"/>
              xyz
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)

        self.assertEqual(
            floor.texts,
            ['asdfxyz']
        )
