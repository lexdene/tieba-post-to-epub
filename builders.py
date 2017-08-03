import os
from collections import namedtuple

import aiohttp
from lxml import etree
# from ebooklib import epub


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'


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
        self.book.set_identifier(
            'tieba_post_%s' % self.opts.post_id
        )
        self.book.set_language('zh-cn')

        path = 'https://tieba.baidu.com/p/{post_id}'.format(
            post_id=self.opts.post_id
        )

        params = {}
        if self.opts.see_lz:
            params['see_lz'] = '1'

        page = 1

        while self.total_page is None or page <= self.total_page:
            await self.get_page(path, params, page)
            break

            page += 1

        return

        self.book.set_title(self.title)

        self.book.toc = (
            (
                epub.Section('Languages'),
                self.chapter_list,
            ),
        )
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        self.book.spine = self.chapter_list

        epub.write_epub(
            self.opts.output,
            self.book,
            {}
        )

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
                for ele in doc.xpath('//div[@class="pb_footer"]//div[@class="l_thread_info"]/ul[@class="l_posts_num"]/li[@class="l_reply_num"]/span[@class="red"][2]'):
                    print(ele.text)
                    self.total_page = int(ele.text)

            floors = [
                self._get_floor_by_ele(ele)
                for ele in doc.xpath('//div[contains(concat(" ", @class, " "), " d_post_content_main ")]')
            ]


        return Page(
            page_num=page_num,
            floors=floors,
        )

    def _get_floor_by_ele(self, ele):
        texts = []

        title = ' '.join([
            info_ele.text
            for info_ele in ele.xpath('.//span[@class="tail-info"]')
        ])


        for content_ele in ele.xpath('.//div[contains(concat(" ", @class, " "), " d_post_content ")]'):
            texts.extend([
                text.strip()
                for text in content_ele.itertext()
            ])

        return Floor(
            title=title,
            texts=texts
        )

    @classmethod
    def create(cls, opts):
        _, ext = os.path.splitext(opts.output)
        ext = ext.lstrip('.')
        print('ext:', ext)

        for value in globals().values():
            if isinstance(value, type) and \
                    issubclass(value, cls) and \
                    value.output_type == ext:
                return value(opts)


class HtmlBuilder(Builder):
    output_type = 'html'

    async def run(self):
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        pages = [
            page
            async for page in self.iter_pages()
        ]

        env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['xml', 'html']),
            enable_async=True,
        )
        tmpl = env.get_template('template.html')
        context = {
            'title': self.title,
            'pages': pages,
        }

        with open(self.opts.output, 'w') as f:
            async for fragment in tmpl.generate_async(**context):
                f.write(fragment)
                
