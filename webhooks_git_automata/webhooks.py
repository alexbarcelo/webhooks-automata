import sys
import logging
from functools import partial
from threading import Thread

from flask import Flask

from .settings import Configuration
from .worker import async_worker
from .automata import Automata
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

    try:
        webhook_func = getattr(providers, "webhook_%s" % Configuration.provider)
    except AttributeError:
        raise RuntimeError("Could not prepare the webhook for provider %s. "
                           "Maybe it is not supported?" % Configuration.provider)

    webhook = partial(
        webhook_func,
        **Configuration.provider_options
    )

    app.add_url_rule('/webhook', 'webhook', webhook, methods=['POST'])
    app.run(host=Configuration.listen_ip,
            port=Configuration.listen_port)


def manual_trigger():
    if len(sys.argv) != 3:
        raise RuntimeError("You should provide the path to the settings YAML file as first argument "
                           "and the repository entry name (YAML key) that will be triggered")

    Configuration.load(sys.argv[1])
    try:
        automaton = Automata[sys.argv[2]]
    except KeyError:
        raise RuntimeError("Unrecognized repository name '%s'" % sys.argv[2])

    automaton.pull_sources()
    automaton.perform_commands()
