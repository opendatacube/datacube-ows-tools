FROM ubuntu:18.04

# Make sure apt doesn't ask questions
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    # Extra python components, to speed things up
    python3 python3-setuptools python3-wheel\
    python3-pip python3-dev \
    # Git to work out the ODC version number
    git  git-core \
    && rm -rf /var/lib/apt/lists/*

# Set the locale, this is required for some of the Python packages
ENV LC_ALL C.UTF-8

# Ensure pip is up to date
RUN pip3 install --upgrade pip \
    && rm -rf $HOME/.cache/pip

RUN pip3 install -U pip && rm -rf $HOME/.cache/pip

RUN pip3 install flask flask-s3 requests gunicorn gevent owslib && rm -rf $HOME/.cache/pip

WORKDIR /opt/odc/datacube-ows-tools
ADD . .

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--timeout", "121", "datacube-ows-tools.app:app"]
