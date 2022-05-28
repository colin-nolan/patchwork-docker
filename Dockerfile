ARG baseImage=python:3.8
FROM ${baseImage}

ENV INSTALL_DIRECTORY=/usr/local/src/patchwork-docker
ENV PYTHONPATH=${INSTALL_DIRECTORY}

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . "${INSTALL_DIRECTORY}"

# TODO: Install into CLI
ENTRYPOINT ["python", "/usr/local/src/patchwork-docker/patchworkdocker/cli.py"]

CMD ["--help"]
