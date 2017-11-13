from io import StringIO

from ebooklib import epub

from .base import Builder
from ..nodes import NodeType, ImageNode


class EpubBuilder(Builder):
    output_type = 'epub'

    async def run(self):

        book = epub.EpubBook()

        book.set_identifier(
            'tieba_post_%s' % self.opts.post_id
        )
        book.set_language('zh-cn')

        # remove duplicate file
        book._images = {}

        env = self.jinja_env
        tmpl = env.get_template('chapter.html')

        chapter_list = []
        async for page in self.iter_pages():
            page = await self._trans_page(page, book)

            chapter = await self._make_chapter(page, tmpl)

            book.add_item(chapter)
            chapter_list.append(chapter)

        book.set_title(self.title)

        book.toc = (
            (
                epub.Section('Languages'),
                chapter_list,
            ),
        )
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = chapter_list

        epub.write_epub(
            self.opts.output,
            book,
            {}
        )

    async def _make_chapter(self, page, tmpl):
        buffer = StringIO()

        async for fragment in tmpl.generate_async(page=page):
            buffer.write(fragment)

        content = buffer.getvalue()
        chapter = epub.EpubHtml(
            title='第 %d 页' % page.page_num,
            file_name='page_%d.html' % page.page_num,
            lang='zh-cn',
            content=content
        )

        return chapter

    async def _trans_page(self, page, book):
        return page._replace(
            floors=[
                await self._trans_floor(f, book)
                for f in page.floors
            ]
        )

    async def _trans_floor(self, floor, book):
        return floor._replace(
            nodes=[
                await self._trans_node(n, book)
                for n in floor.nodes
            ]
        )

    async def _trans_node(self, node, book):
        if node.type != NodeType.IMAGE:
            return node

        if node.name not in book._images:
            item = epub.EpubItem(
                file_name=node.name,
                content=node.content,
            )
            book._images[node.name] = item
            book.add_item(item)

        return ImageNode(
            url=node.name,
        )
