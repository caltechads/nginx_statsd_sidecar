#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="nginx_statsd_sidecar",
    version="0.1.0",
    description="A sidecar container for sending nginx performance stats to statsd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['nginx', 'docker', 'monitoring', 'observability', 'statsd'],
    author="Caltech IMSS ADS",
    author_email="imss-ads-staff@caltech.edu",
    packages=find_packages(exclude=["bin"]),
    include_package_data=True,
    package_data={'nginx_statsd': ["py.typed"]},
    entry_points={
        'console_scripts': ['sidecar = nginx_statsd.main:main']
    },
    install_requires=[
        # https://github.com/MagicStack/uvloop
        'uvloop==0.17.0',
        # https://github.com/projectdiscovery/httpx
        'httpx[http2]==0.24.0',
        # https://github.com/Gr1N/aiodogstatsd
        'aiodogstatsd==0.16.0.post0',
        # https://github.com/samuelcolvin/pydantic
        'pydantic>=1.9.0',
        # https://github.com/hynek/structlog
        'python-json-logger==2.0.7',
        # https://github.com/pallets/click
        'click>=8.0'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring"
    ],
)
