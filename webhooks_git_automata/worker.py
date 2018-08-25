import os
from logging import getLogger
from queue import Queue

from .automata import Automata

logger = getLogger('webhooks.worker')

event_queue = Queue()


def async_worker():
    """Asynchronous worker to trigger automaton operations."""
    logger.info("Worker started, going into eternal loop")

    while True:
        data = event_queue.get()

        logger.debug("Received ref: %s from repository %s (%s)",
                     data["ref"], data["repository"]["name"],
                     data["repository"]["html_url"])

        refs, heads, branch = data["ref"].split('/')
        if refs != "refs" or heads != "heads":
            logger.error("Received unrecognized ref: %s", data["ref"])
            continue

        repo = data["repository"]["name"]

        try:
            automaton = Automata[repo, branch]
        except KeyError:
            logger.info('Repository %s for branch %s ("%s" at %s) not found in actions.json',
                        repo, branch, data["repository"]["name"], data["repository"]["html_url"])
            continue

        automaton.pull_sources()

        logger.debug("All git operations finished, proceeding to commands")

        automaton.perform_commands()

        logger.debug("All comands finished, job is done")
