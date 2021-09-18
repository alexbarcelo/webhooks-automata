import os
from logging import getLogger

from .base_classes import Automaton

logger = getLogger(__name__)


class PlainAutomaton(Automaton):
    """Automaton for plain webhooks.

    This automaton is very simple and just executed a list of commands,
    with no request verification whatsoever.
    """
    def receive_webhook(self, request):
        self._schedule()
        return ""

    def perform_actions(self):
        os.chdir(self._action["workdir"])

        self._execute_commands(self._action["commands"])

        logger.info("All commands executed")
