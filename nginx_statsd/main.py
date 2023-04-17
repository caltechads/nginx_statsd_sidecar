"""
This file is used as the entrypoint for the command line interface.
"""

# Use uvloop as our event loop
# https://uvloop.readthedocs.io/user/index.html
import asyncio
import uvloop


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main() -> None:
    from .cli import cli
    cli(obj={})  # pylint: disable=no-value-for-parameter


if __name__ == '__main__':
    main()
