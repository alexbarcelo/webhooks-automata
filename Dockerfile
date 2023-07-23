FROM python:3.11

WORKDIR /app

COPY requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY webhooks_automata ./webhooks_automata

ENV AUTOMATA_SETTINGS /config/wha_settings.yaml

VOLUME [ "/config" ]
VOLUME [ "/plugins" ]

EXPOSE 8000

CMD ["uvicorn", "webhooks_automata.app:app", "--host", "0.0.0.0", "--port", "8000"]
