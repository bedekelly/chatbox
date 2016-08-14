FROM python
MAINTAINER chatbox@bede.io
EXPOSE 80

# Install nginx and nano.
RUN apt-get update     &&         \
    apt-get upgrade -y &&         \
    apt-get install -y            \
        nginx                     \
        nano           &&         \
    apt-get clean      &&         \
    rm -rf /var/lib/apt/lists/*   \
           /tmp/*                 \
           /var/tmp/*

# Install python dependencies.
COPY ops/config/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Configure nginx.
COPY ops/config/nginx.conf /etc/nginx/nginx.conf

# Copy our source code.
COPY src /src
COPY ops/scripts /scripts

WORKDIR /src/
CMD nginx && cd /src/src && gunicorn chatbox:app --workers 9 -k "eventlet"
