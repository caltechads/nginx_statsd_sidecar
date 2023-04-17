import asyncio
import pprint

from ..settings import Settings

from .cli import cli
from ..app import NginxStatusScraper, NginxMonitor


@cli.command('settings', short_help="Print our application settings.")
def settings():
    """
    Print our settings to stdout.  This should be the completely evaluated settings including
    those imported from any environment variable.
    """
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(Settings().dict())


@cli.command('stats', short_help="Print current stats from our nginx server")
def stats():
    scraper = NginxStatusScraper(Settings().status_url)
    print(asyncio.run(scraper.get_stats()))


@cli.command('run', short_help="Run the monitor process")
def run():
    asyncio.run(NginxMonitor(Settings()).run())
