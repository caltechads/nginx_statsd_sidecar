Configuration
=============

This guide covers all configuration options for ``nginx_statsd_sidecar``, including
its environment variables, and how to configure ``nginx`` to expose the stats.

nginx configuration
-------------------

First, check that ``nginx`` has been compiled with the ``ngx_http_stub_status_module`` module;
it usually is.

.. code-block:: bash

    $ nginx -V 2>&1 | grep -q "with-http_stub_status_module"
    $ if [ $? -ne 0 ]; then
        echo "nginx must be compiled with the ngx_http_stub_status_module module"
        exit 1
    fi

Then in your ``server`` block, you need to add a location block that exposes the stats.

.. code-block:: nginx

    # nginx stats location
    location = /server-status {
      stub_status;
      allow 127.0.0.1;
      allow ::1;
      deny all;
    }


Set the ``allow`` and ``deny`` directives to allow access to the requests
from the ``nginx_statsd_sidecar`` container.  For ECS, this will be 127.0.0.1,
and the IPv6 equivalent ``::1`` since the container runs on the same host as your application.

If you're testing locally with Docker Desktop, you'll need to set the
``allow`` and ``deny`` directives to the network CIDR block for the Docker
Desktop NAT network.  This is usually ``192.168.0.0/24``.  To find your CIDR
range with ``docker``, in the same folder as your ``docker-compose.yml`` file, run:

.. code-block:: bash

    $ docker network inspect bridge | grep 'Subnet'

Allow that subnet CIDR block in addition to the 127.0.0.1 and ::1, and deny
all other access.

For all other cases, you'll need to set the ``allow`` and ``deny`` directives
to the network CIDR block for the network that the ``nginx_statsd_sidecar``
container is running on, or its particular IP address.  This is left as an
exercise for the reader.

Once you get everything working, you can add the ``access_log off;`` to the
``location`` block to prevent logging the requests to the ``nginx`` logs and
clogging up your logs.


nginx_statsd_sidecar configuration
----------------------------------

The ``nginx_statsd_sidecar`` container supports environment variables as configuration.

Environment
-----------


.. important::

    You must set at least these environment variables:

    * :envvar:`STATSD_HOST`
    * :envvar:`STATSD_PREFIX`
    * :envvar:`NGINX_HOST`

    You should also look at these variables to see whether their defaults work
    for you:

    * :envvar:`DEBUG`
    * :envvar:`INTERVAL`
    * :envvar:`NGINX_IS_HTTPS`
    * :envvar:`NGINX_PORT`
    * :envvar:`NGINX_STATUS_PATH`
    * :envvar:`SENTRY_URL`


General
^^^^^^^

.. envvar:: DEBUG

    Set to ``1`` or ``True`` to enable debug mode for additional logging. Defaults to ``False``.

.. envvar:: INTERVAL

    The interval in seconds between reporting metrics to StatsD. Defaults to ``10``.

.. envvar:: SENTRY_URL

    The Sentry DSN to use for error reporting.  If this is ``None``, no
    error reporting will be done.  This is optional.

nginx settings
^^^^^^^^^^^^^^

.. envvar:: NGINX_PORT

    The port of the nginx server. Defaults to ``443``.

.. envvar:: NGINX_HOST

    The host of the nginx server. Defaults to ``localhost``.

.. envvar:: NGINX_IS_HTTPS

    Whether the nginx server is using HTTPS. Defaults to ``True``.

.. envvar:: NGINX_STATUS_PATH

    The path to the nginx status page. Defaults to ``/server-status``.


statsd settings
^^^^^^^^^^^^^^^

.. envvar:: STATSD_HOST

    The host of the StatsD server. Defaults to ``127.0.0.1``.

.. envvar:: STATSD_PORT

    The port of the StatsD server. Defaults to ``8125``.

.. envvar:: STATSD_PREFIX

    The prefix to use for the StatsD metrics. Defaults to ``nginx``.
