from unittest import TestCase

from lxml import etree

from tieba_to_epub.nodes import NodeType
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

        self.assertEqual(1, len(floor.nodes))
        self.assertEqual(NodeType.TEXT, floor.nodes[0].type)
        self.assertEqual('asdf', floor.nodes[0].text)

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

        self.assertEqual(1, len(floor.nodes))
        self.assertEqual(NodeType.TEXT, floor.nodes[0].type)
        self.assertEqual('asdfbcdexyz', floor.nodes[0].text)

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
        nodes = floor.nodes

        self.assertEqual(5, len(nodes))

        # index 0
        self.assertEqual(NodeType.TEXT, nodes[0].type)
        self.assertEqual('asdf', nodes[0].text)

        # index 1
        self.assertEqual(NodeType.NEW_LINE, nodes[1].type)

        # index 2
        self.assertEqual(NodeType.TEXT, nodes[2].type)
        self.assertEqual('bcde', nodes[2].text)

        # index 3
        self.assertEqual(NodeType.NEW_LINE, nodes[3].type)

        # index 4
        self.assertEqual(NodeType.TEXT, nodes[4].type)
        self.assertEqual('xyz', nodes[4].text)

    def test_floor_with_p_tag_as_last(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <p>bcde</p>
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)
        nodes = floor.nodes

        self.assertEqual(3, len(nodes))

        # index 0
        self.assertEqual(NodeType.TEXT, nodes[0].type)
        self.assertEqual('asdf', nodes[0].text)

        # index 1
        self.assertEqual(NodeType.NEW_LINE, nodes[1].type)

        # index 2
        self.assertEqual(NodeType.TEXT, nodes[2].type)
        self.assertEqual('bcde', nodes[2].text)

    def test_floor_with_img_tag(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <img src="bcde" />
              xyz
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)
        nodes = floor.nodes

        self.assertEqual(1, len(nodes))
        self.assertEqual('asdfxyz', nodes[0].text)

    def test_floor_with_br_tag(self):
        source = '''
          <div class="p_content">
            <div class="d_post_content j_d_post_content ">
              asdf
              <br />
              bcde
            </div>
          </div>
        '''

        ele = etree.HTML(source)
        floor = parse_floor(ele)
        nodes = floor.nodes

        self.assertEqual(3, len(nodes))

        # index 0
        self.assertEqual(NodeType.TEXT, nodes[0].type)
        self.assertEqual('asdf', nodes[0].text)

        # index 1
        self.assertEqual(NodeType.NEW_LINE, nodes[1].type)

        # index 2
        self.assertEqual(NodeType.TEXT, nodes[2].type)
        self.assertEqual('bcde', nodes[2].text)
