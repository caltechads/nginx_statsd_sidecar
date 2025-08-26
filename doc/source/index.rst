====================
nginx_statsd_sidecar
====================

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   overview/installation
   overview/quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   overview/configuration
   overview/faq

.. toctree::
   :maxdepth: 2
   :caption: Development
   :hidden:

   runbook/contributing
   runbook/coding_standards

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   changelog

Current version is |release|.

``nginx_statsd_sidecar`` is a Docker container that runs as a sidecar to
``nginx``.  It scrapes the stats from the `ngx_http_stub_status_module
<https://nginx.org/en/docs/http/ngx_http_stub_status_module.html>`_ and forwards
them to `statsd <https://github.com/statsd/statsd>`_.  This is useful for both
server-bound and serverless (e.g. ECS Fargate) services, where you don't have
access to the underlying server filesystem and processes.

``nginx_statsd_sidecar`` polls stats from ``nginx`` every 10 seconds (this is
configurable via an environment variable) and reports stats to ``statsd`` (with
a configurable prefix).

- ``requests`` the number of requests that ``nginx`` has handled since the last time ``nginx_statsd_sidecar`` retrieved stats from ``nginx``
- ``active_connections`` the number of currently active ``nginx`` connections
- ``reading`` the number of active ``nginx`` connections in reading state
- ``writing`` the number of active ``nginx`` connections in writing state
- ``waiting`` the number of active ``nginx`` connections in waiting state

If your prefix is ``myapp.nginx``, then the stats will be reported to ``statsd`` as follows:

- ``stats.myapp.nginx.requests``
- ``stats.myapp.nginx.active_connections``
- ``stats.myapp.nginx.workers.reading``
- ``stats.myapp.nginx.workers.writing``
- ``stats.myapp.nginx.workers.waiting``

Architectures
-------------

``nginx_statsd_sidecar`` is available for the following architectures:

- ``linux/amd64``
- ``linux/arm64``

Getting Started
---------------

To get started with ``nginx_statsd_sidecar``:

1. **Installation**: Follow the :doc:`/overview/installation` guide
2. **Quick Start**: See the :doc:`/overview/quickstart` guide for basic usage
3. **Configuration**: Learn about configuration options in :doc:`/overview/configuration`
4. **FAQ**: Check the :doc:`/overview/faq` section for common questions and troubleshooting

For developers, see the :doc:`/runbook/contributing` and :doc:`/runbook/coding_standards` guides.