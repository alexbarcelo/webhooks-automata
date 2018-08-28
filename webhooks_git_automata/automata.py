import os.path
import subprocess
from logging import getLogger, DEBUG

logger = getLogger("webhooks.actions")


class MetaAutomata(type):
    """Metaclass required to provide a `__getitem__` method to Automata class.

    When Automata[<repo>, <branch>] is called, the corresponding Automaton
    instance is returned ready to be used by the worker.

    The alias Automata[<name_as_in_yaml>] is also stored, and used by the
    manual trigger entrypoint. See also webhooks.manual_trigger
    """
    actions = dict()

    def __getitem__(cls, item):
        """Given a (repo, branch) tuple, return its automaton."""
        return cls.actions[item]

    def load_config(cls, actions):
        """Given its configuration section, create and store the automaton instances."""
        for name, automaton in actions.items():
            repo = automaton.pop("repo", name)
            branch = automaton.pop("branch", "master")

            instance = cls(automaton, repo, branch)

            # Store both lookups
            cls.actions[repo, branch] = instance
            cls.actions[name] = instance


class Automata(object, metaclass=MetaAutomata):
    """Manage the set of automaton instances.

    With the method helpers of its metaclass MetaAutomata, manage a set of
    automaton (one per repository and branch).
    """
    def __init__(self, action, repo, branch):
        self._action = action
        self._repo = repo
        self._branch = branch

    def pull_sources(self):
        os.chdir(self._action["repodir"])
        submodules = self._action.get("submodules", True)
        logger.info("Proceeding to pull changes (fetch + checkout)")

        git_fetch = ["/usr/bin/git", "fetch"]
        if submodules:
            git_fetch.append("--recurse-submodules=yes")

        git_checkout = ["/usr/bin/git", "checkout", "-f", "origin/%s" % self._branch]

        git_submodule_update = ["/usr/bin/git", "submodule", "update"]

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

    def perform_commands(self):
        os.chdir(self._action["workdir"])
        for command in self._action["commands"]:
            ret = subprocess.call(command)
            if ret != 0:
                logger.error("Could not perform the following command: `%s`",
                             " ".join(command))
                raise RuntimeError("A subprocess command failed")
            logger.debug("Command `%s` executed", " ".join(command))

        logger.info("All commands executed")
