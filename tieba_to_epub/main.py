import asyncio
import argparse

from .builders import get_builder


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
    parser.add_argument(
        '--page-num',
        metavar='N',
        type=int,
        help='fetch only one page (default: fetch all pages)',
    )

    args = parser.parse_args()
    return args


async def _main():
    opts = parse_args()

    b = get_builder(opts)
    await b.run()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main())
