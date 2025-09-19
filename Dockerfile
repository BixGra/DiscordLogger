FROM python:3.13

WORKDIR /etc/DiscordLogger

COPY . /etc/DiscordLogger/.

RUN pip install --upgrade pip && pip --no-cache-dir install -r /etc/DiscordLogger/requirements.txt

ENV PYTHONPATH $PYTHONPATH:$PATH:/etc/DiscordLogger/src/

ENV PATH /opt/conda/envs/env/bin:$PATH

ENV PROJECT_PATH /etc/DiscordLogger/src/

EXPOSE 8000

ENTRYPOINT gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker src.main:app --threads 2 --workers 1 --timeout 1000 --graceful-timeout 30
