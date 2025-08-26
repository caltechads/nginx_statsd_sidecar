Installation Guide
==================

This guide covers installing ``nginx_statsd_sidecar``.

``nginx_statsd_sidecar`` is a Docker container that runs ``nginx`` and ``statsd`` and forwards the metrics to ``statsd``.

Prerequisites
-------------

**System Requirements**
    - Something that can run Docker containers: Docker Desktop, ECS, containerd, Kubernetes, etc.
    - An ``nginx`` container configured with the `ngx_http_stub_status_module <https://nginx.org/en/docs/http/ngx_http_stub_status_module.html>`_ enabled

Installation Methods
--------------------

Using docker compose
^^^^^^^^^^^^^^^^^^^^

I'm assuming here you have Docker Desktop installed.  If you don't, you can
install it from `Docker Desktop <https://www.docker.com/products/docker-desktop/>`_.

I'm also assuming you have a ``nginx`` configuration file in ``./etc/nginx/nginx.conf`` and
SSL certificates in ``./etc/nginx/certs``.  If you don't, you can create them.

Here's an example ``docker-compose.yml`` file:

.. code-block:: yaml

    nginx:
      image: nginx:latest
      container_name: nginx
      ports:
        - "8443:443"
      volumes:
        - ./etc/nginx/nginx.conf:/etc/nginx/nginx.conf
        - ./etc/nginx/certs:/certs

    nginx_statsd_sidecar:
      image: caltechads/nginx_statsd_sidecar:0.2.0
      container_name: nginx_statsd_sidecar
      environment:
        - NGINX_HOST=nginx
        # Note that you need to use the container port here, not the host port.
        - NGINX_PORT=443
        - NGINX_STATUS_PATH=/server-status
        - STATSD_HOST=statsd.example.com
        - STATSD_PREFIX=myapp.nginx
      links:
        - nginx

This will:

- Start an ``nginx`` container and a ``nginx_statsd_sidecar`` container
- ``nginx_statsd_sidecar`` will:

    - scrape stats from ``nginx:443``, path ``/server-status`` on port 443 using SSL
    - Report them every 10 seconds and to ``statsd.example.com``
    - The stats will be reported with the prefix ``myapp.nginx``

Assuming you're using graphite to store your metric data, the stats will be available
at the following paths:

- ``stats.myapp.nginx.requests``
- ``stats.myapp.nginx.active_connections``
- ``stats.myapp.nginx.workers.reading``
- ``stats.myapp.nginx.workers.writing``
- ``stats.myapp.nginx.workers.waiting``

Using deployfish
^^^^^^^^^^^^^^^^

``deployfish`` is a tool for deploying Docker containers to AWS ECS that we use at Caltech.  It's
available on `GitHub: deployfish <https://github.com/caltechads/deployfish>`_.

Let's say you have a ``myapp`` container that runs ``nginx`` on port 8443 using SSL and you want to
forward the stats to ``statsd.example.com`` with the prefix ``myapp.nginx``.

Here's a ``deployfish.yml`` file that will deploy the ``nginx_statsd_sidecar`` container to AWS ECS:

.. code-block:: yaml

    services:
      - name: myapp-prod
        cluster: my-cluster
        environment: prod
        count: 1
        load_balancer:
          target_group_arn: arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-app/123456789012
          container_name: myapp
          container_port: 8443
        family: myapp-prod
        launch_type: FARGATE
        network_mode: awsvpc
        enable_exec: true
        vpc_configuration:
          subnets: subnet-01234567890123456,subnet-01234567890123457
          security_groups: sg-01234567890123456
        task_role_arn: arn:aws:iam::123456789012:role/my-app-task-role
        execution_role: arn:aws:iam::123456789012:role/my-app-execution-role
        cpu: 2048
        memory: 4096
        containers:
          - name: myapp
            image: my-org/myapp:latest
            cpu: 1920
            memory: 3840
            ports:
              - 8443:8443
            logging:
              driver: awslogs
              options:
                awslogs-group: /my/loggroup
                awslogs-region: us-west-2
                awslogs-stream-prefix: myapp-prod
          - name: nginx_statsd_sidecar
            image: caltechads/nginx_statsd_sidecar:0.2.0
            cpu: 128
            memory: 256
            environment:
              # The name of the container running nginx.
              - NGINX_HOST=myapp
              # Note that you need to use the container port here, not the host port.
              - NGINX_PORT=8443
              - NGINX_STATUS_PATH=/server-status
              - STATSD_HOST=statsd.example.com
              - STATSD_PREFIX=myapp.nginx
            logging:
              driver: awslogs
              options:
                awslogs-group: /my/loggroup
                awslogs-region: my-region
                awslogs-stream-prefix: myapp-prod


This will:

- Start a single task with two containers: ``myapp`` and ``nginx_statsd_sidecar``
- ``myapp`` will run ``nginx`` on port 8443 using SSL, and has the ``ngx_http_stub_status_module`` enabled on the ``/server-status`` path
- ``nginx_statsd_sidecar`` will scrape stats from the ``myapp`` container, port 8443, path ``/server-status`` using SSL
- ``nginx_statsd_sidecar`` will report them every 10 seconds to ``statsd.example.com``
- The stats will be reported with the prefix ``myapp.nginx``
- The stats will be available at the following paths:

    - ``stats.myapp.nginx.requests``
    - ``stats.myapp.nginx.active_connections``
    - ``stats.myapp.nginx.workers.reading``
    - ``stats.myapp.nginx.workers.writing``
    - ``stats.myapp.nginx.workers.waiting``

- The Fargate task will have 2048 CPU and 4096 MB of memory
- The ``myapp`` container will have 1920 CPU and 3840 MB of memory
- The ``nginx_statsd_sidecar`` container will have 128 CPU and 256 MB of memory
- Note that we restrict the ``nginx_statsd_sidecar`` container to 128 CPU and 256 MB of memory to avoid
  using too much memory on the Fargate task, leaving most for your app.

ECS Task definition JSON
^^^^^^^^^^^^^^^^^^^^^^^^

Here's a JSON file that will create an ECS Task definition for the ``nginx_statsd_sidecar`` container:

.. code-block:: json

    {
        # ...
        "containerDefinitions": [
        {
            "name": "myapp",
            "image": "my-org/myapp:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8443,
                    "protocol": "tcp"
                }
            ],
            # ...
        },
        {
            "name": "nginx-statsd-sidecar",
            "image": "caltechads/nginx_statsd_sidecar:latest",
            "essential": false,
            "environment": [
                {
                    "name": "NGINX_HOST",
                    "value": "myapp"
                },
                {
                    "name": "NGINX_PORT",
                    "value": "8443"
                },
                {
                    "name": "NGINX_STATUS_PATH",
                    "value": "/server-status"
                },
                {
                    "name": "STATSD_HOST",
                    "value": "statsd.example.com"
                },
                {
                    "name": "STATSD_PREFIX",
                    "value": "myapp.nginx"
                }
            ],
            # ...
        },
        # ...
    }


Troubleshooting
---------------

See :doc:`/overview/faq` for troubleshooting tips.

Getting Help
------------

If you encounter installation issues:

1. **Read the docs**: :doc:`/overview/installation`
2. **Check the FAQ**: :doc:`/overview/faq`
3. **Report Issues**: Open an issue on GitHub with detailed error information
