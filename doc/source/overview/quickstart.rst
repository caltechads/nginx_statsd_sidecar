Quickstart Guide
================

This guide will get you up and running with ``nginx_statsd_sidecar`` quickly,
showing the ``nginx`` configuration and a ``docker-compose.yml`` file to run both it
and the ``nginx_statsd_sidecar`` container.

.. note::

    For a `deployfish <https://github.com/caltechads/deployfish>`_ example, see
    :doc:`/overview/installation`.

Prerequisites
-------------

- Docker Desktop

Configuration
-------------

Let's start with the ``nginx`` configuration.  We can use the official ``nginx``
docker image, create our own ``nginx.conf`` file and mount it into the container
along with some certs.

First ensure that ``nginx`` has been compiled with the ``ngx_http_stub_status_module`` module;
it usually is.

.. code-block:: bash

    $ docker run --rm nginx:latest nginx -V

If you see ``--with-http_stub_status_module`` in the output, you're good to go.

Now create a ``nginx.conf`` file that looks like this:

.. code-block:: text

    user nginx;
    worker_processes auto;

    error_log  /dev/stderr info;
    pid /tmp/nginx.pid;

    events {
      worker_connections 1024;
    }


    http {
      include /etc/nginx/mime.types;
      default_type application/octet-stream;

      # Write our logs a JSON to stdout, just like a good citizen.
      log_format json_combined escape=json
      '{'
          '"type": "access", '
          '"program": "nginx", '
          '"time_local": "$time_iso8601", '
          '"remote_addr": "$http_x_forwarded_for", '
          '"remote_user": "$http_user", '
          '"request": "$request", '
          '"status": "$status", '
          '"method": "$request_method", '
          '"path": "$uri", '
          '"response_length": "$body_bytes_sent", '
          '"request_time": "$request_time", '
          '"http_referrer": "$http_referer", '
          '"http_user_agent": "$http_user_agent", '
          '"host": "$http_host" '
      '}';
      access_log /dev/stdout json_combined;

      sendfile on;
      tcp_nopush on;

      server {
        listen 443 ssl http2;
        server_name localhost;

        # Don't send the nginx version number in error pages or the Server header.
        server_tokens off;

        ssl_certificate /certs/localhost.crt;
        ssl_certificate_key /certs/localhost.key;

        ssl_session_cache shared:SSL:50m;
        ssl_session_timeout 1d;
        ssl_session_tickets on;
        add_header Strict-Transport-Security "max-age=63072000";
        add_header X-XSS-Protection "1; mode=block";

        # Disable the TRACE and TRACK methods.
        if ($request_method ~ ^(TRACE|TRACK)$ ) {
           return 405;
        }

        location = /server-status {
            stub_status;
            allow 127.0.0.1;
            allow ::1;
            allow 192.168.0.0/24;
            deny all;
        }

        location = /favicon.ico { access_log off; log_not_found off; }

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }
      }
    }

Finally, create a ``certs`` directory and put your SSL certificates in it.

.. code-block:: bash

    $ mkdir -p certs
    # Generate a self-signed SSL cert for nginx to use, good for 10 years.
    $ openssl req -x509 -nodes \
        -days 3650 \
        -subj "/CN=localhost"
        -newkey rsa:4096 \
        -keyout certs/localhost.key \
        -out certs/localhost.crt


Docker Compose
--------------

Create a ``docker-compose.yml`` file that looks like this:

.. code-block:: yaml

    ---
    services:

      nginx:
        image: nginx:latest
        container_name: nginx
        ports:
          - "8443:443"
        volumes:
          - ./nginx.conf:/etc/nginx/nginx.conf
          - ./certs:/certs

      nginx_statsd:
        image: nginx_statsd_sidecar:latest
        container_name: nginx_statsd
        environment:
          - NGINX_HOST=nginx
          # Note that you need to use the container port here, not the host port.
          - NGINX_PORT=443
          - STATSD_HOST=statsd.example.com
          - STATSD_PREFIX=test.nginx
        links:
          - nginx
        volumes:
          - .:/app

Run it
------

.. code-block:: bash

    $ docker compose up

After any pulls are done, you should see the following output:

.. code-block:: text

    nginx_statsd  | {"message": "HTTP Request: GET https://nginx/server-status \"HTTP/2 200 OK\""}
    nginx_statsd  | {"message": "reporter.success", "retrieved": true, "active_connections": 1, "requests": 1, "reading": 0, "writing": 1, "waiting": 0}

Go to ``https://localhost:8443/`` and refresh a bunch of times and you'll see
the stats being reported to ``statsd.example.com``.

.. code-block:: text

    nginx_statsd  | {"message": "reporter.success", "retrieved": true, "active_connections": 5, "requests": 10, "reading": 0, "writing": 3, "waiting": 2}


Getting Help
------------

- Check the full documentation for detailed examples
- Review the troubleshooting sections in each guide
- Report issues on the GitHub repository
