from collections import namedtuple

import aiohttp
from lxml import etree


USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
    'AppleWebKit/537.36 (KHTML, like Gecko)'
    'Chrome/60.0.3112.78 Safari/537.36'
)


Page = namedtuple(
    'Page',
    ['page_num', 'floors'],
    module=__name__,
)
Floor = namedtuple(
    'Floor',
    ['title', 'texts'],
    module=__name__,
)


class Builder:
    output_type = None

    def __init__(self, opts):
        self.opts = opts

        self.total_page = None
        self.title = None

    async def run(self):
        raise NotImplemented

    async def iter_pages(self):
        path = 'https://tieba.baidu.com/p/{post_id}'.format(
            post_id=self.opts.post_id
        )

        params = {}
        if self.opts.see_lz:
            params['see_lz'] = '1'

        page_num = 1

        async with aiohttp.ClientSession() as session:
            while self.total_page is None or page_num <= self.total_page:
                page = await self.get_page(session, path, params, page_num)
                yield page

                page_num += 1

    async def get_page(self, session, path, params, page_num):
        headers = {
            'User-Agent': USER_AGENT,
        }

        if page_num > 1:
            params['pn'] = page_num

        async with session.get(path, params=params, headers=headers) as resp:
            print('url:', resp.url)
            print('status: %d' % resp.status)
            if resp.status != 200:
                raise ValueError(
                    'status code error: %d' % resp.status
                )

            text = await resp.text()

            doc = etree.HTML(text)

            if self.title is None:
                for ele in doc.xpath('//h3'):
                    print(ele.text)
                    self.title = ele.text

            if self.total_page is None:
                for ele in doc.xpath(
                    '//div[@class="pb_footer"]//div[@class="l_thread_info"]'
                    '/ul[@class="l_posts_num"]/li[@class="l_reply_num"]'
                    '/span[@class="red"][2]'
                ):
                    print(ele.text)
                    self.total_page = int(ele.text)

            floors = [
                self._get_floor_by_ele(ele)
                for ele in doc.xpath(
                    '//div[contains(concat(" ", @class, " "), " d_post_content_main ")]'  # noqa
                )
            ]

        return Page(
            page_num=page_num,
            floors=floors,
        )

    def _get_floor_by_ele(self, ele):
        title = ' '.join([
            info_ele.text
            for info_ele in ele.xpath('.//span[@class="tail-info"]')
        ])

        texts = []

        for content_ele in ele.xpath(
            './/div[@class="d_post_content j_d_post_content "]'
        ):
            texts = [
                text.strip()
                for text in get_text_iter_from_ele(content_ele)
            ]

        return Floor(
            title=title,
            texts=texts
        )


def get_text_iter_from_ele(root):
    print('=' * 50)

    text = ''

    stop = False
    print_html = False

    for event, ele in etree.iterwalk(
        root,
        events=('start', 'end'),
    ):
        if ele.tag == 'a':
            print_html = True

            if event == 'start':
                print('=' * 20)
                print(ele.text)

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

    if print_html:
        print(etree.tostring(root, encoding='unicode', pretty_print=True))

    if stop:
        print(etree.tostring(root, encoding='unicode', pretty_print=True))
        raise ValueError(1)
