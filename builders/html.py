from .base import Builder


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
