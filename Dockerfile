FROM ubuntu:20.04

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y python3-pip unzip curl python3.8-venv

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add poetry install location to PATH
ENV PATH=/usr/local/bin:$PATH

# Disable virtualenv for docker
RUN /root/.local/bin/poetry config virtualenvs.create false --local

# Add poetry requirements lock
ADD poetry.lock pyproject.toml ./

# Install
RUN pip install awscli &&\
    /root/.local/bin/poetry export --without-hashes > requirements.txt && \
    pip install -r requirements.txt

# Fetch-and-run setup
# https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/
ADD fetch_and_run.sh /usr/local/bin/fetch_and_run.sh
RUN chmod +x /usr/local/bin/fetch_and_run.sh
WORKDIR /tmp
ENTRYPOINT ["/usr/local/bin/fetch_and_run.sh"]
