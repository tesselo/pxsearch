FROM ubuntu:20.04

# Install python dependencies
ADD requirements.txt requirements.txt
RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y python3-pip unzip &&\
    pip install -r requirements.txt &&\
    pip install awscli

# Fetch-and-run setup
# https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/
ADD fetch_and_run.sh /usr/local/bin/fetch_and_run.sh
RUN chmod +x /usr/local/bin/fetch_and_run.sh
WORKDIR /tmp
ENTRYPOINT ["/usr/local/bin/fetch_and_run.sh"]
