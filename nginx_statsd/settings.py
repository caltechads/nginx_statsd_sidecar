from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    debug: bool = False

    # --------
    # nginx
    # --------
    #: the name of the host with nginx
    nginx_host: str = 'localhost'
    #: Will we be speaking HTTPS to nginx to get to the status URL?
    nginx_is_https: bool = True
    #: The port on which nginx offers the status url
    nginx_port: int = 443
    #: The path within nginx that serves our status page
    nginx_status_path: str = '/server-status'
    #: how often (in seconds) should we report
    interval: int = 10

    # -------
    # statsd
    # -------
    #: Hostname for the statsd server
    statsd_host: str = '127.0.0.1'
    #: The UDP port for the statsd server
    statsd_port: int = 8125
    #: The prefix to use for our metrics
    statsd_prefix: str = 'nginx'

    # Sentry
    sentry_url: Optional[str] = None

    @property
    def status_url(self) -> str:
        """
        Return the full URL of the ``ngx_http_stub_status_module`` page we
        should hit on our target container.

        Returns:
            A status URL
        """
        url = f'//{self.nginx_host}:{self.nginx_port}{self.nginx_status_path}'
        if self.nginx_is_https:
            return f'https:{url}'
        return f'http:{url}'

    class Config:
        fields = {
            'debug': {'env': 'DEBUG'},
            'nginx_host': {'env': 'NGINX_HOST'},
            'nginx_is_https': {'env': 'NGINX_IS_HTTPS'},
            'nginx_port': {'env': 'NGINX_PORT'},
            'nginx_status_path': {'env': 'NGINX_STATUS_PATH'},
            'interval': {'env': 'INTERVAL'},
            'statsd_host': {'env': 'STATSD_HOST'},
            'statsd_port': {'env': 'STATSD_PORT'},
            'statsd_prefix': {'env': 'STATSD_PREFIX'},
        }
