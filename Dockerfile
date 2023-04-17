FROM python:3.11.3-alpine3.17

USER root

ENV LC_ALL=en_US.utf8 LANG=en_US.utf8 PYCURL_SSL_LIBRARY=nss TZ=America/Los_Angeles

RUN apk update && \
    apk upgrade && \
    # Set the container's timezone to Los Angeles time.
    ln -snf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && \
    rm -r /usr/share/zoneinfo/Africa && \
    rm -r /usr/share/zoneinfo/Antarctica && \
    rm -r /usr/share/zoneinfo/Arctic && \
    rm -r /usr/share/zoneinfo/Asia && \
    rm -r /usr/share/zoneinfo/Atlantic && \
    rm -r /usr/share/zoneinfo/Australia && \
    rm -r /usr/share/zoneinfo/Europe  && \
    rm -r /usr/share/zoneinfo/Indian && \
    rm -r /usr/share/zoneinfo/Mexico && \
    rm -r /usr/share/zoneinfo/Pacific && \
    rm -r /usr/share/zoneinfo/Chile && \
    rm -r /usr/share/zoneinfo/Canada && \
    echo 'America/Los_Angeles' > /etc/timezone && \
    # Add the user under which we will run.
    adduser -H -D sidecar && \
    # Make our virtualenv
    python3 -m venv /ve

ENV PATH /ve/bin:$PATH

RUN pip install --upgrade pip wheel && \
    rm -rf $(pip cache dir)

COPY . /app
WORKDIR /app

RUN pip install -e . && \
    rm -rf $(pip cache dir)

USER sidecar

CMD ["/ve/bin/sidecar", "run"]
