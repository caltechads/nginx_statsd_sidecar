Frequently Asked Questions
==========================

This section addresses common questions and troubleshooting scenarios for ``nginx_statsd_sidecar``.

I never see hits to the ``ngx_http_stub_status_module`` endpoint in ``nginx``
-----------------------------------------------------------------------------

You're up and running, but when you check your application logs, you don't see
any hits to the ``ngx_http_stub_status_module`` endpoint in ``nginx``.

You should see something like this in the ``nginx_statsd_sidecar`` logs:

.. code-block:: json

    {"message": "scraper.init url=https://myapp:8443/server-status"}

.. note::

    This line will, of course, be different depending on what you configured as ``NGINX_HOST``, ``NGINX_STATUS_PATH``
    and ``NGINX_PORT`` to be.

The ``url`` in the log is the URL that ``nginx_statsd_sidecar`` has been configured with to GET the stats from the ``ngx_http_stub_status_module`` endpoint in ``nginx``.

- Is ``myapp:8443`` the correct host and port?
- Are you not logging the ``nginx_statsd_sidecar`` hits (aka you have ``access_log off`` in your ``location = /server-status`` block)?

If you're not sure, you can try to reach the endpoint from the ``nginx_statsd_sidecar`` container using ``curl``:

.. code-block:: bash

    curl -s https://myapp:8443/server-status

I see the hits from ``nginx_statsd_sidecar`` in ``nginx`` logs, but they all return 401/403
-------------------------------------------------------------------------------------------

You're up and running, but when you check your ``nginx`` logs, you see hits to
the ``ngx_http_stub_status_module`` endpoint, but they all return 401/403.

You should see something like this in the ``nginx`` logs:

.. code-block:: json

    {"message": "HTTP Request: GET https://nginx:8443/server-status \"HTTP/2 401 Unauthorized\""}

.. note::

    This line will, of course, be different depending on what you configured as ``NGINX_HOST``, ``NGINX_STATUS_PATH``
    and ``NGINX_PORT`` to be.

- In your ``location = /server-status`` block, are you restricting access to the endpoint?

    - If you're using ``allow`` and ``deny`` directives, make sure that the ``nginx_statsd_sidecar`` container's IP address is in the ``allow`` list.

        - For ECS, this will be 127.0.0.1, and the IPv6 equivalent ``::1`` since the container runs on the same host as your application.
        - Otherwise, see what your ``nginx_statsd_sidecar`` container's IP address is and ensure that it is in the ``allow`` list.


I see the hits from ``nginx_statsd_sidecar`` in ``nginx`` logs, but they all return 404
---------------------------------------------------------------------------------------

Again look at the ``nginx_statsd_sidecar`` logs to see if you can see this line:

.. code-block:: json

    {"message": "HTTP Request: GET https://nginx:8443/server-status \"HTTP/2 404 Not Found\""}

.. note::

    This line will, of course, be different depending on what you configured as ``NGINX_HOST``, ``NGINX_STATUS_PATH``
    and ``NGINX_PORT`` to be.

If you see the hits from ``nginx_statsd_sidecar`` in ``nginx`` logs, but they all return 404, there are a few things you can check:

- Is ``ngx_http_stub_status_module`` enabled in ``nginx``?
- Is the ``/server-status`` endpoint enabled in ``nginx`` as ``location = /server-status`` (or whatever you configured as ``NGINX_STATUS_PATH``)?

Stats seem to be being gathered, but not being reported to statsd
-----------------------------------------------------------------

``nginx_statsd_sidecar`` will log each time it scrapes stats from ``nginx`` and reports them to ``statsd``, in JSON format.

You should see something like this in the logs:

.. code-block:: json

    {"message": "scraper.init url=https://myapp:8443/server-status"}
    {"message": "HTTP Request: GET https://nginx/server-status \"HTTP/2 200 OK\""}
    {"message": "reporter.success", "retrieved": true, "active_connections": 1, "requests": 4, "reading": 0, "writing": 1, "waiting": 0}

If you see this last line (``reporter.success``), but the stats are not being
reported to ``statsd``, there are a few things you can check:


1. Are you looking in the right place for the ``statsd`` stats in your backend storage?

    - If you're using graphite, you'll want to look in the ``stats.${STATSD_PREFIX}.`` prefix.
    - I've never used any other backend storage for ``statsd``, so I can't say for sure what the correct prefix is for InfluxDB, for example.

2. Check that the ``statsd`` host is reachable from the ``nginx_statsd_sidecar`` container

    - Its domain name resolves (``host statsd.example.com``)
    - You can reach it from the ``nginx_statsd_sidecar`` container.  The container has ``nmap`` installed,  So you can
      run ``nmap -sU statsd.example.com`` to see if UDP port 8125 is open and reachable.

3. If possible, look at the ``statsd`` logs to see if the metrics are being accepted.  You should see something like this:

    .. code-block:: text

       {
         counters: {
           'statsd.bad_lines_seen': 0,
           'statsd.packets_received': 5,
           'statsd.metrics_received': 5,
           'myapp.nginx.requests': 1,
           'myapp.nginx.active_connections': 1,
           'myapp.nginx.workers.reading': 0,
           'myapp.nginx.workers.writing': 1,
           'myapp.nginx.workers.waiting': 0
         },
         timers: {},
         gauges: { 'statsd.timestamp_lag': 0 },
         timer_data: {},
         counter_rates: {
           'statsd.bad_lines_seen': 0,
           'statsd.packets_received': 0.5,
           'statsd.metrics_received': 0.5,
           'myapp.nginx.requests': 0.1,
           'myapp.nginx.active_connections': 0.1,
           'myapp.nginx.workers.reading': 0,
           'myapp.nginx.workers.writing': 0.1,
           'myapp.nginx.workers.waiting': 0
         },
         sets: {},
         pctThreshold: [ 90 ]
       }

4. Check that the backend storage for ``statsd`` is not full and thus cannot accept new metrics

Getting Help
------------

Where can I get more help?
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Documentation**:

    - **Usage Guide**: :doc:`/overview/installation` for detailed nginx and ``nginx_statsd_sidecar`` setup options
    - **Configuration**: :doc:`/overview/configuration` for setup options
    - **Quickstart**: :doc:`/overview/quickstart` for basic examples

**Troubleshooting**:

    - Check this FAQ section
    - Review error messages carefully

**Community Support**:

    - GitHub Issues: Report bugs and request features
    - GitHub Discussions: Ask questions and share solutions
    - Documentation Issues: Report documentation problems
