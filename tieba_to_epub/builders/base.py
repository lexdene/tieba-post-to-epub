import os
import urllib

import aiohttp
from jinja2 import Environment, PackageLoader, select_autoescape

from ..parsers import parse_page
from ..nodes import NodeType

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

        async with aiohttp.ClientSession() as session:
            if self.opts.page_num is None:
                page_num = 1

                while self.total_page is None or page_num <= self.total_page:
                    page = await self.get_page(session, path, params, page_num)
                    yield page

                    page_num += 1
            else:
                page = await self.get_page(
                    session, path, params, self.opts.page_num
                )
                yield page

    async def get_page(self, session, path, params, page_num):
        headers = {
            'User-Agent': USER_AGENT,
        }

        if page_num > 1:
            params['pn'] = page_num

        async with session.get(path, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise ValueError(
                    'status code error: %d. url: %s' % (
                        resp.status,
                        resp.url
                    )
                )

            text = await resp.text()

        page = parse_page(text)
        page = page._replace(page_num=page_num)

        for floor in page.floors:
            for node in floor.nodes:
                if node.type == NodeType.IMAGE:
                    await _trans_image_node(
                        node,
                        session,
                    )

        if self.title is None and page.title:
            self.title = page.title

        if self.total_page is None and page.total_page:
            self.total_page = page.total_page

        return page

    @property
    def jinja_env(self):
        package_name = __name__.split('.')[0]

        return Environment(
            loader=PackageLoader(package_name, 'templates'),
            autoescape=select_autoescape(['xml', 'html']),
            enable_async=True,
        )


async def _trans_image_node(node, session):
    url = node.url
    r = urllib.parse.urlparse(url)
    node.name = os.path.basename(r.path)

    async with session.get(url, headers={'User-Agent': USER_AGENT}) as resp:
        if resp.status != 200:
            raise ValueError(
                'status code error: %d. url: %s' % (
                    resp.status,
                    resp.url
                )
            )

        node.content = await resp.read()
