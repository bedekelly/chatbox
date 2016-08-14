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

# Configure nginx.
COPY ops/nginx.conf /etc/nginx/nginx.conf

# Install python dependencies.
COPY ops/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Copy our source code.
COPY src /src
COPY scripts /scripts

WORKDIR /src
CMD nginx && bash /scripts/prod_run.sh
