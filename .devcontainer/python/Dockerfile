FROM python:3.11-slim

WORKDIR /tmp/work

COPY requirements.txt ${PWD}

RUN apt-get update \
&& apt-get install -y git \
&& git config --global core.editor "code --wait" \
&& pip install -r requirements.txt

