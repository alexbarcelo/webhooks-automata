from functools import partial
import os.path
import subprocess
from abc import ABC, abstractmethod
from logging import getLogger, DEBUG

from flask import request

from ..worker import event_queue

logger = getLogger("webhooks.automata")


class Automaton(ABC):
    """An Automaton, a thing that will be executed as a reaction to a webhook."""
    @abstractmethod
    def __init__(self, name, provider_opts, config, action):
        """Initialization of the automaton instance.

        provider_opts: configuration options for the provider (e.g. GitHub secret)
        config: configuration for this automaton (e.g. repository path)
        action: configuration for the action to perform (e.g. list of commands)
        """
        self._name = name
        self._provider_opts = provider_opts
        self._config = config
        self._action = action

        # Default is to accept POST
        self._methods = ["POST"]

    @abstractmethod
    def perform_actions(self):
        pass

    @abstractmethod
    def receive_webhook(self, request):
        pass

    def _schedule(self, data = None):
        """Schedule the `perform_actions` call through the worker.

        This typically is called from an ongoing request. An entry is added
        to the worker event_queue for later processing.
        """
        event_queue.put((self, data))

    def _execute_commands(self, command_list):
        for command in command_list:
            ret = subprocess.call(command)
            if ret != 0:
                logger.error("Could not perform the following command: `%s`",
                             " ".join(command))
                raise RuntimeError("A subprocess command failed")

            logger.debug("Command `%s` executed", " ".join(command))

    def _view_wrapper(self):
        logger.info("Automata `%s` is attending a call", self._name)
        self.receive_webhook(request)
        return ""

    def to_flask_view(self):
        ret = partial(self._view_wrapper)
        ret.methods = self._methods
        return ret


class GitAutomaton(ABC):
    def _pull_sources(self):
        os.chdir(self._config["repodir"])
        submodules = self._action.get("submodules", True)
        gitbinary = self._action.get("git_binary", "/usr/bin/git")
        logger.info("Proceeding to pull changes (fetch + checkout)")

        git_fetch = [gitbinary, "fetch"]
        if submodules:
            git_fetch.append("--recurse-submodules=yes")

        git_checkout = [gitbinary, "checkout", "-f", "origin/%s" % self._branch]

        git_submodule_update = [gitbinary, "submodule", "update"]

        ret = subprocess.call(git_fetch)
        if ret != 0:
            raise RuntimeError("git fetch process failed with exitcode %d" % ret)

        ret = subprocess.call(git_checkout)
        if ret != 0:
            raise RuntimeError("git checkout process failed with exitcode %d" % ret)

        if submodules:
            ret = subprocess.call(git_submodule_update)
            if ret != 0:
                raise RuntimeError("git submodule update failed with exitcode %d" % ret)

    def perform_actions(self):
        os.chdir(self._action["workdir"])

        self._execute_commands(self._action.get("pre_commands", []))

        if self._action.get("pull", True):
            logger.info("Performing a git pull")
            self._pull_sources()

        # I couldn't settle between "commands" and "post_commands",
        # so decided to make them almost equivalent. Please don't use both.
        self._execute_commands(self._action.get("commands", []))
        self._execute_commands(self._action.get("post_commands", []))

        logger.info("All commands executed")
