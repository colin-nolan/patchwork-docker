FROM ubuntu:16.04

COPY . /data
WORKDIR /data
RUN ./setup-1.sh \
    && ./setup-2.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["--help"]
