import sys
import logging
from functools import partial
from threading import Thread

from flask import Flask

from .settings import Configuration
from .worker import async_worker
from .automata import automata
from . import providers


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("webhooks")
app = Flask(__name__)


def main_func():
    if len(sys.argv) != 2:
        raise RuntimeError("You should provide the path to the settings YAML file as first argument")

    Configuration.load(sys.argv[1])

    # Future work: check the settings and allow multiple worker implementations (e.g. Celery)
    Thread(target=async_worker,
           name="webhook worker").start()

    for name, automaton in automata.items():
        app.add_url_rule(f'{ Configuration.webhook_url_path }/{ name }', 
                         name, automaton.to_flask_view())

    app.run(host=Configuration.listen_ip,
            port=Configuration.listen_port)


def manual_trigger():
    if len(sys.argv) != 3:
        raise RuntimeError("You should provide the path to the settings YAML file as first argument "
                           "and the name of the automaton to be triggered (YAML key)")

    Configuration.load(sys.argv[1])
    try:
        automaton = automata[sys.argv[2]]
    except KeyError:
        raise RuntimeError("Unrecognized automaton name '%s'" % sys.argv[2])

    automaton.perform_actions()
