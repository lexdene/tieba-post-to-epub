import os

from .base import Builder
from .html import HtmlBuilder
from .epub import EpubBuilder

__all__ = [
    'get_builder',
    'HtmlBuilder', 'EpubBuilder',
]


def get_builder(opts):
    _, ext = os.path.splitext(opts.output)
    ext = ext.lstrip('.')

    for value in globals().values():
        if isinstance(value, type) and \
                issubclass(value, Builder) and \
                value.output_type == ext:
            return value(opts)
