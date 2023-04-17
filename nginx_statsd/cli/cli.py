#!/usr/bin/env python
import sys

import click

import nginx_statsd


@click.group(invoke_without_command=True)
@click.option('--version/--no-version', '-v', default=False, help="Print the current version and exit.")
@click.pass_context
def cli(ctx, version):
    """
    nginx_statsd_sidecar command line interface.
    """
    if version:
        print(nginx_statsd.__version__)
        sys.exit(0)
