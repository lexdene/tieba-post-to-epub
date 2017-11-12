from collections import namedtuple

from lxml import etree

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
    ['title', 'texts'],
    module=__name__,
)


def dump_element(ele):
    return etree.tostring(
        ele,
        pretty_print=True,
        encoding='unicode'
    )


def parse_page(text, page_num):
    doc = etree.HTML(text)

    title = None
    for ele in doc.xpath('//h3'):
        print(ele.text)
        title = ele.text

    total_page = None
    for ele in doc.xpath(
        '//div[@class="pb_footer"]//div[@class="l_thread_info"]'
        '/ul[@class="l_posts_num"]/li[@class="l_reply_num"]'
        '/span[@class="red"][2]'
    ):
        print(ele.text)
        total_page = int(ele.text)

    floors = [
        parse_floor(ele)
        for ele in doc.xpath(
            '//div[contains(concat(" ", @class, " "), " d_post_content_main ")]'  # noqa
        )
    ]

    return Page(
        page_num=page_num,
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
        texts=list(
            iter_text_from_floor(ele)
        ),
    )


def iter_text_from_floor(ele):
    for content_ele in ele.xpath(
        './/div[@class="d_post_content j_d_post_content "]'
    ):
        for text in iter_text_from_content(content_ele):
            text = text.strip()

            if text:
                yield text


def iter_text_from_content(root):
    text = ''

    stop = False

    for event, ele in etree.iterwalk(
        root,
        events=('start', 'end'),
    ):
        take = None
        if event == 'start':
            if ele.text:
                take = ele.text.strip()

            if take:
                if ele is root or ele.tag == 'a':
                    # append but dont yield
                    text += take
                elif ele.tag == 'p':
                    # yield and yield and clean
                    if text:
                        yield text

                    yield take

                    text = ''
                else:
                    # no possible
                    print(event, ele, ele.tag)
                    stop = True
        elif ele is not root:
            if ele.tail:
                take = ele.tail.strip()

            if take:
                if ele.tag == 'br':
                    # yield and then append
                    if text:
                        yield text

                    text = take
                elif ele.tag in ('a', 'p', 'img'):
                    # append but dont yield
                    text += take
                else:
                    # no possible
                    print(event, ele, ele.tag)
                    stop = True

    if text:
        yield text

    if stop:
        raise ValueError('unexpected')
