from collections import namedtuple

from lxml import etree

from . import nodes


Page = namedtuple(
    'Page',
    [
        'page_num',
        'title',
        'total_page',
        'floors',
    ],
    module=__name__,
)
Floor = namedtuple(
    'Floor',
    ['title', 'nodes'],
    module=__name__,
)


def dump_element(ele):
    return etree.tostring(
        ele,
        pretty_print=True,
        encoding='unicode'
    )


def parse_page(text):
    doc = etree.HTML(text)

    title = None
    for ele in doc.xpath('//h3'):
        title = ele.text

    total_page = None
    for ele in doc.xpath(
        '//div[@class="pb_footer"]//div[@class="l_thread_info"]'
        '/ul[@class="l_posts_num"]/li[@class="l_reply_num"]'
        '/span[@class="red"][2]'
    ):
        total_page = int(ele.text)

    floors = [
        parse_floor(ele)
        for ele in doc.xpath(
            '//div[contains(concat(" ", @class, " "), " d_post_content_main ")]'  # noqa
        )
    ]

    return Page(
        page_num=None,
        title=title,
        total_page=total_page,
        floors=floors,
    )


def parse_floor(ele):
    title = ' '.join([
        info_ele.text
        for info_ele in ele.xpath('.//span[@class="tail-info"]')
    ])

    return Floor(
        title=title,
        nodes=list(
            iter_node_from_floor(ele)
        ),
    )


def iter_node_from_floor(ele):
    for content_ele in ele.xpath(
        './/div[@class="d_post_content j_d_post_content "]'
    ):
        last_node = None
        for node in iter_node_from_content(content_ele):
            if node.type == nodes.NodeType.IMAGE:
                if last_node:
                    yield last_node
                    last_node = None

                yield node
            else:
                if last_node:
                    if node.type == last_node.type:
                        if node.type == nodes.NodeType.NEW_LINE:
                            # do nothing
                            pass
                        elif node.type == nodes.NodeType.TEXT:
                            last_node.text += node.text.strip()
                    else:
                        yield last_node
                        last_node = node
                else:
                    last_node = node

        if last_node and last_node.type != nodes.NodeType.NEW_LINE:
            yield last_node


def iter_node_from_content(root):
    for event, ele in etree.iterwalk(
        root,
        events=('start', 'end'),
    ):
        text = None
        if event == 'start':
            if ele.text:
                text = ele.text.strip()

            if ele.tag == 'img':
                yield nodes.ImageNode(
                    ele.get('src')
                )

            if text:
                if ele is root or ele.tag == 'a':
                    yield nodes.TextNode(text)
                elif ele.tag == 'p':
                    yield nodes.NewLineNode()
                    yield nodes.TextNode(text)
                    yield nodes.NewLineNode()
                elif ele.tag == 'img':
                    # do nothing
                    pass
                else:
                    # no possible
                    raise ValueError(
                        'unexpected tag: %s when %s with text %s' % (
                            ele.tag, event, text
                        )
                    )
        elif ele is not root:
            if ele.tail:
                text = ele.tail.strip()

            if text:
                if ele.tag == 'br':
                    yield nodes.NewLineNode()
                    yield nodes.TextNode(text)
                elif ele.tag in ('a', 'p', 'img'):
                    yield nodes.TextNode(text)
                else:
                    # no possible
                    raise ValueError(
                        'unexpected tag: %s when %s with text %s' % (
                            ele.tag, event, text
                        )
                    )
