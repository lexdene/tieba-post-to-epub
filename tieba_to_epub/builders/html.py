from .base import Builder


class HtmlBuilder(Builder):
    output_type = 'html'

    async def run(self):
        pages = [
            page
            async for page in self.iter_pages()
        ]

        env = self.jinja_env
        tmpl = env.get_template('template.html')
        context = {
            'title': self.title,
            'pages': pages,
        }

        with open(self.opts.output, 'w') as f:
            async for fragment in tmpl.generate_async(**context):
                f.write(fragment)
