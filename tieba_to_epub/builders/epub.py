from io import StringIO

from ebooklib import epub

from .base import Builder


class EpubBuilder(Builder):
    output_type = 'epub'

    async def run(self):

        book = epub.EpubBook()

        book.set_identifier(
            'tieba_post_%s' % self.opts.post_id
        )
        book.set_language('zh-cn')

        env = self.jinja_env
        tmpl = env.get_template('chapter.html')

        chapter_list = []
        async for page in self.iter_pages():
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
        # print(content)
        chapter = epub.EpubHtml(
            title='第 %d 页' % page.page_num,
            file_name='page_%d.html' % page.page_num,
            lang='zh-cn',
            content=content
        )

        return chapter
