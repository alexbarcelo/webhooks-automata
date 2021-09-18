from logging import getLogger
from werkzeug.exceptions import Forbidden, BadRequest

from .base_classes import GitAutomaton

logger = getLogger(__name__)


class GogsAutomaton(GitAutomaton):
    """Automaton for Gogs webhooks.
    
    This automaton requires a `secret` config entry.
    """
    def receive_webhook(self, request):
        data = request.get_json(force=True, cache=False)
        if not data:
            raise BadRequest("Unconsistent JSON received")

        secret = self._provider_opts.get("secret")
        if not secret:
            raise SystemError("No `secret` configured, refusing to accept petition")

        try:
            if data["secret"] != secret:
                logger.debug("Received secret: %s, which did not match the expected", data["secret"])
                raise Forbidden("Invalid `secret` provided in HTTP method payload")
        except KeyError:
            raise Forbidden("The request should include the `secret`. "
                            "Have you configured correctly the gogs sever webhook?")

        self._schedule(data)
