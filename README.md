# nginx_statsd_sidecar

The purpose of this container is to be deployed alongside a docker container
running nginx and to report the stats that are output from the
[ngx_http_stub_status_module](http://nginx.org/en/docs/http/ngx_http_stub_status_module.html)
module to a statsd server.  It polls stats from nginx every 10 seconds (this is
configurable via an environment variable).

`nginx_statsd_sidecar` reports these stats to statsd:

* `requests` the number of requests that nginx has handled since the last time
  `nginx_statsd_sidecar` retrieved stats from nginx
* `active_connections` the number of currently active nginx connections
* `reading` the number of active nginx connections in reading state
* `writing` the number of active nginx connections in writing state
* `waiting` the number of active nginx connections in waiting state

## Configuration

`nginx_statsd_sidecar` looks at these environment variables when configuring itself:

* `NGINX_HOST`: The host name for the nginx host you want to monitor
* `NGINX_PORT`: The port on which your nginx server listens.  Defaults to 443
* `NGINX_IS_HTTPS`: ``True`` if our `${NGINX_HOST}:${NGINX_PORT}` speaks HTTPS,
  ``False`` otherwise. Defaults to ``True``.
* ``NGINX_STATUS_PATH`: the path on which you've registered your
  `nginx_http_stub_status_module` route.  This must start with a `/`. Defaults
  to `/server-status`
* `INTERVAL`: the reporting interval, in seconds. Default is 10.
* `STATSD_HOST`: the hostname for your statsd host
* `STATSD_PORT`: the port for your statsd host's UDP interface.  Default is 8125.
* `STATSD_PREFIX`: the prefix to use when reporting our metrics.  Do not add a
  trailing period to this.  Defaults to `nginx`

## Deployment in ECS Fargate

Include the `nginx_statsd_sidecar` container in the same task definition as the
container you are wanting to monitor, and add a link from the
`nginx_statsd_sidecar` container to the container you want to monitor.  For example:

```json
{
    ...
    "containerDefinitions": [
        {
            "name": "my-nginx-container",
            "image": "nginx-image:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 443,
                    "hostPort": 443,
                    "protocol": "tcp"
                }
            ],
            ...
        },
        {
            "name": "nginx-statsd-sidecar",
            "image": "caltechads/nginx_statsd_sidecar:latest",
            "essential": false,
            "links: [
                "my-nginx-container:my-nginx-container"
            ]
            "environment": [
                {
                    "name": "NGINX_HOST",
                    "value": "my-nginx-container"
                },
                {
                    "name": "NGINX_PORT",
                    "value": "443"
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
                    "value": "my_nginx_container"
                }
            ],
            ...
        }
    ]
    ...
}
```

## Contributing to the code

### Setup your local virtualenv

You'll need this at least to do `bumpversion` and run `deployfish`.

```bash
pyenv virtualenv 3.11.3 nginx_statsd_sidecar
pyenv local nginx_statsd_sidecar
pip install --upgrade pip wheel
pip install -r requirements.dev.txt
```

### Build the Docker image

Build the image:

```bash
make build
```

### Run the stack

The stack that `docker-compose.yml` runs is comprised of an `nginx` container, a
`statsd` container that writes its data to stdout, and an `nginx_statsd_sidecar`
that reads from `/server-status` on the `nginx` container and sends metrics to
the `statsd` container.

```bash
make dev
```
