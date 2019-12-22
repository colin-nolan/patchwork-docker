ARG baseImage=python:3.7
FROM ${baseImage}

ARG dockerVersion=18.06.1-ce

ENV INSTALL_DIRECTORY=/patchworkdocker
ENV PYTHONPATH=${INSTALL_DIRECTORY}

RUN architecture="$(uname -m)"; \
	case "$architecture" in \
		x86_64) architecture="x86_64" ;; \
		armv7l) architecture="armhf" ;; \
		*) echo >&2 "Error: unsupported architecture ($architecture)"; exit 1 ;;\
    esac; \
    wget -O /tmp/docker.tgz "https://download.docker.com/linux/static/stable/${architecture}/docker-${dockerVersion}.tgz" && \
    tar --extract --file /tmp/docker.tgz --strip-components 1 --directory /usr/local/bin/ && \
    rm /tmp/docker.tgz

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . ${INSTALL_DIRECTORY}
WORKDIR /root

ENTRYPOINT ["python", "/patchworkdocker/patchworkdocker/cli.py"]

CMD ["--help"]
