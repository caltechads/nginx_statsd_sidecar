from dataclasses import dataclass, asdict
import asyncio

import aiodogstatsd
from aiodogstatsd.compat import get_event_loop
import httpx

from .logging import logger
from .settings import Settings


@dataclass
class NginxStats:

    #: This will be ``True`` if we actually retreived stats
    retrieved: bool = False
    #: How many active connections does nginx currently have
    active_connections: int = 0
    #: The current request counter.  This is a running total of requests
    #: served by nginx since it started.
    requests: int = 0
    #: How many of our connections are currently in reading state
    reading: int = 0
    #: How many of our connections are currently in writing state
    writing: int = 0
    #: How many of our connections are currently in waiting state
    waiting: int = 0


class NginxStatusScraper:
    """
    This class is hits the URL named by
    :py:class:`nginx_statsd.settings.Settings.status_url` and extracts the
    relevant data from it, returning it to the caller as an :py:class:`NginxStatus`
    object.

    Args:
        status_url: the URL for the `ngx_http_stub_status_module` output page on
            our nginx server
    """

    def __init__(self, status_url: str) -> None:
        self.status_url: str = status_url
        logger.info('scraper.init url=%s', self.status_url)

    async def get_status_page(self) -> str:
        """
        Return the status data from our target nginx status page.  This will
        look like:

        .. code::

            Active connections: 291
            server accepts handled requests
            16630948 16630948 31070465
            Reading: 6 Writing: 179 Waiting: 106

        Returns:
            The text from the status page.
        """
        async with httpx.AsyncClient(http2=True, verify=False) as client:
            try:
                response = await client.get(self.status_url)
                response.raise_for_status()
            except httpx.ConnectError as e:
                logger.warning(
                    'scraper.get_status_page.connecterror url=%s err=%s',
                    e.request.url,
                    str(e)
                )
                return ''
            except httpx.HTTPStatusError as e:
                logger.warning(
                    'scraper.get_status_page.bad_status url=%s err=%s',
                    e.request.url,
                    e.response.status_code
                )
                return ''
        return response.text

    async def get_stats(self) -> NginxStats:
        """
        Retrieve the nginx status page data and parse it into a
        :py:class:`NginxStatus` object.

        If we successfully retrieved the data, the status object we return will
        have its :py:attr:`NginxStatus.retrieved` flag set to ``True``.  Thus
        if you check the :py:attr:`NginxStatus.retrieved` flag and it is ``False``,
        you'll know we couldn't retrieve the status page and the data can be
        ignored.

        Returns:
            The parsed data from our status page.
        """
        data = NginxStats()
        html = await self.get_status_page()
        if not html:
            return data
        data.retrieved = True
        lines = html.split('\n')
        data.active_connections = int(lines[0].split(':')[1].strip())
        data.requests = int(lines[2].strip().split()[2])
        items = lines[3].split()
        data.reading = int(items[1])
        data.writing = int(items[3])
        data.waiting = int(items[5])
        return data


class StatsdReporter:

    def __init__(
        self,
        scraper: NginxStatusScraper,
        settings: Settings
    ) -> None:
        self.scraper = scraper
        self.settings = settings
        #: The request count for the last status object retrieved
        self.last_request_count: int = -1

    async def report(self) -> None:
        stats = await self.scraper.get_stats()
        if not stats.retrieved:
            logger.error('reporter.failed.no-stats-retrieved')
            return
        if self.last_request_count == -1 or stats.requests < self.last_request_count:
            # Either this is our first iteration (last_request_count is -1), or
            # nginx rebooted (current request count is less than our last
            # request count) so just save our current counter and don't report
            # for this iteration
            self.last_request_count = stats.requests
            logger.error('reporter.reset last_request_count=%d', self.last_request_count)
            return
        async with aiodogstatsd.Client(
            host=self.settings.statsd_host,
            port=self.settings.statsd_port,
            namespace=self.settings.statsd_prefix
        ) as statsd:
            # We only want to send the diff between last sample and this sample
            statsd.increment('requests', value=stats.requests - self.last_request_count)
            self.last_request_count = stats.requests
            statsd.increment('active_connections', value=stats.active_connections)
            statsd.increment('workers.reading', value=stats.reading)
            statsd.increment('workers.writing', value=stats.writing)
            statsd.increment('workers.waiting', value=stats.waiting)
        logger.info('reporter.success', extra=asdict(stats))


class NginxMonitor:
    """
    This is the main monitoring task.  We run in an eternal loop, reporting our
    nginx stats to statsd every
    :py:class:`nginx_statsd.settings.Settings.interval` seconds.
    """

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self.scraper = NginxStatusScraper(settings.status_url)
        self.settings = settings
        self.reporter = StatsdReporter(self.scraper, settings)
        self.interval = settings.interval

    async def run(self) -> None:
        loop = get_event_loop()
        logger.info(
            'monitor.start',
            extra={
                'interval': self.interval,
                'prefix': self.settings.statsd_prefix
            }
        )
        sleep_time = self.interval
        while loop.is_running():
            start = loop.time()
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.reporter.report(), name='reporter')
                tg.create_task(asyncio.sleep(sleep_time), name='sleep')
            # Get our current lag
            time_slept = loop.time() - start
            lag = time_slept - self.interval
            sleep_time = self.interval - lag
