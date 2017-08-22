import asyncio
import argparse

from builders import get_builder


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


async def main():
    opts = parse_args()

    b = get_builder(opts)
    await b.run()


def _main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == '__main__':
    _main()
