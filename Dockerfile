FROM python:3.7
COPY . /app_resource
COPY ./docker/README.md /data/README.md
COPY ./docker/supervisord.conf /etc/supervisor/supervisord.conf
WORKDIR /app_resource

ENV STREAM_SYNC=True

RUN cd /app_resource && \
    apt-get update && \
    apt-get install -y python-pip && \
    pip2 install supervisor && \
    pip install -r requirements.txt && \
    pip install https://codeload.github.com/ZeoAlliance/aiomongo/zip/master

CMD ["supervisord"]
