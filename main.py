import asyncio
import argparse
from io import StringIO

import aiohttp
import markdown
from lxml import etree
from ebooklib import epub

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'


def parse_args():
    parser = argparse.ArgumentParser(
        description='fetch tieba post and convert to epub.'
    )

    parser.add_argument(
        'post_id',
        metavar='id',
        type=int,
        help='post id'
    )
    parser.add_argument(
        'output',
        metavar='file',
        type=str,
        help='output file name'
    )
    parser.add_argument(
        '--see-lz',
        action='store_const',
        const=True,
        default=False,
        help='see louzhu (default: false)'
    )

    args = parser.parse_args()
    return args


class Builder:
    def __init__(self, session, opts):
        self.session = session
        self.opts = opts

        self.total_page = 1
        self.title = None

        self.book = epub.EpubBook()
        self.chapter_list = []

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

        while page <= self.total_page:
            await self.get_page(path, params, page)

            page += 1

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

    async def get_page(self, path, params, page):
        headers = {
            'User-Agent': USER_AGENT,
        }

        if page > 1:
            params['pn'] = page

        f = StringIO()

        page_title = '第 %d 页' % page
        f.write('# %s\n\n' % page_title)

        async with self.session.get(path, params=params, headers=headers) as resp:
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

            for ele in doc.xpath('//div[@class="pb_footer"]//div[@class="l_thread_info"]/ul[@class="l_posts_num"]/li[@class="l_reply_num"]/span[@class="red"][2]'):
                print(ele.text)
                self.total_page = int(ele.text)

            for ele in doc.xpath('//div[contains(concat(" ", @class, " "), " d_post_content_main ")]'):
                f.write("## %s\n\n" % ' '.join([
                    info_ele.text
                    for info_ele in ele.xpath('.//span[@class="tail-info"]')
                ]))

                for content_ele in ele.xpath('.//div[contains(concat(" ", @class, " "), " d_post_content ")]'):
                    for text in content_ele.itertext():
                        f.write(text.strip() + '\n\n')

        content = f.getvalue()
        html = markdown.markdown(content)

        chapter = epub.EpubHtml(
            title=page_title,
            file_name='page_%d.xhtml' % page,
            lang='zh-cn',
        )
        chapter.content = html
        self.book.add_item(chapter)
        self.chapter_list.append(chapter)


async def main():
    opts = parse_args()

    async with aiohttp.ClientSession() as session:
        b = Builder(session, opts)
        await b.run()


def _main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    _main()
