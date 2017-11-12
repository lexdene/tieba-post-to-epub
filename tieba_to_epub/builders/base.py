import aiohttp
from jinja2 import Environment, PackageLoader, select_autoescape

from ..parsers import parse_page

USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) '
    'AppleWebKit/537.36 (KHTML, like Gecko)'
    'Chrome/60.0.3112.78 Safari/537.36'
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

                break

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

            page = parse_page(text, page_num)

            if self.title is None and page.title:
                self.title = page.title

            if self.total_page is None and page.total_page:
                self.total_page = page.total_page

            return page

    @property
    def jinja_env(self):
        return Environment(
            loader=PackageLoader('tieba_to_epub', 'templates'),
            autoescape=select_autoescape(['xml', 'html']),
            enable_async=True,
        )
